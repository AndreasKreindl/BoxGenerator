import svgwrite
import math
import numpy as np
import matplotlib.pyplot as plt
import sys

size=[300,200]
lengthUnit="mm"
filename="box.svg"

def rotate2d(xyList, angle, center=[0, 0]):
    return [[math.cos(angle) * (xy[0]-center[0]) - math.sin(angle) * (xy[1]-center[1]) + center[0],
             math.sin(angle) * (xy[0]-center[0]) + math.cos(angle) * (xy[1]-center[1]) + center[1]
             ] for xy in xyList]

def addCords(c0,c1):
    return [c0[0]+c1[0],c0[1]+c1[1]]

dwg = svgwrite.Drawing(filename=filename,
             size=("{}{}".format(size[0],lengthUnit), "{}{}".format(size[1],lengthUnit)),
             viewBox=("0 0 {} {}".format(size[0], size[1])))

def export_svg_svgwrite(path, line_width=0.2, engrave=1):
    if(len(path) > 1):
        path = [[x[0],size[1]-x[1]] for x in path]
        str_list = []
        str_list.append("M {},{}".format(path[0][0],path[0][1]))
        for e in path[1:]:
            str_list.append(" L {},{}".format(e[0],e[1]))
        s = ''.join(str_list)
        dwg.add(dwg.path(s).stroke(color="rgb(0,0,255)" if engrave else "rgb(255,0,0)",width=line_width).fill("none"))
#export_svg_svgwrite(path=[[0,0],[0,10],[10,10],[10,0],[0,0]],engrave=0)

def addToAll(elem,list):
    return [[x[i]+elem[i] for i in range(len(elem))] for x in list]
def mulToAll(elem,list):
    return [[x[i]*elem[i] for i in range(len(elem))] for x in list]
def vlMax(l):
    return [max([v[i] for v in l]) for i in range(len(l[0]))]
def vlMin(l):
    return [min([v[i] for v in l]) for i in range(len(l[0]))]
def vlMinMax(l):
    cMax = vlMax(l)
    cMin = vlMin(l)
    return cMin, cMax
def vlPosSize(l):
    cMax, cMin = vlMinMax(l)
    return cMin, vSub(cMax,cMin)
def vScal(v,s):
    return [i*s for i in v]
def vLen(v):
    return math.sqrt(sum([i**2 for i in v]))
def vDot(v0,v1):
    return sum([i0*i1 for i0,i1 in zip(v0,v1)])
def vCross(a, b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]
def vSub(v0,v1):
    return [i0-i1 for i0,i1 in zip(v0,v1)]
def vAdd(v0,v1):
    return [i0+i1 for i0,i1 in zip(v0,v1)]
def vAngle(v0,v1):
    if(vLen(v0)==0 or vLen(v1)==0):
        return 0
    return math.acos(min(max(vDot(v0,v1)/vLen(v0)/vLen(v1),-1),1))
def vPntAngle(p0,p1,p2):#p1 is the middle one
    return vAngle(vSub(p0,p1),vSub(p2,p1))
def vAngleSgn(v0,v1,norm):
    if(vLen(v0)==0 or vLen(v1)==0):
        return 0
    return vAngle(v0,v1) * (1 if vDot(vCross(v0,v1),norm) > 0 else -1) # TODO: Check for inner edges
def vPntAngleSgn(p0,p1,p2,norm):#p1 is the middle one
    return vAngleSgn(vSub(p0,p1),vSub(p2,p1),norm)
def vCenter(pnts):
    return [sum([p[i] for p in pnts]) / len(pnts) for i in range(len(pnts[0]))]
def rotate3dV(list, angle, vRot, cent=[0, 0, 0]):
    return [vAdd(vAdd(vAdd(
        vScal(vSub(v,cent),math.cos(angle)),
        vScal(vCross(vRot,vSub(v,cent)),math.sin(angle))),
        vScal(vRot,vDot(vRot,vSub(v,cent))*(1-math.cos(angle))))
        ,cent) for v in list]
def rotate3dYPR(list, ypr, cent=[0, 0, 0]):
    return rotate3dV(rotate3dV(rotate3dV(list,ypr[2],[1,0,0],cent),ypr[1],[0,1,0],cent),ypr[0],[0,0,1],cent)
