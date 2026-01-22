import os,sys
import ROOT as rt

def load_xsecflux_file( input_rootfile ):
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
      print("skip")

  # Get the CV and MC num histograms
  cvhists = {}
  mcNhists = {}
  for var in varlist:
    for sample in samplelist:
      hname_cv  = f"h{var}_{sample}_cv"
      hcv = rinput.Get(hname_cv)
      if hcv is not None:
        cvhists[(var,sample)] = hcv
      hname_n  = f"h{var}_{sample}_N"
      hN = rinput.Get(hname_n)
      if hN is not None:
        mcNhists[(var,sample)] = hN

      
  samplelist.sort()
  varlist.sort()
  parlist.sort()

  hist_dict = {"samples":samplelist,"params":parlist,"variables":varlist,"num_universe":param_nuniverses,"num_bins":var_nbins,"hists":hists,"cvhists":cvhists,"mcNhists":mcNhists}
  return hist_dict

def form_covariance_matrices( hist_dict, root_outputfile ):

  """
  We use the histograms we've formed and stored in self.var_bininfo to form covariance matrice
  We make a covariance matrix for observable bins between (sample,parameter) combinations 
  """

  root_outputfile.cd()

  print("Form Covariance Matrices ...")
  # get list of datasets with MC variations
  sample_list = hist_dict['samples']
  par_list = hist_dict['params']
  var_list = hist_dict['variables']
  nbins_per_variable = hist_dict['num_bins']
  hists = hist_dict["hists"]
  cvhists = hist_dict["cvhists"]
        
  # index all observable bins
  globalindex = 0
  bin_list = []
  for sample in sample_list:
    for var in var_list:
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
            var_i = ihout.GetBinContent(ibin+1,1)-ihout.GetBinContent(ibin+1,2)
            var_j = jhout.GetBinContent(jbin+1,1)-jhout.GetBinContent(jbin+1,2)
            covar = var_i*var_j
        elif i_nvariations>2:
            for ii in range(i_nvariations):
                var_i = ihout.GetBinContent(ibin+1,ii)-ihmean.GetBinContent(ibin+1)
                var_j = jhout.GetBinContent(jbin+1,ii)-jhmean.GetBinContent(jbin+1)
                covar += (var_i*var_j)/float(i_nvariations)

        frac_covar = 0.0
        if iNcv>0.0 and jNcv:
          frac_covar = covar/(iNcv*jNcv)
        
        hcovar.SetBinContent( ibin+1, jbin+1, covar )
        hfrac_covar.SetBinContent( ibin+1, jbin+1, frac_covar )
        if ibin!=jbin:
            hcovar.SetBinContent(jbin+1,ibin+1,covar)
            hfrac_covar.SetBinContent(jbin+1,ibin+1,frac_covar)

        i_label = f"{ivariable},{isample}"
        j_label = f"{jvariable},{jsample}"
        hcovar.GetXaxis().SetBinLabel(ibin+1,i_label)
        hcovar.GetYaxis().SetBinLabel(jbin+1,j_label)
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
  for par,hcovar in covar_hists.items():
    hcovar_total_xsecflux.Add( hcovar )
    hfrac_covar_total_xsecflux.Add( hcovar )
  hfrac_covar_total_xsecflux.Divide( hNN )
  hcovar_total_xsecflux.Write()
  hfrac_covar_total_xsecflux.Write()
  hNN.Write()
    

if __name__=="__main__":

  # test
  #input_rootfilename = "../numu_cc_inclusive/output_numu_run4a_surprise/xsecflux_numu_cc_inclusive_run4a_surprise.root"
  input_rootfilename = "../numu_cc_inclusive/output_numu_run3b_1mil/output_xsecflux_numu_cc_inclusive_run3b_1mil.root"
  rinput = rt.TFile(input_rootfilename)

  output_rootfile = "test_covariance.root"
  rout = rt.TFile(output_rootfile,'recreate')

  histdata = load_xsecflux_file( rinput )
  form_covariance_matrices( histdata, rout )

  rout.Close()