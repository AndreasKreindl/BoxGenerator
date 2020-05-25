import svgwrite
import math

sizeCutLength=4
sizeWood=6

pos0=[3,3]
size=[100,100]
lengthUnit="mm"
filename="testPattern" + str(sizeWood) + "_" + str(sizeCutLength) + ".svg"

def addCords(c0,c1):
    return [c0[0]+c1[0],c0[1]+c1[1]]

dwg = svgwrite.Drawing(filename=filename,
             size=("{}{}".format(size[0],lengthUnit), "{}{}".format(size[1],lengthUnit)),
             viewBox=("0 0 {} {}".format(size[0], size[1])))

def export_svg_svgwrite(path, line_width=0.2, engrave=1):
   if(len(path) > 1):
       str_list = []
       str_list.append("M {},{}".format(path[0][0],path[0][1]))
       for e in path[1:]:
           str_list.append(" L {},{}".format(e[0],e[1]))
       s = ''.join(str_list)
       dwg.add(dwg.path(s).stroke(color="rgb(0,0,255)" if engrave else "rgb(255,0,0)",width=line_width).fill("none"))
#export_svg_svgwrite(path=[[0,0],[0,10],[10,10],[10,0],[0,0]],engrave=0)
#dwg.add(dwg.rect(insert=[0, 0], size=sizeTotal, rx=None, ry=None,stroke="rgb(0,0,255)",stroke_width=0.2,fill="none"))

cntTest=[5,5] #Test Cuts in X and Y
sizeCutBasic=[sizeCutLength,sizeWood] #Nominal Cut Size
sizeCutVariation=[0.1,0.1] #Variation between two cut tests
sizeCutVariationStart=[-sizeCutVariation[i]*cntTest[i] for i in [0,1]]
sizeClearance=[3,3]
sizeBoarder=[2.5,2.5]
fontSize=3
sizeText=[fontSize*2,fontSize*1.5]
sizeTotal=[sizeBoarder[i]*2+sizeCutBasic[i]*cntTest[i]+sizeClearance[i]*(cntTest[i]-1)+sizeText[i] for i in [0,1]]

def finalSizeCutVariation(xy):
    return [sizeCutVariationStart[i]+sizeCutVariation[i]*xy[i] for i in [0,1]]


g = dwg.g(style="font-size:"+str(fontSize)+";font-family:Comic Sans MS, Arial;font-weight:normal;font-style:oblique;stroke:blue;stroke-width:0.1;fill:none")

dwg.add(dwg.rect(insert=pos0, size=sizeTotal,stroke="rgb(255,0,0)",stroke_width=0.2,fill="none"))
for x in range(cntTest[0]):
    for y in range(cntTest[1]):
        xy=[x,y]
        finalSizeCutVariation(xy)
        pos=[sizeBoarder[i]+(sizeCutBasic[i]+sizeClearance[i])*xy[i] for i in [0,1]]
        size=[sizeCutBasic[i]+sizeCutVariationStart[i]+sizeCutVariation[i]*xy[i] for i in [0,1]]
        dwg.add(dwg.rect(insert=addCords(pos,pos0), size=size, stroke="rgb(255,0,0)", stroke_width=0.2, fill="none"))

for x in range(cntTest[0]):
    sizeX=sizeCutVariationStart[0]+sizeCutVariation[0]*x
    pos=[sizeBoarder[0]+(sizeCutBasic[0]+sizeClearance[0])*x,sizeBoarder[1]+sizeText[1]+sizeCutBasic[1]*cntTest[1]+sizeClearance[1]*(cntTest[1]-1)]
    g.add(dwg.text(str(round(sizeX*100)), insert=addCords(pos,pos0)))
for y in range(cntTest[1]):
    sizeY=sizeCutVariationStart[1]+sizeCutVariation[1]*y
    pos=[sizeBoarder[0]+sizeCutBasic[0]*cntTest[0]+sizeClearance[0]*(cntTest[0]-1)+fontSize/3,sizeBoarder[1]+sizeCutBasic[1]*(y+1/2)+fontSize/3+sizeClearance[1]*y]
    g.add(dwg.text(str(round(sizeY*100)), insert=addCords(pos,pos0)))


testKeySize = 10
testKeyDepthVariationStep = 0.1
testKeyDepthVariationStart = 0
testKeyCorners = 5
testKeyWidth = sizeCutBasic[0]
testKeyDepthNominal = sizeCutBasic[1]
testKeyDepthVariation = [testKeyDepthVariationStart+testKeyDepthVariationStep*i for i in range(testKeyCorners)]
testKeyRadius = testKeySize/(2*math.tan(math.pi/testKeyCorners))
testKeyTextPosition=[-fontSize*0.8,fontSize/3]
testKeyFontRadius = testKeyRadius*0.8
offsetPosition = addCords([3+sizeTotal[0]+testKeyDepthNominal+testKeyRadius,testKeyDepthNominal+testKeyRadius],pos0)

def transform(xyList,angle):
    return [[math.cos(angle) * xy[0] - math.sin(angle) * xy[1], math.sin(angle) * xy[0] + math.cos(angle) * xy[1]] for xy in xyList]
points=[]
for s in range(testKeyCorners):
    posTrans = transform([[0,testKeyFontRadius]], -s * 2*math.pi / testKeyCorners)[0]
    posTrans = [testKeyTextPosition[i]+posTrans[i] for i in [0,1]]
    posOffset = [posTrans[i]+offsetPosition[i] for i in [0,1]]
    g.add(dwg.text(str(round(testKeyDepthVariation[s]*100)), insert=posOffset))

    curPoints = []
    curPoints.append([-testKeySize/2,testKeyRadius])
    curPoints.append([-testKeyWidth/2,testKeyRadius])
    curPoints.append([-testKeyWidth/2,testKeyRadius+testKeyDepthNominal+testKeyDepthVariation[s]])
    curPoints.append([testKeyWidth/2,testKeyRadius+testKeyDepthNominal+testKeyDepthVariation[s]])
    curPoints.append([testKeyWidth/2,testKeyRadius])
    curPoints.append([testKeySize/2,testKeyRadius])
    points=points+transform(curPoints, -s * 2*math.pi / testKeyCorners)
points=[[p[0]+offsetPosition[0],p[1]+offsetPosition[1]] for p in points]
export_svg_svgwrite(path=points,engrave=0)

dwg.add(g)
dwg.save()
