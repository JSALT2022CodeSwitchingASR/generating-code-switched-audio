#!/bin/bash 
#SBATCH -J seame2 #job name
##SBATCH --mail-user=anh21@mail.aub.edu
##SBATCH --mail-type=ALL
#SBATCH -o output-%j.txt #standard output file
#SBATCH -e errors-%j.txt #standard error file
#SBATCH -p gpu-all #queue used
#SBATCH --gres gpu:4 #number of gpus needed
#SBATCH -N 1
#SBATCH --cpus-per-task 20
#SBATCH --mem=50G
#SBATCH -w crimv3mgpu026
##SBATCH -w crimv3mgpu018

module purge
module load slurm
#module load cuda10.0/toolkit
module load cuda11.3/toolkit
module load gcc

./run_bigram_subset2.sh

# srun -p gpu-all --gres gpu:3 --mem-per-cpu=10G -w crimv3mgpu005 --pty bash