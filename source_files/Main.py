# -*- coding: utf-8 -*-
import networkx as nx    
from ClausesSimple import *
from source_files.ProblemTrianFactor import *
from time import *
from source_files.utils import *
from source_files.TablesVar import *

def openFileCNF(fileCNF):
    reader=open(fileCNF,"r") 
    line = reader.readline()
    while line[0]=='c':
        line = reader.readline()
    line.strip()
    listaux = line.split()
    nvar = int(listaux[2])
    nclaus = int(listaux[3])
    while line[0]=='c':
        line = reader.readline()
    infor = simpleClauses()
    for line in reader:
        if (line[0]!='c'):
            line.strip()
            listaux=line.split()
            listaux.pop()
            listaux = map(int,listaux)
            clause= set(listaux)
            nc = set( map(lambda t: -t, clause))
            infor.listclausOriginal.append(clause.copy())
            if not nc.intersection(clause):
                infor.insert(clause, test = False)
            # else:
            #    print("trivial ", clause)
            if infor.contradict:
                print("reading contradiction")    
    return infor, nvar, nclaus

    
def triangulap(pot):
    order = []
    clusters = []
    borr = []
    child = []
    posvar = dict()
    total = set()
    dvar = dict()
    for p in pot.listp:
        con = set(p.listvar)
        total.update(con)
        for v in con:
            if v in dvar:
                dvar[v].append(con)
            else:
                dvar[v] = [con]
    n = len(total.union(pot.unit))
    parent = [-1]*(n+1)
    for i in range(n+1):
        child.append(set())
    i= 0
    units = pot.unit.copy()
    while units:
        nnode = abs(units.pop())
        order.append(nnode)
        clus = {nnode}
        clusters.append(clus)
        posvar[nnode] = i
        i+=1
    value = dict()
    totvar = dict()
    for x in dvar:
        totvar[x] = set()
        for h in dvar[x]:
            totvar[x].update(h)
        value[x] = 2**(len(totvar[x])-1) - sum([2**len(y) for y in dvar[x]])  
    i = 0
    while total:
        nnode = min(value, key = value.get )
        order.append(nnode)
        clus = set()
        for x in dvar[nnode]:
            clus.update(x)
        clusters.append(clus)
        posvar[nnode] = i
        i+=1
        clustersin = clus-{nnode}
        for y in clustersin:
            dvar[y] = list(filter( lambda h: nnode not in h  ,dvar[y] ))
            dvar[y].append(clustersin)
            totvar[y] = set()
            for h in dvar[y]:
                totvar[y].update(h)
            value[y] = 2**(len(totvar[y])-1) - sum([2**len(z) for z in dvar[y]])
        del value[nnode]
        del dvar[nnode]
        del totvar[nnode]
        total.discard(nnode)
    clusters.append(set())
    for i in range(n):
            con = clusters[i]
            cons = con - {order[i]}
            if not cons:
                parent[i] = n
                child[n].add(i)
            else:
                pos = min(map(lambda h: posvar[h], cons))
                parent[i] = pos
                child[pos].add(i)
    return (order,clusters,borr,posvar,child,parent) 
    

def main(prob, Prior=True, Upgrade=False, see_messages=False):
        prob.initial.solved = False         
        prob.start0()        
        print(see_messages)
        t = varpot(see_mess=see_messages)
        t.createfrompot(prob.pinitial)
        prob.rela = t         
        if Upgrade:
            prob.rela.localUpgrade()  
        list_ = prob.rela.extractlist()
        prob.pinitial.listp = list_
        if Prior:
            prob.prior()
        if prob.contradict:
            print("problema contradictorio")
        else:
            t = varpot(prob.Q, prob.Split, see_mess=see_messages)
            t.createfrompot(prob.pinitial)
            prob.rela = t
            prob.deletein()
        if not prob.contradict:
            prob.sol = prob.findsol()
            prob.checkSol()
            return True
        else:
            print(" problema contradictorio ")
            return False


def treeWidth(prob):
    (order,clusters,borr,posvar,child,parent) = triangulap(prob.pinitial)
    sizes = map(len,clusters)
    return(max(sizes))


def deleting_with_tables(fileCNF, Q=[5,10,15,20,25,30],Upgrade=[False], Prior=[True], Split=[True], Smessages=False,fileResults="salida.csv"):
    try:
        reader=open(fileCNF,"r")
        writer=open(fileResults,"w")
        writer.write("Problem;Vars;Clauses;TreeWidth;Q;LocalUpgrade;Prior;splitVars;TRead;TSearch;TTotal;SAT\n")
        ttotal = 0
        for line in reader:
            line = line.rstrip()
            if len(line)>0:
                string = ""
                name=line.strip()   
                t1 = time()
                (info, nvar, nclaus) = openFileCNF(name)
                print("File:" + name + "; Vars:" + str(nvar) + "; Clauses:" + str(nclaus))
                t2= time()
                probtw = problemTrianFactor(info)
                probtw.start0()                  
                tw = treeWidth(probtw)
                for Qev in Q:
                    for Mej in Upgrade:
                        for Pre in Prior:
                            for Part in Split:
                                try:
                                    t3 = time()
                                    print("\tQ:" + str(Qev) + "; Upgrade:" + str(Mej) + "; Prior:" + str(Pre) + "; splitVars:" +str(Part))
                                    string= name + ";" + str(nvar) + ";" + str(nclaus) + ";" + str(tw) + ";" + str(Qev) + ";" + str(Mej) + ";" + str(Pre) + ";" + str(Part) + ";"
                                    prob = problemTrianFactor(info,Qin=Qev,see_mess=Smessages)
                                    t4 = time()
                                    bolSAT = main(prob, Pre,Mej,Smessages)
                                    t5 = time()
                                    if (Smessages): print("\tRead time: ",t2-t1)
                                    if (Smessages):print("\tSearch time: ",t5-t4)
                                    print("\tTotal time: " + str(t5-t3+t2-t1) + "\n")
                                    string =  string + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + (";SAT" if bolSAT else ";UNSAT") + "\n"
                                except ValueError:
                                    print("ERROR")
                                    t5 = time()
                                    string = string + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + "ERROR" + "\n"
                                except MemoryError:
                                    print("ERROR de Memoria")
                                    t5 = time()
                                    string = string + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + "Memory Error" + "\n"
                                writer.write(string)
        writer.close()
        reader.close()    
    except ValueError:
        print("Error")