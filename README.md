# Deletion Algorithm for the Satisfiability Problem based on Boolean Arrays
_This algorithm is a particular case of the Shafer and Shenoy deletion algorithm or the bucket elimination scheme. This algorithm can solve moderate problems, even in cases where the associated connectivity graph has a large three-width, which would imply that the usual deletion algorithm is unfeasible._

## Running experiments
### Format
_The file that controls the execution of the experiments is "abc.txt", in which a call to the function "xyz" is made, with the following format:_
```
deleting_with_tables(fileCNF[,Q][,Upgrade][,Prior][,Split][,Smessages][,fileResults])
```
