import os,sys
#sys.argv.append( '-b' )
import ROOT as rt

rt.gStyle.SetOptStat(0)
rt.gStyle.SetPadBottomMargin(0.2)
rt.gStyle.SetPadLeftMargin(0.15)
rt.gStyle.SetPadRightMargin(0.05)
rt.gStyle.SetPadTopMargin(0.05)

"""
"""

"""
"""
targetpot = 1.3e+20
true_vertex_dwallcut = 5.0
output_png_prefix = "run4b_cutbycut"
plot_folder = "output_cutbycut_plots_run4b"
os.system(f"mkdir -p {plot_folder}")

samples = ['nue_sig','nue_bg','numu','extbnb','data']

scaling = {"numu":targetpot/7.881656209241413e+20,
           "nue_sig":targetpot/1.1785765118473412e+23,
           "nue_bg":targetpot/1.1785765118473412e+23,
           "extbnb":23090946.0/94414115.0,
           "data":1.0}
files = {
    "numu":"./output_nue_run4b_surprise/run4b_v10_04_07_09_BNB_nu_overlay_surprise_20250904_003901.root",
    "nue_sig":"./output_nue_run4b_surprise/run4b_v10_04_07_09_BNB_nue_overlay_surprise_20250904_004759.root",
    "nue_bg":"./output_nue_run4b_surprise/run4b_v10_04_07_09_BNB_nue_overlay_surprise_20250904_004759.root",
    "extbnb":"./output_nue_run4b_surprise/run4b_v10_04_07_09_extbnb_20250901_104613.root",
    "data":"./output_nue_run4b_surprise/run4b_beamon_20250901_104738.root"
}

cut_stages = ['fvvertex','cosmicfrac','num_muons','primary_electron','max_muscore','electron_confidence']

cut_stage_def = {
    'fvvertex':"vertex_properties_infiducial==1",
    'cosmicfrac':"vertex_properties_cosmicfrac<1.0",
    'num_muons':"recoMuonTrack_nMuTracks==0",
    'primary_electron':"(recoElectron_has_primary_electron==1 && recoElectron_emax_primary_score>recoElectron_emax_fromcharged_score && recoElectron_emax_primary_score>recoElectron_emax_fromneutral_score)",
    'max_muscore':"(recoMuonTrack_max_muscore<-3.7)",
    'electron_confidence':"(recoElectron_emax_econfidence>7.0)"
}

signal_def = "nueCCinc_is_target_nuecc_inclusive_nofvcut==1 && nueCCinc_dwalltrue>=%.2f"%(true_vertex_dwallcut)

tfiles = {}
trees = {}

for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] )
    trees[sample] = tfiles[sample].Get("analysis_tree")
    nentries = trees[sample].GetEntries()
    print(f"sample={sample} has {nentries} entries")

out = rt.TFile("temp.root","recreate")

vars = [('eventweight_weight',200,0,10,';event weight;',0,True),
    ('recoElectron_emax_econfidence', 40, 0, 20,';electron confidence score',0,False),
    ('recoElectron_emax_primary_score',40,0,1.0,';primary score',0,False),
    ('recoElectron_emax_fromneutral_score',40,0,1.0,';from neutral parent score',0,False),
    ('recoElectron_emax_fromcharged_score',40,0,1.0,';from charged parent score',0,False),
    ('recoElectron_emax_el_normedscore',40,0,1.0,';electron-like score (normalized)',0,False),
    ('recoMuonTrack_nMuTracks',20,0,20,';num of muon-like tracks',0,False),
    ('recoMuonTrack_max_muscore',50,-20,0.5,';max mu-like score',0,False),
    ('vertex_properties_score',60,0.4,1.0,';keypoint score',0,False),
    ('vertex_properties_cosmicfrac',50,0,1.01,';fraction of cosmic pixel near vertex',0,False),
    ('visible_energy',15,0,3000,';visible energy (MeV)',0,True),
    ('trueNu_Enu',15,0,1.0,';true Neutrino Energy (GeV)',0,True)
]

hists = {}

# Each canvas will have hist (stacked prediction vs data), efficiency, purity
canvs = {}



