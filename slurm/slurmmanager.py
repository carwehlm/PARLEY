import subprocess
import sys
# scontrol show job JOBID
# scontrol show node NODE
# squeue -u bertogla
# scancel JOBID

def createjobs(min_map:str, max_map:str):
    print(f"Creating Job for {min_map, max_map}")

    slurm_script = """#!/bin/bash
    #SBATCH --job-name=parley_MINMAP_MAXMAP        		                # Job name
    #SBATCH --output=slurm/logs/output_MINMAP_MAXMAP.txt                # Standard output file
    #SBATCH --error=slurm/logs/error_MINMAP_MAXMAP.txt          	    # Standard error file
    #SBATCH --time=02:00:00                 		                    # Time limit (2 hours)
    #SBATCH --partition=longrun             		                    # Partition name
    #SBATCH --nodes=1                       		                    # Number of nodes
    #SBATCH --ntasks-per-node=16                                        # Number of processes per Node
    #SBATCH --cpus-per-task=1                 		                    # Number of CPU cores per task
    #SBATCH --ntasks-per-core=1                                         # Disable Hyperthreads
    #SBATCH --mem=128G                      		                    # Memory per node

    export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
    
    # Load your specific Python module if needed
    module load anaconda/3-2023.03

    # Run your Python script with two integer arguments
    python /vol/fob-vol5/nebenf22/bertogla/MA/PARLEY/RQ1_2.py MINMAP MAXMAP

    # Deactivate the virtual environment (optional, for clean-up)
    conda deactivate"""

    slurm_script = slurm_script.replace("MINMAP",min_map)
    slurm_script = slurm_script.replace("MAXMAP",max_map)

    # Write the SLURM job script to a file
    filepath_slurmscript = f'slurm/parley_{min_map}_{max_map}.slurm'
    with open(filepath_slurmscript, 'w') as f:
        f.write(slurm_script)

    print(f"SLURM job script 'parley_{min_map}_{max_map}.slurm has been created successfully.")
    return filepath_slurmscript

def submit_slurm_job(filepath_slurm_script):
    # Command to submit SLURM job using sbatch
    command = f"sbatch {filepath_slurm_script}"

    # Execute the command
    try:
        output = subprocess.check_output(command, shell=True)
        job_id = output.decode('utf-8').strip().split()[-1]  # Extract job ID from sbatch output
        print(f"SLURM job submitted successfully with Job ID: {job_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting SLURM job: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: python slurmmanager.py <int1 min_maps> <int2 max_maps> <s for Single or m for Multiple>")
        sys.exit(1)
    min_maps    = int(sys.argv[1]) #This changes the Number of ROBOTs. -Starts at 10
    max_maps    = int(sys.argv[2]) #This changes the Number of ROBOTs. -Ends at 100
    workmode      = sys.argv[3] #This changes if its multiple single jobs or one big one
    
    #The Whole 10 Reps for a Map take about 60 Minutes in Grünau1
    #Run Multiple small jobs
    if workmode == "m":
        for i in range(min_maps, max_maps):
            filepath_slurmscript = createjobs(str(i), str(i+1))     #Create the slurm script
            submit_slurm_job(filepath_slurmscript)                  #Submit the slurm script
    
    #Run one big Job
    if workmode == "s":
        filepath_slurmscript = createjobs(str(min_maps), str(max_maps))     #Create the slurm script
        submit_slurm_job(filepath_slurmscript)                              #Submit the slurm script

    else:
        print(f"Workmode {workmode} not recognized. Use either 'm' for multiple jobs with one map or 's' for a single job with multiple maps")