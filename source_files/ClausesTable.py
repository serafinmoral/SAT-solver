# -*- coding: utf-8 -*-
from xmlrpc.client import boolean
import source_files.Utils as u

import networkx as nx
import numpy as np
from source_files.ClausesSimple import * 
from time import *
import math
import random

class nodeTable:
    def __init__(self, lista):
        
        self.listvar = lista
        n = len(lista)
        t = (2,)*n
        self.tabla = np.ones( dtype = boolean, shape = t)
    
    def copia(self):
        result = nodeTable(self.listvar.copy())
        result.tabla = self.tabla.copy()
        return result

    def descomponev(self,v):
        res = []
        h = self.borra([v], inplace = False)

        

        t = self.minimiza(h, pro = {v})

        if len(t.listvar) ==len(self.listvar):
            res.append(self)
        else:
            res.append(t)
            res.append(h)


        return res



    def entropia(self,v):
            (x0,x1) = self.cuenta(v)
            if x0==0 or x1==0:
                return 0.0
            else:
                z0 = x0/(x0+x1)
                z1  = x1/(x0+x1)
                x = (-z0*math.log(z0) - z1*math.log(z1))
            return x

    def minentropia(self):
            
            return min(self.listvar,key = lambda v: self.entropia(v))


    def neg(self,inplace=False):
        
        nuevatabla = np.logical_not(self.tabla)
        if inplace:
            self.tabla = nuevatabla
            res = self
        else:
            res = nodeTable(self.listvar.copy())
            res.tabla = nuevatabla

        return res


    def equivalente(self,p):
       
       
        if self.suma(p.neg()).trivial() and p.suma(self.neg()).trivial():
            return True
        else:
            return False


    def implicadopor(self,p):
        if self.suma(p.neg()).trivial():
            return True
        else:
            return False

    def minimiza(self, con  , pro = set()):
        rest =  set(self.listvar)-pro
        if not rest:
            return self
        else:
            v = rest.pop()
            h = self.borra([v], inplace=False)
            if self.implicadopor(h.combina(con)):
                return h.minimiza(con,pro)
            else:
                pro.add(v)
                return self.minimiza(con,pro)





    def combina(self,op,inplace = False, des= False):
        result = self if inplace else self.copia()
        if isinstance(op,boolean):
            if op:
                return result
            else:
                result.tabla = result.tabla & op
                return result

        if not des:
            op = op.copia()
        extra = set(op.listvar) - set(result.listvar)
        if extra:
                slice_ = [slice(None)] * len(result.listvar)
                slice_.extend([np.newaxis] * len(extra))

                result.tabla = result.tabla[tuple(slice_)]

                result.listvar.extend(extra)

        extra = set(result.listvar) - set(op.listvar)
        if extra:
                slice_ = [slice(None)] * len(op.listvar)
                slice_.extend([np.newaxis] * len(extra))

                op.tabla = op.tabla[tuple(slice_)]

                op.listvar.extend(extra)
                # No need to modify cardinality as we don't need it.

            # rearranging the axes of phi1 to match phi
        for axis in range(result.tabla.ndim):
            exchange_index = op.listvar.index(result.listvar[axis])
            op.listvar[axis], op.listvar[exchange_index] = (
                op.listvar[exchange_index],
                op.listvar[axis],
            )
            op.tabla = op.tabla.swapaxes(axis, exchange_index)

        result.tabla = result.tabla & op.tabla    
        if not inplace:
            return result

    def checkdetermi(self,v):
        if v not in self.listvar:
            return False
        t0 = self.reduce([v])
        t1 = self.reduce([-v])

        t = t0.combina(t1, inplace=False)

        if t.contradict():
            return True
        else:
            return False

    def contenida(self,listanodos):
        return u.contenida(self,listanodos) 

    def minimizadep(self,v, seg = set()):
        vars = set(self.listvar) - seg
        vars.remove(v)

        if not vars:
            return self
        nv = vars.pop()

        np = self.borra([nv])



        if not np.trivial() and np.checkdetermi(v):
            return np.minimizadep(v, seg.copy())
        else:
            seg.add(nv)
            return self.minimizadep(v,seg)


    def extraesimple(self):
        
        vars = set(self.listvar)
        if not vars:
            return nodeTable([])
        v = vars.pop()

        pv = self.borra(list(vars))
        if not pv.trivial():
            return pv
        else:
            pr = self.borra([v])

            if not pr.trivial():
                sr = pr.extraesimple()
                if not sr.trivial():
                    return sr
                else:
                    h2 = self.extrasimple2(v,vars)
                    return h2
            else:
                return nodeTable([])

    def upgrade(self,q):
            vars = list(set(q.listvar) - set(self.listvar))
            res = self.combina(q.borra(vars))
            return res

    def extrasimple2(self,v1,vars):
        if not vars:
            return nodeTable([])
        v2 = vars.pop()

        pv12 = self.borra(list(vars))

        if pv12.checkdetermi(v2) or pv12.checkdetermi(v1):
            return pv12
        else:
            pr = self.borra([v2])

            return pr.extrasimple2(v1,vars)



    


    def suma(self,op,inplace = False, des= False):
        result = self if inplace else self.copia()
        if isinstance(op,boolean):
            if op:
                return result
            else:
                result.tabla = result.tabla | op
                return result

        if not des:
            op = op.copia()
        extra = set(op.listvar) - set(result.listvar)
        if extra:
                slice_ = [slice(None)] * len(result.listvar)
                slice_.extend([np.newaxis] * len(extra))

                result.tabla = result.tabla[tuple(slice_)]

                result.listvar.extend(extra)

        extra = set(result.listvar) - set(op.listvar)
        if extra:
                slice_ = [slice(None)] * len(op.listvar)
                slice_.extend([np.newaxis] * len(extra))

                op.tabla = op.tabla[tuple(slice_)]

                op.listvar.extend(extra)
                # No need to modify cardinality as we don't need it.

            # rearranging the axes of phi1 to match phi
        for axis in range(result.tabla.ndim):
            exchange_index = op.listvar.index(result.listvar[axis])
            op.listvar[axis], op.listvar[exchange_index] = (
                op.listvar[exchange_index],
                op.listvar[axis],
            )
            op.tabla = op.tabla.swapaxes(axis, exchange_index)

        result.tabla = result.tabla | op.tabla    
        if not inplace:
            return result


    def reduce(self, val, inplace=False):
        
        values = filter(lambda x: abs(x) in  self.listvar, val)
        phi = self if inplace else self.copia()

        values = [
                (abs(var), 0 if var<0 else 1) for var in values
            ]

        var_index_to_del = []
        slice_ = [slice(None)] * len(self.listvar)
        for var, state in values:
            var_index = phi.listvar.index(var)
            slice_[var_index] = state
            var_index_to_del.append(var_index)

        var_index_to_keep = sorted(
            set(range(len(phi.listvar))) - set(var_index_to_del)
        )
        # set difference is not guaranteed to maintain ordering
        phi.listvar = [phi.listvar[index] for index in var_index_to_keep]
        

        phi.tabla= phi.tabla[tuple(slice_)]

        
        return phi

    
    def introducelista(self,lista):
        for cl in lista:
            self.introduceclau(cl)
    
    def introduceclau(self, values):
        for var in values:
            if abs(var) not in self.listvar:
                raise ValueError(f"La variable: {abs(var)} no está en el potencial")


        values = [
                (abs(var), 1 if var<0 else 0) for var in values
            ]

        slice_ = [slice(None)] * len(self.listvar)
        for var, state in values:
            var_index = self.listvar.index(var)
            slice_[var_index] = state

        
        # set difference is not guaranteed to maintain ordering
        

        self.tabla[tuple(slice_)] = False

        

    

    def borra(self,variables, inplace=False):

        phi = self if inplace else self.copia()   
        for var in variables:
            if var not in phi.listvar:
                raise ValueError(f"{var} no está en la lista.")

        var_indexes = [phi.listvar.index(var) for var in variables]

        index_to_keep = sorted(set(range(len(self.listvar))) - set(var_indexes))
        phi.listvar = [phi.listvar[index] for index in index_to_keep]

        phi.tabla = np.amax(phi.tabla, axis=tuple(var_indexes))

        if not inplace:
            return phi

    def contradict(self):
        return not np.amax(self.tabla)

    def cuenta(self,v):
        t0 = self.reduce([v],inplace=False)
        t1 = self.reduce([-v],inplace=False)
        x0 = np.sum(t0.tabla)
        x1 = np.sum(t1.tabla)
        return (x0,x1)

    def annul(self):
        self.listvar = []
        self.tabla = False

    def trivial(self):
        return  np.amin(self.tabla)

    def calculaunit(self):
        result = set()
        n = len(self.listvar)
        total = set(range(n))
        for i in range(n):
            
            borra = tuple(total-{i})
            marg = np.amax(self.tabla,axis = borra)
            
            if not marg[0]:
                if not marg[1]:
                    result.add(0)
                    return result
                else:
                    result.add(self.listvar[i])
            elif  not marg[1]:    
                    result.add(-self.listvar[i])
        return result
          
    