def vGetYPR(p0,p1,p2,p3):
    v01 = vSub(p1,p0)
    v02 = vSub(p2,p0)
    v03 = vSub(p3,p0)
    v21 = vSub(p1,p2)
    v20 = vSub(p0,p2)
    v23 = vSub(p3,p2)
    wallAngleYaw = math.atan2(v01[1],v01[0])
    wallAnglePitch = -math.atan2(v01[2],vLen([v01[0],v01[1]]))
    wallAngleRoll = -(vAngleSgn(vCross(v03,v01),vCross([0,0,1],v01 if (v01[0] != 0 or v01[1] != 0) else [1,0,0]),v01)) # TODO: Check for inner edges
    return [wallAngleYaw,wallAnglePitch,wallAngleRoll]


# 1234 Clockwise front side
# 5678 Clockwise back side (Seen through cube)
#  5     8
# 1     4
#
#  6     7
# 2     3

def connectionLine(length,play,positive,widthFinger,widthSpaces,minSurroundingSpacesLeft,minSurroundingSpacesRight,fingerLength,angleSnag=0):
    #finger goes to negative y
    widthFingerSpace = widthFinger + widthSpaces
    minSurroundingSpacesSum = minSurroundingSpacesLeft+minSurroundingSpacesRight
    fingerCnt = math.floor((length-minSurroundingSpacesSum+widthSpaces)/widthFingerSpace)
    surroundingSpacesLeft = (length+widthSpaces-widthFingerSpace*fingerCnt)*(0.5 if minSurroundingSpacesSum == 0 else minSurroundingSpacesLeft/minSurroundingSpacesSum)
    signFingerLength = -fingerLength*(1 if positive else -1)
    signPlay = play/math.cos(angleSnag)*(1 if positive else -1)
    addAngle = fingerLength/2*math.tan(angleSnag)
    coords = []
    #coords.append([0,0])
    for i in range(fingerCnt):
        coords.append([surroundingSpacesLeft+i*widthFingerSpace+signPlay+addAngle,0])
        coords.append([surroundingSpacesLeft+i*widthFingerSpace+signPlay-addAngle,signFingerLength])
        coords.append([surroundingSpacesLeft+i*widthFingerSpace-signPlay+addAngle+widthFinger,signFingerLength])
        coords.append([surroundingSpacesLeft+i*widthFingerSpace-signPlay-addAngle+widthFinger,0])
    #coords.append([length,0])
    return coords

#Connection Type
ctMax = 1
ctMin = 2
ctWallSize = 0

#Calculates the Length of the finger and the start of the holes. The minimum edge of the face need to be reduced from the center of the material by the calculated reduction
def connectionLineTypeReductionFingerLength(ct, matStrength, angle, positiveEdge):
    if math.sin(math.pi-angle) == 0: # Straight connections need compensation of the length and have no conneciton type
        return 0, matStrength
    if ct == ctWallSize: # Nut == Wall Size
        fingerLength = matStrength
        lengthReduction = 0
    elif ct == ctMax: # Fläche überschneidet sich maximal
        if angle > math.pi/2:
            fingerLength = matStrength / math.sin(angle)
        else:
            fingerLength = matStrength * ( 1 / math.sin(angle) + 1 / math.tan(angle))
    elif ct == ctMin: # Holz steht nicht über
        if angle > math.pi/2:
            fingerLength = matStrength * ( 1 / math.sin(angle) + 1 / math.tan(angle))
        else:
            fingerLength = matStrength / math.sin(angle)
    lengthReduction = max(0,min(-matStrength/math.tan(angle),-fingerLength*math.cos(angle))) #Length where the hole is not filed by the finger on the outside.
    fingerLength = fingerLength+lengthReduction
    lengthReduction += matStrength/2 * 1/math.tan(angle/2) - (0 if positiveEdge else fingerLength) #Length from the center to the border of the wall and reduction from the holes / negative fingers.
#    fingerLength = matStrength
#    lengthReduction = 0*max(0,min(-matStrength/math.tan(angle),-fingerLength*math.cos(angle)/2)+matStrength*(math.sin(angle/2)*math.tan(angle/2)))
    return lengthReduction, fingerLength

