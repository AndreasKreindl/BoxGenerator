import svgwrite
import math
import matplotlib.pyplot as plt
import sys
import vector as v

size=[300,4000]
#size=[180,180]
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
    return v.addToAll([0,lengthReduction],coords)

def standardiceFace(face):
    posSmallest = face.index(min(face))
    directionUp = 1 if (face[(posSmallest+1)%len(face)] < face[(posSmallest-1+len(face))%len(face)]) else -1
    return [face[(posSmallest+directionUp*i+len(face))%len(face)] for i in range(len(face))]

def addFaces(faces, newFaces):
    for newFace in newFaces:
        standardicedFace = standardiceFace(newFace)
        if standardicedFace not in faces:
            faces += [standardicedFace]
    return faces

def removeFaces(faces, removeFaces):
    for removeFace in removeFaces:
        standardicedFace = standardiceFace(removeFace)
        if standardicedFace in faces:
            faces.remove(standardicedFace)
    return faces

def findFaces(netlist, nodes):
    allFaces = []
    if len(nodes) > 4: # Implement Check if one area for more corners
        return []
    for nextNode in netlist[nodes[-1]]:
        if nextNode == nodes[0]:
            if len(nodes) < 3:
                continue # Not a full face
            return [nodes]
        if nextNode in nodes:
            continue # Found loop, not starting at the beginning
        allFaces = addFaces(allFaces, findFaces(netlist, nodes + [nextNode]))
    return allFaces

def createFaces(netlist):
    facesAll = []
    for nodeNr in range(len(netlist)):
        facesAll = addFaces(facesAll, findFaces(netlist, [nodeNr]))
    # Remove nested faces
    facesSel = []
    for face in facesAll:
        sumFaces = [0 for faceSearch in facesAll if len(face) > len(faceSearch) and len(
            [0 for faceSearchCorner in faceSearch if faceSearchCorner in face]) == len(faceSearch)]
        if not sumFaces:  # TODO Allow Outside Edges => 1
            facesSel.append(face)
            continue
    facesAll = facesSel
    # Remove faces in the inner of the body
    facesSel = []
    for face in facesAll:
        for side in range(len(face)):
            sumFaces = len([0 for faceSearch in facesAll if
                            face[side] in faceSearch and face[(side + 1) % len(face)] in faceSearch])
            if sumFaces == 2:
                facesSel.append(face)
                break
    return facesSel

def createFullNetlist(netlist):
    fullNetlist = [[] for i in range(len(netlist))]
    for n0 in range(len(netlist)):
        for n1 in netlist[n0]:
            if n1 not in fullNetlist[n0]:
                fullNetlist[n0].append(n1)
            if n0 not in fullNetlist[n1]:
                fullNetlist[n1].append(n0)
    return fullNetlist

def findOtherFacePoint(p0,p1,pi=-1): #Find the back point of p0, p0 and p1 are shared, pi ist not shared
    for face in facesAll:
        if p0 in face and p1 in face and not pi in face:
            posP0 = face.index(p0)
            posP1 = face.index(p1)
            if abs(posP0-posP1) != 1 and abs(posP0-posP1) != len(face)-1:
                print("Found not correct connecting faces")
            return face[(posP0+posP0-posP1+len(face))%len(face)]
    print('No Other Face Point found')