class PotencialTabla:
        def __init__(self):
            self.unit = set()
            self.listap = []
            self.contradict = False

        def annul(self):
            self.unit = set()
            self.listap = []
            self.contradict = True
        
        def trivial(self):
            if not self.unit and not self.listap:
                return True
            else:
                return False

        def imprime(self):
            print("unit: ", self.unit)
            print("tablas ")
            print("contradiccion ", self.contradict)
            for x in self.listap:
                print("vars" , x.listvar)
                print(x.tabla)

        def cgrafo(self):
            grafo = nx.Graph()
        
            vars = set(map(abs,self.unit))
            for p in self.listap:
                vars.update(p.listvar)
        
        
            for p in self.listap:
                for i in range(len(p.listvar)):
                    for j in range(i+1,len(p.listvar)):
                           grafo.add_edge(p.listvar[i],p.listvar[j])    
            return grafo 

        

        def copia(self):
            res = PotencialTabla()
            res.unit = self.unit.copy()

            for p in self.listap:
                print(p)
                res.listap.append(p.copia())
            return res

        def getvars(self):
            res = set()
            res.update(set(map(abs,self.unit)))



            for p in self.listap:
                res.update(set(p.listvar))
            return res

        def getvarsp(self):
            res = set()
    
            for p in self.listap:
                res.update(set(p.listvar))
            return res

        def getvarspv(self,v):
            res = set()
    
            for p in self.listap:
                if v in p.listvar:
                    res.update(set(p.listvar))
            return res

        def computefromsimple(self,simple):
            self.unit = simple.unit.copy()
            (sets,clusters) = u.createclusters(simple.listclaus)
            for i in range(len(sets)):
                x = nodeTable(list(sets[i]))
                x.introducelista(clusters[i])
                self.listap.append(x)

        def inserta(self,p):
            self.listap.append(p)

        def calculavarcond(self,m=0):
            cont = dict()

            vars = self.getvars()
            for x in vars:
                cont[x] = 0.0
            
            for p in self.listap:
                if m==0:
                    h = np.sum(p.tabla)

                    for x in p.listvar:
                        if h == 0:
                            
                            cont[x] += 100.0
                        else:
                            cont[x] += 1/h
                else:
                    for x in p.listvar:
                        
                            
                            cont[x]+=1

            return max(cont, key = cont.get)



        def insertap(self,p):
            for x in p.unit:
                self.insertaunit(x)
            for q in p.listap:
                if self.listap:
                    self.listap[0].combina(q, inplace=True, des= True)
                else: 
                    self.listap = [q]
                    

        def insertatablacombinasi(self,p, M):
        
            insertado = False
            p.reduce(self.unit,inplace=True)
            for q in self.listap:
                sql = set(q.listvar)
                spl = set(p.listvar)
                tot = sql.union(spl)

                if len(tot)<= M:
                    q.combina(p,inplace= True)
                    insertado = True
                    break
             
            if not insertado:
                self.listap.append(p)

        def prior(self,Q=2):
            total = 0
            for K in range(2,Q+1):
                varb = []
                potb = []
            
                total = 1
                while total >0:
                    total = 0
                    i=0
                    while i < len(self.listap):
                        p = self.listap[i]
                        if len(p.listvar) == K:
                            for v in p.listvar:
                                    deter = p.checkdetermi(v)
                                    if deter:
                                        varb.append(v)
                                        potb.append(p)
                                        # print("variable ", v, " determinada ", p.listvar)
                                        # print(p.tabla)
                                        self.borrad(v,p)
                                        total += 1
                                        break
                        i+= 1
                    print(total)             

        def borrad(self,v,p, l= []):
            bor = []
            tota = set()
            for i in range(len(self.listap)):
                q = self.listap[i]
                if v in q.listvar:
                    # print("var pot", q.listvar)
                    if q == p:
                        h = q.borra([v],inplace = False)
                        if h.trivial():
                            bor.append(h)
                        else:
                            l.append(h)
                        
                    else:
                        h = q.combina(p,inplace = False, des= False)
                        h.borra([v], inplace = True)
                        if h.trivial():
                            bor.append(h)
                            print("trivial 2")
                    
                    self.listap[i] = h
                    
            for q in bor:
                self.listap.remove(q)

        def borrad2(self,v2,v1,p, l):
            bor = []
            for i in range(len(self.listap)):
                q = self.listap[i]
                if v2 in q.listvar:
                    # print("var pot", q.listvar)
                    if q == p:
                        h = q.borra([v2],inplace = False)
                        if h.trivial():
                            bor.append(h)
                        else:
                            l.append(h)
                        
                    else:
                        h = q.combina(p,inplace = False, des= False)
                        if v1 in p.listvar:
                            an = True
                        else:
                            an = False
                        h.borra([v2], inplace = True)
                        if h.trivial():
                            bor.append(h)
                            print("trivial 2")
                        elif an:
                            l.append(h)
                    
                    self.listap[i] = h
                    
            for q in bor:
                self.listap.remove(q)

                    
        def localUpgrade(self,M=25,Q=10):
            for p in self.listap:
                if len(p.listvar)<=Q:
                    old = np.sum(p.tabla)
                    vars = set(p.listvar)
                    tvars = set(p.listvar)
                    lista = []
                    for q in self.listap:
                        if not q==p:
                            qv = set(q.listvar)
                            if set(qv.intersection(vars)):
                                if len(tvars.union(qv))<=M:
                                    tvars.update(qv)
                                    lista.append(q)
                    vars = tvars.copy()
                    for q in self.listap:
                        if not q==p:
                            qv = set(q.listvar)
                            if set(qv.intersection(vars)):
                                if len(tvars.union(qv))<=M:
                                    tvars.update(qv)
                                    lista.append(q)
                    r = nodeTable([])
                    for q in lista:
                        r.combina(q,inplace=True)
                    r.borra(list(tvars-set(p.listvar)),inplace=True)
                    p.combina(r,inplace=True)
                    ns = np.sum(p.tabla)

                    if (ns < old):
                        print("mejopra", ns, old,len(p.listvar))

                    



        


        def insertaa(self,p,M):
            
            for x in p.unit:
                self.insertaunit(x)
            for q in p.listap:
                self.listap.append(q)

            
        


        def insertaunit(self,x):
            print("INSERTANDO UNIDAD")
            if -x in self.unit:
                self.annul()
                return set()
            self.reduce({x}, inplace=True)
            if not self.contradict:
                self.unit.add(x)
            
        def cuenta(self,v):
            if v in self.unit:
                return (0,1)
            elif -v in self.unit:
                return (1,0)
            else:
                x0 = 1.0
                x1 = 1.0
                for p in self.listap:
                    if v in p.listvar:
                        (y0,y1) = p.cuenta(v)
                        x0 *= y0
                        x1 *= y1
            return (x0,x1)

        def logcuenta(self,v):
            if v in self.unit:
                return (0,1)
            elif -v in self.unit:
                return (1,0)
            else:
                x0 = 0.0
                x1 = 0.0
                for p in self.listap:
                    if v in p.listvar:
                        (y0,y1) = p.cuenta(v)
                        if y0 == 0:
                            return (0,1)
                        elif y1 == 0:
                            return (1,0)
                        else:
                            x0 += math.log(y0)
                            x1 += math.log(y1)
            return (x0,x1)

        def entropia(self,v):
            (x0,x1) = self.cuenta(v)
            if x0==0 or x1==0:
                return 0.0
            else:
                z0 = x0/(x0+x1)
                z1  = x1/(x0+x1)
                x = (-z0*math.log(z0) - z1*math.log(z1))
            return x

        def minentropia(self):
            vars = self.getvars()
            return min(vars,key = lambda v: self.entropia(v))

        def prop(self):
            y = np.sum(self.tabla)
            return y/2**(len(self.listvar))

            


        def propagaunits(self,su):
            negu = set(map(lambda x: -x, su))
            if negu.intersection(self.unit):
                self.annul()
                return 
            else:
                self.unit.update(su)
            
            vars = set(map(abs,su))
            nu = set()
            borr = []
            for p in self.listap:
                inter = vars.intersection(set(p.listvar))
                if inter:
                        nsu = set(filter(lambda x: abs(x) in inter, su))
                        p.reduce(nsu , inplace = True)
                        if p.contradict():
                            self.annul()
                            return
                        if p.trivial():
                            borr.append(p)
                        else:
                            nu.update(p.calculaunit())
            for p in borr:
                self.listap.remove(p)
            if nu:
                self.propagaunits(nu)
                        

        def reduceycombina(self, val, inplace = False):
            res = PotencialTabla()
            for x in self.unit:
                if -x in val:
                    res.contradict = True
                    return res
                elif not x in val:
                    res.unit.add(x)
            t = nodeTable([])
            for p in self.listap:
                q = p.reduce(val,inplace = False)
                t.combina(q, inplace=True)
            res.listap.append(t)
            return res

        def reduce(self, val, inplace = False):
            res = self if inplace else self.copia()   
            varv = set(map(abs,val))
            for x in self.unit:
                if -x in val:
                    res.contradict = True
                    return res
            res.unit.difference_update(set(val))
            bor = []
            un = set()
            for p in res.listap:
                if varv.intersection(set(p.listvar)):
                    p.reduce(val,inplace = True)
        
                    if len(p.listvar)<= 1:
                        if p.trivial():
                            bor.append(p)
                        if p.contradict():
                            res.annul()
                            return res
                        if len(p.listvar) == 1:
                            if not p.tabla[0]:
                                un.add(p.listvar[0])
                                bor.append(p)
                            elif not p.tabla[1]:
                                un.add(-p.listvar[0])
                                bor.append(p)

            for p in bor:
                res.listap.remove(p)
            for x in un:
                res.insertaunit(x)




            if not inplace:
                return res

        def reducenv(self, val, l, inplace = False):
            res = PotencialTabla()
            if -val in self.unit:
                    res.annul()
                    return res
            res.unit = self.unit-{val}
            for p in self.listap:
                if abs(val) in p.listvar:
                    q = p.reduce([val],inplace)
                    res.listap.append(q)
                    l.append(q)
                elif not inplace:
                     res.listap.append(p.copia())
                else:
                    res.listap.append(p)
            return res

        def precalculo(self,M=32):
            varsl = self.getvarsp()
            for v in varsl:
                print("var ", v)
                if v in self.getvarsp():
                    self.preagrupa(v,M)

        def preagrupa(self,v,M):
            lista = []
            varst = set()
            actual = []
            for p in self.listap:
                if v in p.listvar:
                    if len(varst.union(set(p.listvar))) <= M:
                        actual.append(p)
                        varst.update(set(p.listvar))
                    else:
                        lista.append(actual)
                        actual = [p]
                        varst = set(p.listvar)
                    
            if actual:
                lista.append(actual)

            for l in lista:
                total = nodeTable([])
                for p in l:
                    self.listap.remove(p)
                    total.combina(p,inplace= True)
                for p in l:
                    npr = total.borra( set(total.listvar)- set(p.listvar)  , inplace=False)
                    self.listap.append(npr)
                    print(np.sum(p.tabla))
                    print(np.sum( npr.tabla))
 
        def simplifica(self,l,M=15):
            bor = []
            uni = set()
            for p in l:
                if len(p.listvar)<= M:
                    if p.trivial():
                        bor.append(p)
                    elif p.contradict():
                        self.annul()
                        return
                    else:
                        uni.update(p.calculaunit())

             

            for p in bor:
                self.listap.remove(p)

            if uni:
                self.propagaunits(uni)
            return


        def simplifican(self,l):
            
            while l:

                p= l.pop()

                if not l in self.listap:
                    continue

                sp = p.extraesimple()
                if not sp.trivial():
                    if len(sp.listvar) == 1:
                        var = sp.listvar[0]
                        if not sp.tabla[0]:
                            val = var
                        else:
                            val = -var
                        nl = []
                        self.reducenv(val,nl, inplace=True)
                        for q in nl:
                            if not q in l:
                                l.append(q)
                    elif len(sp.listvar) == 2:
                        v1 = sp.listvar[0]
                        v2 = sp.listvar[1]
                        
                        det1 = sp.checkdetermi(v2)
                        if not det1:
                            det2 = sp.checkdetermi(v1)
                        if not det1 and not det2:
                            continue
                        if not det1 and det2:
                            v1,v2 = v2,v1
                        nl = []
                        self.borrad2(v2,v1,nl)
                        for q in nl:
                            if not q in l:
                                l.append(q)

        

        def extraeunits(self):
            bor = []
            uni = set()
            for p in self.listap:
                    if p.trivial():
                        bor.append(p)
                    elif p.contradict():
                        self.annul()
                        return
                    else:
                        uni.update(p.calculaunit())

             

            for p in bor:
                self.listap.remove(p)

            if uni:
                self.propagaunits(uni)
            return

        def combinafacil(self,order,M):
            
            for var in order:
                su = self.combinacond(var,M)
                if not su:
                    break
                else:
                    print("borrada 2", var)




        def marginalizacond(self,var,M, inplace=True):
            
            if inplace:
                if self.contradict:
                        return True
                if var in  self.unit:
                        self.unit.discard(var)
                        return True
                elif -var in self.unit:
                        self.unit.discard(-var) 

                        return True
                
                si = []    
                vars =set()
                deter = False
            
                for p in self.listap:
            
                
                    if var in p.listvar:
                            vars.update(p.listvar)
                            si.append(p)
                            if not deter:
                                deter = p.checkdetermi(var)
                                if deter: 
                                    keyp = p
        
                if not si:
                    return True

                if deter:
                    dele = True
                    for q in si:
                        if len(set(q.listvar).union(keyp.listvar)) >M+1:
                            dele = False
                    if not dele:
                        return False
                    else:
                        while si:
                            q = si.pop()
                            self.listap.remove(q) 
                            if q == keyp:
                                r = q.borra([var],inplace = False)
                            else:
                                r = q.combina(keyp,inplace = False, des = False)
                                r.borra([var],inplace = True)
                            self.listap.append(r)
                        return True




        
                elif len(vars) <= M+1:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = nodeTable([])

 
                        
                        while si:
                            
                            q = si.pop()
                            self.listap.remove(q)
                            p.combina(q,inplace = True, des = True)

                        r = p.borra([var], inplace = False)
                        if r.contradict():
                            self.annul()
                            return True
                        
                        if r.trivial():
                            return True

                        self.listap.append(r)
                        su = r.calculaunit()
                        if su:
                            self.propagaunits(su)
                        
                        return True
                else:
                        return False



        


                                    

        def marginalizacond2(self,var,M = 30, Q=20):

            
            lista = []
            
            if self.contradict:
                    return (True,lista,[])
            if var in  self.unit:
                    self.unit.discard(var)
                    return (True,lista,[u.potdev(var)])
            elif -var in self.unit:
                    self.unit.discard(-var) 

                    return (True,lista,[u.potdev(-var)])
            
            si = []    

               

            for p in self.listap:
                if var in p.listvar:
                    si.append(p)
            
            for p in si:
                self.listap.remove(p)

            (exact,lista,listaconvar) = u.marginaliza(si,var,M,Q)

            
            if exact and lista and not lista[0].listvar:
                if lista[0].contradict():
                    self.annul()    
                    return(True,lista)
            for p in lista:
                self.listap.append(p)     

                        
            return (exact,lista,listaconvar)
                

        def combinacond(self,var,M, inplace=True):
            
            if inplace:
                if self.contradict:
                        return True
                if var in  self.unit:
                        self.unit.discard(var)
                        return True
                elif -var in self.unit:
                        self.unit.discard(-var) 

                        return True
                
                si = []    
                vars =set()
                for p in self.listap:
            
                
                    if var in p.listvar:
                            vars.update(p.listvar)
                            si.append(p)
        
                if len(si) <= 1:
                    return True
                if len(vars) <= M:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = nodeTable([])

 
                        
                        while si:
                            
                            q = si.pop()
                            self.listap.remove(q)
                            p.combina(q,inplace = True, des = True)


                        if p.contradict():
                            self.annul()
                            return True
                        
                        self.listap.append(p)
                        su = p.calculaunit()
                        if su:
                            self.propagaunits(su)
                        
                        return True
                else:
                         
                    return False

        

                        
        def marginaliza(self,var, inplace = False):

            if not inplace:
                res = PotencialTabla()

                if self.contradict:
                    res.contradict = True
                    return res
                for x in self.unit:
                    if x == var:
                        res.unit = self.unit-{var}
                        res.listap = self.listap.copy()
                        return res
                    elif x== -var:
                        res.unit = self.unit-{-var}
                        res.listap = self.listap.copy()
                        return res
                    else:
                        res.unit.add(x)
    
                
                si = self.listap.copy()
                

                if si:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = si.pop()
                        self.listap.remove(p)
 
                        
                        while si:
                            
                            q = si.pop()
                            self.listap.remove(q)
                            p.combina(q,inplace = True, des =True)
                    
                            
                        r = p.borra([var], inplace=False)
                        
                        self.listap.append(p)
                        res.listap.append(r)
                        

                        

                return res

        def marginalizas(self,vars, inplace = False):


            
            
            if not inplace:
                res = PotencialTabla()

                if self.contradict:
                    res.contradict = True
                    return res
                uv = self.unit.intersection(set(vars))
                nvars = set(map(lambda x: -x, vars))
                nuv = self.unit.intersection(nvars)

                if uv:
                    res.unit = self.unit - uv
                    vars = vars - uv
                else:
                    res.unit = self.unit.copy()
                if nuv:
                    res.unit = res.unit - nuv
                    puv = set(map(lambda x: -x, nuv)) 
                    vars = vars - puv

                
                
                
                si = self.listap.copy()

                if si:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = nodeTable([])
                        
 
                        
                        while si:
                            
                            q = si.pop()
                            p.combina(q,inplace = True)
                    
                        if vars:   
                            p.borra(vars, inplace=True)
                            r = p
                        else:
                            r = p.copia()
                        
                        res.listap.append(r)
                        
                

                        

                return res


        def atabla(self,un):
            res = nodeTable([])
            for p in self.listap:
                res.combina(p, inplace=True)
            for x in un:
                parcial = nodeTable([abs(x)])
                if x>0:
                    parcial.tabla[0] = False
                else:
                    parcial.tabla[1] = False
                res.combina(parcial, inplace=True)
            return res




        def suma(self, opera, inplace = False):
            inter = self.unit.intersection(opera.unit)
            res = PotencialTabla()
            res.unit = inter

            t0 = self.atabla(self.unit-inter)
            t1 = opera.atabla(opera.unit-inter)

            tt = t0.suma(t1,inplace=True)
            res.listap = [tt]

            return res


            

        
        def marginalizapro(self,var, L,inplace = False, M=7):

            if not inplace:
                res = PotencialTabla()

                if self.contradict:
                    res.contradict = True
                    return res
                for x in self.unit:
                    if x == var:
                        res = self.copia()
                        res.unit.discard(var)
                        return res
                    elif x== -var:
                        res = self.copia()
                        res.unit.discard(-var)
                        return res
                    else:
                        res.unit.add(x)
                si = []
                encontr = False
                
                for p in self.listap:
            
                
                    if var in p.listvar:
                            si.append(p)
                            if not encontr and len(p.listvar)<= M:
                                encontr = p.checkdetermi(var)
                                if encontr:
                                    keyp = p
                                    print("variable determinada ", p.listvar)
                                    # sleep(0.5)
                    else:
                            res.listap.append(p)
        
                if si and (not encontr or len(si)<=2):
                        if encontr:
                            print("solo 2")
                        random.shuffle(si)

                        
                        p = nodeTable([])
                        

                        while si:

                            q = si.pop()
                            if len(set(p.listvar).union(set(q.listvar)))<=L:                    
                                p.combina(q,inplace = True, des=False)
                            else:
                                p.borra([var], inplace=True)
                                r = p
                                if not r.trivial():
                                
                                    res.listap.append(r)
                                else:
                                    print(p.listvar, " trivial")
                                    # sleep(2)
                                p = q.copia()
                                print("aproximo")

                        p.borra([var], inplace=True)
                        r = p

                        if not r.trivial():
                                res.listap.append(r)
                        else:
                                    print(p.listvar, " trivial")   
                                    # sleep(2)
                       
                        
                        
                        
                        
                if encontr:

                    while si:

                            q = si.pop()
                            if q == keyp:
                                r = q.borra([var], inplace=False)
                                if not r.trivial():
                                    res.listap.append(r)
                                else:
                                    print("trivial 1")
                            else:
                                if  len(set(keyp.listvar).union(set(q.listvar)))<=L:     
                                    r = q.combina(keyp,inplace = False, des=False)
                                else:
                                    r = q.copia()
                                    print("aproximo")

                                r.borra([var],inplace = True)
                                if not r.trivial():
                                    res.listap.append(r)
                                else:
                                    print("trivial 2")
                            

                            
        
                        
                    
                        

                return res


        def marginalizapros(self,vars,M,inplace = False):

            res = PotencialTabla()
        
            res.unit = self.unit.copy()
            res.listap = self.listap.copy()
            while vars:
                x = vars.pop()
                res = res.marginalizapro(x,M)
            return 
