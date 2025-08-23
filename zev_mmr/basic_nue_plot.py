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
out = rt.TFile("./my_simple_hists.root","recreate")

# var, nbins, xmin, xmax, htitle, setlogy
vars = [('recoNuE/1000.0', 20, 0, 3, "Reconstructed Neutrino Energy (#nu_{e} CC Selection); GeV", 0), 
	('visible_energy',15,0,3000,'visible energy; MeV',1)]


hists = {}
canvs = {}

# Electron neutrino (nue) CC selection cuts:

# 1. LArMatch-identified neutrino candidate vertex found inside the fiducial volume
cut = "(nuselvar_vtx_found>0.0 && nuselvar_vtx_infiducial==1)" 


# 2. 3D spacepoints of prongs attached to neutrino candidate do not all overlap with Wire-Cell-tagged cosmics
cut += " && (vertex_properties_cosmicfrac<0.2)"     # not a hard cut 

# 3. No LArPID-identified muon tracks are attached to neutrino candidate
# Check that no tracks are identified as muons (PID != 13)
# cut += " && (Sum$(trackClassified==1 && trackPID==13)==0)"  # No muon-identified tracks
cut += " && (muvar_max_muscore<-99)"

# 4. At least one LArPID-identified electron shower is attached to neutrino candidate,
#    the largest (in visible energy) of which is also classified as a primary final state particle
# This requires at least one primary shower identified as electron (PID==11) with showerProcess==0
cut += " && (Sum$(showerClassified==1 && showerPID==11 && showerProcess==0)>=1)"  # At least one primary electron shower

# 5. No tracks attached to neutrino candidate have a high LArPID muon score: max log(muon score) < −3.7
# This is equivalent to muon score < exp(-3.7) ≈ 0.025
cut += " && (Max$(trackClassified==1 ? trackMuScore : -999)<-3.7)"  # Max log(muon score) < -3.7

# 6. The largest identified electron was classified by LArPID as an electron with high confidence:
#    log(electron score) − (log(pion score) + log(photon score))/2 > 7.1
# We need to find the largest electron shower and check its confidence
# For now, we'll use a simplified version that requires any electron shower to have this confidence
# Note: This is a complex cut that ideally needs event-by-event evaluation
cut += " && (Max$(showerClassified==1 && showerPID==11 ? (showerElScore - (showerPiScore + showerPhScore)/2.0) : -999)>7.1)"

print(f"Applied νₑ CC selection cuts: {cut}")

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

"""
EXPLANATION OF THE νₑ CC SELECTION CUTS:

1. foundVertex==1 && vtxIsFiducial==1
   - LArMatch-identified neutrino vertex in fiducial volume

2. vtxFracHitsOnCosmic<1.0  
   - Not all space points overlap with cosmic-tagged pixels

3. Sum$(trackClassified==1 && trackPID==13)==0
   - No tracks identified as muons by LArPID

4. Sum$(showerClassified==1 && showerPID==11 && showerProcess==0)>=1
   - At least one primary electron shower identified by LArPID

5. Max$(trackClassified==1 ? trackMuScore : -999)<-3.7
   - Maximum log(muon score) for any track < -3.7
   - Equivalent to muon score < exp(-3.7) ≈ 0.025

6. Max$(showerClassified==1 && showerPID==11 ? (showerElScore - (showerPiScore + showerPhScore)/2.0) : -999)>7.1
   - Electron confidence score > 7.1 for largest electron shower
   - Formula: log(electron score) - (log(pion score) + log(photon score))/2

VARIABLES USED:
- recoNuE: Reconstructed neutrino energy (MeV) - sum of all track and shower energies
- foundVertex: 1 if neutrino vertex found, 0 otherwise  
- vtxIsFiducial: 1 if vertex in fiducial volume
- vtxFracHitsOnCosmic: Fraction of hits matching cosmic-tagged pixels
- trackClassified: 1 if track processed by LArPID
- trackPID: Predicted PDG code (13=muon, 11=electron, etc.)
- trackMuScore: Log(muon score) from LArPID
- showerClassified: 1 if shower processed by LArPID
- showerPID: Predicted PDG code for shower (11=electron)
- showerProcess: 0=primary, 1=secondary with neutral parent, 2=secondary with charged parent
- showerElScore, showerPiScore, showerPhScore: Log scores from LArPID
"""