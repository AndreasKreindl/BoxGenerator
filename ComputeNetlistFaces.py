
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


def computeNetlistFaces(netlist, notUsedFaces):
    netlist = createFullNetlist(netlist)
    faces = createFaces(netlist)
    faces = removeFaces(faces, notUsedFaces)
    return netlist, faces