for var, nbins, xmin, xmax, htitle, setlogy, ismcvar in vars:

    print("="*80)
    print("VARIABLE: ",var)

    # for every variable we need the efficiency denominator histogram
    hvar_denom_name = f"h{var}_signal_denom"
    hvar_denom = rt.TH1D( hvar_denom_name, "", nbins, xmin, xmax )
    trees['nue_sig'].Draw(f"{var}>>{hvar_denom_name}",f"({signal_def})*eventweight_weight")
    hvar_denom.Scale( scaling['nue_sig'] )

    cutstring = ""
    for icut,cutname in enumerate(cut_stages):

        x_cutvar = f"x{var}_cut{icut:02d}_{cutname}"

        cname = f"c{x_cutvar}"
        canvs[x_cutvar] = rt.TCanvas(cname,f"v2me06: {cname}",2400,600)
        canvs[x_cutvar].Divide(3,1)
        canvs[x_cutvar].Draw()

        if cutname == cut_stages[0]:
            cutstring = f"({cut_stage_def[cutname]})"
        else:
            cutstring += f" && ({cut_stage_def[cutname]})"

        # make prediction stack: bnb nu + bnb nue + extbnb
        canvs[x_cutvar].cd(1)
        for sample in samples:
            hname = f'h{x_cutvar}_{sample}'
            hh = rt.TH1D( hname, "", nbins, xmin, xmax )
            hh.GetXaxis().SetLabelSize(0.05)
            hh.GetXaxis().SetTitleSize(0.05)
            hh.GetXaxis().SetTitleOffset(1.2)
            hh.GetYaxis().SetLabelSize(0.05)
            hh.GetYaxis().SetTitleSize(0.05)

            hists[(x_cutvar,sample)] = hh
            print("fill ",hname)

            cutapplied = cutstring

            # we split nue sample into sig and bg as well
            if sample=='nue_sig':
                cutapplied = f"({cutstring}) && ({signal_def})"
            elif sample=="nue_bg":
                cutapplied = f"({cutstring}) && !({signal_def})"

            trees[sample].Draw(f"{var}>>{hname}",f"({cutapplied})*eventweight_weight")
            #trees[sample].Draw(f"{var}>>{hname}",f"({cutapplied})") # for debug: do not use GENIE tune

            hists[(x_cutvar,sample)].Scale( scaling[sample] )
            print(f"{x_cutvar}-{sample}: ",hists[(x_cutvar,sample)].Integral())
    
        # color the different components of the prediction stack
        hists[(x_cutvar,"nue_sig")].SetFillColor(rt.kRed)
        hists[(x_cutvar,"nue_sig")].SetFillStyle(3001)
        hists[(x_cutvar,"nue_bg")].SetFillColor(rt.kOrange)
        hists[(x_cutvar,"nue_bg")].SetFillStyle(3001)
        hists[(x_cutvar,"numu")].SetFillColor(rt.kBlue-3)
        hists[(x_cutvar,"numu")].SetFillStyle(3003)
        hists[(x_cutvar,"extbnb")].SetFillColor(rt.kGray)
        hists[(x_cutvar,"extbnb")].SetFillStyle(3144)
        hists[(x_cutvar,"data")].SetLineColor(rt.kBlack)
        hists[(x_cutvar,"data")].SetLineWidth(2)

        # Canvas 1: prediction stack
        canvs[x_cutvar].cd(1)
        canvs[x_cutvar].cd(1).SetLogy(setlogy)
        if icut+1<len(cut_stages):
            canvs[x_cutvar].cd(1).SetLogy(1)
        canvs[x_cutvar].cd(1).SetGridx(1)
        canvs[x_cutvar].cd(1).SetGridy(1)
        hstack_name = f"hs_{x_cutvar}"
        hstack = rt.THStack(hstack_name,"")
        if not ismcvar:
            hstack.Add( hists[(x_cutvar,"extbnb")])
        hstack.Add( hists[(x_cutvar,"numu")])
        hstack.Add( hists[(x_cutvar,"nue_sig")])
        if hists[(x_cutvar,"nue_bg")].Integral()>0.0:
            hstack.Add( hists[(x_cutvar,"nue_bg")] )
        hists[(hstack_name,sample)] = hstack

        hstack.Draw("hist")
        hstack.GetXaxis().SetLabelSize(0.05)
        hstack.GetXaxis().SetTitleSize(0.05)
        hstack.GetXaxis().SetTitleOffset(1.2)
        hstack.GetYaxis().SetLabelSize(0.05)
        hstack.GetYaxis().SetTitleSize(0.05)

        predmax = hstack.GetMaximum()
        datamax = hists[(x_cutvar,"data")].GetMaximum()

        if predmax>datamax or ismcvar:
            hstack.SetTitle(htitle)
            hstack.Draw("hist")
        else:
            hists[(x_cutvar,"data")].SetTitle(htitle)
            hists[(x_cutvar,"data")].Draw("E1")
            hstack.Draw("histsame")

        if not ismcvar:
            hists[(x_cutvar,"data")].Draw("E1same")

        # Canvas 2: efficiency
        canvs[x_cutvar].cd(2)
        canvs[x_cutvar].cd(2).SetGridx(1)
        canvs[x_cutvar].cd(2).SetGridy(1)
        hvar_eff_name = f"h{x_cutvar}_eff"
        hvar_eff = hists[(x_cutvar,'nue_sig')].Clone(hvar_eff_name)
        hvar_eff.SetFillStyle(0)
        hvar_eff.SetFillColor(0)
        hvar_eff.SetLineWidth(2)
        hvar_eff.Divide(hvar_denom)
        hists[(x_cutvar,'eff')] = hvar_eff
        hvar_eff.Draw("hist")
        hvar_eff.GetYaxis().SetRangeUser(0.0,1.0)
        hvar_eff.GetXaxis().SetLabelSize(0.05)
        hvar_eff.GetXaxis().SetTitleSize(0.05)
        hvar_eff.GetXaxis().SetTitleOffset(1.2)
        hvar_eff.GetYaxis().SetLabelSize(0.05)
        hvar_eff.GetYaxis().SetTitleSize(0.05)
        hvar_eff.SetTitle(htitle)
        hvar_eff.GetYaxis().SetTitle("efficiency")
        # to do: binomial errors

        # Canvas 3: purity
        canvs[x_cutvar].cd(3)
        canvs[x_cutvar].cd(3).SetGridx(1)
        canvs[x_cutvar].cd(3).SetGridy(1)
        hvar_pur_name = f"h{x_cutvar}_purity"
        hvar_pur = hists[(x_cutvar,'nue_sig')].Clone(hvar_pur_name)
        print(hvar_pur_name,": ",hvar_pur.Integral())
        hvar_pur.SetFillStyle(0)
        hvar_pur.SetFillColor(0)
        hvar_pur.GetXaxis().SetLabelSize(0.05)
        hvar_pur.GetXaxis().SetTitleSize(0.05)
        hvar_pur.GetXaxis().SetTitleOffset(1.2)
        hvar_pur.GetYaxis().SetLabelSize(0.05)
        hvar_pur.GetYaxis().SetTitleSize(0.05)  
        hvar_pur.SetLineWidth(2)      

        hvar_pur_denom_name = f"h{x_cutvar}_purity_denom"
        hvar_pur_denom = hists[(x_cutvar,'nue_sig')].Clone(hvar_pur_denom_name)
        hvar_pur_denom.Reset()
        hvar_pur_denom.SetFillStyle(0)
        hvar_pur_denom.SetFillColor(0)
        for ibin in range(1,hvar_pur_denom.GetXaxis().GetNbins()+1):
            bintot = 0.0
            for sample in ['nue_sig','nue_bg','numu','extbnb']:
                if ismcvar and sample=='extbnb':
                    continue
                bintot += hists[(x_cutvar,sample)].GetBinContent(ibin)
            hvar_pur_denom.SetBinContent(ibin,bintot)
        print(hvar_pur_denom_name,": ",hvar_pur_denom.Integral())
        hvar_pur.Divide( hvar_pur_denom )
        hvar_pur.Draw("hist")
        hvar_pur.SetTitle(htitle)
        hvar_pur.GetYaxis().SetRangeUser(0.0,1.0)
        hvar_pur.GetYaxis().SetTitle('purity')
        hists[(x_cutvar,'purity')] = hvar_pur

        canvs[x_cutvar].Update()
        canvs[x_cutvar].SaveAs(f'{plot_folder}/plot_v2me06_{output_png_prefix}_{cname}.png')

    print("[enter] to continue")
    #input()

out.Write()
print("[enter] to close")
input()
