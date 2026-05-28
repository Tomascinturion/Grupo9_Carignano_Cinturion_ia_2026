import itertools

from simpleai.search import (CspProblem, backtrack, min_conflicts,
                             MOST_CONSTRAINED_VARIABLE,
                             LEAST_CONSTRAINING_VALUE,
                             HIGHEST_DEGREE_VARIABLE)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

    # VARIABLES: cada uno de los modulos es var, se distinguen por su tipo y numero
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
    
    # DOMINIOS: cada var puede tomar como valor una celda del campamento, pero no pueden ser crateres
    dominios_validos = []

    for fila in range(camp_size[0]):
        for columna in range(camp_size[1]):
            if (fila, columna) not in craters:
                dominios_validos.append((fila, columna))
        
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

    # RESTRICCIONES
    restricciones = []

    def sin_superposicion(vars, values):
        return values[0] != values[1]
    
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
        restricciones.append(((var1, var2), sin_superposicion))

    def cadena_de_suministro_cientifico(vars, values):

        pos_lab = values[0]
        pos_depositos = values[1:]

        for dep in pos_depositos:
            #checkeo adyacencia entre laboratorio y deposito
            if abs(pos_lab[0] - dep[0]) + abs(pos_lab[1] - dep[1]) == 1:
                return True

        return False
    
    depositos_vars = [v for v in variables if v.startswith("dep")]
    for lab in variables:
        if lab.startswith("lab"):
            restricciones.append(((lab, *depositos_vars),cadena_de_suministro_cientifico))

    def ruta_de_evacuacion(vars, values):

        pos_hab = values[0]
        pos_otros_modulos = values[1:]

        adyacencias = [
            (pos_hab[0] + 1, pos_hab[1]),
            (pos_hab[0] - 1, pos_hab[1]),
            (pos_hab[0], pos_hab[1] + 1),
            (pos_hab[0], pos_hab[1] - 1),
        ]

        for adyacente in adyacencias:
            # no puede ser cráter
            if adyacente not in dominios_validos:
                continue
            # si nadie ocupa la celda
            if adyacente not in pos_otros_modulos:
                return True

        return False

    for hab in variables:
        if hab.startswith("hab"):
            otras_modulos = [v for v in variables if v != hab]
            restricciones.append(((hab, *otras_modulos), ruta_de_evacuacion))
    
    # RESOLUCION
    problema = CspProblem(variables, dominios, restricciones)
    solucion = backtrack(problema, variable_heuristic=MOST_CONSTRAINED_VARIABLE, value_heuristic=LEAST_CONSTRAINING_VALUE)

    if solucion is None:
        return None
    
    def tipo_base(tipo):
        if tipo.startswith("hab"):
            return "hab"
        if tipo.startswith("gen"):
            return "gen"
        if tipo.startswith("lab"):
            return "lab"
        if tipo.startswith("dep"):
            return "dep"
        if tipo.startswith("air"):
            return "air"

    resultado = []
    for tipo, (fila, columna) in solucion.items():
        resultado.append((tipo_base(tipo), fila, columna))
    return resultado