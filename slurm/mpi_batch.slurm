#!/bin/bash -i

# Request resources:
#SBATCH -n 32          # number of MPI ranks (1 per CPU core)
## SBATCH --mem=1G       # memory required per node, in units M, G or T
#SBATCH --mem-per-cpu=2G
#SBATCH --gres=tmp:2G  # temporary disk space required on each allocated compute node ($TMPDIR)
#SBATCH -N 1           # number of compute nodes.
#SBATCH -t 72:00:0       # time limit for job (format: days-hours:minutes:seconds)
#SBATCH -p shared
#SBATCH --array=425-486     # Job array range, adjust as needed


# Commands to execute start here 
# mpirun will automatically set the number of ranks to the number requested above
module load gcc/native openmpi openblas

filepath = "/nobackup/tkqk62/diss/code/v5_num_only"

# Adjust the file name format to include zero-padding to three digits
# Assuming your files are named like parameter001, parameter002, etc 
FILE= filepath "/parameter$(printf "%03d" ${SLURM_ARRAY_TASK_ID}).prm"  # Replace 'ext' with your actual file extension

# Execute the MPI program with the specified file
# Assuming your program can take a file as an argument
mpirun ./aspect $FILE
