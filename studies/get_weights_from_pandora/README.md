This folder contains scripts used to extract weights from the pandora selection tree.

## Getting the GENIE tune weight

We needed to grab the GENIE tune weights for each event, which did not get passed into the lantern ntuple properly.

But no matter, as the pandora tree has this information.

To use the script, you have to first go into the script, `Strip_xsecweight.C`, to select which input and output path you want.

There are two hard-coded options currently for the BNB nu and BNB nue overlay files.

Then to run the script, enter:

```
root -x Strip_xsecweight.C
```

## Xsec and Flux systematic uncertainties

The pandora tree also has the xsec and flux weights from the N throws of the systematic uncertainty parameter priors.

TODO: extract these for use by the lantern ana framework.