#return coords,reduction in length
def connectionLineType(ct, matStrength, angle, length, play, positive, widthFinger=None, widthSpaces=None, minSurroundingSpacesLeft=None, minSurroundingSpacesRight=None, addCornerLeftWidth=0, addCornerRightWidth=0):
    if widthFinger is None:
        widthFinger = matStrength
    if widthSpaces is None:
        widthSpaces = matStrength
    if minSurroundingSpacesLeft is None:
        minSurroundingSpacesLeft = matStrength/2
    if minSurroundingSpacesRight is None:
        minSurroundingSpacesRight = matStrength/2
    # Logic definition
    lengthReduction, fingerLength = connectionLineTypeReductionFingerLength(ct, matStrength, angle,positive)

    coords = []
    coords.append([-addCornerRightWidth,0])
    coords.extend(connectionLine(length,play,positive,widthFinger,widthSpaces,minSurroundingSpacesLeft,minSurroundingSpacesRight,fingerLength,0))
    coords.append([length+addCornerLeftWidth,0])
    return addToAll([0,lengthReduction],coords)

def addFaces(edges, newEdges):
    for newEdge in newEdges:
        posSmallest = newEdge.index(min(newEdge))
        directionUp = 1 if (newEdge[(posSmallest+1)%len(newEdge)] < newEdge[(posSmallest-1+len(newEdge))%len(newEdge)]) else -1
        normalizedEdge = [newEdge[(posSmallest+directionUp*i+len(newEdge))%len(newEdge)] for i in range(len(newEdge))]
        if normalizedEdge not in edges:
            edges += [normalizedEdge]
    return edges

def findFaces(netlist, nodes):
    allFaces = []
    if len(nodes) > 4: # Implement Check if one area for more corners
        return []
    for nextNode in netlist[nodes[-1]]:
        if len(nodes) >= 2 and nextNode == nodes[-2]:
            continue
        if nextNode == nodes[0]:
            return [nodes]
        if nextNode in nodes:
            print("found loop, not starting at the beginning")
            return []
        allFaces = addFaces(allFaces, findFaces(netlist, nodes + [nextNode]))
    return allFaces

def findOtherFacePoint(p0,p1,pi=-1): #Find the back point of p0, p0 and p1 are shared, pi ist not shared
    for face in facesAll:
        if p0 in face and p1 in face and not pi in face:
            posP0 = face.index(p0)
            posP1 = face.index(p1)
            if abs(posP0-posP1) != 1 and abs(posP0-posP1) != len(face)-1:
                print("Found not correct connecting faces")
            return face[(posP0+posP0-posP1+len(face))%len(face)]
    print('No Other Face Point found')

