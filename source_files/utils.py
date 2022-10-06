# -*- coding: utf-8 -*-
from source_files.ClausesTable import *
from source_files.TablesVar import *
import source_files.ProblemTrianFactor as pt


def tam(l):
    tot = set()
    if l:
        for h in l:
            tot.update(set(h.listvar))
        return len(tot)
    else:
        return 0    


def valord(p):
    if not len(p.listvar)==1:
        print("llamada impropia")
    else:
        v = p.listvar[0]
        if not p.tabla[0]:
            return v
        else:
            return -v


def contenida(nodo, listanodos):
    if (len(listanodos)>0):
        nodoaux = nodeTable([])
        for x in range(len(listanodos)):
            nodoaux.combina(listanodos[x], inplace=True)
        listaBorra = list(set(nodoaux.listvar)-set(nodo.listvar))
        nodoaux.borra(listaBorra, inplace=True)
        nodoaux.tabla = np.logical_not(nodoaux.tabla)
        nodoaux=nodoaux.suma(nodo)
        return nodoaux.trivial()
    else:
        return False


def partev(lista,v):
    bor = []
    nl = []
    for p in lista:
        if p.trivial():
            bor.append(p)
            # print("trivial antes ")
            break 
        if v in p.listvar:
            l = p.descomponev(v)
            if len(l)>1:
                for q in l:
                    if not q.trivial():
                        nl.append(q)
                    # else:
                        # print("trivial ", q.listvar)
                bor.append(p)
                # print("descomposicion ", len(p.listvar))
                # print([len(q.listvar) for q in l])
                # sleep(1)
    for p in bor:
        lista.remove(p)
    lista.extend(nl)
    lista.sort(key = lambda x : len(x.listvar) )


def potdev(v):
    res = nodeTable([abs(v)])
    if v>0:
        res.tabla[0] = False
    else:
        res.tabla[1] = False
    return res


def calculaclusters1(lista,p,var):
    li = [set(q.listvar).union(p.listvar) - {var} for q in lista]
    borraincluidos(li)
    return li


def calculaclusters2(lista,var):
    li = []
    for p in lista:
        s = set(p.listvar)
        for q in lista:
            li.append(s.union(q.listvar)- {var})
    borraincluidos(li)
    return li


def borraincluidos(lista):
    lista.sort(key = lambda x : - len(x) )
    i=0
    while i <len(lista)-1:
        j = i+1
        while j < len(lista):
            con1 = lista[i]
            con2 = lista[j]
            if con2 <= con1:
                lista.remove(con2)
            else:
                j+=1
        i += 1


def ordenaycombinaincluidas(lista,rela, borrar = True, inter=False):
    lista.sort(key = lambda x : - len(x.listvar) )
    i=0
    while i <len(lista)-1:
        j = i+1
        while j < len(lista):
            # print("lista, i, j", len(lista), i, j)
            if set(lista[j].listvar) <= set(lista[i].listvar):
                p = lista[i]
                q = lista[j]
                rela.borrarpot(p)
                if borrar:
                    rela.borrarpot(q)
                t = p.combina(q)
                if t.contradict():
                    rela.annul()
                    print("contradicion ")
                    return 
                rela.insertar(t)
                lista[i] = t
                if borrar:
                    lista.remove(q)
                else:
                    j +=1
            else:
                if inter:
                    p = lista[i]
                    q = lista[j]
                    tp = p.upgrade(q)
                    tq = q.upgrade(p)
                    if tp.contradict() or tq.contradict():
                        rela.annul()
                        print("contradicion ")
                        return
                    rela.borrarpot(p)
                    rela.borrarpot(q)
                    lista[i] = tp
                    lista[j] = tq
                    rela.insertar(tp)
                    rela.insertar(tq)
                j+=1
        i+=1
    lista.reverse()
    
    
def agrupatam(lista):
    lista.sort(key = lambda x : - len(x.listvar) )
    i=0
    while i <len(lista)-1:
        j = i+1
        while j < len(lista):
            # print("lista, i, j", len(lista), i, j)
            s1 = set(lista[j].listvar)
            s2 = set(lista[i].listvar)
            if s1 <= s2 or ((len(s1) == len(s2) and (len(s1-s2) == 1))):
                p = lista[i]
                q = lista[j]
                t = p.combina(q)
                if t.contradict():
                    print("contradicion ")
                    return 
                lista[i] = t
                del lista[j]
            else:
                j+=1
        i+=1
    lista.reverse()


