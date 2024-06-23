#!/bin/bash
    #SBATCH --job-name=parley_11_12        		                # Job name
    #SBATCH --output=slurm/logs/output_11_12.txt                # Standard output file
    #SBATCH --error=slurm/logs/error_11_12.txt          	    # Standard error file
    #SBATCH --time=02:00:00                 		                    # Time limit (2 hours)
    #SBATCH --partition=longrun             		                    # Partition name
    #SBATCH --nodes=1                       		                    # Number of nodes
    #SBATCH --ntasks-per-node=1                                        # Number of processes per Node
    #SBATCH --cpus-per-task=16                 		                    # Number of CPU cores per task
    #SBATCH --ntasks-per-core=1                                         # Disable Hyperthreads
    #SBATCH --mem=128G                      		                    # Memory per node

    export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
    

    # Load your specific Python module if needed
    module load anaconda/3-2023.03

    # Run your Python script with two integer arguments
    python /vol/fob-vol5/nebenf22/bertogla/MA/PARLEY/RQ1_2.py 11 12

    # Deactivate the virtual environment (optional, for clean-up)
    conda deactivate