def wall(p,wallNr,matStrength,play,edgeTypeAll):
    face = facesAll[wallNr]
    coords=[]
    pOrig0 = p[face[0]]
    pOrig1 = p[face[1]]
    pOrig2 = p[face[2]]
    norm = vCross(vSub(pOrig1,pOrig0),vSub(pOrig2,pOrig0))
    sideCnt = len(face)
    for side in range(sideCnt):
        #Points:
        #0-1: aktive edge
        #2: after 1
        #3: before 0
        #bXY_X === BYX_X === edge X-Y on the side of X
        p0nr = face[side]
        p1nr = face[(1+side)%sideCnt]
        p2nr = face[(2+side)%sideCnt]
        p3nr = face[(sideCnt-1+side)%sideCnt]
        p0 = p[p0nr]
        p1 = p[p1nr]
        p2 = p[p2nr]
        p3 = p[p3nr]
        b01_0nr = findOtherFacePoint(p0nr,p1nr,p2nr)
        b01_1nr = findOtherFacePoint(p1nr,p0nr,p2nr)
        b03_0nr = findOtherFacePoint(p0nr,p3nr,p2nr)
        b03_3nr = findOtherFacePoint(p3nr,p0nr,p2nr)
        b12_1nr = findOtherFacePoint(p1nr,p2nr,p3nr)
        b12_2nr = findOtherFacePoint(p2nr,p1nr,p3nr)
        b01_0 = p[b01_0nr]
        b01_1 = p[b01_1nr]
        b03_0 = p[b03_0nr]
        b12_1 = p[b12_1nr]
        # The edge with the node with the higher number has the positive edge
        edgePos01 = max(p3nr,p2nr) > max(b01_0nr,b01_1nr) #Positive, wen pointing out of the basic shape
        edgePos12 = max(p0nr,p3nr) > max(b12_1nr,b12_2nr)
        edgePos30 = max(p1nr,p2nr) > max(b03_0nr,b03_3nr)
        angleCornerLeft = vPntAngle(p2,p1,p0)
        angleCornerRight = vPntAngle(p3,p0,p1)
        angleCornerMinLeft = min(angleCornerLeft,vPntAngle(p0,p1,b12_1))
        angleCornerMinRight = min(angleCornerRight,vPntAngle(p1,p0,b03_0))
        #MinSurroundingSpace defines a minimum of space to the inner corner)
        minSurSpaces = 1 #SurroundingSpace realtive to material strength
        minSurroundingSpacesLeft = matStrength * max(0.5,(minSurSpaces/math.sqrt(2*(1-math.cos(angleCornerMinLeft)))+1/math.tan(angleCornerMinLeft/2))) #TODO
        minSurroundingSpacesRight = matStrength * max(0.5,(minSurSpaces / math.sqrt(2 * (1 - math.cos(angleCornerMinRight))) + 1 / math.tan(angleCornerMinRight / 2)))

        lenSide = vLen(vSub(p1,p0)) # TODO
        lenOrig = vLen(vSub(p0,pOrig0))

        angleEdge = vPntAngle(p3,p0,b01_0)
        angleEdgeLeft = vPntAngle(p0,p1,b12_1)
        angleEdgeRight = vPntAngle(p1,p0,b03_0)
        lengthReduction, fingerLength = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdge, edgePos01)
        lengthReductionLeft, fingerLengthLeft = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeLeft, edgePos12)
        lengthReductionRight, fingerLengthRight = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeRight, edgePos30)
        #AddCorner fills the outer corner of wall
        addCornerLeftWidth = - lengthReduction * math.tan(math.pi/2-angleCornerLeft) - lengthReductionLeft / math.cos(math.pi/2-angleCornerLeft)
        addCornerRightWidth = - lengthReduction * math.tan(math.pi/2-angleCornerRight) - lengthReductionRight / math.cos(math.pi/2-angleCornerRight)

        coordsSide = connectionLineType(edgeTypeAll,matStrength,angleEdge,lenSide,play,edgePos01,minSurroundingSpacesLeft=minSurroundingSpacesLeft,minSurroundingSpacesRight=minSurroundingSpacesRight,addCornerLeftWidth=addCornerLeftWidth,addCornerRightWidth=addCornerRightWidth)
        angle2d = vAngleSgn(vSub(pOrig1, pOrig0), vSub(p1, p0), norm)
        angle2dOrig = 0 if side == 0 else vAngleSgn(vSub(pOrig1,pOrig0),vSub(p0,pOrig0),norm)
        pos2d = [math.cos(angle2dOrig) * lenOrig, math.sin(angle2dOrig) * lenOrig]
        coordsSidePositioned = addToAll(pos2d, rotate2d(coordsSide, angle2d))
        coords.extend(coordsSidePositioned)
    coords.append(coords[0])
    return coords
#
# Drawing
#
def drawCoords3d(coords):
    data = [[c[i] for c in coords] for i in range(3)]
    ax.plot(data[0],data[1],data[2], label='w1')

def drawWall(wallNr,points,matStrength,coords,displayInner=1,displayOuter=0,displayCenter=0):
    p0 = points[facesAll[wallNr][0]]
    p1 = points[facesAll[wallNr][1]]
    p2 = points[facesAll[wallNr][2]]
    p3 = points[facesAll[wallNr][3]]
    centerP0123 = vCenter([p0,p1,p2,p3])
    v01 = vSub(p1,p0)
    v03 = vSub(p3,p0)
    v01x03 = vCross(v03, v01)
    #Inside is defined as lookings from the center! Can be improved in the future.
    vWall = vScal(v01x03,matStrength/2*(1/vLen(v01x03) if vLen(v01x03) != 0 else 1)*(1 if vDot(v01x03,vSub(centerP0123,centerPoints)) > 0 else -1))

    coords = [[i[0],0,i[1]] for i in coords]
    coords = rotate3dYPR(coords, vGetYPR(p0,p1,p2,p3))
    coords = addToAll(p0,coords)
    coordsOut = addToAll(vWall,coords)
    coordsIn = addToAll(vScal(vWall,-1),coords)
    if displayCenter:
        drawCoords3d(coords)
    if displayInner:
        drawCoords3d(coordsIn)
    if displayOuter:
        drawCoords3d(coordsOut)



