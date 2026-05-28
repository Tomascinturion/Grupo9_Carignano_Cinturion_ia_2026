from simpleai.search import CspProblem, backtrack, MOST_CONSTRAINED_VARIABLE
from itertools import combinations

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size
    craters_set = set(craters)
    
    # 1. Variables
    variables = []
    variables.extend([f"hab_{i}" for i in range(habs)])
    variables.extend([f"gen_{i}" for i in range(generators)])
    variables.extend([f"lab_{i}" for i in range(labs)])
    variables.extend([f"dep_{i}" for i in range(deposits)])
    variables.extend([f"air_{i}" for i in range(airlocks)])
    
    # Si no hay módulos a ubicar, devolvemos la lista vacía inmediatamente
    if not variables:
        return []

    # 2. Dominios (Optimizados)
    domains = {}
    for var in variables:
        allowed_cells = []
        for r in range(rows):
            for c in range(cols):
                pos = (r, c)
                
                # Restricción 2: Sin cráteres
                if pos in craters_set:
                    continue
                    
                is_border = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)
                
                # Restricción 3: Esclusas en el borde
                if var.startswith("air") and not is_border:
                    continue
                    
                # Restricción 4: Habitacionales al interior
                if var.startswith("hab") and is_border:
                    continue
                    
                allowed_cells.append(pos)
                
        # Si a alguna variable le quedó el dominio vacío, es irresoluble
        if not allowed_cells:
            return None
            
        domains[var] = allowed_cells

    # Agrupamos variables por tipo para facilitar las restricciones
    habs_list = [v for v in variables if v.startswith("hab")]
    gens_list = [v for v in variables if v.startswith("gen")]
    labs_list = [v for v in variables if v.startswith("lab")]
    deps_list = [v for v in variables if v.startswith("dep")]
    airs_list = [v for v in variables if v.startswith("air")]

    # 3. Restricciones
    constraints = []

    # Restricción 1: Sin superposición (todas las variables deben tener posiciones distintas)
    def diff_pos(vars, vals):
        return vals[0] != vals[1]

    for v1, v2 in combinations(variables, 2):
        constraints.append(((v1, v2), diff_pos))

    # Optimización: Ruptura de simetría para módulos idénticos
    def symmetry_break(vars, vals):
        return vals[0] < vals[1]
        
    for mod_list in [habs_list, gens_list, labs_list, deps_list, airs_list]:
        for i in range(len(mod_list) - 1):
            constraints.append(((mod_list[i], mod_list[i+1]), symmetry_break))

    # Helper para adyacencia
    def is_adjacent(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

    def not_adjacent(vars, vals):
        return not is_adjacent(vals[0], vals[1])

    # Restricción 5: Generador no puede ser adyacente a habitacional
    for g in gens_list:
        for h in habs_list:
            constraints.append(((g, h), not_adjacent))

    # Restricción 6: Dos generadores no pueden ser adyacentes entre sí
    for g1, g2 in combinations(gens_list, 2):
        constraints.append(((g1, g2), not_adjacent))

    # Restricción 7: Cada laboratorio adyacente a al menos un depósito
    if labs_list and not deps_list:
        return None # Imposible ubicar un lab sin depósitos

    def lab_dep_adj(vars, vals):
        lab_pos = vals[0]
        deps_pos = vals[1:]
        # Verifica si el lab está adyacente a alguno de los depósitos provistos
        for d in deps_pos:
            if is_adjacent(lab_pos, d):
                return True
        return False

    for l in labs_list:
        constraints.append((tuple([l] + deps_list), lab_dep_adj))

    # Restricción 8: Ruta de evacuación (habitacional debe tener al menos una celda libre)
    def hab_evac(vars, vals):
        hab_pos = vals[0]
        other_modules_pos = set(vals[1:])
        
        # Revisamos vecinos ortogonales
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = hab_pos[0] + dr, hab_pos[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                # Si el vecino está dentro del mapa, no es cráter, y no hay otro módulo ahí
                if (nr, nc) not in craters_set and (nr, nc) not in other_modules_pos:
                    return True
        return False

    for h in habs_list:
        others = [v for v in variables if v != h]
        constraints.append((tuple([h] + others), hab_evac))

    # 4. Configurar el problema y ejecutar el solver
    problem = CspProblem(variables, domains, constraints)
    
    # MOST_CONSTRAINED_VARIABLE ayuda enormemente a arrancar por las variables más complicadas
    result = backtrack(problem, variable_heuristic=MOST_CONSTRAINED_VARIABLE)

    # 5. Formatear la salida requerida
    if result is None:
        return None
        
    formatted_result = []
    for var, pos in result.items():
        tipo = var.split('_')[0]
        formatted_result.append((tipo, pos[0], pos[1]))
        
    return formatted_result