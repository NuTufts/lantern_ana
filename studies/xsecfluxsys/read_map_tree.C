// Example script to read TTree with map<string, vector<double>> branch
// Usage: root -l read_map_tree.C

#include <iostream>
#include <map>
#include <vector>
#include <string>
#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"
#include "MapTypes.h"

void read_map_tree(const char* inputFile = "input.root",
                   const char* treeName = "eventweight_tree",
                   const char* branchName = "sys_weights",
                   const char* outputFile = "output.root") {
    
    // Load the dictionary
    gSystem->Load("./libMapDict.so");
    
    // Open input file
    TFile* inFile = TFile::Open(inputFile, "READ");
    if (!inFile || inFile->IsZombie()) {
        std::cerr << "Error: Cannot open input file " << inputFile << std::endl;
        return;
    }
    
    // Get tree
    TTree* inTree = (TTree*)inFile->Get(treeName);
    if (!inTree) {
        std::cerr << "Error: Cannot find tree " << treeName << std::endl;
        inFile->Close();
        return;
    }
    
    // Create pointer to map
    std::map<std::string, std::vector<double>>* dataMap = nullptr;
    
    // Set branch address
    inTree->SetBranchAddress(branchName, &dataMap);
    
    // Create output file and tree
    TFile* outFile = TFile::Open(outputFile, "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cerr << "Error: Cannot create output file " << outputFile << std::endl;
        inFile->Close();
        return;
    }
    TTree* outTree = new TTree("convertedTree", "Converted data from map");
    
    // Variables for output tree
    std::string key;
    std::vector<double> values;
    Int_t nValues;
    
    // Create branches
    outTree->Branch("key", &key);
    outTree->Branch("nValues", &nValues);
    outTree->Branch("values", &values);
    
    // Loop over entries
    Long64_t nEntries = inTree->GetEntries();
    std::cout << "Processing " << nEntries << " entries..." << std::endl;
    
    for (Long64_t iEntry = 0; iEntry < nEntries; iEntry++) {
        if (iEntry % 1000 == 0) {
            std::cout << "Processing entry " << iEntry << "/" << nEntries << std::endl;
        }
        
        inTree->GetEntry(iEntry);
        
        // Check if map is valid
        if (!dataMap) {
            std::cerr << "Warning: Null pointer at entry " << iEntry << std::endl;
            continue;
        }
        
        // Loop over map elements
        for (const auto& pair : *dataMap) {
            key = pair.first;
            values = pair.second;
            nValues = values.size();

	    std::cout << "key: " << key << ": vector<double>.size()=" << nValues << std::endl;

            // Fill output tree
            //outTree->Fill();
        }
    }
    
    // Write and close files
    outFile->cd();
    outTree->Write();
    
    std::cout << "Output tree written to " << outputFile << std::endl;
    std::cout << "Total entries in output tree: " << outTree->GetEntries() << std::endl;
    
    // Cleanup
    outFile->Close();
    inFile->Close();
    
    delete outFile;
    delete inFile;
}
