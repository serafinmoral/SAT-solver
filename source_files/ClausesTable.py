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
        self.table = np.ones( dtype = boolean, shape = t)


    def copyto(self):
        result = nodeTable(self.listvar.copy())
        result.table = self.table.copy()
        return result


    def decomposev(self,v):
        res = []
        h = self.delete([v], inplace = False)
        t = self.minimize(h, pro = {v})
        if len(t.listvar) ==len(self.listvar):
            res.append(self)
        else:
            res.append(t)
            res.append(h)
        return res


    def neg(self,inplace=False):
        newtable = np.logical_not(self.table)
        if inplace:
            self.table = newtable
            res = self
        else:
            res = nodeTable(self.listvar.copy())
            res.table = newtable
        return res
    
    
    def impliedby(self,p):
        if self.sum(p.neg()).trivial():
            return True
        else:
            return False


    def minimize(self, con  , pro = set()):
        rest =  set(self.listvar)-pro
        if not rest:
            return self
        else:
            v = rest.pop()
            h = self.delete([v], inplace=False)
            if self.impliedby(h.combine(con)):
                return h.minimize(con,pro)
            else:
                pro.add(v)
                return self.minimize(con,pro)


    def combine(self,op,inplace = False, des= False):
        result = self if inplace else self.copyto()
        if isinstance(op,boolean):
            if op:
                return result
            else:
                result.table = result.table & op
                return result
        if not des:
            op = op.copyto()
        extra = set(op.listvar) - set(result.listvar)
        if extra:
                slice_ = [slice(None)] * len(result.listvar)
                slice_.extend([np.newaxis] * len(extra))
                result.table = result.table[tuple(slice_)]
                result.listvar.extend(extra)
        extra = set(result.listvar) - set(op.listvar)
        if extra:
                slice_ = [slice(None)] * len(op.listvar)
                slice_.extend([np.newaxis] * len(extra))
                op.table = op.table[tuple(slice_)]
                op.listvar.extend(extra)
                # No need to modify cardinality as we don't need it.
            # rearranging the axes of phi1 to match phi
        for axis in range(result.table.ndim):
            exchange_index = op.listvar.index(result.listvar[axis])
            op.listvar[axis], op.listvar[exchange_index] = (
                op.listvar[exchange_index],
                op.listvar[axis],
            )
            op.table = op.table.swapaxes(axis, exchange_index)
        result.table = result.table & op.table    
        if not inplace:
            return result


    def checkdetermi(self,v):
        if v not in self.listvar:
            return False
        t0 = self.reduce([v])
        t1 = self.reduce([-v])
        t = t0.combine(t1, inplace=False)
        if t.contradict():
            return True
        else:
            return False


    # def contenida(self,nodelist):
    #     return u.contenida(self,nodelist) 


    def minimizedep(self,v, seg = set()):
        vars = set(self.listvar) - seg
        vars.remove(v)
        if not vars:
            return self
        nv = vars.pop()
        np = self.delete([nv])
        if not np.trivial() and np.checkdetermi(v):
            return np.minimizedep(v, seg.copy())
        else:
            seg.add(nv)
            return self.minimizedep(v,seg)


    def extraesimple(self):
        vars = set(self.listvar)
        if not vars:
            return nodeTable([])
        v = vars.pop()
        pv = self.delete(list(vars))
        if not pv.trivial():
            return pv
        else:
            pr = self.delete([v])

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
            res = self.combine(q.delete(vars))
            return res


    def extrasimple2(self,v1,vars):
        if not vars:
            return nodeTable([])
        v2 = vars.pop()
        pv12 = self.delete(list(vars))
        if pv12.checkdetermi(v2) or pv12.checkdetermi(v1):
            return pv12
        else:
            pr = self.delete([v2])

            return pr.extrasimple2(v1,vars)


    def sum(self,op,inplace = False, des= False):
        result = self if inplace else self.copyto()
        if isinstance(op,boolean):
            if op:
                return result
            else:
                result.table = result.table | op
                return result
        if not des:
            op = op.copyto()
        extra = set(op.listvar) - set(result.listvar)
        if extra:
                slice_ = [slice(None)] * len(result.listvar)
                slice_.extend([np.newaxis] * len(extra))
                result.table = result.table[tuple(slice_)]
                result.listvar.extend(extra)
        extra = set(result.listvar) - set(op.listvar)
        if extra:
                slice_ = [slice(None)] * len(op.listvar)
                slice_.extend([np.newaxis] * len(extra))
                op.table = op.table[tuple(slice_)]
                op.listvar.extend(extra)
                # No need to modify cardinality as we don't need it.
            # rearranging the axes of phi1 to match phi
        for axis in range(result.table.ndim):
            exchange_index = op.listvar.index(result.listvar[axis])
            op.listvar[axis], op.listvar[exchange_index] = (
                op.listvar[exchange_index],
                op.listvar[axis],
            )
            op.table = op.table.swapaxes(axis, exchange_index)
        result.table = result.table | op.table    
        if not inplace:
            return result


    def reduce(self, val, inplace=False):
        values = filter(lambda x: abs(x) in  self.listvar, val)
        phi = self if inplace else self.copyto()
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
        phi.table= phi.table[tuple(slice_)]
        return phi

    
    def introducelist(self,lista):
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
        self.table[tuple(slice_)] = False
    

    def delete(self,variables, inplace=False):
        phi = self if inplace else self.copyto()   
        for var in variables:
            if var not in phi.listvar:
                raise ValueError(f"{var} no está en la lista.")
        var_indexes = [phi.listvar.index(var) for var in variables]
        index_to_keep = sorted(set(range(len(self.listvar))) - set(var_indexes))
        phi.listvar = [phi.listvar[index] for index in index_to_keep]
        phi.table = np.amax(phi.table, axis=tuple(var_indexes))
        if not inplace:
            return phi


    def contradict(self):
        return not np.amax(self.table)

    def cuenta(self,v):
        t0 = self.reduce([v],inplace=False)
        t1 = self.reduce([-v],inplace=False)
        x0 = np.sum(t0.table)
        x1 = np.sum(t1.table)
        return (x0,x1)

    def annul(self):
        self.listvar = []
        self.table = False

    def trivial(self):
        return  np.amin(self.table)

    def calculaunit(self):
        result = set()
        n = len(self.listvar)
        total = set(range(n))
        for i in range(n):
            
            delete = tuple(total-{i})
            marg = np.amax(self.table,axis = delete)
            
            if not marg[0]:
                if not marg[1]:
                    result.add(0)
                    return result
                else:
                    result.add(self.listvar[i])
            elif  not marg[1]:    
                    result.add(-self.listvar[i])
        return result
          
    



