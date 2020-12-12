import math
import sys
import vector as v
import Draw3dSolution as draw3d
import Draw2dSolution as draw2d
import ComputeWall as wall
import ComputeNetlistFaces as nlf

# Info:
# Sometimes the result looks wrong because of the negative clearance (a laser will remove some material)
# Sometimes the result looks wrong because of the scaling of the 3d plot
# Please help me to fix bugs!
# Points: List of coordinates
# Netlist: List of connections between Coordinates (list of index)



def computeResult(points, netlistIn, notUsedFaces, materialStrength, clearance, connectionType=wall.ctWallSize):
    netlist, faces = nlf.computeNetlistFaces(netlistIn,notUsedFaces)
    coords = [wall.computeWall(faces, points, wallNr, materialStrength, clearance, connectionType) for wallNr in range(len(faces))]
    draw2d.draw2d(coords)
    draw3d.draw3d(points, faces, coords, materialStrength)


points0=v.mulToAll([60,60,60],[[0,2,0],[0,0,0],[2,0,0],[0.5,0.5,0],[0,2,2],[0,0,2],[2,0,2],[0.5,0.5,2]]) # 1 inner Edge #TODO: Not correct
points0=v.mulToAll([80,80,80],[[0,1,0],[0,0,0],[1,0,0],[0.4,0.4,0],[0,1,1],[0,0,1],[1,0,1],[0.4,0.4,1]]) # 1 inner Edge #TODO: Not correct
points0=v.mulToAll([60,60,60],[[1,1,0.3],[0,0,0],[3,0,0],[2,1,0.3],[1,1,0.7],[0,0,1],[3,0,1],[2,1,0.7]]) # truncated pyramid
points0=v.mulToAll([60,60,60],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1]]) # Cube
points0=v.mulToAll([60,60,60],[[1,1,0.3],[0,0,0],[3,0,0],[2,1,0.3],[1,1,1.7],[0,0,1],[3,0,1],[2,1,1.7]]) # 4 trapezial sides
points0=v.mulToAll([60,60,60],[[0,1,0],[0,0,0],[1.5,0,0],[1,1,0],[0,1,1],[0,0,1],[1.5,0,1],[1,1,1]]) # 1 non rectangular edge
points0=v.mulToAll([60,60,60],[[0.5,1,0],[0,0,0],[1.5,0,0],[1,1,0],[0.5,1,1],[0,0,1],[1.5,0,1],[1,1,1]]) # 2 trapezial parallel sides

netlist0 = [
    [1,3,4],    # 0
    [2,5],      # 1
    [3,6],      # 2
    [7],        # 3
    [5,7],      # 4
    [6],        # 5
    [7],        # 6
    [],         #
]

points0=v.mulToAll([60,60,60],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1],[0,1,2],[0,0,2],[1,0,2],[1,1,2]]) # Cube
points0=v.mulToAll([35,35,35],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1],[-0.5,1.5,2],[-0.5,-0.5,2],[1.5,-0.5,2],[1.5,1.5,2]]) # Cube
netlist0 = [
    [1,3,4],    # 0
    [2,5],      # 1
    [3,6],      # 2
    [7],        # 3
    [5,7,8],      # 4
    [6,9],        # 5
    [7,10],        # 6
    [11],         # 7
    [9,11],         # 8
    [10],         # 9
    [11],         # 10
    [],         # 11
]

#Pyramide
points0 = v.mulToAll([20,20,20],[[1,1,0],[-1,1,0],[-1,-1,0],[1,-1,0],[0,0,1]])
netlist0 = [[1,3,4],[2,4],[3,4],[4],[]]


# Air Window Outlet
points0=v.mulToAll([150/2,150/2,150],[
    [-1,-1,0],[1,-1,0],
    [-1,1,1],[1,1,1],[1,-1,1],[-1,-1,1],])+\
v.addToAll([0,0,150*2],v.mulToAll([190/2,34/2,30],[
    [-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0],]))+\
v.addToAll([0,0,150*2+30],v.mulToAll([190/2,30/2,290],[
    [-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0],]))+\
v.addToAll([0,0,150*2+30+290],v.mulToAll([190/2,30/2,230],[
    [-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0],]))+\
v.addToAll([0,0,150*2+30+290+230],v.mulToAll([190/2,30/2,30],[
    [-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0],
    [-1,1,1],[1,1,1],[1,-1,2],[-1,-1,2],
#    [1,0,3],[-1,0,3],
#    [1,1,4],[-1,1,4],
    ]))
#points = v.mulToAll([1/8,1/5,1/3],points)
netlist0 = [[1,2,5],[3,4]] + \
           [v.add(v.scal([1, 1, 1], 2 + iz * 4), [i, (i + 3) % 4, i + 4]) for iz in range(5) for i in range(4)] + \
           [[23,25],[24],[25],[]]
#    [[23,25,27,29],[24,26,28],[26,25],[27],
#     [27,28],[29],
#     [29],[]]
#Sum Edges 59



#Three Edge Test TODO: Does not work yet. Buggy minimumSpaceLeft/Right, Maybe wrong calculated angles or wrong chosen points
points0 = v.mulToAll([60,60,60],[[-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0],[-1,0,1],[1,0,1],[-1,1,3],[1,1,3]])
netlist0 = [[1,3,4,6],[2,5,7],[3,5],[4],[5,6],[7],[7],[]]


points = v.mulToAll([20,20,30],[[1,1,0],[-1,1,0],[-1,-1,0],[1,-1,0],[0,0,1]])
netlist = [[1,3,4],[2,4],[3,4],[4],[]]

notUsedFaces=[]
materialStrength = 4
clearance = -0.14
# Points: List of coordinates
# Netlist: List of connections between Coordinates (list of index)
computeResult(points,netlist,notUsedFaces,materialStrength,clearance,wall.ctWallSize)



#TODO: Inner Edges
#Buggy minimumSpaceLeft/Right, Maybe wrong calculated angles or wrong chosen points, Problem propably in connectionLineByTypeReductionFingerLength
#YPR coordinates for 3d display wrong
#Size of plates wrong
#TODO: Features
#Different amount of corners edges
#Inner Planes defined by point and direction of plane