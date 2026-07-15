import os, sys
import ROOT as rt

# ── Variables of interest ────────────────────────────────────────────────────
# These must match the varname as parsed from the file, i.e. everything after
# the leading 'h' in the histogram name up to the first '__'.
# From the file: hnumuCC1piNpReco_delAlphaT__...__..., the varname is
# "numuCC1piNpReco_delAlphaT" (the full prefix including sample tag).
VARIABLES_OF_INTEREST = [
    "numuCC1piNpReco_delAlphaT",
    "numuCC1piNpReco_pN",
    "numuCC1piNpReco_delPTT",
    "numuCC1piNpReco_muKE",
    "numuCC1piNpReco_pionKE",
    "numuCC1piNpReco_maxprotonKE",
]

# ─────────────────────────────────────────────────────────────────────────────
def load_xsecflux_file(input_rootfile):
    """
    Parse an xsecflux ROOT file and return a dict of histograms keyed by
    (varname, samplename, parname, histtype).

    Expected histogram naming convention:
      h{varname}__{samplename}__{parname}             -> 2D universe hist
      h{varname}__{samplename}__{parname}_mean        -> 1D mean over universes
      h{varname}__{samplename}__{parname}_variance    -> 1D variance over universes
      h{varname}__{samplename}__{parname}_badweights  -> 1D bad-weight count
      h{varname}_{samplename}_cv                      -> central-value histogram
      h{varname}_{samplename}_N                       -> MC-stat histogram
    """
    rfile = input_rootfile
    keys  = rfile.GetListOfKeys()

    hists            = {}
    varlist          = []
    parlist          = []
    samplelist       = []
    param_nuniverses = {}
    var_nbins        = {}

    for ikey in range(keys.GetEntries()):
        key      = str(keys.At(ikey))
        keyinfo  = key.split(" ")
        histname = keyinfo[1].strip()
        print(f"=== [{ikey}] {histname} ===")

        # Only process histograms with the double-underscore naming pattern
        histsplit = histname.split("__")
        if len(histsplit) != 3:
            print("  skip (not a systematic universe hist)")
            continue

        varname    = histsplit[0][1:]   # strip leading 'h'
        samplename = histsplit[1]
        parname    = histsplit[2]

        # Determine histogram type from suffix
        histtype = "universes"
        if parname.endswith("_mean"):
            parname  = parname[:-5]
            histtype = "mean"
        elif parname.endswith("_variance"):
            parname  = parname[:-9]
            histtype = "variance"
        elif parname.endswith("_badweights"):
            parname  = parname[:-11]
            histtype = "badweights"

        h = rfile.Get(histname)
        print(f"  variable={varname}  sample={samplename}  par={parname}  type={histtype}  h={h}")

        hists[(varname, samplename, parname, histtype)] = {"name": histname, "h": h}

        if histtype == "universes":
            param_nuniverses[parname] = h.GetYaxis().GetNbins()
            var_nbins[varname]        = h.GetXaxis().GetNbins()

        if varname    not in varlist:    varlist.append(varname)
        if parname    not in parlist:    parlist.append(parname)
        if samplename not in samplelist: samplelist.append(samplename)

    # ── Load CV and MC-N histograms ───────────────────────────────────────────
    # Naming: h{varname}_{samplename}_cv  (single underscore, no double)
    # e.g. hnumuCC1piNpReco_delAlphaT_run1_bnb_nu_overlay_mcc9_v28_wctagger_cv
    cvhists  = {}
    mcNhists = {}
    for var in varlist:
        for sample in samplelist:
            hcv = rfile.Get(f"h{var}_{sample}_cv")
            if hcv:
                cvhists[(var, sample)] = hcv
            else:
                print(f"  WARNING: CV hist not found: h{var}_{sample}_cv")
            hN = rfile.Get(f"h{var}_{sample}_N")
            if hN:
                mcNhists[(var, sample)] = hN
            else:
                print(f"  WARNING: N hist not found: h{var}_{sample}_N")

    samplelist.sort()
    varlist.sort()
    parlist.sort()

    return {
        "samples":      samplelist,
        "params":       parlist,
        "variables":    varlist,
        "num_universe": param_nuniverses,
        "num_bins":     var_nbins,
        "hists":        hists,
        "cvhists":      cvhists,
        "mcNhists":     mcNhists,
    }


