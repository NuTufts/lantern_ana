import yaml
import networkx as nx
from typing import Dict, List, Any, Optional, Set
from lantern_ana.io.SampleDataset import SampleDataset
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import ProducerFactory
import ROOT

class ProducerManager:
    """
    Manager class for handling producer dependencies and execution.
    """
    
    def __init__(self):
        """Initialize an empty producer manager."""
        self.producers: Dict[str, ProducerBaseClass] = {}
        self.execution_order: List[str] = []
        self.data_sources = {}  # Will hold SampleDataset instances
    
    def load_configuration(self, config_file: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_file: Path to the YAML configuration file
        """
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create producers from configuration
        for producer_name, producer_config in config.get('producers', {}).items():
            producer_type = producer_config.get('type')
            if not producer_type:
                raise ValueError(f"Producer '{producer_name}' missing required 'type' field")
            
            # Create producer instance
            producer = ProducerFactory.create(
                producer_type, 
                producer_name, 
                producer_config.get('config', {})
            )
            
            self.producers[producer_name] = producer
        
        # Set up sample datasets
        for dataset_name, dataset_config in config.get('datasets', {}).items():
            # Here we would create SampleDataset instances
            # For now, we'll just store the configuration
            self.data_sources[dataset_name] = dataset_config
        
        # Determine execution order based on dependencies
        self._determine_execution_order()
    
    def _determine_execution_order(self) -> None:
        """
        Determine the execution order of producers based on dependencies.
        
        Raises:
            ValueError: If there is a circular dependency
        """
        # Create directed graph for dependency resolution
        graph = nx.DiGraph()
        
        # Add all producers as nodes
        for name in self.producers:
            graph.add_node(name)
        
        # Add edges based on required inputs
        for name, producer in self.producers.items():
            for required in producer.requiredInputs():
                if required in self.producers:
                    graph.add_edge(required, name)  # required must run before name
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(graph):
            print("================================================")
            print("Circular dependency detected in producer configuration")
            self.print_dependency_graph()
            print("-------------------------------------------------")
            raise ValueError("Circular dependency detected in producer configuration")
        
        # Get topological sort (execution order)
        self.execution_order = list(nx.topological_sort(graph))
    
    def prepare_storage(self, output_interface: Any) -> None:
        """
        Prepare storage for all producers.
        
        Args:
            output_interface: The output storage interface
        """
        for name in self.execution_order:
            self.producers[name].prepareStorage(output_interface)
    
    def process_event(self, event_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event through all producers.
        
        Args:
            event_data: Initial data for the event (e.g., gen2ntuple tree entry)
            params: Additional parameters for processing
            
        Returns:
            Dictionary mapping producer names to their outputs for this event
        """
        results = {}
        
        # Include initial data in results
        results.update(event_data)
        
        # Process each producer in order
        for name in self.execution_order:
            producer = self.producers[name]
            result = producer.processEvent(results, params)
            results[name] = result
        
        return results
    
    def process_events(self, dataset: SampleDataset, output_tree: ROOT.TTree, max_events: Optional[int] = None) -> Dict[str, Any]:
        """
        Process all events in a sample.
        
        Args:
            sample: Instance of SampleDataset to process producers on
            max_events: Maximum number of events to process (None for all)
            
        Returns:
            Dictionary with summary information about the processing
        """

        sample_name = dataset.getname()

        # Get dataset
        if sample_name not in self.data_sources:
            raise ValueError(f"Unknown sample '{sample_name}'")
        
        ntuple = dataset.ntuple  # Assume ntuple is accessible as in SampleDataset
        
        n_events = ntuple.GetEntries()
        if max_events is not None:
            n_events = min(n_events, max_events)
        
        # Process each event
        for i in range(n_events):
            ntuple.GetEntry(i)
            
            # Create event data dictionary with gen2ntuple as initial input
            event_data = {"gen2ntuple": ntuple}
            
            # Process event through all producers
            self.process_event(event_data, {"event_index": i})

            # hack: need to think about this
            output_tree.Fill()
        
        # Return summary information
        return {
            "sample_name": sample_name,
            "n_processed": n_events
        }

    def visualize_dependencies(self, output_file: Optional[str] = None, show: bool = False) -> None:
        """
        Visualize the producer dependency graph.
        
        This method creates a visual representation of the dependency graph
        showing the execution order and dependencies between producers.
        
        Args:
            output_file: Path to save the visualization (PNG, PDF, etc.)
                        If None, the graph is only displayed if show=True
            show: Whether to display the graph interactively
        
        Raises:
            ImportError: If matplotlib or networkx is not installed
        """
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            raise ImportError("Visualization requires matplotlib and networkx. "
                            "Install with: pip install matplotlib networkx")
        
        # Create directed graph for visualization
        graph = nx.DiGraph()
        
        # Add all producers as nodes
        for name in self.producers:
            graph.add_node(name)
        
        # Add edges based on required inputs
        for name, producer in self.producers.items():
            for required in producer.requiredInputs():
                if required in self.producers:
                    graph.add_edge(required, name)  # required must run before name
        
        # Create the figure
        plt.figure(figsize=(12, 8))
        
        # Use hierarchical layout for clearer visualization
        pos = nx.nx_agraph.graphviz_layout(graph, prog="dot") if hasattr(nx, 'nx_agraph') else nx.spring_layout(graph)
        
        # Draw nodes and edges
        nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color="skyblue", alpha=0.8)
        nx.draw_networkx_edges(graph, pos, width=2, alpha=0.7, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=12, font_weight="bold")
        
        # Add title and improve layout
        plt.title("Producer Dependency Graph", fontsize=16)
        plt.axis("off")
        plt.tight_layout()
        
        # Save the figure if requested
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Dependency graph saved to {output_file}")
        
        # Show the figure if requested
        if show:
            plt.show()
        
        # Close the figure to free memory
        plt.close()


    def print_dependency_graph(self) -> None:
        """
        Print a text representation of the producer dependency graph to stdout.
        
        This method provides a simple ASCII visualization of the dependencies
        to help users understand the execution order without requiring
        additional libraries.
        """
        # Build the dependency graph
        graph = {}
        for name, producer in self.producers.items():
            dependencies = [dep for dep in producer.requiredInputs() if dep in self.producers]
            graph[name] = dependencies
        
        # Print execution order
        print("=== Execution Order ===")
        for i, name in enumerate(self.execution_order):
            print(f"{i+1}. {name}")
        
        # Print dependency tree
        print("\n=== Dependency Tree ===")
        
        def print_node(node, depth=0, visited=None):
            if visited is None:
                visited = set()
            
            if node in visited:
                print("  " * depth + f"└─ {node} (circular reference!)")
                return
            
            visited.add(node)
            
            # Get dependencies
            dependencies = graph.get(node, [])
            
            # Print current node
            prefix = "  " * depth
            if depth > 0:
                prefix = prefix[:-2] + "└─ "
            print(f"{prefix}{node}")
            
            # Print dependencies
            for i, dep in enumerate(dependencies):
                print_node(dep, depth + 1, visited.copy())
        
        # Print from leaf nodes (those without dependents)
        leaf_nodes = [name for name in self.producers 
                    if not any(name in deps for deps in graph.values())]
        
        for node in leaf_nodes:
            print_node(node)