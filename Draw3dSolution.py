import matplotlib.pyplot as plt
import vector as v

def drawCoords3d(ax, coords):
    data = [[c[i] for c in coords] for i in range(3)]
    ax.plot(data[0],data[1],data[2], label='w1')

def drawWall(ax, face,points,matStrength,coords,centerPoint,relPos,displayInner=1,displayOuter=1,displayCenter=1):
    p0 = points[face[0]]
    p1 = points[face[1]]
    p3 = points[face[-1]]
    centerP0123 = v.center([points[p] for p in face])
    v01 = v.sub(p1, p0)
    v03 = v.sub(p3, p0)
    v01x03 = v.cross(v03, v01)
    #Inside is defined as lookings from the center! TODO: Can be improved in the future.
    vWall = v.scal(v01x03, matStrength / 2 * (1 / v.vlen(v01x03) if v.vlen(v01x03) != 0 else 1) * (1 if v.dot(v01x03, v.sub(centerP0123, centerPoint)) > 0 else -1))
    coords = [[i[0],0,i[1]] for i in coords]
    coords = v.rotate3dYPR(coords, v.getYPR(p0, p1, p3))
    coords = v.addToAll(p0,coords)
    coords = v.addToAll(v.scal(relPos, -1), coords)
    coordsOut = v.addToAll(vWall,coords)
    coordsIn = v.addToAll(v.scal(vWall, -1), coords)
    if displayCenter:
        drawCoords3d(ax, coords)
    if displayInner:
        drawCoords3d(ax, coordsIn)
    if displayOuter:
        drawCoords3d(ax, coordsOut)

def draw3d(points, faces, coords, materialStrength):
    centerPoint = v.center(points)
    relPos = centerPoint
    #relPos = points[0]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlim3d(-100, 100)
    ax.set_ylim3d(-100, 100)
    ax.set_zlim3d(-100, 100)
    ax.scatter(*[[p[xyz]-relPos[xyz] for p in points] for xyz in range(3)], label='w1')
    for i in range(len(coords)):
        drawWall(ax, faces[i], points, materialStrength, coords[i], centerPoint, relPos, displayInner=1,displayOuter=1,displayCenter=0)
    plt.show()