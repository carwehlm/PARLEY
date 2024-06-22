#!/bin/bash
    #SBATCH --job-name=parley_12_13        		                # Job name
    #SBATCH --output=slurm/logs/output_12_13.txt                # Standard output file
    #SBATCH --error=slurm/logs/error_12_13.txt          	    # Standard error file
    #SBATCH --time=02:00:00                 		                    # Time limit (2 hours)
    #SBATCH --partition=gruenau             		                    # Partition name
    #SBATCH --nodes=1                       		                    # Number of nodes
    #SBATCH --ntasks=1                      		                    # Number of tasks
    #SBATCH --cpus-per-task=16              		                    # Number of CPU cores per task
    #SBATCH --mem=128G                      		                    # Memory per node

    # Load your specific Python module if needed
    module load anaconda/3-2023.03

    # Run your Python script with two integer arguments
    python /vol/fob-vol5/nebenf22/bertogla/MA/PARLEY/RQ1_2.py 12 13

    # Deactivate the virtual environment (optional, for clean-up)
    conda deactivate