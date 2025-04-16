import argparse

from lantern_ana.io.SampleDataset import SampleDataset
from lantern_ana.tags import TagFactory

def main( ntuple_name, ntuple_path, event_limit=None ):
    # Create a sample dataset
    dataset = SampleDataset(ntuple_name, ntuple_path, ismc=True)
    eventTree = dataset.ntuple
    
    # Create a tag factory
    factory = TagFactory()
    
    # List available tags
    print("Available tags:", factory.list_available_tags())
    
    # Add tag with parameters
    factory.add_tag('tag_truth_finalstate_mode', {
        'ignore_gammas':True # Ignore gamma count when making tag
    })

    # Counts of different tags
    tag_counts = {}
    n_total = 0

    print("Number of entries: ",eventTree.GetEntries())

    if event_limit is None:
        nentries = eventTree.GetEntries()
    if event_limit is not None and event_limit>0:
        event_limit = min( event_limit, eventTree.GetEntries())
    else:
        event_limit = eventTree.GetEntries()
    
    for i in range(event_limit):
        if i > 0 and i % 1000 == 0:
            print(f"Processing entry {i}/{eventTree.GetEntries()}")
            
        eventTree.GetEntry(i)
        n_total += 1
        
        # Apply tags
        event_tags = factory.apply_tags(eventTree)
        for event_tag in event_tags:
            if event_tag not in tag_counts:
                tag_counts[event_tag] = 0
            tag_counts[event_tag] += 1

            
    # Print results
    print(f"Events processed: {n_total}")
    
    print("")
    print("Tag Counts")
    for tag in tag_counts:
        print(f" {tag}: ",tag_counts[tag])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("example_tag_factory_usage.py","Provides an example of how to define tags using TagFactory")
    parser.add_argument('ntuple_path',help='ntuple file')
    parser.add_argument('--nentries',default=None,type=int,help='Number of entries to run.')
    args = parser.parse_args()
    main("ntuple",args.ntuple_path, event_limit=args.nentries)