Check out more about PARLEY in our SEAMS 2024 paper, publicly available on Arxiv.org here: https://arxiv.org/pdf/2401.17187.pdf. 

To replicate our experiments, you need to install EvoChecker using maven.
To this end, navigate to ./Applications/EvoChecker-master and run mvn install
EvoChecker should be installed and executable from ./Applications/EvoChecker-master/target/EvoChecker-1.1.0.jar

You might need to download the correct PRISM version for your machine from
https://www.prismmodelchecker.org/download.php
so that it is installed in ./Applications/prism
with the terminal command to run PRISM as
./Applications/prism/bin/prism

Finally, we require the following python packages:
- numpy
- collections
- copy
- csv
- heapq
- os
- seaborn
- matplotlib.pyplot
- deap.tools._hypervolume.pyhv
- scipy.stats
- subprocess
- json
- multiprocessing
- re

This command should be sufficient:
```
pip3 install -r requirements.txt
```

You can replicate our experiments with running the following scripts:
RQ1_2.py
- creates 90 random maps of size 10x10
- synthesises PRISM models from these maps with Dijkstra's shortest path algorithm
- uses PRISM to generate the baseline solution
- invokes our script to synthesise an uncertainty controller using the PARLEY methodology
- invokes EvoChecker (with multiple processors, set num_processes=1 if you want to use only one processor)
- generates Pareto-fronts and puts them in the plots/fronts directory
- runs a statistical analysis using Hypervolume and Spread across all 90 maps over 10 repetitions

RQ3.py generates maps of different sizes that can be used for scalability analysis

Alongside, we provide a PRISM model for the web-server in ./models/servers/

Finally, we provide the code to replicate the turtlebot application in the ./turtlebot directory alongside a dedicated README file.

Any generated data used in our study can be found in the ./Applications/EvoChecker-main/data directory
