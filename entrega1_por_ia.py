from simpleai.search import SearchProblem, astar

class AresProblem(SearchProblem):
    def __init__(self, inicio, bateria, sombras, igneas, sedimentarias):
        self.sombras = set(sombras)
        # Usamos frozenset para que el estado sea inmutable y rápido en el hash de A*
        self.initial_state = (inicio, bateria, None, 0, frozenset(igneas), frozenset(sedimentarias))
        super().__init__(initial_state=self.initial_state)

    def actions(self, state):
        pos, bat, drill, carga, ign, sed = state
        acts = []
        
        # OJO: La batería NUNCA debe llegar a 0. Por ende, la batería debe ser
        # ESTRICTAMENTE MAYOR al costo de la acción para poder ejecutarla.

        # 1. Recolectar (Costo bat: 3 -> requiere bat > 3)
        if bat > 3 and carga < 2:
            if pos in ign and drill == "termico":
                acts.append(("recolectar", "ignea"))
            elif pos in sed and drill == "percusion":
                acts.append(("recolectar", "sedimentaria"))

        # 2. Depositar (Costo bat: 1 -> requiere bat > 1)
        total_mapa = len(ign) + len(sed)
        if carga > 0 and bat > 1:
            if carga == 2 or total_mapa == 0:
                acts.append(("depositar", None))

        # 3. Equipar taladro (Costo bat: 1 -> requiere bat > 1)
        if bat > 1:
            if ign and drill != "termico":
                acts.append(("equipar", "termico"))
            if sed and drill != "percusion":
                acts.append(("equipar", "percusion"))

        # 4. Movimientos (Priorizamos sobremarcha)
        # Sobremarcha (Costo bat: 4 -> requiere bat > 4)
        if bat > 4:
            for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                acts.append(("sobremarcha", (pos[0] + dr, pos[1] + dc)))
                
        # Moverse normal (Costo bat: 1 -> requiere bat > 1)
        if bat > 1:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                acts.append(("moverse", (pos[0] + dr, pos[1] + dc)))

        # 5. Recargar (No puede hacerse en sombra, la bat debe ser menor a 20)
        if bat < 20 and pos not in self.sombras:
            acts.append(("recargar", None))

        return acts

    def result(self, state, action):
        pos, bat, drill, carga, ign, sed = state
        tipo, param = action

        if tipo == "moverse":
            return (param, bat - 1, drill, carga, ign, sed)
        if tipo == "sobremarcha":
            return (param, bat - 4, drill, carga, ign, sed)
        if tipo == "equipar":
            return (pos, bat - 1, param, carga, ign, sed)
        if tipo == "recolectar":
            if param == "ignea":
                return (pos, bat - 3, drill, carga + 1, ign - {pos}, sed)
            else:
                return (pos, bat - 3, drill, carga + 1, ign, sed - {pos})
        if tipo == "depositar":
            return (pos, bat - 1, drill, 0, ign, sed)
        if tipo == "recargar":
            return (pos, min(20, bat + 10), drill, carga, ign, sed)
        return state

    def is_goal(self, state):
        # Meta: No hay muestras en el mapa ni en la bahía de carga
        return not state[4] and not state[5] and state[3] == 0

    def cost(self, state, action, next_state):
        tipo, _ = action
        if tipo == "depositar":
            return state[3]  # Toma 1 minuto por cada muestra que tenía en bodega
        return {"moverse": 1, "sobremarcha": 1, "equipar": 3, "recolectar": 2, "recargar": 4}[tipo]

    def heuristic(self, state):
        pos, bat, drill, carga, ign, sed = state
        len_ign = len(ign)
        len_sed = len(sed)
        total_restantes = len_ign + len_sed
        
        if total_restantes == 0 and carga == 0:
            return 0
            
        h = 0
        
        # 1. Costos de tiempo obligatorios (inmutables y 100% admisibles)
        h += total_restantes * 2               # Recolectar (2 min por c/u)
        h += carga + total_restantes           # Depositar (1 min por c/u en bodega y mapa)
        
        # 2. Penalizaciones de equipamiento
        if len_ign > 0 and drill != "termico":
            h += 3
        if len_sed > 0 and drill != "percusion":
            h += 3
            
        # 3. Penalización estricta por falta de batería crítica
        # Si hay muestras, para recolectar necesitamos al menos que bat >= 4. 
        # Si tenemos <= 3, estamos OBLIGADOS a recargar al menos una vez (4 min).
        if total_restantes > 0 and bat <= 3:
            h += 4
            
        # 4. Cálculo de Distancia: Algoritmo de Árbol de Expansión Mínima (MST)
        # Esto calcula la distancia mínima requerida para visitar todas las piedras.
        if total_restantes > 0:
            puntos = list(ign) + list(sed)
            unvisited = puntos[:]
            visited = [pos]
            mst_dist = 0
            
            # Algoritmo de Prim para conectar la posición del rover con todas las muestras
            while unvisited:
                min_d = float('inf')
                best_p = None
                for v in visited:
                    for u in unvisited:
                        # Distancia Manhattan
                        d = abs(v[0]-u[0]) + abs(v[1]-u[1])
                        if d < min_d:
                            min_d = d
                            best_p = u
                visited.append(best_p)
                unvisited.remove(best_p)
                mst_dist += min_d
                
            # Como podemos ir a doble velocidad con "sobremarcha" (2 celdas por min), 
            # dividimos la distancia por 2.0 para garantizar que sea admisible.
            h += mst_dist / 2.0
            
        return h

def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    problema = AresProblem(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)
    
    # Graph Search mantiene en memoria los estados visitados, vital para no ciclar
    resultado = astar(problema, graph_search=True)
    
    if resultado:
        return [accion for accion, _ in resultado.path() if accion is not None]
    return []