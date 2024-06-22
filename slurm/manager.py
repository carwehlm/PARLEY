def createjobs(min_map:str, max_map:str):
    print(f"Creating Job for {min_map, max_map}")

    slurm_script = """#!/bin/bash
    #SBATCH --job-name=parley_MINMAP_MAXMAP        		# Job name
    #SBATCH --output=output_MINMAP_MAXMAP.txt               # Standard output file
    #SBATCH --error=error_MINMAP_MAXMAP.txt          	# Standard error file
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
    python /vol/fob-vol5/nebenf22/bertogla/MA/PARLEY/RQ1_2.py MINMAP MAXMAP

    # Deactivate the virtual environment (optional, for clean-up)
    deactivate"""

    slurm_script = slurm_script.replace("MINMAP",min_map)
    slurm_script = slurm_script.replace("MAXMAP",max_map)

    # Write the SLURM job script to a file
    with open(f'slurm/parley_{min_map}_{max_map}.slurm', 'w') as f:
        f.write(slurm_script)

    print(f"SLURM job script 'parley_{min_map}_{max_map}.slurm has been created successfully.")


if __name__ == '__main__':
    min_map = 11
    max_map = 21
    
    #The Whole 10 Reps for a Map take about 60 Minutes
    for i in range(min_map, max_map):
        createjobs(str(i), str(i+1))