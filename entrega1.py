from simpleai.search import (
    SearchProblem,
    breadth_first,
    depth_first,
    limited_depth_first,
    uniform_cost,
    iterative_limited_depth_first,
    greedy,
    astar,
)
from simpleai.search.viewers import BaseViewer, WebViewer

class RoverProblem(SearchProblem):
    
    def cost(self, state, action, state2):

        costo = 0
        accion, _ = action

        if(accion == "recargar"):
            costo = 4
        elif(accion == "moverse"):
            costo = 1 
        elif(accion == "equipar"):
            costo = 3
        elif(accion == "depositar"):
            if(state[6] == 2):
                costo += 1
            costo += 1
        elif(accion == "recolectar"):
            costo = 2
        elif(accion == "sobremarcha"):
            costo = 1

        return costo

    def actions(self, state):
        
        lista_acciones = []
        posicion_rover, bateria, zonas_sombra, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas = state
        rover_x, rover_y = posicion_rover
        cantidad_muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

        if (bateria > 0 and bateria < 20):
            #Desplegar paneles solares
            if posicion_rover not in zonas_sombra:
                lista_acciones.append(("recargar", None))

        if (bateria > 1):
            #Moverse
            posibles_movimientos = [(1,0), (-1,0), (0,1), (0,-1)]
            
            for mov_x, mov_y in posibles_movimientos:
                nueva_posicion = (rover_x + mov_x, rover_y + mov_y)
                lista_acciones.append(("moverse", nueva_posicion))

            #Equipar taladro
            if (taladro_equipado == "termico"):
                lista_acciones.append(("equipar", "percusion"))
            elif (taladro_equipado == "percusion"):
                lista_acciones.append(("equipar", "termico"))
            else:
                lista_acciones.append(("equipar", "termico"))
                lista_acciones.append(("equipar", "percusion"))

            #Depositar cápsula con muestras
            if(muestras_almacenadas == 2 or (cantidad_muestras_restantes == 0 and muestras_almacenadas == 1)):
                lista_acciones.append(("depositar", None))
        
        if (bateria > 3):
            #Perforar y recolectar
            if (muestras_almacenadas < 2 and cantidad_muestras_restantes > 0):
                if (taladro_equipado == "termico"):
                    for muestra in muestras_igneas:
                        if(muestra == posicion_rover):
                            lista_acciones.append(("recolectar", "ignea"))		
                elif (taladro_equipado == "percusion"):
                    for muestra in muestras_sedimentarias:
                        if(muestra == posicion_rover):
                            lista_acciones.append(("recolectar", "sedimentaria"))
        
        if (bateria > 4):
            #Sobremarcha (overdrive)
            posibles_overdrive = [(2,0), (-2,0), (0,2), (0,-2)]
            for mov_x, mov_y in posibles_overdrive:
                nueva_posicion = (rover_x + mov_x, rover_y + mov_y)
                lista_acciones.append(("sobremarcha", nueva_posicion))
        
        return tuple(lista_acciones)

    def result(self, state, action):

        nuevo_estado = list(state)
        accion, parametro = action

        if(accion == "recargar"):
            nuevo_estado[1] += 10
            if(nuevo_estado[1] > 20):
                nuevo_estado[1] = 20
        elif(accion == "moverse"):
            nuevo_estado[1] -= 1
            nuevo_estado[0] = parametro
        elif(accion == "equipar"):
            nuevo_estado[1] -= 1
            nuevo_estado[5] = parametro
        elif(accion == "depositar"):
            nuevo_estado[1] -= 1
            nuevo_estado[6] = 0
        elif(accion == "recolectar"):
            nuevo_estado[1] -= 3
            nuevo_estado[6] += 1
            if parametro == "ignea":
                nuevo_estado[3] = tuple(p for p in nuevo_estado[3] if p != nuevo_estado[0])
            else:
                nuevo_estado[4] = tuple(p for p in nuevo_estado[4] if p != nuevo_estado[0])
            # if(parametro == "ignea"):
            #     nuevo_estado[3].remove(nuevo_estado[0])
            # else:
            #     nuevo_estado[4].remove(nuevo_estado[0])
        elif(accion == "sobremarcha"):
            nuevo_estado[1] -= 4
            nuevo_estado[0] = parametro

        return tuple(nuevo_estado)
   
    #Implementar is_goal
    def is_goal(self, state):

        _, bateria, _, muestras_igneas, muestras_sedimentarias, _, muestras_almacenadas = state
        cantidad_muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

        return cantidad_muestras_restantes == 0 and muestras_almacenadas == 0 and bateria > 0
    
    #Implementar heuristic
    def heuristic(self, state):

        valor = 0
        posicion_rover, bateria, zonas_sombra, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas = state

        #(posicion_rover -  pos_piedra_mas_lejana)
        # muestras_restantes = muestras_igneas + muestras_sedimentarias
        # diferencia_muestras = []
        # for muestra in muestras_restantes:
        #     distancia = abs(posicion_rover[0] - muestra[0]) + abs(posicion_rover[1] - muestra[1])
        #     diferencia_muestras.append(distancia)
        
        # valor += max(diferencia_muestras)
        
        cantidad_muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)
        valor += (cantidad_muestras_restantes - muestras_almacenadas)

        if(taladro_equipado is None):
            valor += 1

        return valor

def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    muestras_igneas,
    muestras_sedimentarias,
):
    estado_inicial = (
        rover_inicio,
        bateria_inicial,
        tuple(zonas_sombra),
        tuple(muestras_igneas),
        tuple(muestras_sedimentarias),
        None, #Taladro
        0, #Muestras almacenadas
    )

    problema = RoverProblem(estado_inicial)
    #viewer = WebViewer() # BaseViewer() para consola. IMPORTANTE: DESACTIVAR AL ENTREGAR
    resultado = astar(problema)
    acciones = [accion for accion, estado in resultado.path()] #(problema.actions(estado_inicial))
    
    return acciones


if __name__ == "__main__":
    # Formato coordenadas: (fila, columna)
    acciones = planear_rover(
        rover_inicio=(0, 0),
        bateria_inicial=20,
        zonas_sombra=[(0, 1), (0, 2)],
        muestras_igneas=[(1, 1), (1, 2)],
        muestras_sedimentarias=[(2, 3)],
    )

    print(acciones)