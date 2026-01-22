
Steps:

First start the container, setup uboone software products, and then uboonecode environment.

```
> apptainer shell --cleanenv -B /cvmfs -B /exp/uboone -B /pnfs/uboone -B /run/user -s /bin/bash --env UPS_OVERRIDE="\
-H Linux64bit+3.10-2.17" /cvmfs/uboone.opensciencegrid.org/containers/uboone-devel-sl7
> source /cvmfs/uboone.opensciencegrid.org/products/setup_uboone.sh
> setup uboonecode v10_04_07_20 -q e26:prof
```

Then run the script which prints out spill and POT totals for a data sample given a SAMWEB definition:

Example for run 4b beam on whose samweb def is `MCC9.10_Run4b_v10_04_07_11_BNB_beam_on_surprise_reco2_hist`

```
>python3 getDataInfo.py -v3 -d MCC9.10_Run4b_v10_04_07_11_BNB_beam_on_surprise_reco2_hist
```

You should get the following:

```
Definition MCC9.10_Run4b_v10_04_07_11_BNB_beam_on_surprise_reco2_hist contains 636 files
           EXT         Gate2        E1DCNT        tor860        tor875   E1DCNT_wcut   tor860_wcut   tor875_wcut
    96638186.0    36647889.0    36526495.0     1.493e+20     1.493e+20    34317881.0      1.45e+20      1.45e+20
Warning!! BNB data for some of the requested runs/subruns is not in the database.
Warning!! EXT data for some of the requested runs/subruns is not in the database.
1 runs missing BNB data (number of subruns missing the data): 19900 (7),
1 runs missing EXT data (number of subruns missing the data): 19900 (7),
```

## Output for past samples


```
Definition MCC9.10_Run4b_v10_04_07_11_BNB_beam_on_surprise_reco2_hist contains 636 files
           EXT         Gate2        E1DCNT        tor860        tor875   E1DCNT_wcut   tor860_wcut   tor875_wcut
    96638186.0    36647889.0    36526495.0     1.493e+20     1.493e+20    34317881.0      1.45e+20      1.45e+20
Warning!! BNB data for some of the requested runs/subruns is not in the database.
Warning!! EXT data for some of the requested runs/subruns is not in the database.
1 runs missing BNB data (number of subruns missing the data): 19900 (7),
1 runs missing EXT data (number of subruns missing the data): 19900 (7),
```

```
Definition MCC9.10_Run4b_v10_04_07_09_Run4b_BNB_beam_off_surprise_reco2_hist contains 1681 files
           EXT         Gate2        E1DCNT        tor860        tor875   E1DCNT_wcut   tor860_wcut   tor875_wcut
    94412192.0    35926588.0    35807885.0     1.464e+20     1.464e+20    33645948.0     1.422e+20     1.422e+20
Warning!! BNB data for some of the requested runs/subruns is not in the database.
Warning!! EXT data for some of the requested runs/subruns is not in the database.
1 runs missing BNB data (number of subruns missing the data): 19900 (7),
1 runs missing EXT data (number of subruns missing the data): 19900 (7),
```