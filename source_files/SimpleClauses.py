# -*- coding: utf-8 -*-
import networkx as nx

class simpleClauses:
    def __init__(self):
         self.listclaus = []
         self.contradict = False
         self.listvar = set()    
         self.solved = False
         self.solution = set()
         self.unit = set()
         self.listclausOriginal = []
         
    def insert(self,x, test=True):
        if self.contradict:
            return []
        if not x:
            self.anula()
            self.contradict= True
            self.listclaus.append(set())
            return []
        y = []
        borr = []
        if len(x) ==1:
            v = x.pop()
            if -v in self.unit:
                self.insert(set())
            else:
                self.listvar.add(abs(v))
                self.unit.add(v)
                for cl in self.listclaus:
                    if v in cl:
                        borr.append(cl)
                    if -v in cl:
                        borr.append(cl)
                        cl.discard(-v)
                        y.append(cl)
        else:
            if x.intersection(self.unit):
                return []
            else:
                neg = set(map(lambda x: -x, self.unit))
                x = x-neg
                if len(x) <= 1:
                    self.insert(x)
                    return
                
            if test:
                for cl in self.listclaus:
                    if len(x) <= len(cl):
                        claudif = x-cl
                        if not claudif:
                            borr.append(cl)
                        elif len(claudif) == 1:
                            var = claudif.pop()
                            if -var in cl:
                                cl.discard(-var)
                                borr.append(cl)
                                y.append(cl)
                    if len(cl) <= len(x):
                        claudif = cl-x
                        if not claudif:
                            return []
                        elif len(claudif) == 1:
                            var = claudif.pop()
                            if -var in x:
                                x.discard(-var)
                                for cl in borr:
                                    self.eliminar(cl)
                                self.insert(x)
                                return []
            nvar = set(map(abs,x))
            self.listvar.update(nvar)
            self.listclaus.append(x)
        for cl in borr:
            self.eliminars(cl)
        for cl in y:
            self.insert(cl)


    def eliminar(self,x):
        if len(x)==1:
            v = x.pop()
            self.unit.discard(v)
            return
        try:
            self.listclaus.remove(x)
        except:
            ValueError

            
    def eliminars(self,x):
        try:
            self.listclaus.remove(x)
        except:
            ValueError

            
    def anula(self):
        self.listclaus.clear()
        self.listvar.clear()
        self.unit.clear()


    
    def simplificaunit(self,v):
        if -v in self.unit:
            self.insert(set())
        if v in self.unit:
            self.unit.discard(v)
            self.listvar.discard(abs(v))
        else:
            y = []
            borr = []
            for cl in self.listclaus:
                if -v in cl:
                    borr.append(cl)
                    cl.discard(-v)
                    y.append(cl)
                elif v in cl:
                    borr.append(cl)
            for cl in borr:
                self.eliminars(cl)
            for cl in y:
                self.insert(cl)
                        
                
    def combina(self,simple):
        if self.contradict:
            return
        neg = set(map(lambda x: -x, simple.unit))
        if neg.intersection(self.unit):
            self.insert(set())
        else:
            for v in simple.unit:
                self.insert({v})
            for cl in simple.listclaus:
                self.insert(cl)