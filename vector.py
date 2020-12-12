import math

def addToAll(elem,list):
    return [[x[i]+elem[i] for i in range(len(elem))] for x in list]
def mulToAll(elem,list):
    return [[x[i]*elem[i] for i in range(len(elem))] for x in list]
def lMax(l):
    return [max([v[i] for v in l]) for i in range(len(l[0]))]
def lMin(l):
    return [min([v[i] for v in l]) for i in range(len(l[0]))]
def lMinMax(l):
    cMax = lMax(l)
    cMin = lMin(l)
    return cMin, cMax
def lPosSize(l):
    cMax, cMin = lMinMax(l)
    return cMin, sub(cMax, cMin)
def scal(v, s):
    return [i*s for i in v]
def vlen(v):
    return math.sqrt(sum([i**2 for i in v]))
def dot(v0, v1):
    return sum([i0*i1 for i0,i1 in zip(v0,v1)])
def cross(a, b): #3D
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]
def sub(v0, v1):
    return [i0-i1 for i0,i1 in zip(v0,v1)]
def add(v0, v1):
    return [i0+i1 for i0,i1 in zip(v0,v1)]
def angle(v0, v1):
    if(vlen(v0)==0 or vlen(v1)==0):
        return 0
    return math.acos(min(max(dot(v0, v1) / vlen(v0) / vlen(v1), -1), 1))
def pntAngle(p0, p1, p2):#p1 is the middle one
    return angle(sub(p0, p1), sub(p2, p1))
def angleSgn(v0, v1, norm):
    if(vlen(v0)==0 or vlen(v1)==0):
        return 0
    return angle(v0, v1) * (1 if dot(cross(v0, v1), norm) > 0 else -1) # TODO: Check for inner edges
def pntAngleSgn(p0, p1, p2, norm):#p1 is the middle one
    return angleSgn(sub(p0, p1), sub(p2, p1), norm)
def center(pnts):
    return [sum([p[i] for p in pnts]) / len(pnts) for i in range(len(pnts[0]))]
def rotate3dV(list, angle, vRot, cent=[0, 0, 0]):
    return [add(add(add(
        scal(sub(v, cent), math.cos(angle)),
        scal(cross(vRot, sub(v, cent)), math.sin(angle))),
        scal(vRot, dot(vRot, sub(v, cent)) * (1 - math.cos(angle))))
        ,cent) for v in list]
def rotate3dYPR(list, ypr, cent=[0, 0, 0]):
    return rotate3dV(rotate3dV(rotate3dV(list,ypr[2],[1,0,0],cent),ypr[1],[0,1,0],cent),ypr[0],[0,0,1],cent)
def rotate2d(xyList, angle, center=[0, 0]):
    return [[math.cos(angle) * (xy[0]-center[0]) - math.sin(angle) * (xy[1]-center[1]) + center[0],
             math.sin(angle) * (xy[0]-center[0]) + math.cos(angle) * (xy[1]-center[1]) + center[1]
             ] for xy in xyList]
def getYPR(p0, p1, p3):
    v01 = sub(p1, p0)
    v03 = sub(p3, p0)
    wallAngleYaw = math.atan2(v01[1],v01[0])
    wallAnglePitch = -math.atan2(v01[2], vlen([v01[0], v01[1]]))
    wallAngleRoll = -(angleSgn(cross(v03, v01), cross([0, 0, 1], v01 if (v01[0] != 0 or v01[1] != 0) else [1, 0, 0]), v01)) # TODO: Check for inner edges
    return [wallAngleYaw,wallAnglePitch,wallAngleRoll]