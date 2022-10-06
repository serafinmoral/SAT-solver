# -*- coding: utf-8 -*-
from statistics import variance
from source_files.Utils import *


class varpot:
        def __init__(self, Qin=20, SplitIn=True): 
            self.tabla = dict()
            self.unit = set()
            self.contradict = False
            self.Q = Qin 
            self.split=SplitIn          


        def annul(self):
            self.tabla = dict()
            self.unit = set()
            self.contradict = True


        def insertaru(self,v):
            self.reduce(v, inplace=True)
            self.unit.add(v)


        def getvars(self):
            res = set(map(abs,self.unit))
            for v in self.tabla:
                if self.tabla[v]:
                    res.add(v)
            return res


        def trivial(self):
            if self.unit:
                return False
            if self.tabla:
                for v in self.tabla:
                    if self.tabla[v]:
                        return False
            return True


        def insertar(self,p):
            if len(p.listvar) ==1:
                if p.contradict():
                    self.annul()
                    return
                if not p.trivial():
                    u = valord(p)
                    self.insertaru(u)
                    return
                else:
                    return 
            if self.unit:
                varsu = set(map(abs,self.unit))
                if varsu.intersection(set(p.listvar)):
                    varr = filter(lambda x: abs(x) in varsu, self.unit)
                    p = p.reduce(varr,inplace=False)
            for v in p.listvar:
                if v in self.tabla:
                    self.tabla[v].append(p)
                else:
                    self.tabla[v] = [p]


        def reduce(self,v,inplace=True):
            res = self if inplace else  self.copia()
            if v in self.unit:
                res.unit.discard(v)
            elif -v in self.unit:
                res.annul()
            elif v in self.tabla:
                lista = res.get(v)
                res.borrarv(v)
                for p in lista:
                    q = p.reduce([v],inplace = False)
                    res.insertar(q)
            elif -v in self.tabla:
                lista = res.get(-v)
                res.borrarv(-v)
                for p in lista:
                    q = p.reduce([v],inplace = False)
                    res.insertar(q)
            return res


        def copia(self):
            res = varpot()
            res.unit = self.unit.copy()
            res.contradict = self.contradict
            for x in self.tabla.keys():
                res.tabla[x] = self.tabla[x].copy()
            return res


        def createfrompot(self,pot):
            self.contradict = self.contradict
            self.unit = pot.unit.copy()
            for p in pot.listap:
                self.insertar(p)
        

        def createfromlista(self,l):
            for p in l:
                self.insertar(p)


        def borrarpot(self,p):
            if len(p.listvar) == 1:
                v = p.listvar[0]
                if not p.tabla[0]:
                    self.unit.discard(-v)
                elif not p.tabla[1]:
                    self.unit.discard(v)
                return 
            for v in p.listvar:
                if v in self.tabla:
                    try:
                        self.tabla[v].remove(p)
                    except ValueError:
                        pass # or scream: thing not in some_list!self.tabla[v].remove(p)


        def borrarv(self,v):
            self.unit.discard(v)
            self.unit.discard(-v)
            if v in self.tabla:
                for p in self.tabla[v].copy():
                    self.borrarpot(p)
                del self.tabla[v]


        def siguiente(self):
            if self.unit:
                x = self.unit.pop()
                self.unit.add(x)
                return abs(x)
            miv = min(self.tabla,key = lambda x: len(self.tabla.get(x)))
            mav = max(self.tabla,key = lambda x: len(self.tabla.get(x)))
            # print(miv,mav,len(self.tabla.get(miv)),len(self.tabla.get(mav)))
            if len(self.tabla.get(miv)) == 1:
                return (miv)
            miv = min(self.tabla,key = lambda x: tam(self.tabla.get(x)))
            mav = max(self.tabla,key = lambda x: tam(self.tabla.get(x)))
            # print (miv,mav,tam(self.tabla.get(miv)),tam(self.tabla.get(mav)))
            return miv


        def getmax(self):
            if not self.tabla and self.unit:
                x = self.unit.pop()
                self.unit.add(x)
                return abs(x)
            else:
                mav = max(self.tabla,key = lambda x: len(self.tabla.get(x)))
                return mav

        
        def combina(self,rela, inplace=True):
            res = self if inplace else  self.copia()
            for u in rela.unit:
                res.insertaru(u)
            for v in rela.tabla:
                for p in rela.tabla[v]:
                    if min(p.listvar) ==v:
                        res.insertar(p)
            return res


        def marginaliza(self,var,M = 30, Q=20):
            lista = []
            if self.contradict:
                    print("contradiction ")
                    return (True,lista,[])
            if var in  self.unit:
                    self.unit.discard(var)
                    return (True,lista,[u.potdev(var)])
            elif -var in self.unit:
                    self.unit.discard(-var) 
                    return (True,lista,[u.potdev(-var)])
            (exact,lista,listaconvar) = u.marginaliza(self.get(var).copy(),var,self.split,M,Q)
            if exact and lista and not lista[0].listvar:
                if lista[0].contradict():
                    print ("contradict")
                    self.annul()    
                    return(True,lista,listaconvar)
            for p in lista:
                if p.contradict():
                    print ("contradict")
                    self.annul()
                else:
                    # print(p.listvar)
                    self.insertar(p)     
            self.borrarv(var)
            return (exact,lista,listaconvar)


        def marginalizae(self,var,M = 30, Q=20):
            lista = []
            if self.contradict:
                    return (True,lista,[])
            if var in  self.unit:
                    self.unit.discard(var)
                    return (True,lista,[u.potdev(var)])
            elif -var in self.unit:
                    self.unit.discard(-var) 
                    return (True,lista,[u.potdev(-var)])
            (exact,lista,listaconvar) = u.marginaliza(self.get(var).copy(),var,self.split,M,Q) #EEDM
            if exact and lista and not lista[0].listvar:
                if lista[0].contradict():
                    self.annul()    
                    return(True,lista,listaconvar)
            if exact:
                for p in lista:
                    self.insertar(p)     
                self.borrarv(var)
            return (exact,lista,listaconvar)


        def marginalizaset(self,vars,M = 30, Q=20, ver = True, inplace = True, pre = False, order = []):
            if not pre:
                vars.intersection_update(self.getvars())
            if inplace:
                if not pre:
                    order = []
                listan = []
                listaq = []
                nuevas = []
                if pre:
                    nvars = [x for x in order if x in vars]
                    nvars.reverse()
                    vars = nvars
                e = True
                while vars and not self.contradict:
                    if pre:
                        var = vars.pop()
                    else:
                        var = self.siguientep(vars)
                    tama = tam(self.tabla.get(var))
                    lista = self.get(var)
                    if not pre:
                        pos = vars.copy()
                        dif = 0
                        while pos and dif <=2:
                            met = calculamethod(lista,var)
                            if met == 1:
                                break
                            else:
                                if not pre:
                                    pos.discard(var)
                                if pos:
                                    var = self.siguientep(pos)
                                    lista =self.get(var)
                                    dif = tam(self.tabla.get(var))- tama
                        if met==2:
                            var = self.siguientep(vars)
                            lista = self.get(var)
                    u.ordenaycombinaincluidas(lista,self, borrar = True, inter=False)
                    if ver:
                        print("var", var, "quedan ", len(vars))
                    if not pre:
                        vars.discard(var)
                    (exac,nuevas,antiguas) = self.marginaliza(var,M,Q)
                    if not exac:
                        print("borrado no exacto " )
                        e = False
                    if not pre:
                        order.append(var)
                    listan.append(nuevas)
                    listaq.append(antiguas)
                    if not self.contradict:
                        u.ordenaycombinaincluidas(nuevas,self, borrar=True)
                return(e,order,nuevas,listaq)
            else:
                res = self.copia()
                res.marginalizaset(vars,M , Q, ver , inplace = True)
                return res

        
        def extraelista(self):
            lista = []
            for v in self.tabla:
                for p in self.tabla[v]:
                    if min(p.listvar) == v:
                        lista.append(p)
            return lista


        def atabla(self):
            res = nodeTable([])
            for v in self.unit:
                res.combina(potdev(v), inplace=True)
            for v in self.tabla:
                for p in self.tabla[v]:
                    if min(p.listvar) == v:
                        res.combina(p, inplace=True)
            return res


        def localUpgrade(self,M=25,Q=20,N=2):
            listap = self.extraelista()        
            for p in listap:                
                    old = np.sum(p.tabla)
                    vars = set(p.listvar)
                    nvars = vars.copy()
                    tvars = set(p.listvar)
                    lista = []
                    for i in range(N):
                        for v in nvars:
                            for q in self.tabla[v]:
                                if not q in lista:
                                    lista.append(q)
                                    qv = set(q.listvar)
                                    tvars.update(qv)
                            nvars = tvars-vars
                            vars = tvars.copy()
                    r = varpot()
                    r.createfromlista(lista)
                    r.marginalizaset(tvars-set(p.listvar),M,self.Q, ver=False) #EDM
                    nl = r.extraelista()
                    lk = nodeTable([])
                    for q in nl:
                        lk.combina(q,inplace=True)
                    ns = np.sum(lk.tabla)
                    if (ns < old):
                        # print("Upgrade", ns, old,len(p.listvar), len(lk.listvar)) #EDM
                        self.borrarpot(p)
                        self.insertar(lk)


        def siguientep(self,pos):
            if self.unit:
                varu = set(map(abs,self.unit))
                if varu.intersection(pos):
                    x = varu.pop()
                    return x
            miv = min(pos,key = lambda x: len(self.tabla.get(x)))
            mav = max(pos,key = lambda x: len(self.tabla.get(x)))
            # print(miv,mav,len(self.tabla.get(miv)),len(self.tabla.get(mav)))
            if len(self.tabla.get(miv)) == 1:
                # print("un solo potencial !!!!!!!!!!!!!!!!")
                return (miv)
            miv = min(pos,key = lambda x: tam(self.tabla.get(x)))
            mav = max(pos,key = lambda x: tam(self.tabla.get(x)))
            # print (miv,mav,tam(self.tabla.get(miv)),tam(self.tabla.get(mav)))
            return miv


        def get(self,i):
            return self.tabla.get(i,[]).copy()