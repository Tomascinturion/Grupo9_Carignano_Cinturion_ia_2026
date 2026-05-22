import itertools

from simpleai.search import (CspProblem, backtrack, min_conflicts,
                             MOST_CONSTRAINED_VARIABLE,
                             LEAST_CONSTRAINING_VALUE,
                             HIGHEST_DEGREE_VARIABLE)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

    #casillas
    variables = [
        (fila, columna)
        for fila in range(camp_size[0])
        for columna in range(camp_size[1])
        if (fila, columna) not in craters
    ]

    #modulos posibles por celda
    dom_validos = []
    if habs == 0 and generators == 0 and labs == 0 and deposits == 0 and airlocks == 0:
        return [] #en caso de que no haya nada, el campamento es vacio, no hay restricciones de dominio
    
    dom_validos.append("emp")
    if habs > 0:
        dom_validos.append("hab")
    if generators > 0:
        dom_validos.append("gen")
    if labs > 0:
        dom_validos.append("lab")
    if deposits > 0:
        dom_validos.append("dep")
    if airlocks > 0:
        dom_validos.append("air")

    dominios = {}
    for var in variables:
        fila, columna = var
        if (fila == 0 or fila == camp_size[0] - 1) or (columna == 0 or columna == camp_size[1] - 1):            
            dominios[var] = [dom_validos[i] for i in range(len(dom_validos)) if dom_validos[i] != "hab"]
        else:
            dominios[var] = [dom_validos[i] for i in range(len(dom_validos)) if dom_validos[i] != "air"]

    restricciones = []

    #Globales
    def cantidad_habs(vars, values):
        return values.count("hab") <= habs
    restricciones.append((tuple(variables), cantidad_habs))

    def cantidad_generadores(vars, values):
        return values.count("gen") <= generators
    restricciones.append((tuple(variables), cantidad_generadores))

    def cantidad_labs(vars, values):
        return values.count("lab") <= labs
    restricciones.append((tuple(variables), cantidad_labs))

    def cantidad_depositos(vars, values):
        return values.count("dep") <= deposits
    restricciones.append((tuple(variables), cantidad_depositos))

    def cantidad_airlocks(vars, values):
        return values.count("air") <= airlocks
    restricciones.append((tuple(variables), cantidad_airlocks))

    #Especificas
    def seguridad_energetica(vars, values):
        m1, m2 = values
        if (m1 == "hab" and m2 == "gen") or (m1 == "gen" and m2 == "hab"):   
            return False
        return True

    def aislamiento_entre_generadores(vars, values):
        m1, m2 = values
        if (m1 == "gen" and m2 == "gen"):
            return False
        return True

    for var1, var2 in itertools.combinations(variables, 2):
        if abs(var1[0] - var2[0]) + abs(var1[1] - var2[1]) == 1:
            restricciones.append(((var1, var2), seguridad_energetica)) 
            restricciones.append(((var1, var2), aislamiento_entre_generadores))
    
    
    def cadena_de_suministro_cientifico(vars, values):
        centro = values[0]
        lista_adyacentes = values[1:]
        # si no es laboratorio, no importa lo que tengan los vecinos
        if centro != "lab":
            return True

        # si es laboratorio, necesita al menos un depósito vecino
        return "dep" in lista_adyacentes
    
    def ruta_de_evacuacion(vars, values):
        centro = values[0]
        lista_adyacentes = values[1:]
        # si no es habitacion, no importa lo que tengan los vecinos
        if centro != "hab":
            return True

        # si es habitacion, necesita al menos un espacio de evacuacion vecino
        return "emp" in lista_adyacentes

    for var1 in variables:
        adyacentes = []
        for var2 in variables:
            if abs(var1[0] - var2[0]) + abs(var1[1] - var2[1]) == 1:
                adyacentes.append(var2)
        restricciones.append(((var1, *adyacentes), cadena_de_suministro_cientifico))
        restricciones.append(((var1, *adyacentes), ruta_de_evacuacion))
    
    problema = CspProblem(variables, dominios, restricciones)

    solucion = backtrack(problema, variable_heuristic=MOST_CONSTRAINED_VARIABLE, value_heuristic=LEAST_CONSTRAINING_VALUE)

    if solucion is None:
        return None

    resultado = []

    for (fila, columna), tipo in solucion.items():
        if tipo != "emp":
            resultado.append((tipo, fila, columna))

    return resultado