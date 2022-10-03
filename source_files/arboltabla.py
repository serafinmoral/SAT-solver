# -*- coding: utf-8 -*-
from re import I
import networkx as nx    

import os
import math
from pickle import FALSE
from tablaClausulas  import *
from time import * 


def triangulacond(pot):
    orden = []
    clusters = []
    
    borr = []
   

    grafo = pot.cgrafo()

    ma = 0
    mv = 0
    n = len(grafo.nodes)
    

    i= 0
    total = set()
    cnodo = max(grafo.nodes,key = lambda x : grafo.degree[x])

    while grafo.nodes:

        nnodo = min(grafo.nodes,key = lambda x : grafo.degree[x])
        # print(nnodo)
        orden.append(nnodo)
        veci = set(grafo[nnodo])
        clus = veci.union({nnodo})
        clusters.append(clus)


        # print( i, clus) 
        i += 1
        grafo.remove_node(nnodo)
        for x in veci:
            for y in veci:
                if not x==y:
                    grafo.add_edge(x,y)

    
    clusters.append(set())

    h = list(map(len,clusters))
    mh = max(h)
    sh = sum(h)
    print("maximo: ", mh, "suma: ", sh)
    
    



    
    
    
    return (orden,cnodo,mh)
    

def calculadesdePotencial(pot):

        result = arbol()
        result.asignaval(pot)
        return result
        
def calculaglobal(pot, conf = [], L=30, M=5):

        result = arbol()
        vars = pot.getvars()
        if len(vars)<= L:
            result.value = pot
            return result
        print(conf) 
        (orden,cnodo,maxp) = triangulacond(pot)
        
        cnodo = pot.calculavarcond()

        if maxp <= L:
            result.value = pot
        else:
            pot.combinafacil(orden,M=6)
            l0 = []
            l1 = []
            p0 = pot.reducenv(cnodo, l0, inplace = False)
            p1 = pot.reducenv(-cnodo, l1, inplace = False)
            p0.simplifica(l0,M)
            p1.simplifica(l1,M)

            if p0.contradict and p1.contradict:
                result.anula()
                return result

            if p0.trivial() and p1.trivial():
                return result

            conf.append(-cnodo)
            h0 = calculaglobal(p0,conf,L)
            conf.pop()

            conf.append(cnodo)

            h1 = calculaglobal(p1,conf,L)
            conf.pop()
            
            
            


            if h0.value.contradict and h1.value.contradict:
                result.anula()

                return result

            if h0.trivial() and h1.trivial():
                return result
            
            result.asignavarhijos(cnodo,h0,h1)

            

        return result

def createft(nt):
    ar = arbol()
    
    if len(nt.listavar)==0:
        if ar.contradict:
            ar.anula()
        return ar
    elif len(nt.listavar) == 1:
        if nt.tabla.trivial:
            return ar
        elif nt.tabla.contradict:
            ar.anula()
            return ar
        elif not nt.tabla[0]:
            ar.unit.add(nt.listavar[0])
        elif not nt.tabla[1]:
            ar.unit.add(-nt.listavar[0])
    else:
        ar.value = nt
    return ar



