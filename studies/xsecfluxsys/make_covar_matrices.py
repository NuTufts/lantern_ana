import os,sys
import ROOT as rt

def load_xsecflux_file( input_rootfile, verbose=False ):
  """"
  KEY: TH1D	hvisible_energy_run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_cv;1	
  KEY: TH1D	hvisible_energy_run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_N;1	
  KEY: TH2D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__All_UBGenie;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__All_UBGenie_mean;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__All_UBGenie_variance;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__All_UBGenie_badweights;1	
  KEY: TH2D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__AxFFCCQEshape_UBGenie;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__AxFFCCQEshape_UBGenie_mean;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__AxFFCCQEshape_UBGenie_variance;1	
  KEY: TH1D	hvisible_energy__run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise__AxFFCCQEshape_UBGenie_badweights;1	
  """

  rfile = input_rootfile
  keys = rfile.GetListOfKeys()
  keys.GetEntries()

  hkeylist = []
  hists = {}
  varlist = []
  parlist = []
  samplelist = []
  param_nuniverses = {}
  var_nbins = {}

  for ikey in range( keys.GetEntries() ):
    key = str(keys.At(ikey))
    keyinfo = key.split(" ")
    histname = keyinfo[1].strip()
    if verbose:
      print(f"=== [{ikey}] {histname} ===")
    hkeylist.append( histname )

    # parse the hist name h[varname]__[samplename]__[parname]{'','_mean','_variance','_badweights'}\
    histsplit = histname.split("__")
    if len(histsplit)==3:
      varname = histsplit[0][1:]
      samplename = histsplit[1]
      parname = histsplit[2]
      histtype = ""
      if "_mean" in parname:
        parname = parname[:-5]
        histtype = "mean"
      elif "_variance" in parname:
        parname = parname[:-9]
        histtype = "variance"
      elif "_badweights" in parname:
        parname = parname[:-11]
        histtype = "variance"
      else:
        histtype = "universes"
      h = rfile.Get(histname)
      if verbose:
        print("  variable name: ",varname)
        print("  sample name: ",samplename)
        print("  par name: ",parname)
        print("  hist type: ",histtype)
        print("  hist: ",h)
        print("  type(h): ",type(h))

      hists[(varname,samplename,parname,histtype)] = {"name":histname,"h":h}
      if histtype=="universes":
        param_nuniverses[parname] = h.GetYaxis().GetNbins()
        var_nbins[varname] = h.GetXaxis().GetNbins()

      if varname not in varlist:
        varlist.append(varname)
      if parname not in parlist:
        parlist.append(parname)
      if samplename not in samplelist:
        samplelist.append(samplename)

    else:
      if verbose:
        print("skip")

  # Get the CV and MC num histograms
  cvhists = {}
  mcNhists = {}
  for var in varlist:
    for sample in samplelist:
      has_universes = any((var,sample,par,"universes") in hists for par in parlist)
      hname_cv  = f"h{var}_{sample}_cv"
      hcv = rfile.Get(hname_cv)
      if hcv and not hcv.IsZombie() and hcv.Integral() == 0:
        hcv = rfile.Get(hname_cv + ";1")
      if hcv and not hcv.IsZombie():
        cvhists[(var,sample)] = hcv
      elif has_universes:
        print(f"WARNING: CV histogram not found or null: {hname_cv}")
      hname_n  = f"h{var}_{sample}_N"
      hN = rfile.Get(hname_n)
      if hN and not hN.IsZombie():
        mcNhists[(var,sample)] = hN

      
  print("=== CV histogram diagnostics ===")
  for (var,sample), hcv in cvhists.items():
    integral = hcv.Integral()
    print(f"  cvhist ({var}, {sample}): integral={integral:.4g}, nbins={hcv.GetNbinsX()}")

  samplelist.sort()
  varlist.sort()
  parlist.sort()

  hist_dict = {"samples":samplelist,"params":parlist,"variables":varlist,"num_universe":param_nuniverses,"num_bins":var_nbins,"hists":hists,"cvhists":cvhists,"mcNhists":mcNhists}
  return hist_dict

