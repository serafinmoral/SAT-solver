# Deletion Algorithm for the Satisfiability Problem based on Boolean Arrays
__

## Running experiments ⚙️
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
* **fileResults:** File in CSV format, with the results of the experiments. The resolution times for each combination of Q, Upgrade, Prior and Split are shown here. The file is saved in the directory "data_In_Out". Default value: "salida.csv"

## Built with 🛠️

_This software was built with the Python programming language, version 3.8, using the Numpy library to work with Boolean tables._

* [Python](https://www.python.org/downloads/release/python-380/) - Versión 3.8
* [Numpy](https://numpy.org/install/) - Numpy library installation

## Contributions 🖇️

* Elaboration of scientific articles: Deletion Algorithm for the Satisfiability Problem based on Boolean Arrays. This paper proposes a deletion algorithm for the satisfiability problem. The algorithm is based on the general Davis and Putnam deletion algorithm DP, expressed as a bucket elimination algorithm, representing sets of clauses with the same set of variables by means of a Boolean array. This algorithm is a particular case of the Shafer and Shenoy deletion algorithm or the bucket elimination scheme. This algorithm can solve moderate problems, even in cases where the associated connectivity graph has a large three-width, which would imply that the usual deletion algorithm is unfeasible.

* Library with the Python source code of the erasure algorithm, highlighting the marginalization process.

## Authors ✒️

_This library is the product of a doctoral thesis work to solve Boolean satisfiability problems and their variants using the strategies used in graphical models._

* **Efraín Díaz Macías** - *PhD Candidate* - [efraindiaz@uteq.edu.ec](efraindiaz@uteq.edu.ec)
* **Serafín Moral Callejón** - *Thesis Director* - [smc@decsai.ugr.es](efraindiaz@uteq.edu.ec)