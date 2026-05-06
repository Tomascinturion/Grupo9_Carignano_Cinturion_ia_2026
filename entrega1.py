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
    
    #Implementar cost
    def cost(self, state, action, state2):
        pass

    def actions(self, state):
        
        lista_acciones = []
        estado_actual = list(state)
        muestras_restantes = len(estado_actual[3]) + len(estado_actual[4])
        posicion_actual = estado_actual[0]

        if (estado_actual[1] > 0 and estado_actual[1] < 20):
            #Desplegar paneles solares
            habilitado = 0
            for zonas_sombra in estado_actual[2]:
                if(zonas_sombra == posicion_actual):
                    habilitado += 1
            if(habilitado == 0):
                lista_acciones.append(("recargar", None))

        if (estado_actual[1] > 1):
            #Moverse
            lista_acciones.append(("moverse", (posicion_actual[0] + 1, posicion_actual[1])))
            lista_acciones.append(("moverse", (posicion_actual[0] - 1, posicion_actual[1])))
            lista_acciones.append(("moverse", (posicion_actual[0], posicion_actual[1] + 1)))
            lista_acciones.append(("moverse", (posicion_actual[0], posicion_actual[1] - 1)))

            #Equipar taladro
            if (estado_actual[5] == "termico"):
                lista_acciones.append(("equipar", "percusion"))
            elif (estado_actual[5] == "percusion"):
                lista_acciones.append(("equipar", "termico"))
            else:
                lista_acciones.append(("equipar", "termico"))
                lista_acciones.append(("equipar", "percusion"))

            #Depositar cápsula con muestras
            if(estado_actual[6] == 2 or (muestras_restantes == 0 and estado_actual[6] == 1)):
                lista_acciones.append(("depositar", None))
        
        if (estado_actual[1] > 3):
            #Perforar y recolectar
            if (estado_actual[6] < 2 and muestras_restantes > 0):
                if (estado_actual[5] == "termico"):
                    for posicion_muestra in estado_actual[3]:
                        if(posicion_muestra == posicion_actual):
                            lista_acciones.append(("recolectar", "ignea"))		
                elif (estado_actual[5] == "percusion"):
                    for posicion_muestra in estado_actual[4]:
                        if(posicion_muestra == posicion_actual):
                            lista_acciones.append(("recolectar", "sedimentaria"))
        
        if (estado_actual[1] > 4):
            #Sobremarcha (overdrive)
            lista_acciones.append(("sobremarcha", (posicion_actual[0] + 2, posicion_actual[1])))
            lista_acciones.append(("sobremarcha", (posicion_actual[0] - 2, posicion_actual[1])))
            lista_acciones.append(("sobremarcha", (posicion_actual[0], posicion_actual[1] + 2)))
            lista_acciones.append(("sobremarcha", (posicion_actual[0], posicion_actual[1] - 2)))
        
        return tuple(lista_acciones)

    #Implementar result  ACORDARSE DE ELIMINAR PIEDRA PICADA - BAJAR BATERIA O SUBIR - AUMENTAR O DISMINUIR CARGA
    def result(self, state, action):
        pass
   
    #Implementar is_goal
    def is_goal(self, state):
        pass
    
    #Implementar heuristic
    def heuristic(self, state):
        pass

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
        0, #Muestras recogidas
    )

    problema = RoverProblem(estado_inicial)

    resultado = astar(problema)

    acciones = [accion for accion, estado in resultado.path()]
    
    return acciones


# Formato coordenadas: (fila, columna)
acciones = planear_rover(
    rover_inicio=(0, 0),
    bateria_inicial=20,
    zonas_sombra=[(0, 1), (0, 2)],
    muestras_igneas=[(1, 1), (1, 2)],
    muestras_sedimentarias=[(2, 3)],
)

print(acciones)