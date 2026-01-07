#include <iostream>
#include <string>
#include <map>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TInterpreter.h"


int main(int nargs, char** argv ) {

  std::cout << "Inspect weights in Pandora tree." << std::endl;

  // Generate dictionary for the complex STL container at runtime
  gInterpreter->GenerateDictionary("map<string,vector<double> >", "map;string;vector");

  std::string inputfile = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4a_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4a.root";

  TFile rfile( inputfile.c_str(), "open" );

  TTree* pandora = (TTree*)rfile.Get( "nuselection/NeutrinoSelectionFilter" );

  std::map<std::string,std::vector<double> >* weights = nullptr;

  pandora->SetBranchAddress( "weights", &weights );

  size_t nentries = pandora->GetEntries();

  std::cout << "Number of entries: " << nentries << std::endl;

  size_t ientry = 0;
  size_t nbytes = pandora->GetEntry(ientry);

  std::cout << "Data in map for Entry[" << ientry << "]" << std::endl;

  for ( auto it=weights->begin(); it!=weights->end(); it++ ) {
    std::cout << "  " << it->first << ": nweights=" << it->second.size() << std::endl;
  }
  
}
