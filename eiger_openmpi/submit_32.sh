#!/bin/bash -l
#SBATCH --job-name=mpi_32
#SBATCH --account="s1069"
#SBATCH --time=01:00:00
#SBATCH --nodes=32
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --partition=normal
#SBATCH --constraint=mc
#SBATCH --hint=nomultithread
#SBATCH --output=slurm-%x.%j.out

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
~/bin/mpirun ../mpi_bandwidth
