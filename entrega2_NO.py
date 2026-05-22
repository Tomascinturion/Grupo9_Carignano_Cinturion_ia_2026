import itertools

from simpleai.search import (CspProblem, backtrack, min_conflicts,
                             MOST_CONSTRAINED_VARIABLE,
                             LEAST_CONSTRAINING_VALUE,
                             HIGHEST_DEGREE_VARIABLE)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

    #cada uno de los modulos es var
    variables = []

    for i in range(habs):
        variables.append((f"hab{i}"))
    for i in range(generators):
        variables.append((f"gen{i}"))
    for i in range(labs):
        variables.append((f"lab{i}"))
    for i in range(deposits):
        variables.append((f"dep{i}"))
    for i in range(airlocks):
        variables.append((f"air{i}"))

    if not variables:
        return []
    
    #celdas posibles para cada var, se eliminan crateres
    dominios_validos = []

    for i in range(camp_size[0]):
        for j in range(camp_size[1]):
            if (i, j) not in craters:
                dominios_validos.append((i, j))
        
    dominios = {}
    for var in variables:
        if (var.startswith("air")):
            dominios[var] = []
            for celda in dominios_validos:
                fila, columna = celda
                if (fila == 0 or fila == camp_size[0] - 1 or columna == 0 or columna == camp_size[1] - 1):
                    dominios[var].append(celda)
        
        elif (var.startswith("hab")):
            dominios[var] = []
            for celda in dominios_validos:
                fila, columna = celda
                if (fila != 0 and fila != camp_size[0] - 1 and columna != 0 and columna != camp_size[1] - 1):
                    dominios[var].append(celda)
        
        else:
            dominios[var] = dominios_validos

    restricciones = []

    #sin_superposicion
    ...

    def seguridad_energetica(vars, values):
        m1, m2 = vars
        c1, c2 = values
        if (m1.startswith("hab") and m2.startswith("gen")) or (m1.startswith("gen") and m2.startswith("hab")): #si uno es habitacion y el otro generador,   
            if abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1: #checkeo adyacencia
                return False        
        return True

    def aislamiento_entre_generadores(vars, values):
        m1, m2 = vars
        c1, c2 = values
        if (m1.startswith("gen") and m2.startswith("gen")): #si ambos son generadores, 
            if abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1: #checkeo adyacencia
                return False
        return True

    for var1, var2 in itertools.combinations(variables, 2):
        restricciones.append(((var1, var2), seguridad_energetica)) 
        restricciones.append(((var1, var2), aislamiento_entre_generadores)) 
    
    def cadena_de_suministro_cientifico(vars, values):
        m_centro = vars[0]
        m_adyacentes = vars[1:]
        
        # si no es laboratorio, no importa lo que tengan los vecinos
        if not m_centro.startswith("lab"):
            return True

        # si es laboratorio, necesita al menos un depósito vecino
        return "dep" in m_adyacentes
    
    def ruta_de_evacuacion(vars, values):
        m_centro = vars[0]
        m_adyacentes = vars[1:]
        
        # si no es habitacion, no importa lo que tengan los vecinos
        if not m_centro.startswith("hab"):
            return True

        # si es habitacion, necesita al menos un espacio de evacuacion vecino
        return "emp" in m_adyacentes

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
        resultado.append((tipo, fila, columna))

    return resultado