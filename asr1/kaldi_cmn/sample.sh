#!/bin/bash 
#SBATCH -J kaldi#job name
##SBATCH --mail-user=anh21@mail.aub.edu
##SBATCH --mail-type=ALL
#SBATCH -o output-%j.txt #standard output file
#SBATCH -e errors-%j.txt #standard error file
#SBATCH -p gpu-all #queue used
#SBATCH --gres gpu:0 #number of gpus needed
#SBATCH -n 30
#SBATCH --mem-per-cpu=8G

module purge
module load slurm
#module load cuda10.1/toolkit
module load gcc

./run.sh --stage 9

