# -*- coding: utf-8 -*-
import networkx as nx    
from source_files.SimpleClauses import *
from source_files.ProblemaTrianFactor import *
from time import *
from source_files.utils import *


def openFileCNF(fileCNF):
    reader=open(fileCNF,"r") 
    line = reader.readline()
    while line[0]=='c':
        line = reader.readline()
    line.strip()
    listaux = line.split()
    print(listaux)
    nvar = int(listaux[2])
    nclaus = int(listaux[3])
    print(nvar)
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
            else:
               print("trivial ", clause)
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
    for p in pot.listap:
        con = set(p.listvar)
        print(con)
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
        print( i, clus) 
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
        print( i, clus)
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
    

def main(prob, Previo=True, Mejora=False):
        prob.inicial.solved = False         
        print("entro en main")
        prob.inicia0()        
        t = varpot()
        t.createfrompot(prob.pinicial)
        prob.rela = t         
        if Mejora:
            prob.rela.mejoralocal()  
        lista = prob.rela.extraelista()
        prob.pinicial.listap = lista
        if Previo:
            prob.previo()
        if prob.contradict:
            print("problema contradictorio")
        else:
            t = varpot(prob.Q, prob.Partir)
            t.createfrompot(prob.pinicial)
            prob.rela = t
            prob.borradin()
        print("salgo de borrado")
        if not prob.contradict:
            prob.sol = prob.findsol()
            prob.compruebaSol()
            return True
        else:
            print(" problema contradictorio ")
            return False


def treeWidth(prob):
    (order,clusters,borr,posvar,child,parent) = triangulap(prob.pinicial)
    sizes = map(len,clusters)
    return(max(sizes))


def computetreewidhts(archivolee):
    archivogenera = "treewidths" + archivolee
    reader=open(archivolee,"r")
    writer=open(archivogenera,"w")
    writer.write("Problema;TreeWidth\n")
    for linea in reader:
            linea = linea.rstrip()
            if len(linea)>0:
                cadena = ""
                nombre=linea.strip()
                print(nombre)     
                (info, nvar, nclaus) = openFileCNF(nombre)
                cadena= nombre 
                prob = problemaTrianFactor(info)
                prob.inicia0()                  
                tw = treeWidth(prob)
                cadena = cadena + ";" + str(tw) + "\n"
                writer.write(cadena)
    writer.close()
    reader.close()


def deleting_with_tables(archivolee, Q=[5,10,15,20,25,30],Mejora=[False], Previo=[True], Partir=[True], archivogenera="salida.csv"):
    try:
        reader=open(archivolee,"r")
        writer=open(archivogenera,"w")
        writer.write("Problema;Variable;Claúsulas;Q;MejoraLocal;Previo;PartirVars;TLectura;TBúsqueda;TTotal;SAT\n")
        ttotal = 0
        for linea in reader:
            linea = linea.rstrip()
            if len(linea)>0:
                cadena = ""
                nombre=linea.strip()
                print(nombre)     
                t1 = time()
                (info, nvar, nclaus) = openFileCNF(nombre)
                t2= time()
                for Qev in Q:
                    for Mej in Mejora:
                        for Pre in Previo:
                            for Part in Partir:
                                try:
                                    t3 = time()
                                    cadena= nombre + ";" + str(nvar) + ";" + str(nclaus) + ";" + str(Qev) + ";" + str(Mej) + ";" + str(Pre) + ";" + str(Part) + ";"
                                    prob = problemaTrianFactor(info,Qin=Qev)
                                    t4 = time()
                                    bolSAT = main(prob, Pre,Mej)
                                    t5 = time()
                                    print("tiempo lectura ",t2-t1)
                                    print("tiempo busqueda ",t5-t4)
                                    print("tiempo TOTAL ",t5-t3+t2-t1)
                                    cadena =  cadena + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + (";SAT" if bolSAT else ";UNSAT") + "\n"
                                except ValueError:
                                    print("ERROR")
                                    t5 = time()
                                    cadena = cadena + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + "ERROR" + "\n"
                                except MemoryError:
                                    print("ERROR de Memoria")
                                    t5 = time()
                                    cadena = cadena + str(t2-t1) + ";" + str(t5-t4) + ";" + str(t5-t3+t2-t1) + "Memory Error" + "\n"
                                writer.write(cadena)
        writer.close()
        reader.close()    
    except ValueError:
        print("Error")
# computetreewidhts("ListaCNF_Experimento.txt")
# deleting_with_tables("../data_In_Out/entrada",[5,10,15,20,25],[False],[False],[False,True],"../data_In_Out/prueba05.txt")