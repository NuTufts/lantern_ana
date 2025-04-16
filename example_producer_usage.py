# Example usage
if __name__ == "__main__":
    import sys
    import ROOT
    import yaml
    import lantern_ana
    import tempfile
    from lantern_ana.io.SampleDataset import SampleDataset
    from lantern_ana.producers.producer_factory import ProducerFactory
    from lantern_ana.producers.producerManager import ProducerManager
    
    example_cfg="""
    datasets:
        run4b_bnbnu:
            filename: /home/twongjirad/working/data/ntuples/v2me06_03_test/lantern_ntuple_mcc9.10_run4b_bnb_nu_overlay_v2me06_03_test.root
            ismc: true

    producers:
        track_energy:
            type: TrackEnergyProducer
            config:
                min_energy: 50.0  # MeV
                max_tracks: 20
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
        temp_file.write(example_cfg)
        config_path = temp_file.name

    # Load SampleDataset
    # Create a sample datasets
    datasets = {}
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        datasets_cfg = config['datasets']
        for ntuple_name in datasets_cfg:
            print("Creating dataset name=",ntuple_name)
            ntuple_cfg = datasets_cfg[ntuple_name]
            dataset = SampleDataset(ntuple_name, ntuple_cfg['filename'], ismc=bool(ntuple_cfg['ismc']))
            datasets[ntuple_name] = dataset

    # Discover and register producers
    ProducerFactory.discover_producers("lantern_ana/producers")
    
    # Create manager and load configuration
    manager = ProducerManager()
    manager.load_configuration(config_path)
    
    # Set up output ROOT file and TTree
    output_file = ROOT.TFile("output.root", "RECREATE")
    output_tree = ROOT.TTree("analysis", "Analysis Tree")
    
    # Prepare storage in output tree
    manager.prepare_storage(output_tree)
    
    # Process events from a sample
    manager.process_events(datasets["run4b_bnbnu"], output_tree, max_events=1000)
    
    # Write tree to file
    output_tree.Write()
    output_file.Close()
    
    print("Processing complete!")