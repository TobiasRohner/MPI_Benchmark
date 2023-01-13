#!/bin/bash -l
#SBATCH --job-name=mpi_2
#SBATCH --account="s1069"
#SBATCH --time=00:05:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --hint=nomultithread
#SBATCH --output=slurm-%x.%j.out

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
~/openmpi/bin/mpirun ../mpi_bandwidth