def createclusters (lista):
    listasets = []
    for cl in lista:
        va = set(map(abs,cl))
        encontrado = False
        for x in listasets:
            if va <= x:
                encontrado = True
                break
        if not encontrado:
            listasets.append(va)
    i = 0
    j = 1
    while (i<len(listasets)-1):
        if listasets[i] <= listasets[j]:
            del listasets[i]
            j = i+1
        elif listasets[j] <= listasets[i]:
            del listasets[j]
            if j >= len(listasets):
                i += 1
                j = i+1
        else:
            j += 1
            if j >= len(listasets):
                i += 1
                j = i+1
    listclaus = []
    for i in range(len(listasets)):
        listclaus.append([])
    for cl in lista:
        va = set(map(abs,cl))
        for i in range(len(listasets)):
            if va <= listasets[i]:
                listclaus[i].append(cl)
                break
    return(listasets,listclaus)


def marginaliza(lista, var, Split_In, M=30, Q=20):
    if not lista:
        return (True,[],[])
    if Split_In:
        partev(lista,var)
    res = []
    si = []
    vars = set()
    deter = False
    for p in lista:
        # print(p.listvar)
        if var in p.listvar:
            vars.update(p.listvar)
            si.append(p)
            if not deter:
                deter = p.checkdetermi(var)
                if deter: 
                    nv = set()
                    keyp = p.minimizadep(var,nv)
                    setkey = set(keyp.listvar)
                    # if len(keyp.listvar) < len(p.listvar):
                        # print("minimizo ",len(keyp.listvar) ,  len(p.listvar))
        else:
            # print("warning: variable no en tabla")
            res.append(p)
    if not si:
        return (True,res,[nodeTable([var])])
    exact = True
    if deter:
        print("determinista ")
        vars.discard(var)
        listp = [keyp]
        if len(vars) <= Q:
            # print("global ")
            r = nodeTable([])
            lc = calculaclusters1(si,keyp,var)
            while si:
                q = si.pop()
                r.combina(q,inplace=True)
            r.borra([var],inplace=True)
            if r.contradict():
                con = nodeTable([])
                con.annul()
                print("contradiccion")
                return (True,[con],[keyp])
            for h in lc:
                rh = r.borra(list(vars-h)) 
                        
                if not rh.trivial():
                    res.append(rh)
        else:
            while si:
                q = si.pop() 
                if q == keyp:
                    r = q.borra([var],inplace = False)
                else:
                    if len(setkey.union(set(q.listvar))) < M+1:
                        r = q.combina(keyp,inplace = False, des = False)
                        r.borra([var],inplace = True)
                        if r.contradict():
                            con = nodeTable([])
                            con.annul()
                            return (True,[con],[])
                        if not r.trivial():
                            res.append(r)
                    else:
                        exact = False
    else:
            si.sort(key = lambda h: - len(h.listvar) )
            print("borrada " , var, "metodo 2, n potenciales", len(si))
            if len(si) >= 30:
                    agrupatam(si)
            lc = calculaclusters2(si,var)
            vars.discard(var)
            sizes = 0.0
            for xx in lc:
                sizes += 2**len(xx)
            lista = []
            if 2**(len(vars)-1) <= sizes and len(vars) <=31:
                print ("global total ")
                r = nodeTable([])
                while si:
                    q = si.pop()
                    r.combina(q,inplace=True)
                listp = [r.copia()]
                r.borra([var],inplace=True)
                if r.contradict():
                    con = nodeTable([])
                    con.annul()
                    return (True,[con],[])
                if not r.trivial():
                        res.append(r)
            elif len(vars)<= Q:
                print("global ")
                r = nodeTable([])
                while si:
                    q = si.pop()
                    r.combina(q,inplace=True)
                listp = [r.copia()]
                
                r.borra([var],inplace=True)
                if r.contradict():
                    con = nodeTable([])
                    con.annul()
                    return (True,[con],[])
                for h in lc:
                    rh = r.borra(list(vars-h)) 
                    if not rh.trivial():
                        res.append(rh)
            else:
                print("no global", len(vars), vars)
                # if len(si) >= 30:
                #     print("arupando en tamaño ", len(si))
                #     agrupatam(si)
                #     print(len(si))
                #     sleep(3)
                si2 = si.copy()
                listp = si2
                while si:
                    q = si.pop()
                    # print(q.listvar)
                    for p in si2:
                        if len(set(q.listvar).union(set(p.listvar))) >M+1:
                            print( "no exacto")
                            exact = False
                        else:
                            r = p.combina(q)
                            r.borra([var], inplace = True)
                            if r.contradict():
                                con = nodeTable([])
                                con.annul()
                                r = nodeTable([var])
                                r.tabla[0] = False
                                r.tabla[1] = False
                                return (True, [con],listp)
                            if not r.trivial():
                                res.append(r)      
    return (exact,res,listp)


def calculamethod(lista,var):
            si = []    
            deter = False
            vars = set()
            if len(lista)<=2:
                return 1
            for p in lista:
                if var in p.listvar:
                        vars.update(p.listvar)
                        si.append(p)
                        if not deter:
                            deter = p.checkdetermi(var)
                            if deter: 
                                return 1
            return 2              