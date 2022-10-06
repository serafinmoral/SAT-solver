# -*- coding: utf-8 -*-
from operator import index
import time
from numpy import False_
from source_files.TablesVar import *
from source_files.ClausesSimple import *
from source_files.ClausesTable import *
from source_files.Utils import *
import random as ra


class problemTrianFactor:
    def __init__(self,info=None,M=30, Qin=20, SplitIn=True):
         self.M = M
         self.initial = info
         self.pinitial = PotencialTabla()
         self.rela = varpot(Qin,SplitIn)
         self.order = []
         self.clusters = []
         self.lqueue  = []
         self.lfloat = []
         self.posvar = dict()
         self.sol = set()
         self.borr = []
         self.child = []
         self.parent = []
         if info:
            self.contradict = info.contradict
         self.evid = set()
         self.toriginalfl = []
         self.Q=Qin
         self.Split=SplitIn


    def inicia0(self):
            self.pinitial.computefromsimple(self.initial)


    def prior(self, Q = 2, pre = False):
        if pre:
            return
        for x in self.pinitial.unit:
            # print("unitaria ", x)
            self.order.append(abs(x))
            t = potdev(x)
            self.lqueue.append(t)
        self.pinitial.unit = set()
        vars = self.pinitial.getvars()
        total = 0
        for K in range(2,Q+1):
            varb = []
            potb = []
        
            total = 1
            while total >0:
                total = 0
                i=0
                while i < len(self.pinitial.listap):
                    p = self.pinitial.listap[i]
                    if len(p.listvar) == K:
                        for v in p.listvar:
                                deter = p.checkdetermi(v)
                                if deter:
                                    varb.append(v)
                                    potb.append(p)
                                    self.order.append(v)
                                    self.lqueue.append(p)
                                    # print("variable ", v, " determinada ", p.listvar)
                                    # print(p.tabla)
                                    self.borrad(v,p)
                                    total += 1
                                    break
                    i+= 1
                print(total)
        if self.pinitial.contradict:
            self.contradict = True
        return (varb,potb)


    def borrad(self,v,p):
        bor = []
        tota = set()
        for i in range(len(self.pinitial.listap)):
            q = self.pinitial.listap[i]
            if v in q.listvar:
                # print("var pot", q.listvar)
                if q == p:
                    h = q.borra([v],inplace = False)
                    if h.trivial():
                        bor.append(h)
                else:
                    h = q.combina(p,inplace = False, des= False)
                    h.borra([v], inplace = True)
                    if h.trivial():
                        bor.append(h)
                        # print("trivial 2")
                        # sleep(1)
                    if h.contradict():
                        self.annul()
                        print("contradictorio")
                self.pinitial.listap[i] = h
        for q in bor:
            self.pinitial.listap.remove(q)


    def annul(self):
        for i in range(len(self.order)):
            self.lqueue[i].annul()
        self.contradict = True

           
    def insertaunit(self,x):
        xp = abs(x)
        nu = set()
        for pos in range(len(self.clusters)):
            if xp in self.clusters[pos]:
                pot = self.lqueue[pos]  
                pot.insertaunit(x)
    

    def insertacolapot(self,p):
            vcl = p.listvar
            if vcl:
                pos = min(map(lambda h: self.posvar[h], vcl))
            else:
                pos = len(self.order)
            pot = self.lqueue[pos]
            pot.listap.append(p)


    def borradin(self, pre = False):
        if self.rela.contradict:
                print("contradictorio")
                self.annul()
                return
        if pre:
            (e,order,nuevas,antiguas)= self.rela.marginalizaset(set(self.order), Q=self.Q,pre = True, order = self.order.copy()) #EDM
        else:
            (e,order,nuevas,antiguas)= self.rela.marginalizaset(self.pinitial.getvars(), Q=self.Q,pre = False) #EDM
        self.contradict =  self.rela.contradict
        if not pre:
            self.order = self.order +  order
        i=0
        if not self.contradict:
            for x in antiguas:
                # print(i, x) #EDM
                i+=1
                y = nodeTable([])
                for t in x:
                    y.combina(t,inplace= True)
                self.lqueue.append(y)
        return e                
            
    
    def borra(self):
        print(len(self.order))
        for i in range(len(self.order)):
            if self.initial.contradict:
                break
            var = self.order[i]
            print("i= ", i, "var = ", self.order[i], "cluster ", self.clusters[i])
            pot = self.lqueue[i]
            if pot.contradict:
                self.initial.contradict=True #ojo
                print("contradiccion antes de normalizar ")
                break
            potn = pot.marginaliza(var)
            print("fin marginaliza")
            pos = self.parent[i]
            poti = self.lqueue[pos]
            poti.inserta(potn)
            print("fin de combina")


    def inserta(self,pot):
        for x in pot.unit:
                self.insertaunit(x)
        for p in pot.listap:
                self.insertacolapot(p)
       

    def findsol(self):
        sol = set()
        for i in reversed(range(len(self.order))):
            print(i)
            tabla = self.lqueue[i]
            var = self.order[i]
            print(var) #EDM
            # print(tabla.listvar,tabla.tabla)
            t = tabla.reduce(list(sol))
            # print(t.listvar,t.tabla)
            if len(t.listvar) > 1:
                for x in t.listvar:
                    if not x == var:
                        sol.add(x) 
                t = t.reduce(list(sol))
            if t.contradict():
                print("contradiccion buscando solucion" , sol )
                break
            elif t.trivial():
                sol.add(var)
                # print("elijo ", var) #EDM
            elif t.tabla[0]:
                sol.add(-var)
                # print(-var) #EDM
            else:
               sol.add(var)
               # print(var)  #EDM
        self.sol = sol
        return sol


    def compruebaSol(self):
        aux = 0
        print("entro en comprueba solucion")
        for clau in self.initial.listclausOriginal:
            print(clau)
            aux = aux + 1
            if len(clau.intersection(self.sol))==0:
                print("Error en cláusula: ", clau)
                return False
        print("Cumple solución satisfactoriamente, Número de cláusulas validadas: ", aux)
        return True


    def insertacola(self,t,i,conf=set()):
        if not t.value.nulo():
                if t.value.contradict and not conf:
                    self.contradictproblem()
                else:
                    j = i+1
                    vars = set(map(lambda x: abs(x),conf.union(t.value.listvar)) )
                    # j = min(map(lambda h: self.posvar[h],vars))
                    while not vars <= self.clusters[j]:
                        j += 1
                        if j == len(self.clusters):
                            print(vars)
                    pot = self.lqueue[j]
                    # if pot.checkrep():
                    #     print("problema de repecion antes de insertar")
                    #     time.sleep(30)
                    if pot.value.contradict:
                        print("contradiccion antes")
                    pot.insertasimple(t.value,self.N,conf) 
                    # if pot.checkrep():
                    #     print("problema de repecion despyes de insertar",conf)
                    #     time.sleep(30)
                    pot.normaliza(self.N) 
        if not t.var ==0:
            v = t.var
            conf.add(v)
            self.insertacola(t.hijos[0],i,conf)
            conf.discard(v)
            conf.add(-v)
            self.insertacola(t.hijos[1],i,conf)
            conf.discard(-v)


    def contradictproblem(self):
        print("contradiccion")
        self.initial.solved = True
        self.initial.contradict = True


    def annul(self):
        self.initial.solved = True
        self.initial.contradict = True
        for pot in self.lpot:
            pot.annul()
        for por in self.lqueue:
            pot.annul()