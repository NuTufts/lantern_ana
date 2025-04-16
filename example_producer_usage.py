# Example usage
if __name__ == "__main__":
    import sys
    import ROOT
    import lantern_ana
    from lantern_ana.SampleDataset import SampleDataset
    from lantern_ana.producers.producer_factory import ProducerFactory

    
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


    # Discover and register producers
    ProducerFactory.discover_producers("my_producers")
    
    # Create manager and load configuration
    manager = ProducerManager()
    manager.load_configuration(config_path)
    
    # Set up output ROOT file and TTree
    output_file = ROOT.TFile("output.root", "RECREATE")
    output_tree = ROOT.TTree("analysis", "Analysis Tree")
    
    # Prepare storage in output tree
    manager.prepare_storage(output_tree)
    
    # Process events from a sample
    manager.process_events("run4b_bnbnu", max_events=1000)
    
    # Write tree to file
    output_tree.Write()
    output_file.Close()
    
    print("Processing complete!")