# ─────────────────────────────────────────────────────────────────────────────
def form_covariance_matrix_for_variable(variable, hist_dict, root_outputfile):
    """
    Build absolute and fractional covariance matrices for a single variable,
    summed over all parameters (xsec + flux).

    Outputs written to root_outputfile:
      hcovar_{par}_{variable}           per-parameter absolute covariance
      hfrac_covar_{par}_{variable}      per-parameter fractional covariance
      hcovar_total_{variable}           total absolute covariance (all pars summed)
      hfrac_covar_total_{variable}      total fractional covariance (all pars summed)
    """
    root_outputfile.cd()

    sample_list      = hist_dict["samples"]
    par_list         = hist_dict["params"]
    nbins_per_var    = hist_dict["num_bins"]
    hists            = hist_dict["hists"]
    cvhists          = hist_dict["cvhists"]

    # ── Check that this variable actually exists in the file ─────────────────
    if variable not in nbins_per_var:
        print(f"  WARNING: variable '{variable}' not found in input file — skipping.")
        return

    # ── Build the flat bin list for this variable only ───────────────────────
    # Each entry: (global_index, sample, variable, local_bin_index)
    bin_list     = []
    global_index = 0
    for sample in sample_list:
        if (variable, sample) not in cvhists:
            print(f"  WARNING: no CV hist for ({variable}, {sample}) — skipping sample.")
            continue
        numbins = nbins_per_var[variable]
        for ibin in range(numbins):
            bin_list.append((global_index, sample, variable, ibin))
            global_index += 1

    num_bins = len(bin_list)
    if num_bins == 0:
        print(f"  WARNING: no bins found for variable '{variable}' — skipping.")
        return

    print(f"\n  [{variable}] building {num_bins}×{num_bins} covariance matrices "
          f"over {len(par_list)} parameters ...")

    # ── Per-parameter covariance matrices ────────────────────────────────────
    covar_hists      = {}
    frac_covar_hists = {}

    for par in par_list:
        # Check that universe histograms exist for this (variable, par) combo
        has_universes = any(
            (variable, sample, par, "universes") in hists
            for sample in sample_list
        )
        if not has_universes:
            print(f"    skipping par '{par}' — no universe hists for '{variable}'")
            continue

        hcovar_name      = f"hcovar_{par}_{variable}"
        hfrac_covar_name = f"hfrac_covar_{par}_{variable}"
        hcovar           = rt.TH2D(hcovar_name,      f"Covariance ({variable}, {par})",
                                   num_bins, 0, num_bins, num_bins, 0, num_bins)
        hfrac_covar      = rt.TH2D(hfrac_covar_name, f"Frac. Covariance ({variable}, {par})",
                                   num_bins, 0, num_bins, num_bins, 0, num_bins)

        for ibin in range(num_bins):
            for jbin in range(ibin, num_bins):
                igidx, isample, ivar, ilocalidx = bin_list[ibin]
                jgidx, jsample, jvar, jlocalidx = bin_list[jbin]

                # ── Retrieve histograms; skip if missing ──────────────────────
                ikey_uni  = (ivar, isample, par, "universes")
                jkey_uni  = (jvar, jsample, par, "universes")
                ikey_mean = (ivar, isample, par, "mean")
                jkey_mean = (jvar, jsample, par, "mean")

                if ikey_uni not in hists or jkey_uni not in hists:
                    continue

                ihout  = hists[ikey_uni]["h"]
                jhout  = hists[jkey_uni]["h"]
                ihmean = hists[ikey_mean]["h"] if ikey_mean in hists else None
                jhmean = hists[jkey_mean]["h"] if jkey_mean in hists else None

                iNcv = cvhists[(ivar, isample)].GetBinContent(ilocalidx + 1)
                jNcv = cvhists[(jvar, jsample)].GetBinContent(jlocalidx + 1)

                i_nvariations = ihout.GetYaxis().GetNbins()
                j_nvariations = jhout.GetYaxis().GetNbins()
                if i_nvariations != j_nvariations:
                    raise ValueError(
                        f"Universe count mismatch for par={par}: "
                        f"i={i_nvariations}, j={j_nvariations}"
                    )

                # ── Compute covariance ────────────────────────────────────────
                covar = 0.0

                if i_nvariations == 2:
                    # Unisim: two-point (high/low) variation
                    # BUG FIX: use local bin indices (ilocalidx/jlocalidx), not global
                    delta_i = (ihout.GetBinContent(ilocalidx + 1, 1)
                               - ihout.GetBinContent(ilocalidx + 1, 2))
                    delta_j = (jhout.GetBinContent(jlocalidx + 1, 1)
                               - jhout.GetBinContent(jlocalidx + 1, 2))
                    covar   = delta_i * delta_j

                elif i_nvariations > 2:
                    # Multisim: average over universes
                    # Fall back to bin content mean if no mean histogram
                    if ihmean is None or jhmean is None:
                        print(f"    WARNING: no mean hist for par={par}, "
                              f"({ivar},{isample}) or ({jvar},{jsample}) — using 0 as mean")
                    for iuniv in range(i_nvariations):
                        # ROOT bins are 1-indexed; iuniv+1 for universe axis
                        i_mean = ihmean.GetBinContent(ilocalidx + 1) if ihmean else 0.0
                        j_mean = jhmean.GetBinContent(jlocalidx + 1) if jhmean else 0.0
                        delta_i = ihout.GetBinContent(ilocalidx + 1, iuniv + 1) - i_mean
                        delta_j = jhout.GetBinContent(jlocalidx + 1, iuniv + 1) - j_mean
                        covar  += (delta_i * delta_j) / float(i_nvariations)

                # ── Fractional covariance ─────────────────────────────────────
                frac_covar = (covar / (iNcv * jNcv)) if (iNcv > 0 and jNcv > 0) else 0.0

                # ── Axis labels ───────────────────────────────────────────────
                ilabel = f"{ivar},{isample},bin{ilocalidx}"
                jlabel = f"{jvar},{jsample},bin{jlocalidx}"
                hcovar.GetXaxis().SetBinLabel(ibin + 1, ilabel)
                hcovar.GetYaxis().SetBinLabel(jbin + 1, jlabel)

                # ── Fill (symmetric) ──────────────────────────────────────────
                hcovar.SetBinContent(ibin + 1, jbin + 1, covar)
                hfrac_covar.SetBinContent(ibin + 1, jbin + 1, frac_covar)
                if ibin != jbin:
                    hcovar.SetBinContent(jbin + 1, ibin + 1, covar)
                    hfrac_covar.SetBinContent(jbin + 1, ibin + 1, frac_covar)

        covar_hists[par]      = hcovar
        frac_covar_hists[par] = hfrac_covar
        hcovar.Write()
        hfrac_covar.Write()

    # ── Total (all-parameter sum) covariance matrices ─────────────────────────
    hcovar_total      = rt.TH2D(f"hcovar_total_{variable}",
                                f"Total xsec+flux covariance ({variable})",
                                num_bins, 0, num_bins, num_bins, 0, num_bins)
    hfrac_covar_total = rt.TH2D(f"hfrac_covar_total_{variable}",
                                f"Total xsec+flux frac. covariance ({variable})",
                                num_bins, 0, num_bins, num_bins, 0, num_bins)

    for par, hcovar in covar_hists.items():
        hcovar_total.Add(hcovar)
        hfrac_covar_total.Add(frac_covar_hists[par])   # BUG FIX: was adding hcovar twice

    hcovar_total.Write()
    hfrac_covar_total.Write()

    print(f"  [{variable}] done — wrote {len(covar_hists)} per-parameter matrices "
          f"+ 2 total matrices.")