def form_covariance_matrices( hist_dict, root_outputfile, verbose=False ):

  """
  We use the histograms we've formed and stored in self.var_bininfo to form covariance matrice
  We make a covariance matrix for observable bins between (sample,parameter) combinations 
  """

  root_outputfile.cd()

  if verbose:
    print("Form Covariance Matrices ...")
  # get list of datasets with MC variations
  sample_list = hist_dict['samples']
  par_list = hist_dict['params']
  var_list = hist_dict['variables']
  nbins_per_variable = hist_dict['num_bins']
  hists = hist_dict["hists"]
  cvhists = hist_dict["cvhists"]
        
  # index all observable bins
  # only include (sample, var) pairs that actually have universe histograms
  globalindex = 0
  bin_list = []
  for sample in sample_list:
    for var in var_list:
      has_universes = any((var,sample,par,"universes") in hists for par in par_list)
      if not has_universes:
        continue
      numbins = nbins_per_variable[var]
      for ii in range(numbins):
          bin_list.append( (globalindex,sample,var,ii) )
          globalindex += 1
  num_global_bins = globalindex

  # make covariances between bins for each parameter
  covar_hists = {}
  frac_covar_hists = {}

  for par in par_list:
    hcovar_name = f"hcovar_{par}"
    hcovar = rt.TH2D(hcovar_name,f"covar for {par}",num_global_bins,0,num_global_bins,num_global_bins,0,num_global_bins)
    hfrac_covar_name = f"hfrac_covar_{par}"
    hfrac_covar = rt.TH2D(hfrac_covar_name,f"fractional covar for {par}",num_global_bins,0,num_global_bins,num_global_bins,0,num_global_bins)
    for ibin, (_globalidx, sample, var, _localidx) in enumerate(bin_list):
      label = f"{var},{sample}"
      hcovar.GetXaxis().SetBinLabel(ibin+1, label)
      hcovar.GetYaxis().SetBinLabel(ibin+1, label)
      hfrac_covar.GetXaxis().SetBinLabel(ibin+1, label)
      hfrac_covar.GetYaxis().SetBinLabel(ibin+1, label)
    for ibin in range(num_global_bins):
      for jbin in range(ibin,num_global_bins):
        ibin_info = bin_list[ibin]
        jbin_info = bin_list[jbin]
        # if par not in ibin_info[-1]:
        #   continue
        # if par not in jbin_info[-1]:
        #   continue

        ilocalindex = ibin_info[-1]
        jlocalindex = jbin_info[-1]
        isample = ibin_info[1]
        jsample = jbin_info[1]
        ivariable = ibin_info[2]
        jvariable = jbin_info[2]
        if (ivariable,isample,par,"universes") not in hists or (jvariable,jsample,par,"universes") not in hists:
          continue
        ihout = hists[(ivariable,isample,par,"universes")]['h']
        jhout = hists[(jvariable,jsample,par,"universes")]['h']
        ihmean = hists[(ivariable,isample,par,"mean")]['h']
        jhmean = hists[(jvariable,jsample,par,"mean")]['h']

        iNcv = cvhists[(ivariable,isample)].GetBinContent(ilocalindex+1)
        jNcv = cvhists[(jvariable,jsample)].GetBinContent(jlocalindex+1)

        i_nvariations = ihout.GetYaxis().GetNbins()
        j_nvariations = jhout.GetYaxis().GetNbins()
        if i_nvariations!=j_nvariations:
          raise ValueError(f"num universes for i and j bin do not match: {i_nvariations} and {j_nvariations}")

        covar = 0.0
        if i_nvariations==2:
            var_i = ihout.GetBinContent(ilocalindex+1,1)-ihout.GetBinContent(ilocalindex+1,2)
            var_j = jhout.GetBinContent(jlocalindex+1,1)-jhout.GetBinContent(jlocalindex+1,2)
            covar = var_i*var_j
        elif i_nvariations>2:
            for ii in range(i_nvariations):
                var_i = ihout.GetBinContent(ilocalindex+1,ii+1)-ihmean.GetBinContent(ilocalindex+1)
                var_j = jhout.GetBinContent(jlocalindex+1,ii+1)-jhmean.GetBinContent(jlocalindex+1)
                covar += (var_i*var_j)/float(i_nvariations)

        frac_covar = 0.0
        if iNcv>0.0 and jNcv:
          frac_covar = covar/(iNcv*jNcv)
        
        hcovar.SetBinContent( ibin+1, jbin+1, covar )
        hfrac_covar.SetBinContent( ibin+1, jbin+1, frac_covar )
        if ibin!=jbin:
            hcovar.SetBinContent(jbin+1,ibin+1,covar)
            hfrac_covar.SetBinContent(jbin+1,ibin+1,frac_covar)

    covar_hists[par] = hcovar
    frac_covar_hists[par] = hfrac_covar
    hcovar.Write()
    hfrac_covar.Write()

  hNN = rt.TH2D("hNN",f"num in i-bin x num in j-bin",num_global_bins,0,num_global_bins,num_global_bins,0,num_global_bins)
  for ibin in range(num_global_bins):
    for jbin in range(ibin,num_global_bins):
      ibin_info = bin_list[ibin]
      jbin_info = bin_list[jbin]
      ilocalindex = ibin_info[-1]
      jlocalindex = jbin_info[-1]
      isample = ibin_info[1]
      jsample = jbin_info[1]
      ivariable = ibin_info[2]
      jvariable = jbin_info[2]
      iNcv = cvhists[(ivariable,isample)].GetBinContent(ilocalindex+1)
      jNcv = cvhists[(jvariable,jsample)].GetBinContent(jlocalindex+1)
      binBB = iNcv*jNcv
      if binBB==0.0:
        binBB = 1.0
      hNN.SetBinContent( ibin+1, jbin+1, binBB )
      hNN.SetBinContent( jbin+1, ibin+1, binBB )

  # lets total things up
  hcovar_total_xsecflux = rt.TH2D("hcovar_total_xsecflux",f"covar for all xsec and flux",num_global_bins,0,num_global_bins,num_global_bins,0,num_global_bins)
  hfrac_covar_total_xsecflux = rt.TH2D("hfrac_covar_total_xsecflux",f"frac_covar for all xsec and flux",num_global_bins,0,num_global_bins,num_global_bins,0,num_global_bins)
  for ibin, (_globalidx, sample, var, _localidx) in enumerate(bin_list):
    label = f"{var},{sample}"
    hcovar_total_xsecflux.GetXaxis().SetBinLabel(ibin+1, label)
    hcovar_total_xsecflux.GetYaxis().SetBinLabel(ibin+1, label)
    hfrac_covar_total_xsecflux.GetXaxis().SetBinLabel(ibin+1, label)
    hfrac_covar_total_xsecflux.GetYaxis().SetBinLabel(ibin+1, label)
  for par,hcovar in covar_hists.items():
    hcovar_total_xsecflux.Add( hcovar )
    hfrac_covar_total_xsecflux.Add( frac_covar_hists[par] )
  hfrac_covar_total_xsecflux.Divide( hNN )
  hcovar_total_xsecflux.Write()
  hfrac_covar_total_xsecflux.Write()
  hNN.Write()
    

if __name__=="__main__":

  verbose = "--verbose" in sys.argv or "-v" in sys.argv
  args = [a for a in sys.argv[1:] if a not in ("--verbose", "-v")]

  if len(args) == 1:
    input_rootfilename = args[0]
  else:
    input_rootfilename = "/exp/uboone/app/users/imani/lantern_ana/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_allchannels_run4b.root"

  rinput = rt.TFile(input_rootfilename)

  output_rootfile = "output_covariance_run4b_allchannels.root"
  rout = rt.TFile(output_rootfile,'recreate')

  histdata = load_xsecflux_file( rinput, verbose=verbose )
  form_covariance_matrices( histdata, rout, verbose=verbose )

  rout.Close()
  print(f"Output written to: {output_rootfile}")
