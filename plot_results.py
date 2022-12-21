#!/usr/bin/env python3

import sys
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

import matplotlib as mpl
#mpl.rcParams['figure.dpi'] = 300


TMPDIR = sys.argv[1]
OUTDIR = sys.argv[2]


file_re = re.compile(r'^slurm-mpi_\d+\.\d+\.out$')
files = [f for f in os.listdir(TMPDIR) if file_re.match(f) is not None]
print(files)

ranks = list(sorted(list(set([int(f.split('.')[0][10:]) for f in files]))))
print(ranks)

datafiles = [(rank, max(filter(lambda f: int(f.split('_')[1].split('.')[0]) == rank,
                               files
                              ),
                        key=lambda f: int(f.split('.')[1])
                       )) for rank in ranks]
print(datafiles)

bandwidth_cray = {}
bandwidth_custom = {}
for rank, fname in sorted(datafiles, key=lambda f: f[0]):
    if rank not in bandwidth_cray:
        bandwidth_cray[rank] = {}
    if rank not in bandwidth_custom:
        bandwidth_custom[rank] = {}
    with open(os.path.join(TMPDIR, fname), 'r') as f:
        msg_size = None
        for line in f.readlines():
            if line.startswith('Message Size:'):
                msg_size = line.split(' ')[-1].strip()
            if line.startswith('MPI_Alltoall'):
                bandwidth_cray[rank][msg_size] = float(line.split(' ')[-1][:-5])
            if line.startswith('MPI_Sendrecv'):
                bandwidth_custom[rank][msg_size] = float(line.split(' ')[-1][:-5])
print(bandwidth_cray)
print(bandwidth_custom)

msg_sizes = list(sorted(list(reduce(lambda a,b: a|b, [set(bandwidth_cray[rank].keys()) for rank in ranks], set())
                             | reduce(lambda a,b: a|b, [set(bandwidth_custom[rank].keys()) for rank in ranks], set())),
                        key = lambda size: int(size[:-2]) * {'KB':1024, 'MB':1024**2, 'GB':1024**3}[size[-2:]]))
print(msg_sizes)

num_ranks = len(ranks)
num_msg_sizes = len(msg_sizes)
bw_cray_arr = np.full((num_ranks, num_msg_sizes), np.nan)
bw_custom_arr = np.full((num_ranks, num_msg_sizes), np.nan)
for ridx, rank in enumerate(ranks):
    for msidx, msg_size in enumerate(msg_sizes):
        bw_cray_arr[ridx,msidx] = bandwidth_cray[rank].get(msg_size, np.nan)
        bw_custom_arr[ridx,msidx] = bandwidth_custom[rank].get(msg_size, np.nan)
speedup = bw_custom_arr / bw_cray_arr
max_bw = max(np.nanmax(bw_cray_arr), np.nanmax(bw_custom_arr))
min_bw = min(np.nanmin(bw_cray_arr), np.nanmin(bw_custom_arr))
max_diff = max(np.nanmax(speedup), 1/np.nanmin(speedup))

def plot(data, title, **kwargs):
    plt.figure(figsize=(1.25*16, 1.25*9))
    plt.pcolormesh(data, **kwargs)
    plt.colorbar()
    plt.xticks(np.linspace(0.5, num_msg_sizes-0.5, num_msg_sizes), msg_sizes)
    plt.yticks(np.linspace(0.5, num_ranks-0.5, num_ranks), ranks)
    plt.xlabel('Message Size')
    plt.ylabel('Number of MPI Ranks')
    plt.title(title)

plot(bw_cray_arr, 'Bandwidth of Native MPI_Alltoall in GB/s', vmin=min_bw, vmax=max_bw)
plt.savefig(os.path.join(OUTDIR, 'bandwidth_native.png'))
plt.show()
plot(bw_custom_arr, 'Bandwidth of Custom MPI_Alltoall in GB/s', vmin=min_bw, vmax=max_bw)
plt.savefig(os.path.join(OUTDIR, 'bandwidth_custom.png'))
plt.show()
plot(bw_custom_arr / bw_cray_arr, 'Speedup of Custom MPI_Alltoall over Native', cmap='RdBu', norm=mpl.colors.LogNorm(vmin=1/max_diff, vmax=max_diff))
plt.savefig(os.path.join(OUTDIR, 'speedup.png'))
plt.show()