# ─────────────────────────────────────────────────────────────────────────────
def form_all_covariance_matrices(hist_dict, root_outputfile,
                                 variables_of_interest=None):
    """
    Loop over each variable of interest and build its covariance matrices
    independently.  Pass variables_of_interest=None to process every variable
    found in the file.
    """
    all_vars = hist_dict["variables"]
    if variables_of_interest is not None:
        # Warn if a requested variable is missing from the file
        for v in variables_of_interest:
            if v not in all_vars:
                print(f"WARNING: requested variable '{v}' not found in input file.")
        target_vars = [v for v in variables_of_interest if v in all_vars]
    else:
        target_vars = all_vars

    print(f"\nWill build covariance matrices for: {target_vars}\n")

    for variable in target_vars:
        print(f"\n{'='*60}")
        print(f"  Processing variable: {variable}")
        print(f"{'='*60}")
        form_covariance_matrix_for_variable(variable, hist_dict, root_outputfile)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    if len(sys.argv) != 2 or sys.argv[1] == "--help":
        print("usage: python3 make_covar_matrices.py <input_xsecflux.root>")
        sys.exit(1)

    input_rootfilename = sys.argv[1]
    rinput = rt.TFile(input_rootfilename)
    if not rinput or rinput.IsZombie():
        print(f"ERROR: could not open {input_rootfilename}")
        sys.exit(1)

    output_rootfilename = "output_covariance.root"
    rout = rt.TFile(output_rootfilename, "recreate")

    hist_dict = load_xsecflux_file(rinput)
    form_all_covariance_matrices(hist_dict, rout,
                                 variables_of_interest=VARIABLES_OF_INTEREST)

    rout.Close()
    rinput.Close()
    print(f"\nDone. Output written to: {output_rootfilename}")