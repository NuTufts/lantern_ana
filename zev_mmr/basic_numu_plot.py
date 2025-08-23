import os,sys
import ROOT as rt

targetpot = 4.4e19

samples = ['nue','numu','extbnb','data']

scaling = {"numu":targetpot/4.675690535431973e+20,
           "nue":targetpot/9.662529168587103e+22,
           "extbnb":(176153.0)/(433446.0),
           "data":1.0}

files = {"numu":"./my_simple_output/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
         "nue":"./my_simple_output/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
         "extbnb":"./my_simple_output/run1_extbnb_mcc9_v29e_C1.root",
         "data":"./my_simple_output/run1_bnb5e19.root"}

rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] )
    trees[sample] = tfiles[sample].Get("analysis_tree")
    nentries = trees[sample].GetEntries()
    print(f"sample={sample} has {nentries} entries")

# out = rt.TFile("output_mmr/my_hists_mmr.root","recreate")
out = rt.TFile("./my_simple_study/my_simple_hists.root","recreate")

# var, nbins, xmin, xmax, htitle, setlogy
vars = [('my_recoNuE_Energy/1000.0', 20, 0, 2, 'Inclusive CC #nu_{#mu} Selected Events; Reconstructed Neutrino Energy (GeV)', 0)]
	# ('visible_energy',15,0,3000,'visible energy; MeV',1)]


hists = {}
canvs = {}

# 1. LArMatch-identified neutrino candidate vertex found inside the fiducial volume
cut = "(nuselvar_vtx_found>0.0 && nuselvar_vtx_infiducial==1)" 

# 2. 3D space points of prongs attached to neutrino candidate do not all overlap with Wire-Cell-tagged cosmics
cut += " && (vertex_properties_cosmicfrac<0.1)"     # not a hard cut 

# 3. At least one track attached to the candidate neutrino vertex was identified by LArPID as a muon

# For now, let's use a simplified version that requires at least one track with high muon score
# and that track is primary (trackProcess==0)
# cut += " && (Sum$(trackMuScore>0.5))"# && trackProcess==0)>=1)"  # At least one primary muon track
# cut += " && (Sum$(muvar_max_muscore>-5))"# && trackProcess==0)>=1)"  # At least one primary muon track
cut += " && (muvar_max_muscore>-99)"


print(f"Applied cuts: {cut}")

for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var.replace('/','_div_').replace('.','p')}"  # Clean up canvas name
    canvs[var] = rt.TCanvas(cname,f"v2me06: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'.replace('/','_div_').replace('.','p')  # Clean up histogram name
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)
        trees[sample].Draw(f"{var}>>{hname}",f"({cut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"nue")].SetFillColor(rt.kRed)
    hists[(var,"nue")].SetFillStyle(3001)
    hists[(var,"numu")].SetFillColor(rt.kBlue-3)
    hists[(var,"numu")].SetFillStyle(3003)
    hists[(var,"extbnb")].SetFillColor(rt.kGray)
    hists[(var,"extbnb")].SetFillStyle(3144)
    hists[(var,"data")].SetLineColor(rt.kBlack)
    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}".replace('/','_div_').replace('.','p')  # Clean up stack name
    hstack = rt.THStack(hstack_name,"")
    hstack.Add( hists[(var,"extbnb")])
    hstack.Add( hists[(var,"numu")])
    hstack.Add( hists[(var,"nue")])
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")

    predmax = hstack.GetMaximum()
    datamax = hists[(var,"data")].GetMaximum()

    if predmax>datamax:
        hstack.SetTitle(htitle)
        hstack.Draw("hist")
    else:
        hists[(var,"data")].SetTitle(htitle)
        hists[(var,"data")].Draw("E1")
        hstack.Draw("histsame")

    hists[(var,"data")].Draw("E1same")

    # Create and configure legend
    legend = rt.TLegend(0.65, 0.65, 0.89, 0.89)  # x1, y1, x2, y2 in NDC coordinates
    legend.SetTextSize(0.03)
    legend.SetFillStyle(0)  # Transparent background
    legend.SetBorderSize(1)
    
    # Add entries to legend (in reverse order of stacking so topmost appears first)
    legend.AddEntry(hists[(var,"data")], "Data", "lep")
    legend.AddEntry(hists[(var,"nue")], "#nu_{e} CC", "f")
    legend.AddEntry(hists[(var,"numu")], "#nu_{#mu}", "f")
    legend.AddEntry(hists[(var,"extbnb")], "Ext BNB", "f")
    legend.Draw()

    canvs[var].SetLogy(setlogy)
    canvs[var].Update()
    canvs[var].Write()

out.Close() 

# Alternative version with more sophisticated muon identification
# If the above doesn't work well, you can try this approach:

"""
Alternative approach for more precise muon identification:

You could replace the simple muon cut with a loop-based approach:

# Before the main plotting loop, add this helper function:
def has_muon_track(tree, entry):
    tree.GetEntry(entry)
    for i in range(tree.nTracks):
        if (tree.trackMuScore[i] > 0.5 and 
            tree.trackProcess[i] == 0 and 
            tree.trackClassified[i] == 1):
            return True
    return False

# Then use this in your cut by creating a custom event selection
# This would require a different approach where you loop through events
# rather than using the Draw() method with cuts.
"""