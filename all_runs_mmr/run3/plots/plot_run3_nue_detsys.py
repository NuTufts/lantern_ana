import os,sys
import ROOT as rt
from math import sqrt


### from Polina's make tki detsys plots . py 


inputfiles = [
    "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/detsys_final/detsys_cv100k_run3b_nu_CV.root",
    "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/detsys_final/detsys_cv100k_run3b_nue_CV.root",
    "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/detsys_final/detsys_cv500k_run3b_nu_CV_500k.root"
]
plot_folder = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/plots/"
os.system(f"mkdir -p {plot_folder}")

parameters = [
    'LYAtt',
    'LYDown',
    'LYRayleigh',
    'wiremodX',
    'wiremodYZ',
    'wiremodThetaXZ',
    'wiremodThetaYZ',
    'SCE',
    'recomb2'
]

variables = [
    'visible_energy',
    'reco_neutrino_energy',
    'reco_electron_energy',
    'reco_cos_theta',
]

output_file = "hists_run3_nue_detsys.root"

rout = rt.TFile(output_file,'recreate')

canvases = {}
for var in variables:

    print("="*80)
    print(f"[{var}] Calculating Fractional Variance")


    hvar_sum  = None
    hvar_sum_frac = None

    for finput in inputfiles:
        rfile = rt.TFile( finput )
        for par in parameters:
            hpar_cv  = rfile.Get( f"h{var}__{par}__cv")  # central value
            hpar_var = rfile.Get( f"h{var}__{par}__var") # variation
            try:
                # Call a function to test if exits
                hpar_cv.Integral()
                print(f"{par}: ",hpar_cv)
            except:
                continue

            rout.cd()

            if hvar_sum_frac is None:
                hvar_sum_frac = hpar_cv.Clone(f"h{var}__totfracvar")
                hvar_sum_frac.Reset()

            hpar_frac = hpar_cv.Clone(f"h{var}__{par}__fracvar")
            hpar_frac.Reset()
            for ibin in range(1,hpar_cv.GetXaxis().GetNbins()+1):
                counts_cv  = hpar_cv.GetBinContent(ibin)
                counts_var = hpar_var.GetBinContent(ibin)
                stddev = abs(counts_cv-counts_var)
                variance = stddev*stddev
                if counts_cv>0:
                    frac_variance = variance/float(counts_cv)
                    hpar_frac.SetBinContent(ibin,frac_variance)
                    var_tot = hvar_sum_frac.GetBinContent(ibin)
                    print(f"var[{var}]-bin[{ibin}] cv={counts_cv} vari={counts_var} --> frac_var={frac_variance} running_tot=",var_tot + frac_variance)
                    hvar_sum_frac.SetBinContent(ibin, var_tot + frac_variance )
            
            # save to file
            hpar_frac.Write()
    rout.cd()

    # make the fractional stddev plot.
    # we multiply the by the CV to get the variance,
    # then we take the sqrt to get the stdev
    # then we divide by the CV to get fraction stddev
    hstddev_frac = hvar_sum_frac.Clone( f"h{var}__totfracstddev")
    hstddev_frac.Reset()

    # Get CV histogram
    rfilecv = rt.TFile( inputfiles[0] )
    hvar_cv = rfilecv.Get(f"h{var}__CVCV")

    for ibin in range(1,hvar_sum_frac.GetXaxis().GetNbins()+1):
        fracvar = hvar_sum_frac.GetBinContent(ibin) # total fraction variance
        counts_cv = hvar_cv.GetBinContent(ibin)
        if counts_cv>0:
            variance = fracvar*float(counts_cv) # variance of bin due to all detsys
            frac_stddev = sqrt(variance)/counts_cv # frac stddev of bin due to tall detsys
            hstddev_frac.SetBinContent(ibin,frac_stddev) # fractional stddev of bin
            hvar_cv.SetBinError(ibin, sqrt(variance) )

    cvar = rt.TCanvas(f"c{var}",var,1600,600)
    cvar.Divide(2,1)
    cvar.cd(1).SetGridx(1)
    cvar.cd(1).SetGridx(2)
    hvar_cv.SetMinimum(0)
    hvar_cv.Draw("histE1")
    cvar.cd(2).SetGridx(1)
    cvar.cd(2).SetGridy(1)
    hstddev_frac.SetMinimum(0)
    hstddev_frac.Draw("hist")
    cvar.Update()
    cvar.SaveAs(f"{plot_folder}/pngs/c{var}_detsys.png")
    canvases[var] = cvar

    rout.cd()
    hvar_cv.Write()
    hstddev_frac.Write()
    hvar_sum_frac.Write()
    cvar.Write()

print("Done :)")

rout.Close()


            


