# lantern_ana

Package for analyzing Lantern ntuple files.

This package depends on libraries collected in the [ubdl repository](https://github.com/larbys/ubdl).
These must be built and environment variables set for the `lantern_ana` functions to work.
Follow the ubdl repository for build instructions.
A more convenient alternative is to use `lantern_ana` while running inside a docker or singularity container with the ubdl installed.

For information on the ROOT tree within the ntuple file see the [gen2ntuple](https://github.com/NuTufts/gen2ntuple/).

We also aim to provide tools to look at quantities from the upstream reconstruction chain or low-level truth information.

# Getting Setup

The dependencies of this package are:

  * python3
  * python modules
    * yaml
    * yamlinclude
  * ROOT

The easiest thing to do is to run in one of our containers. This will provide the dependencies we use.

We focus for now on how to setup the container and the shell environment to use this analysis framework.

  * On the Tufts cluster
  * On the MicroBooNE GPVM machines -- though in this setup, we access the container located on CVMFS and is more general for those computing environments which can see the container.

## Getting setup (on the Tufts cluster)

Logging into the Tufts cluster and setting up an interactive working node:

  ```
  ssh -XY [username]@login.pax.tufts.edu
  ```

Note: you need to be on the Tufts network to access the cluster.
That means connecting to Tufts or connecting by ethernet cord to the network.
In other cases, you will need to connect to the Tufts VPN.
(Instructions fo rhte Tufts VPON can be found [here](https://access.tufts.edu/vpn)).

To setup a worker node on the cluster, do the following:

  ```
  srun --pty -p wongjiradlab --time 8:00:00 bash
  ```

This is a slurm command. You can learn more about slurm through the following resources
  * a quick [guide](https://huoww07.github.io/Bioinformatics-for-RNA-Seq/slides/Tufts_HPC_Cluster_New_User_Guide.pdf)
  * a [youtube playlist](https://www.youtube.com/watch?v=K_JIPrcPHCg&list=PL7kL5D8ITGyUO4_x5EvVmZ6_NBV0RnDF-) giving a more in-depth introduction.


0. First-time setup: You'll need to get a copy of this repository onto the cluster.
   You only need to do this once (or when you want a new copy of this repository).

    * After logging into the cluster and getting a worker node, go to your working folder in the `wongjiradlabnu` storage area:
      ```
      cd /cluster/tufts/wongjiradlabnu/[username]
      ```
    * Clone this repository
      ```
      git clone https://github.com/nutufts/lantern_ana
      ```

For the following steps: you need to perform them each time you connect to the cluster in a new shell.
      
1. Log into the cluster and start-up a node as instructed above
2. Go to your copy of `lantern_ana`
3. Setup your shell to have singularity and start a new shell in the container
      ```
      module load singularity/3.5.3
      singularity shell --cleanenv /cluster/tufts/wongjiradlabnu/nutufts/containers/lantern_v2_me_06_03_prod/
      ```
    After your run this command, you will be "inside the container".
    Alternatively, use the script in this repository.
       ```
       ./start_tufts_container.sh
       ```
5. Use the script inside this repository to setup the shell environment
      ```
      source setenv_tufts_container.sh
      ```
   
One way to test everything went well is to quickly load the `lantern_ana` module.

```
python3 -c "import lantern_ana"
```

