int Strip_xsecweight() {

  // Run 3
  std::string input_path = "/exp/uboone/data/users/imani/ntuples/run3/dlgen2_reco_v2me05_gen2ntuple_v7_run3b_bnb_nu_overlay_nocrtremerge.root";
  std::string output_path = "xsecweight_dlgen2_reco_v2me05_gen2ntuple_v7_run3b_bnb_nu_overlay_nocrtremerge.root";



  // Runs 4a
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4a_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4a.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4a.root";
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4a_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_4a.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_4a.root";

  // Run 4b (old)
  //std::string input_path  = "/exp/uboone/data/uboonepro/MCC9.10/liangliu/v10_04_07_09/MCC9.10_Run4b_v10_04_07_09_BNB_nu_overlay_surprise_reco2_hist.root";
  //std::string output_path = "/exp/uboone/data/users/tmw/weights/for_run4b_lantern/xsecweight_tree.root";
  // std::string input_path = "/pnfs/uboone/scratch/users/eyandel/SURPRISE/processed_checkout_rootfiles/run4b/MCC9.10_Run4b_v10_04_07_09_BNB_nue_overlay_surprise_reco2_hist.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4b_v10_04_07_09_BNB_nue_overlay_surprise.root";
  
  // Run 4b 
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4b_full_samples/BNB/MCC9.10_Run4b_v10_04_07_09_BNB_nu_overlay_surprise_reco2_hist.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4b_v10_04_07_09_BNB_nu_overlay_surprise_reco2_hist.root";
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4b_full_samples/BNB/MCC9.10_Run4b_v10_04_07_09_BNB_nue_overlay_surprise_reco2_hist.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4b_v10_04_07_09_BNB_nue_overlay_surprise_reco2_hist.root";

  // Run 4c 
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4c_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4c.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4c.root";
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4c_full_samples//BNB/MCC9.10_Run4c_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_redo_reco2_hist.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4c_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_redo_reco2_hist.root";

  // Run 4d
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4d_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4d.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_4d.root";
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run4d_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_4d.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_4d.root";

  // Run 5
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run5_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_5.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_reco2_hist_5.root";
  // std::string input_path = "/pnfs/uboone/persistent/users/uboonepro/surprise/run5_full_samples/BNB/MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_5.root";
  // std::string output_path = "xsecweight_MCC9.10_Run4a4c4d5_v10_04_07_13_BNB_intrinsic_nue_overlay_surprise_reco2_hist_5.root";


  // Open Input File
  TFile* input_rfile = new TFile(input_path.c_str(),"open");
  TTree* pandora_tree = (TTree*)input_rfile->Get("nuselection/NeutrinoSelectionFilter");
  TTree* lantern_tree = (TTree*)input_rfile->Get("lantern/EventTree");

  size_t nentries_pandora = pandora_tree->GetEntries();
  size_t nentries_lantern = lantern_tree->GetEntries();

  if ( nentries_pandora!=nentries_lantern ) {
    std::cout << "Number of entries mismatch: " << std::endl;
    std::cout << "  pandora tree: " << nentries_pandora << std::endl;
    std::cout << "  lantern tree: " << nentries_lantern << std::endl;
    return 0;
  }

  std::cout << "Number of entries: " << nentries_pandora << std::endl;

  int run_pandora = 0;
  int subrun_pandora = 0;
  int event_pandora = 0;
  int run_lantern = 0;
  int subrun_lantern = 0;
  int event_lantern = 0;
  float xsecWeight = 0.0;
  
  pandora_tree->SetBranchAddress("run", &run_pandora );
  pandora_tree->SetBranchAddress("sub", &subrun_pandora );
  pandora_tree->SetBranchAddress("evt", &event_pandora );
  pandora_tree->SetBranchAddress("weightTune", &xsecWeight );

  lantern_tree->SetBranchAddress("run", &run_lantern );
  lantern_tree->SetBranchAddress("subrun", &subrun_lantern );
  lantern_tree->SetBranchAddress("event", &event_lantern );

  TFile* output_rfile = new TFile(output_path.c_str(),"recreate");
  TTree* weight_tree = new TTree("weight_tree","Supplemental Weight Tree");

  weight_tree->Branch("weighttree_run", &run_pandora, "weighttree_run/I" );
  weight_tree->Branch("weighttree_subrun", &subrun_pandora, "weighttree_subrun/I" );
  weight_tree->Branch("weighttree_event", &event_pandora, "weighttree_event/I" );
  weight_tree->Branch("weighttree_xsecweight", &xsecWeight, "weighttree_xsecweight/F");

  for ( size_t ientry=0; ientry<nentries_pandora; ientry++) {
    if ( ientry>0 && ientry%10000==0 ) {
      std::cout << "entry " << ientry << std::endl;
    }

    pandora_tree->GetEntry(ientry);
    lantern_tree->GetEntry(ientry);


    if ( run_pandora!=run_lantern
	 && subrun_pandora!=subrun_lantern
	 && event_pandora!=event_lantern ) {
      std::cout << "Entry Mismatch!" << std::endl;
      std::cout << "  entry: " << ientry << std::endl;
      std::cout << "  pandora: " << std::endl;
      std::cout << "    run: " << run_pandora << std::endl;
      std::cout << "    subrun: " << subrun_pandora << std::endl;
      std::cout << "    event: " << event_pandora << std::endl;      
      std::cout << "  lantern: " << std::endl;
      std::cout << "    run: " << run_lantern << std::endl;
      std::cout << "    subrun: " << subrun_lantern << std::endl;
      std::cout << "    event: " << event_lantern << std::endl;      
      return 0;
    }

    weight_tree->Fill();

    // for debug
    //if ( ientry>=10000 )
    //  break;
  }

  std::cout << "Event Loop Done. Finishing Up." << std::endl;
  
  weight_tree->Write();
  output_rfile->Close();

  
    
  
  return 0;
};
