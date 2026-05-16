import itertools

from simpleai.search import (CspProblem, backtrack, min_conflicts,
                             MOST_CONSTRAINED_VARIABLE,
                             LEAST_CONSTRAINING_VALUE,
                             HIGHEST_DEGREE_VARIABLE)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    ...
    variables = (
        #casillas
    )
    for i in range(camp_size[0]):
        for j in range(camp_size[1]):
            if (i, j) not in craters:
                variables += ((i,j),)
    dominios = {
        #modulos por celda
    }
    for var in variables:
        dominios[var] = ["hab", "gen", "lab", "dep", "air", "emp"]

    restricciones = []
    #seguir restricciones
    def seguridad_energetica(vars, values):
        if generators in values and habs in values:
            pass
        ...