points=mulToAll([60,60,60],[[0,2,0],[0,0,0],[2,0,0],[0.5,0.5,0],[0,2,2],[0,0,2],[2,0,2],[0.5,0.5,2]]) # 1 inner Edge #TODO: Not correct
points=mulToAll([80,80,80],[[0,1,0],[0,0,0],[1,0,0],[0.4,0.4,0],[0,1,1],[0,0,1],[1,0,1],[0.4,0.4,1]]) # 1 inner Edge #TODO: Not correct
points=mulToAll([60,60,60],[[1,1,0.3],[0,0,0],[3,0,0],[2,1,0.3],[1,1,0.7],[0,0,1],[3,0,1],[2,1,0.7]]) # truncated pyramid
points=mulToAll([60,60,60],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1]]) # Cube
points=mulToAll([60,60,60],[[1,1,0.3],[0,0,0],[3,0,0],[2,1,0.3],[1,1,1.7],[0,0,1],[3,0,1],[2,1,1.7]]) # 4 trapezial sides
points=mulToAll([60,60,60],[[0,1,0],[0,0,0],[1.5,0,0],[1,1,0],[0,1,1],[0,0,1],[1.5,0,1],[1,1,1]]) # 1 non rectangular edge
points=mulToAll([60,60,60],[[0.5,1,0],[0,0,0],[1.5,0,0],[1,1,0],[0.5,1,1],[0,0,1],[1.5,0,1],[1,1,1]]) # 2 trapezial parallel sides

netlist = [
    [1,3,4],    # 0
    [2,5],      # 1
    [3,6],      # 2
    [7],        # 3
    [5,7],      # 4
    [6],        # 5
    [7],        # 6
    [],         #
]

points=mulToAll([60,60,60],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1],[0,1,2],[0,0,2],[1,0,2],[1,1,2]]) # Cube
points=mulToAll([40,40,40],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1],[-0.5,1.5,2],[-0.5,-0.5,2],[1.5,-0.5,2],[1.5,1.5,2]]) # Cube

netlist = [
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

nodeCnt = len(netlist)
fullNetlist = [[] for i in range(nodeCnt)]
for n0 in range(len(netlist)):
    for n1 in netlist[n0]:
        fullNetlist[n0].append(n1)
        fullNetlist[n1].append(n0)
netlist = fullNetlist

facesAll = []
for nodeNr in range(nodeCnt):
    facesAll = addFaces(facesAll, findFaces(netlist, [nodeNr]))
# Remove faces in the inner of the body
facesSel = []
for face in facesAll:
    for side in range(len(face)):
        sumFaces = len([0 for faceSearch in facesAll if face[side] in faceSearch and face[(side+1)%len(face)] in faceSearch])
        if sumFaces == 2:
            facesSel.append(face)
            break
facesAll = facesSel

centerPoints = vCenter(points)

materialStrength = 6
play = 1#0.14 #TODO
coords = [wall(points,wallNr,materialStrength,play,ctMax) for wallNr in range(len(facesAll))]

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim3d(0,100)
ax.set_ylim3d(0,100)
ax.set_zlim3d(0,100)
ax.scatter([p[0] for p in points],[p[1] for p in points],[p[2] for p in points], label='w1')
[drawWall(i,points,materialStrength,coords[i],displayOuter=0) for i in range(len(coords))]

space = 4
posX = space
posY = space
maxYInRow = 0
for cCoords in coords:
    cPosMin,cPosMax = vlMinMax(cCoords)
    if posX+cPosMax[0]-cPosMin[0] > size[0]:
        posX = space
        posY += maxYInRow + space
        maxYInRow = 0
    posX -= cPosMin[0]
    maxYInRow = max(cPosMax[1]-cPosMin[1],maxYInRow)
    export_svg_svgwrite(addToAll([posX,posY-cPosMin[1]], cCoords))
    posX += cPosMax[0] + space

dwg.save()

plt.show()

#TODO: Inner Edges
#YPR coordinates for 3d display wrong
#Size of plates wrong
#TODO: Features
#Different amount of corners edges