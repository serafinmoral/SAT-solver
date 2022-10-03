# -*- coding: utf-8 -*-
import networkx as nx    
from SimpleClausulas import *
from  ProblemaTrianFactor import *
from time import *
from utils import *
from arboltablaglobal import *


def openFileCNF(Archivo):
    reader=open(Archivo,"r") 
    cadena = reader.readline()
    while cadena[0]=='c':
        cadena = reader.readline()
    cadena.strip()
    listaaux = cadena.split()
    print(listaaux)
    nvar = int(listaaux[2])
    nclaus = int(listaaux[3])
    print(nvar)
    while cadena[0]=='c':
        cadena = reader.readline()
    infor = simpleClausulas()
    for cadena in reader:
        if (cadena[0]!='c'):
            cadena.strip()
            listaux=cadena.split()
            listaux.pop()
            listaux = map(int,listaux)
            clausula= set(listaux)
            nc = set( map(lambda t: -t, clausula))
            infor.listaclausOriginal.append(clausula.copy())
            if not nc.intersection(clausula):
                infor.insertar(clausula, test = False)
            else:
               print("trivial ", clausula)
            if infor.contradict:
                print("contradiccion leyendo")    
    return infor, nvar, nclaus

    
def triangulap(pot):
    orden = []
    clusters = []
    borr = []
    child = []
    posvar = dict()
    total = set()
    dvar = dict()
    for p in pot.listap:
        con = set(p.listavar)
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
        nnodo = abs(units.pop())
        orden.append(nnodo)
        clus = {nnodo}
        clusters.append(clus)
        posvar[nnodo] = i
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
        nnodo = min(value, key = value.get )
        orden.append(nnodo)
        clus = set()
        for x in dvar[nnodo]:
            clus.update(x)
        clusters.append(clus)
        posvar[nnodo] = i
        print( i, clus)
        i+=1
        clustersin = clus-{nnodo}
        for y in clustersin:
            dvar[y] = list(filter( lambda h: nnodo not in h  ,dvar[y] ))
            dvar[y].append(clustersin)
            totvar[y] = set()
            for h in dvar[y]:
                totvar[y].update(h)
            value[y] = 2**(len(totvar[y])-1) - sum([2**len(z) for z in dvar[y]])
        del value[nnodo]
        del dvar[nnodo]
        del totvar[nnodo]
        total.discard(nnodo)
    clusters.append(set())
    for i in range(n):
            con = clusters[i]
            cons = con - {orden[i]}
            if not cons:
                parent[i] = n
                child[n].add(i)
            else:
                pos = min(map(lambda h: posvar[h], cons))
                parent[i] = pos
                child[pos].add(i)
    return (orden,clusters,borr,posvar,child,parent) 
    

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
    (orden,clusters,borr,posvar,child,parent) = triangulap(prob.pinicial)
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


def borradocontablas(archivolee, Q=[5,10,15,20,25,30],Mejora=[False], Previo=[True], Partir=[True], archivogenera="salida.csv"):
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
borradocontablas("entrada",[5,10,15,20,25],[False],[False],[False,True],"prueba05.txt")