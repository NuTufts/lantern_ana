import os,sys
import ROOT as rt # load the ROOT library 

rootfile="./output/bnbnumu_20250722_125434.root" # change this to be the latest file
#rootfile=sys.argv[1] # or use this line instead to give the file you want to plot with as an argument

rootfile = rt.TFile( rootfile, "open" ) # open the rootfile
rootfile.ls() # print the contents of the ROOT file

analysis_tree = rootfile.Get("analysis_tree") # load the analysis_tree TTree that is in the file
nentries = analysis_tree.GetEntries()

# create a temp root file where the histgrams and canvases we make will be saved
temp = rt.TFile("temp.root","recreate") 

# define the histograms we want to make.
# arguments (histogram name, "title;x axis label; y-axis label", nbins, minimum X, maximum X)
hist_invariantmass_true = rt.TH1D("hist_invariantmass_true", "Title;x axis label;counts", 100, 0, 500)
hist_invariantmass_reco = rt.TH1D("hist_invariantmass_reco", "Title;x axis label;counts", 100, 0, 500)

# create the canvas to display our histgrams when we draw them
canvas_invariantmass_true = rt.TCanvas("canvas_invariantmass_true", "Canvas Title", 800, 600)
# use the TTree's draw command to fill our histogram. also impose conditions using the second argument
# draw the true invariant mass
# the second argument is the condition that entries must pass to be included in the histogram
analysis_tree.Draw("invariantmass>>hist_invariantmass_true","invariantmass>0")
canvas_invariantmass_true.Update()
canvas_invariantmass_true.SaveAs("canvas_invariantmass_true.png") # also save as png file

# create the reco invariant mass canvas to display our histgrams when we draw them
canvas_invariantmass_reco = rt.TCanvas("canvas_invariantmass_reco", "Canvas Title", 800, 600)
# use the TTree's draw command to fill our histogram. also impose conditions using the second argument
# draw the reco invariant mass
analysis_tree.Draw("invariantmass_reco>>hist_invariantmass_reco","invariantmass_reco>0 && proton>=1")
canvas_invariantmass_reco.Update()
canvas_invariantmass_reco.SaveAs("canvas_invariantmass_reco.png") # also save as png file

# pause the program so we can look at histograms before script ends
input()

# save the stuff we made into the output rootfile
temp.Write()