class arbol:
    def __init__(self):
        self.var = 0
        self.value = PotencialTabla()
        self.hijos = [None,None]




    def anula(self):
        self.var = 0
        self.value.anula()
        self.hijos = [None,None]



            



    def void(self):
        self.var = 0
        self.value = PotencialTabla()
        self.unit = set()
        self.hijos = [None,None]

    def trivial(self):
        if self.value.trivial() and self.var == 0:
            return True
        else:
            return False


    def asignavar(self,p):
        self.var = p
        self.value = None

        self.hijos[0] = arbol()
        self.hijos[1] = arbol()

    def asignavarhijos(self,p,h0,h1):
        self.var = p

        self.hijos[0] = h0
        self.hijos[1] = h1


    def asignavarhijosv(self,p,h0,h1,v):
        self.var = p

        self.hijos[0] = h0
        self.hijos[1] = h1
        self.value = v


    def asignaval(self,x):
        self.var = 0
        self.value = x
        self.hijos = [None,None]

    def asignahijo(self,t,i):
        self.hijos[i] = t

    def imprime(self, str = ''):

            print (str +"variable ",self.var)
            if self.var==0:
                self.value.imprime()
            else:
                print(str +"hijo 1")
                self.hijos[0].imprime(str  + '   ')
                print(str +"hijo 2")
                self.hijos[1].imprime(str  + '   ')

    def getvars(self):
        vars = set(self.value.listavar)
        vu = { (abs(x)) for x in self.unit}
        vars.update(vu)
        if not self.var == 0:
            vars.update(self.hijos[0].getvars())
            vars.update(self.hijos[1].getvars())
        return vars



    def lon(self):
        return (len(self.value.unit) + len(self.value.listaclaus))

    def nulo(self):
        if self.var == 0 and not self.unit and self.value.trivial():
            return True
        else:
            return False

    def copia(self):
        res = arbol()

        if self.var == 0:
            res.asignaval(self.value.copia())
            res.value = self.value.copia()

        else:
            v = self.var
            h0 = self.hijos[0].copia()
            h1 = self.hijos[1].copia()
            u = self.value.copia()
            res.asignavarhijosv(v,h0,h1,u)

        return res



    def insertaunit(self,v):
        self.reduce(v,inplace=True)
        self.value.unit.add(v)
    


    def reduce(self,v, inplace = False):
        res = self if inplace else self.copia()
        if v in res.value.unit:
            res.unit.discard(v)
            return res
        if -v in res.value.unit:
            res.anula
            res.contradict = True
            return res
    
        res.value.reduce([v], inplace=True)
        if res.value.contradict:
            res.anula()
            return res 

        
    

        if not res.var == 0:
            if res.var == v:
                res.hijos[1].value.insertaa(res.value, M=30)
                res.value = res.hijos[1].value
                res.var = res.hijos[1].var
                res.hijos = res.hijos[1].hijos
        

            elif -res.var == v:
                res.hijos[0].value.insertaa(res.value, M=30)
                res.value = res.hijos[0].value
                res.var = res.hijos[0].var
                res.hijos = res.hijos[0].hijos
            else:
                res.hijos[0].reduce(v,inplace=True)
                res.hijos[1].reduce(v, inplace=True)
                if res.hijos[0].value.contradict and res.hijos[1].value.contradict:
                    res.anula()

        if not inplace:
            return res

            


    def reduces(self,s, inplace=False):
        res = self if inplace else self.copia()

        for x in s:
            res.reduce(x,inplace=True)

        if not inplace:
            return res



    


                            

        

   

    

    


          

    def insertatabla(self,tab,M):
        
        if self.value.unit:
            tab.reduce(self.value.unit,inplace =True )
        if tab.tabla.ndim==0 and not tab.tabla[0]:
            self.anula()
        
            return

        if tab.tabla.ndim==1:
            if not tab.tabla[0]:
                self.insertaunit(tab.listavar[0])
            elif not tab.tabla[1]:
                self.insertaunit(-tab.listavar[0])
            return

        if self.var == 0:
            self.value.insertatablacombinasi(tab,M)
        else:
            v = self.var
            if v in tab.listavar:
                t0 = tab.reduce([-v],inplace = False)
                t1 = tab.reduce([v],inplace = False)
            else:
                t0 = tab.copia()
                t1 = tab.copia()
            self.hijos[0].insertatabla(t0,M)
            self.hijos[1].insertatabla(t1,M)
        

           

        return
    
    def marginaliza(self,varm, posvar, L):
        res = arbol()
        if self.var == 0:
            tvar = self.value.getvarspv(varm)
            if len(tvar) <= L:
                nvalue = self.value.marginaliza(varm, inplace = False)
                res.asignaval(nvalue)
                return res
            else:
                nvar = max(tvar, key = lambda x: posvar[abs(x)])
                res.value.unit = self.value.unit.copy()
                self.value.unit = set()
                t0 = self.reduce(-nvar, inplace=False)
                t1 = self.reduce(nvar, inplace=False)
                self.value.unit = res.value.unit.copy()

                h0 = t0.marginaliza(varm,posvar,L)
                h1 = t1.marginaliza(varm,posvar,L)
                res.var = nvar
                res.hijos[0] = h0
                res.hijos[1] = h1

        elif not self.var == varm:

            res.asignavarhijos(self.var,self.hijos[0].marginaliza(varm, posvar,L), self.hijos[1].marginaliza(varm, posvar,L))
            
        else:
            res = self.hijos[0].suma(self.hijos[1], posvar, inplace = False)
            res.value.unit.update(self.value.unit)

        return res






                





    def combina(self,t,M,inplace=True,des=True):
        res = self if inplace else self.copia()
        
        newu = res.value.unit
        
        while newu or t.value.unit:
            if newu:
                t.reduces(newu, inplace=True)
            if t.value.unit:
                oldu = res.value.unit.copy()
                res.reduces(t.value.unit, inplace = True)
                newu = res.value.unit-oldu
            if res.value.contradict:
                return res
            res.value.unit.update(t.value.unit)
            t.value.unit = set()

        

        if res.var == 0:
            if t.var == 0:
                for p in t.value.listap:
                    res.value.insertatablacombinasi(p,M)
            else:
                res.hijos = t.hijos
                for x in res.value.listap:
                    t.insertatabla(x,M)
                res.value.listap  = []
                res.var = t.var
                res.hijos = t.hijos
                res.value.contradict = t.value.contradict|res.value.contradict

        else:
            v = res.var
            r0 = t.reduce(v, inplace=False)
            r1 = t.reduce(-v, inplace=False)
            res.hijos[0].combina(r0,M)
            res.hijos[1].combina(r1,M)


        if not inplace:
            return res        
               






    def suma(self,t,M,inplace=True,des=True):
        res = self if inplace else self.copia()
        
        
        if res.var == 0:
            if t.var == 0:
                res.value = res.value.suma(t.value)
                return t
            else:
                t.hijos[0].value.unit.update(t.value.unit)
                t.hijos[1].value.unit.update(t.value.unit)
                t.value.unit = set()
                t.suma(res, inplace=True)
                
                res.var = t.var
                res.value = t.value
                res.contradict = t.contradict
                res.hijos = t.hijos
                
            

        else:
            res.hijos[0].value.unit.update(res.value.unit)
            res.hijos[1].value.unit.update(res.value.unit)
            res.value.unit = set()

            v = res.var
            r0 = t.reduce(v, inplace=False)
            r1 = t.reduce(-v, inplace=False)
            res.hijos[0].suma(r0,M)
            res.hijos[1].suma(r1,M)


        if not inplace:
            return res