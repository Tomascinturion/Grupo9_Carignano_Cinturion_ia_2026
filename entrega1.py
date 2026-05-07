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
        
        #estado_actual = list(state) VERIFICAR SI ANDA - SI SI BORRAR - SI NO USAR estado_actual en linea de abajo
        posicion_rover, bateria, zonas_sombra, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas = state
        
        muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

        if (bateria > 0 and bateria < 20):
            #Desplegar paneles solares
            habilitado = 0
            for zona in zonas_sombra:
                if(zona == posicion_rover):
                    habilitado += 1
            if(habilitado == 0):
                lista_acciones.append(("recargar", None))

        if (bateria > 1):
            #Moverse
            lista_acciones.append(("moverse", (posicion_rover[0] + 1, posicion_rover[1])))
            lista_acciones.append(("moverse", (posicion_rover[0] - 1, posicion_rover[1])))
            lista_acciones.append(("moverse", (posicion_rover[0], posicion_rover[1] + 1)))
            lista_acciones.append(("moverse", (posicion_rover[0], posicion_rover[1] - 1)))

            #Equipar taladro
            if (taladro_equipado == "termico"):
                lista_acciones.append(("equipar", "percusion"))
            elif (taladro_equipado == "percusion"):
                lista_acciones.append(("equipar", "termico"))
            else:
                lista_acciones.append(("equipar", "termico"))
                lista_acciones.append(("equipar", "percusion"))

            #Depositar cápsula con muestras
            if(muestras_almacenadas == 2 or (muestras_restantes == 0 and muestras_almacenadas == 1)):
                lista_acciones.append(("depositar", None))
        
        if (bateria > 3):
            #Perforar y recolectar
            if (muestras_almacenadas < 2 and muestras_restantes > 0):
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
            lista_acciones.append(("sobremarcha", (posicion_rover[0] + 2, posicion_rover[1])))
            lista_acciones.append(("sobremarcha", (posicion_rover[0] - 2, posicion_rover[1])))
            lista_acciones.append(("sobremarcha", (posicion_rover[0], posicion_rover[1] + 2)))
            lista_acciones.append(("sobremarcha", (posicion_rover[0], posicion_rover[1] - 2)))
        
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
        0, #Muestras almacenadas
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
