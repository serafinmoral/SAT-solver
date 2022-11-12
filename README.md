# Deletion Algorithm for the Marginal Problem in Propositional Logic based on Boolean Arrays
_The algorithm is based on the general Davis and Putnam deletion algorithm DP, expressed as a bucket elimination algorithm, representing sets of clauses with the same set of variables by means of a Boolean array. The main contribution is the development of alternative procedures when deleting a variable which allow more efficient computations. In particular, it takes advantage of the case in which the variable to delete is determined by a subset of the rest of variables. It also provides a set of useful results and tools for reasoning with Boolean tables. This algorithm is a particular case of the Shafer and Shenoy deletion algorithm or the bucket elimination scheme. The algorithms are implemented using Python and the NumPy library. Experiments show that this procedure is feasible for intermediate problems._

## Running experiments ⚙️
### Format
_The file that controls the execution of the experiments is "satSolver.py", in which a call to the function "deleting_with_tables" is made, with the following format:_
```
deleting_with_tables(fileCNF[,Q][,Upgrade][,Prior][,Split][,Smessages][,fileResults])
```
* **fileCNF:** File containing the list of boolean satisfiability problems (SAT), each problem represented in a CNF format file.
* **Q:** Default value: [5,10,15,20,25,30].
* **Upgrade:** Default value: [False].
* **Prior:** Default value: [True].
* **Split:** Default value: [True].
* **Smessages:** Boolean parameter that indicates whether to display messages of the resolution process performed by the algorithm. Default value: False.
* **fileResults:** File in CSV format, with the results of the experiments. The resolution times for each combination of Q, Upgrade, Prior and Split are shown here. The file is saved in the directory "data_In_Out". Default value: "salida.csv"

## Built with 🛠️

_This software was built with the Python programming language, version 3.8, using the Numpy library to work with Boolean tables._

* [Python](https://www.python.org/downloads/release/python-380/) - Versión 3.8
* [Numpy](https://numpy.org/install/) - Numpy library installation

## Contributions 🖇️

* Elaboration of scientific articles: A Deletion Algorithm for the Marginal Problem in Propositional Logic based on Boolean Arrays. This algorithm is a particular case of the Shafer and Shenoy deletion algorithm or the bucket elimination scheme. This algorithm can solve moderate problems, even in cases where the associated connectivity graph has a large three-width, which would imply that the usual deletion algorithm is unfeasible.

* Library with the Python source code of the erasure algorithm, highlighting the marginalization process.

## Authors ✒️

_This library is the product of a doctoral thesis work to solve Boolean satisfiability problems and their variants using the strategies used in graphical models._

* **Efraín Díaz Macías** - [efraindiaz@uteq.edu.ec](efraindiaz@uteq.edu.ec)
* **Serafín Moral Callejón** - [smc@decsai.ugr.es](efraindiaz@uteq.edu.ec)