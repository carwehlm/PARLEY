#!/bin/bash
    #SBATCH --job-name=parley_11_12        		# Job name
    #SBATCH --output=output_11_12.txt               # Standard output file
    #SBATCH --error=error_11_12.txt          	# Standard error file
    #SBATCH --time=02:00:00                 		# Time limit (2 hours)
    #SBATCH --partition=gruenau             		# Partition name
    #SBATCH --nodes=1                       		# Number of nodes
    #SBATCH --ntasks=1                      		# Number of tasks
    #SBATCH --cpus-per-task=16              		# Number of CPU cores per task
    #SBATCH --mem=128G                      		# Memory per node

    # Load any required modules (if any)
    module load python/your_python_version  # Load your specific Python module if needed

    # Activate the virtual environment
    source /usr/local/anaconda3-2023.03/envs/flair/bin/activate

    # Run your Python script with two integer arguments
    python /vol/fob-vol5/nebenf22/bertogla/MA/PARLEY/RQ1_2.py 11 12

    # Deactivate the virtual environment (optional, for clean-up)
    deactivate