def wall(p,wallNr,matStrength,play,edgeTypeAll,widthFinger=None, widthSpaces=None):
    face = facesAll[wallNr]
    coords=[]
    pOrig0 = p[face[0]]
    pOrig1 = p[face[1]]
    pOrig2 = p[face[2]]
    norm = v.cross(v.sub(pOrig1, pOrig0), v.sub(pOrig2, pOrig0))
    sideCnt = len(face)
    for side in range(sideCnt):
        #Points:
        #0-1: aktive edge
        #2: after 1
        #3: before 0
        #bXY_X === BYX_X === point over the edge X-Y on the side of X
        #Note: If only three corners point 2 is the same point as point 3
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
        b03_0nr = findOtherFacePoint(p0nr,p3nr,p1nr)
        b03_3nr = findOtherFacePoint(p3nr,p0nr,p1nr)
        b12_1nr = findOtherFacePoint(p1nr,p2nr,p0nr)
        b12_2nr = findOtherFacePoint(p2nr,p1nr,p0nr)
        b01_0 = p[b01_0nr]
        b01_1 = p[b01_1nr]
        b03_0 = p[b03_0nr]
        b12_1 = p[b12_1nr]
        # The edge with the node with the higher number has the positive edge
        edgePos01 = max(p3nr,p2nr) > max(b01_0nr,b01_1nr) #Positive, wen pointing out of the basic shape
        edgePos12 = max(p0nr,p3nr) > max(b12_1nr,b12_2nr)
        edgePos30 = max(p1nr,p2nr) > max(b03_0nr,b03_3nr)
        angleCornerLeft = v.pntAngle(p2, p1, p0)
        angleCornerRight = v.pntAngle(p3, p0, p1)
        angleCornerMinLeft = min(angleCornerLeft, v.pntAngle(b01_1, p1, p0))
        angleCornerMinRight = min(angleCornerRight, v.pntAngle(b01_0, p0, p1))
        #MinSurroundingSpace defines a minimum of space to the inner corner)
        minSurSpaces = 1 #SurroundingSpace realtive to material strength
        minSurroundingSpacesLeft = matStrength * max(1,(minSurSpaces/math.sqrt(2*(1-math.cos(angleCornerMinLeft)))+1/math.tan(angleCornerMinLeft/2))) #TODO This schitt is buggy
        minSurroundingSpacesRight = matStrength * max(1,(minSurSpaces / math.sqrt(2 * (1 - math.cos(angleCornerMinRight))) + 1 / math.tan(angleCornerMinRight / 2)))
        minSurroundingSpacesLeft = matStrength * (1 if angleCornerMinLeft > math.pi*0.95 else max(1,1+(minSurSpaces/math.sqrt(2*(1-math.cos(angleCornerMinLeft)))+1/math.tan(angleCornerMinLeft/2)))) #TODO
        minSurroundingSpacesRight = matStrength * (1 if angleCornerMinLeft > math.pi*0.95 else max(1,1+(minSurSpaces / math.sqrt(2 * (1 - math.cos(angleCornerMinRight))) + 1 / math.tan(angleCornerMinRight / 2))))
        #minSurroundingSpacesLeft = matStrength*4
        #minSurroundingSpacesLeft = matStrength*4

        lenSide = v.vlen(v.sub(p1, p0)) # TODO
        lenOrig = v.vlen(v.sub(p0, pOrig0))

        angleEdge = v.pntAngle(p3, p0, b01_0)
        angleEdgeLeft = v.pntAngle(p0, p1, b12_1) #TODO: Maybe not correct if the area of the points have a normal vector not parallel to the edge
        angleEdgeRight = v.pntAngle(p1, p0, b03_0)
        lengthReduction, fingerLength = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdge, edgePos01)
        lengthReductionLeft, fingerLengthLeft = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeLeft, edgePos12)
        lengthReductionRight, fingerLengthRight = connectionLineTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeRight, edgePos30)
        #AddCorner fills the outer corner of wall
        addCornerLeftWidth = - lengthReduction * math.tan(math.pi/2-angleCornerLeft) - lengthReductionLeft / math.cos(math.pi/2-angleCornerLeft)
        addCornerRightWidth = - lengthReduction * math.tan(math.pi/2-angleCornerRight) - lengthReductionRight / math.cos(math.pi/2-angleCornerRight)

        coordsSide = connectionLineType(edgeTypeAll,matStrength,angleEdge,lenSide,play,edgePos01,widthFinger,widthSpaces,minSurroundingSpacesLeft,minSurroundingSpacesRight,addCornerLeftWidth,addCornerRightWidth)
        angle2d = v.angleSgn(v.sub(pOrig1, pOrig0), v.sub(p1, p0), norm)
        angle2dOrig = 0 if side == 0 else v.angleSgn(v.sub(pOrig1, pOrig0), v.sub(p0, pOrig0), norm)
        pos2d = [math.cos(angle2dOrig) * lenOrig, math.sin(angle2dOrig) * lenOrig]
        coordsSidePositioned = v.addToAll(pos2d, rotate2d(coordsSide, angle2d))
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
    face = facesAll[wallNr]
    p0 = points[face[0]]
    p1 = points[face[1]]
    p3 = points[face[-1]]
    centerP0123 = v.center([points[p] for p in face])
    v01 = v.sub(p1, p0)
    v03 = v.sub(p3, p0)
    v01x03 = v.cross(v03, v01)
    #Inside is defined as lookings from the center! Can be improved in the future.
    vWall = v.scal(v01x03, matStrength / 2 * (1 / v.vlen(v01x03) if v.vlen(v01x03) != 0 else 1) * (1 if v.dot(v01x03, v.sub(centerP0123, centerPoint)) > 0 else -1))

    coords = [[i[0],0,i[1]] for i in coords]
    coords = v.rotate3dYPR(coords, v.getYPR(p0, p1, p3))
    coords = v.addToAll(p0,coords)
    coordsOut = v.addToAll(vWall,coords)
    coordsIn = v.addToAll(v.scal(vWall, -1), coords)
    if displayCenter:
        drawCoords3d(coords)
    if displayInner:
        drawCoords3d(coordsIn)
    if displayOuter:
        drawCoords3d(coordsOut)



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
#points = mulToAll([1/8,1/5,1/3],addToAll([0,0,-(150*2+30+295*2+30*4)],points))
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

points=v.mulToAll([60,60,60],[[0,1,0],[0,0,0],[1,0,0],[1,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1]])
netlist = [[1,3,4,6],[2,5,7],[3,5],[4],[5,6],[7],[7],[]]

notUsedFaces=[]

netlist = createFullNetlist(netlist)
facesAll = createFaces(netlist)
facesAll = removeFaces(facesAll, notUsedFaces)

centerPoint = v.center(points)

materialStrength = 4
play = -0.15 #TODO -0.14
coords = [wall(points,wallNr,materialStrength,play,ctWallSize) for wallNr in range(len(facesAll))]

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim3d(-100,100)
ax.set_ylim3d(-100,100)
ax.set_zlim3d(-100,100)
ax.scatter([p[0] for p in points],[p[1] for p in points],[p[2] for p in points], label='w1')
[drawWall(i,points,materialStrength,coords[i],displayOuter=0) for i in range(len(coords))]

space = 4
posX = space
posY = space
maxYInRow = 0
for cCoords in coords:
    cPosMin,cPosMax = v.lMinMax(cCoords)
    if posX+cPosMax[0]-cPosMin[0] > size[0]:
        posX = space
        posY += maxYInRow + space
        maxYInRow = 0
    posX -= cPosMin[0]
    maxYInRow = max(cPosMax[1]-cPosMin[1],maxYInRow)
    export_svg_svgwrite(v.addToAll([posX,posY-cPosMin[1]], cCoords),engrave=0)
    posX += cPosMax[0] + space

dwg.save()

plt.show()

#TODO: Inner Edges
#YPR coordinates for 3d display wrong
#Size of plates wrong
#TODO: Features
#Different amount of corners edges