class PotentialTable:
        def __init__(self):
            self.unit = set()
            self.listp = []
            self.contradict = False

        def annul(self):
            self.unit = set()
            self.listp = []
            self.contradict = True
        
        def trivial(self):
            if not self.unit and not self.listp:
                return True
            else:
                return False

        def imprime(self):
            print("unit: ", self.unit)
            print("tables ")
            print("contradiccion ", self.contradict)
            for x in self.listp:
                print("vars" , x.listvar)
                print(x.table)

        def cgrafo(self):
            grafo = nx.Graph()
        
            vars = set(map(abs,self.unit))
            for p in self.listp:
                vars.update(p.listvar)
        
        
            for p in self.listp:
                for i in range(len(p.listvar)):
                    for j in range(i+1,len(p.listvar)):
                           grafo.add_edge(p.listvar[i],p.listvar[j])    
            return grafo 

        

        def copyto(self):
            res = PotentialTable()
            res.unit = self.unit.copy()

            for p in self.listp:
                print(p)
                res.listp.append(p.copyto())
            return res

        def getvars(self):
            res = set()
            res.update(set(map(abs,self.unit)))



            for p in self.listp:
                res.update(set(p.listvar))
            return res

        def getvarsp(self):
            res = set()
    
            for p in self.listp:
                res.update(set(p.listvar))
            return res

        def getvarspv(self,v):
            res = set()
    
            for p in self.listp:
                if v in p.listvar:
                    res.update(set(p.listvar))
            return res

        def computefromsimple(self,simple):
            self.unit = simple.unit.copy()
            (sets,clusters) = u.createclusters(simple.listclaus)
            for i in range(len(sets)):
                x = nodeTable(list(sets[i]))
                x.introducelist(clusters[i])
                self.listp.append(x)

        def insert(self,p):
            self.listp.append(p)

        def calculavarcond(self,m=0):
            cont = dict()

            vars = self.getvars()
            for x in vars:
                cont[x] = 0.0
            
            for p in self.listp:
                if m==0:
                    h = np.sum(p.table)

                    for x in p.listvar:
                        if h == 0:
                            
                            cont[x] += 100.0
                        else:
                            cont[x] += 1/h
                else:
                    for x in p.listvar:
                            cont[x]+=1
            return max(cont, key = cont.get)

 
        def localUpgrade(self,M=25,Q=10):
            for p in self.listp:
                if len(p.listvar)<=Q:
                    old = np.sum(p.table)
                    vars = set(p.listvar)
                    tvars = set(p.listvar)
                    lista = []
                    for q in self.listp:
                        if not q==p:
                            qv = set(q.listvar)
                            if set(qv.intersection(vars)):
                                if len(tvars.union(qv))<=M:
                                    tvars.update(qv)
                                    lista.append(q)
                    vars = tvars.copy()
                    for q in self.listp:
                        if not q==p:
                            qv = set(q.listvar)
                            if set(qv.intersection(vars)):
                                if len(tvars.union(qv))<=M:
                                    tvars.update(qv)
                                    lista.append(q)
                    r = nodeTable([])
                    for q in lista:
                        r.combine(q,inplace=True)
                    r.delete(list(tvars-set(p.listvar)),inplace=True)
                    p.combine(r,inplace=True)
                    ns = np.sum(p.table)

                    if (ns < old):
                        print("mejopra", ns, old,len(p.listvar))


        def insertunit(self,x):
            print("INSERTING UNIT")
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
                for p in self.listp:
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
                for p in self.listp:
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


        def prop(self):
            y = np.sum(self.table)
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
            for p in self.listp:
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
                self.listp.remove(p)
            if nu:
                self.propagaunits(nu)
                        

        def reduce(self, val, inplace = False):
            res = self if inplace else self.copyto()   
            varv = set(map(abs,val))
            for x in self.unit:
                if -x in val:
                    res.contradict = True
                    return res
            res.unit.difference_update(set(val))
            bor = []
            un = set()
            for p in res.listp:
                if varv.intersection(set(p.listvar)):
                    p.reduce(val,inplace = True)
        
                    if len(p.listvar)<= 1:
                        if p.trivial():
                            bor.append(p)
                        if p.contradict():
                            res.annul()
                            return res
                        if len(p.listvar) == 1:
                            if not p.table[0]:
                                un.add(p.listvar[0])
                                bor.append(p)
                            elif not p.table[1]:
                                un.add(-p.listvar[0])
                                bor.append(p)

            for p in bor:
                res.listp.remove(p)
            for x in un:
                res.insertunit(x)




            if not inplace:
                return res

        def reducenv(self, val, l, inplace = False):
            res = PotentialTable()
            if -val in self.unit:
                    res.annul()
                    return res
            res.unit = self.unit-{val}
            for p in self.listp:
                if abs(val) in p.listvar:
                    q = p.reduce([val],inplace)
                    res.listp.append(q)
                    l.append(q)
                elif not inplace:
                     res.listp.append(p.copyto())
                else:
                    res.listp.append(p)
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
            for p in self.listp:
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
                    self.listp.remove(p)
                    total.combine(p,inplace= True)
                for p in l:
                    npr = total.delete( set(total.listvar)- set(p.listvar)  , inplace=False)
                    self.listp.append(npr)
                    print(np.sum(p.table))
                    print(np.sum( npr.table))
 
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
                self.listp.remove(p)

            if uni:
                self.propagaunits(uni)
            return


        def extraeunits(self):
            bor = []
            uni = set()
            for p in self.listp:
                    if p.trivial():
                        bor.append(p)
                    elif p.contradict():
                        self.annul()
                        return
                    else:
                        uni.update(p.calculaunit())
            for p in bor:
                self.listp.remove(p)

            if uni:
                self.propagaunits(uni)
            return


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
            
                for p in self.listp:
            
                
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
                            self.listp.remove(q) 
                            if q == keyp:
                                r = q.delete([var],inplace = False)
                            else:
                                r = q.combine(keyp,inplace = False, des = False)
                                r.delete([var],inplace = True)
                            self.listp.append(r)
                        return True




        
                elif len(vars) <= M+1:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = nodeTable([])

 
                        
                        while si:
                            
                            q = si.pop()
                            self.listp.remove(q)
                            p.combine(q,inplace = True, des = True)

                        r = p.delete([var], inplace = False)
                        if r.contradict():
                            self.annul()
                            return True
                        
                        if r.trivial():
                            return True

                        self.listp.append(r)
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

               

            for p in self.listp:
                if var in p.listvar:
                    si.append(p)
            
            for p in si:
                self.listp.remove(p)

            (exact,lista,listaconvar) = u.marginaliza(si,var,M,Q)
            if exact and lista and not lista[0].listvar:
                if lista[0].contradict():
                    self.annul()    
                    return(True,lista)
            for p in lista:
                self.listp.append(p)       
            return (exact,lista,listaconvar)
                        

                        
        def marginaliza(self,var, inplace = False):

            if not inplace:
                res = PotentialTable()

                if self.contradict:
                    res.contradict = True
                    return res
                for x in self.unit:
                    if x == var:
                        res.unit = self.unit-{var}
                        res.listp = self.listp.copy()
                        return res
                    elif x== -var:
                        res.unit = self.unit-{-var}
                        res.listp = self.listp.copy()
                        return res
                    else:
                        res.unit.add(x)
    
                
                si = self.listp.copy()
                

                if si:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = si.pop()
                        self.listp.remove(p)
 
                        
                        while si:
                            
                            q = si.pop()
                            self.listp.remove(q)
                            p.combine(q,inplace = True, des =True)
                    
                            
                        r = p.delete([var], inplace=False)
                        
                        self.listp.append(p)
                        res.listp.append(r)
                        

                        

                return res

        def marginalizas(self,vars, inplace = False):


            
            
            if not inplace:
                res = PotentialTable()

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

                
                
                
                si = self.listp.copy()

                if si:
                        si.sort(key = lambda h: - len(h.listvar) )
                        
                        p = nodeTable([])
                        
 
                        
                        while si:
                            
                            q = si.pop()
                            p.combine(q,inplace = True)
                    
                        if vars:   
                            p.delete(vars, inplace=True)
                            r = p
                        else:
                            r = p.copyto()
                        
                        res.listp.append(r)
                        
                

                        

                return res


        def atable(self,un):
            res = nodeTable([])
            for p in self.listp:
                res.combine(p, inplace=True)
            for x in un:
                parcial = nodeTable([abs(x)])
                if x>0:
                    parcial.table[0] = False
                else:
                    parcial.table[1] = False
                res.combine(parcial, inplace=True)
            return res




        def sum(self, opera, inplace = False):
            inter = self.unit.intersection(opera.unit)
            res = PotentialTable()
            res.unit = inter

            t0 = self.atable(self.unit-inter)
            t1 = opera.atable(opera.unit-inter)

            tt = t0.sum(t1,inplace=True)
            res.listp = [tt]

            return res


            

        
        def marginalizapro(self,var, L,inplace = False, M=7):

            if not inplace:
                res = PotentialTable()

                if self.contradict:
                    res.contradict = True
                    return res
                for x in self.unit:
                    if x == var:
                        res = self.copyto()
                        res.unit.discard(var)
                        return res
                    elif x== -var:
                        res = self.copyto()
                        res.unit.discard(-var)
                        return res
                    else:
                        res.unit.add(x)
                si = []
                encontr = False
                
                for p in self.listp:
            
                
                    if var in p.listvar:
                            si.append(p)
                            if not encontr and len(p.listvar)<= M:
                                encontr = p.checkdetermi(var)
                                if encontr:
                                    keyp = p
                                    print("variable determinada ", p.listvar)
                                    # sleep(0.5)
                    else:
                            res.listp.append(p)
        
                if si and (not encontr or len(si)<=2):
                        if encontr:
                            print("solo 2")
                        random.shuffle(si)

                        
                        p = nodeTable([])
                        

                        while si:

                            q = si.pop()
                            if len(set(p.listvar).union(set(q.listvar)))<=L:                    
                                p.combine(q,inplace = True, des=False)
                            else:
                                p.delete([var], inplace=True)
                                r = p
                                if not r.trivial():
                                    res.listp.append(r)
                                else:
                                    print(p.listvar, " trivial")
                                p = q.copyto()
                                print("aproximo")
                        p.delete([var], inplace=True)
                        r = p
                        if not r.trivial():
                                res.listp.append(r)
                        else:
                                    print(p.listvar, " trivial")        
                if encontr:
                    while si:
                            q = si.pop()
                            if q == keyp:
                                r = q.delete([var], inplace=False)
                                if not r.trivial():
                                    res.listp.append(r)
                                else:
                                    print("trivial 1")
                            else:
                                if  len(set(keyp.listvar).union(set(q.listvar)))<=L:     
                                    r = q.combine(keyp,inplace = False, des=False)
                                else:
                                    r = q.copyto()
                                    print("aproximo")

                                r.delete([var],inplace = True)
                                if not r.trivial():
                                    res.listp.append(r)
                                else:
                                    print("trivial 2")
                            

                            
        
                        
                    
                        

                return res


        def marginalizapros(self,vars,M,inplace = False):

            res = PotentialTable()
        
            res.unit = self.unit.copy()
            res.listp = self.listp.copy()
            while vars:
                x = vars.pop()
                res = res.marginalizapro(x,M)
            return 
