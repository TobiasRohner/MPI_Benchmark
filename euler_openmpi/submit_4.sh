#!/bin/bash -l
#SBATCH --job-name=mpi_4
#SBATCH --time=00:20:00
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=65536MB
#SBATCH --hint=nomultithread
#SBATCH --output=slurm-%x.%j.out

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
mpirun mpi_bandwidth
