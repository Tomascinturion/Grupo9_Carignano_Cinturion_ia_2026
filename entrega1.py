from simpleai.search import (
    SearchProblem,
    astar,
)
from simpleai.search.viewers import BaseViewer, WebViewer

class RoverProblem(SearchProblem):

    def __init__(self, initial_state, zonas_sombra):
        super().__init__(initial_state)
        self.zonas_sombra = zonas_sombra

    def cost(self, state, action, state2):

        costo = 0
        muestras_almacenadas = state[5]
        accion, _ = action

        if(accion == "recargar"):
            costo = 4
        elif(accion == "moverse"):
            costo = 1 
        elif(accion == "equipar"):
            costo = 3
        elif(accion == "depositar"):
            return muestras_almacenadas
        elif(accion == "recolectar"):
            costo = 2
        elif(accion == "sobremarcha"):
            costo = 1

        return costo

    def actions(self, state):
        
        lista_acciones = []
        posicion_rover, bateria, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas = state
        rover_x, rover_y = posicion_rover
        cantidad_muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

        if bateria < 20 and posicion_rover not in self.zonas_sombra:
            lista_acciones.append(("recargar", None))

        if (bateria > 1):
            
            #Moverse
            posibles_movimientos = [(1,0), (-1,0), (0,1), (0,-1)]
        
            for mov_x, mov_y in posibles_movimientos:
                nueva_posicion = (rover_x + mov_x, rover_y + mov_y)
                lista_acciones.append(("moverse", nueva_posicion))

            #Equipar taladro
            if posicion_rover in muestras_igneas and taladro_equipado != "termico": #Solo equipa taladro sobre muestras correctas
                lista_acciones.append(("equipar", "termico"))

            if posicion_rover in muestras_sedimentarias and taladro_equipado != "percusion":
                lista_acciones.append(("equipar", "percusion"))

            #Depositar cápsula con muestras
            if(muestras_almacenadas == 2 or (cantidad_muestras_restantes == 0 and muestras_almacenadas == 1)):
                lista_acciones.append(("depositar", None))
        
        if (bateria > 3 and muestras_almacenadas < 2):
            #Perforar y recolectar
            if (posicion_rover in muestras_igneas and taladro_equipado == "termico"):
                lista_acciones.append(("recolectar", "ignea"))		
            if (posicion_rover in muestras_sedimentarias and taladro_equipado == "percusion"):
                lista_acciones.append(("recolectar", "sedimentaria"))

        if (bateria > 4):
            #Sobremarcha (overdrive)
            posibles_overdrive = [(2,0), (-2,0), (0,2), (0,-2)]
            for mov_x, mov_y in posibles_overdrive:
                nueva_posicion = (rover_x + mov_x, rover_y + mov_y)
                lista_acciones.append(("sobremarcha", nueva_posicion))
        
        return tuple(lista_acciones)

    def result(self, state, action):

        posicion_rover, bateria, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas = state
        accion, parametro = action

        if(accion == "recargar"):
            bateria += 10
            if(bateria > 20):
                bateria = 20
        
        elif(accion == "moverse"):
            bateria -= 1
            posicion_rover = parametro
        
        elif(accion == "equipar"):
            bateria -= 1
            taladro_equipado = parametro
        
        elif(accion == "depositar"):
            bateria -= 1
            muestras_almacenadas = 0
        
        elif(accion == "recolectar"):
            bateria -= 3
            muestras_almacenadas += 1
            if(parametro == "ignea"):
                muestras_igneas = list(muestras_igneas)
                muestras_igneas.remove(posicion_rover)
                muestras_igneas = tuple((muestras_igneas))
            else:
                muestras_sedimentarias = list(muestras_sedimentarias)
                muestras_sedimentarias.remove(posicion_rover)
                muestras_sedimentarias = tuple((muestras_sedimentarias))
        
        elif(accion == "sobremarcha"):
            bateria -= 4
            posicion_rover = parametro
        
        return (posicion_rover, bateria, muestras_igneas, muestras_sedimentarias, taladro_equipado, muestras_almacenadas)
   
    def is_goal(self, state):

        _, bateria, muestras_igneas, muestras_sedimentarias, _, muestras_almacenadas = state
        cantidad_muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

        return cantidad_muestras_restantes == 0 and muestras_almacenadas == 0

    def heuristic(self, state):
        posicion, _, igneas, sedimentarias, _, _ = state
        x, y = posicion

        muestras = igneas + sedimentarias
        restantes = len(muestras)

        if restantes == 0:
            return 0

        # distancia a la muestra más cercana
        dist_min = min(abs(x-mx) + abs(y-my) for mx, my in muestras)

        # costo mínimo de movimiento usando sobremarcha
        movimiento_min = (dist_min + 1) // 2

        # si hay solo una muestra
        if restantes == 1:
            return movimiento_min + 3  # moverse, recolectar + depositar

        # si hay varias muestras
        xd = [m[0] for m in muestras]
        yd = [m[1] for m in muestras]

        dispersion_muestras = (max(xd) - min(xd)) + (max(yd) - min(yd))

        costo_recolectar = 2 * restantes
        costo_depositar = restantes

        return movimiento_min + dispersion_muestras + costo_recolectar + costo_depositar
    
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
        tuple(muestras_igneas),
        tuple(muestras_sedimentarias),
        "ninguno", #Taladro
        0, #Muestras almacenadas
    )

    problema = RoverProblem(estado_inicial, tuple(zonas_sombra))
    #viewer = WebViewer() # BaseViewer() para consola. IMPORTANTE: DESACTIVAR AL ENTREGAR
    resultado = astar(problema, graph_search=True) #, viewer=viewer)
    acciones = [accion for accion, estado in resultado.path() if accion is not None] #(problema.actions(estado_inicial))
    
    return acciones

if __name__ == "__main__":
    # Formato coordenadas: (fila, columna)
    acciones = planear_rover()

    print(acciones)