# Deletion Algorithm for the Satisfiability Problem based on Boolean Arrays
_This algorithm is a particular case of the Shafer and Shenoy deletion algorithm or the bucket elimination scheme. This algorithm can solve moderate problems, even in cases where the associated connectivity graph has a large three-width, which would imply that the usual deletion algorithm is unfeasible._

## Running experiments
### Format
_The file that controls the execution of the experiments is "satSolver.py", in which a call to the function "deleting_with_tables" is made, with the following format:_
```
deleting_with_tables(fileCNF[,Q][,Upgrade][,Prior][,Split][,Smessages][,fileResults])
```
* **fileCNF:** File containing the list of boolean satisfiability problems (SAT), each problem represented in a CNF format file.
* **Q:** .
* **Upgrade:** .
* **Prior:** .
* **Split:** .
* **Smessages:** Boolean parameter that indicates whether to display messages of the resolution process performed by the algorithm. Default value: False.
* **fileResults:** File in CSV format, with the results of the experiments. The resolution times for each combination of Q, Upgrade, Prior and Split are shown here. The file is saved in the directory "data_In_Out". Default value:"salida.csv"