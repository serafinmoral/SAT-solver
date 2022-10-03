# -*- coding: utf-8 -*-
import os
import math
from pickle import FALSE
from tablaClausulas  import *
from time import * 


class arbol:
    def __init__(self):
        self.var = 0
        self.value = True
        self.hijos = [None,None]

    def creadesdetabla(self, t):
        r = t.minimiza(con = nodoTabla([]))
        if len(r.listavar) ==0:
            if r.trivial():
                self.value = True
            else:
                self.value = False
            self.var = 0
        else:
            v = r.minentropia()
            self.var = v
            t0 = t.reduce([-v], inplace = False)
            t1 = t.reduce([v], inplace = False)
            l0 = arbol()
            l1 = arbol()
            l0.creadesdetabla(t0)
            l1.creadesdetabla(t1)
            self.hijos[0] = l0
            self.hijos[1] = l1 
        return


    def imprime(self, str = ''):

            print (str +"variable ",self.var)
            if self.var==0:
                print(str + "valor " , self.value)
            else:
                print(str +"hijo 1")
                self.hijos[0].imprime(str  + '   ')
                print(str +"hijo 2")
                self.hijos[1].imprime(str  + '   ') 