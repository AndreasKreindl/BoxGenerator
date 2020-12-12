import math
import vector as v

#Connection Type
ctMax = 1
ctMin = 2
ctWallSize = 0

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

#Calculates the Length of the finger and the start of the holes. The minimum edge of the face need to be reduced from the center of the material by the calculated reduction
def connectionLineByTypeReductionFingerLength(ct, matStrength, angle, positiveEdge):
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

#return coords, reduction in length
def connectionLineByType(ct, matStrength, angle, length, play, positive, widthFinger=None, widthSpaces=None, minSurroundingSpacesLeft=None, minSurroundingSpacesRight=None, addCornerLeftWidth=0, addCornerRightWidth=0):
    if widthFinger is None:
        widthFinger = matStrength
    if widthSpaces is None:
        widthSpaces = matStrength
    if minSurroundingSpacesLeft is None:
        minSurroundingSpacesLeft = matStrength/2
    if minSurroundingSpacesRight is None:
        minSurroundingSpacesRight = matStrength/2
    # Logic definition
    lengthReduction, fingerLength = connectionLineByTypeReductionFingerLength(ct, matStrength, angle, positive)

    coords = []
    coords.append([-addCornerRightWidth,0])
    coords.extend(connectionLine(length,play,positive,widthFinger,widthSpaces,minSurroundingSpacesLeft,minSurroundingSpacesRight,fingerLength,0))
    coords.append([length+addCornerLeftWidth,0])
    return v.addToAll([0,lengthReduction],coords)

def findOtherFacePoint(faces,p0,p1,pi=-1): #Find the back point of p0 and p1 are shared, pi ist not shared
    for face in faces:
        if p0 in face and p1 in face and not pi in face:
            posP0 = face.index(p0)
            posP1 = face.index(p1)
            if abs(posP0-posP1) != 1 and abs(posP0-posP1) != len(face)-1:
                print("Found not correct connecting faces")
            return face[(posP0+posP0-posP1+len(face))%len(face)]
    print('No Other Face Point found')


def computeWall(faces, p,wallNr,matStrength,play,edgeTypeAll,widthFinger=None, widthSpaces=None):
    face = faces[wallNr]
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
        b01_0nr = findOtherFacePoint(faces,p0nr,p1nr,p2nr)
        b01_1nr = findOtherFacePoint(faces,p1nr,p0nr,p2nr)
        b03_0nr = findOtherFacePoint(faces,p0nr,p3nr,p1nr)
        b03_3nr = findOtherFacePoint(faces,p3nr,p0nr,p1nr)
        b12_1nr = findOtherFacePoint(faces,p1nr,p2nr,p0nr)
        b12_2nr = findOtherFacePoint(faces,p2nr,p1nr,p0nr)
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
        lengthReduction, fingerLength = connectionLineByTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdge, edgePos01)
        lengthReductionLeft, fingerLengthLeft = connectionLineByTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeLeft, edgePos12)
        lengthReductionRight, fingerLengthRight = connectionLineByTypeReductionFingerLength(edgeTypeAll, matStrength, angleEdgeRight, edgePos30)
        #AddCorner fills the outer corner of wall
        addCornerLeftWidth = - lengthReduction * math.tan(math.pi/2-angleCornerLeft) - lengthReductionLeft / math.cos(math.pi/2-angleCornerLeft)
        addCornerRightWidth = - lengthReduction * math.tan(math.pi/2-angleCornerRight) - lengthReductionRight / math.cos(math.pi/2-angleCornerRight)

        coordsSide = connectionLineByType(edgeTypeAll, matStrength, angleEdge, lenSide, play, edgePos01, widthFinger, widthSpaces, minSurroundingSpacesLeft, minSurroundingSpacesRight, addCornerLeftWidth, addCornerRightWidth)
        angle2d = v.angleSgn(v.sub(pOrig1, pOrig0), v.sub(p1, p0), norm)
        angle2dOrig = 0 if side == 0 else v.angleSgn(v.sub(pOrig1, pOrig0), v.sub(p0, pOrig0), norm)
        pos2d = [math.cos(angle2dOrig) * lenOrig, math.sin(angle2dOrig) * lenOrig]
        coordsSidePositioned = v.addToAll(pos2d, v.rotate2d(coordsSide, angle2d))
        coords.extend(coordsSidePositioned)
    coords.append(coords[0])
    return coords