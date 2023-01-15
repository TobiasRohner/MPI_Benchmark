#!/bin/bash -l
#SBATCH --job-name=mpi_1024
#SBATCH --account="s1069"
#SBATCH --time=01:00:00
#SBATCH --nodes=1024
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --hint=nomultithread
#SBATCH --output=slurm-%x.%j.out

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
srun ../mpi_bandwidth
