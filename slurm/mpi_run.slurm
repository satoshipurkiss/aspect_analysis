#!/bin/bash -i

# Request resources:
#SBATCH -n 32          # number of MPI ranks (1 per CPU core)
## SBATCH --mem=1G       # memory required per node, in units M, G or T
#SBATCH --mem-per-cpu=2G
#SBATCH --gres=tmp:2G  # temporary disk space required on each allocated compute node ($TMPDIR)
#SBATCH -N 1           # number of compute nodes.
#SBATCH -t 72:00:0       # time limit for job (format: days-hours:minutes:seconds)
#SBATCH -p shared

# Commands to execute start here 
# mpirun will automatically set the number of ranks to the number requested above
module load gcc/native openmpi openblas

## Execute the MPI program
mpirun ./aspect $1
