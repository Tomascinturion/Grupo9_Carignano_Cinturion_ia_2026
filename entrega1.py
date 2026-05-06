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
    
    #TODO: Implementar cost
    def cost(self, state, action, state2):
        pass

    #TODO: Implementar actions
    def actions(self, state):
        pass
    
    #TODO: Implementar result
    def result(self, state, action):
        pass
   
    #TODO: Implementar is_goal
    def is_goal(self, state):
        pass
    
    #TODO: Implementar heuristic
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
        zonas_sombra,
        muestras_igneas,
        muestras_sedimentarias,
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

#TODO: uv pip install --> pydot flask
