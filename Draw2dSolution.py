import svgwrite
import vector as v

size=[300,4000]
#size=[180,180]
lengthUnit="mm"
filename="box.svg"

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

def draw2d(coords):
    space = 4
    posX = space
    posY = space
    maxYInRow = 0
    for cCoords in coords:
        cPosMin, cPosMax = v.lMinMax(cCoords)
        if posX + cPosMax[0] - cPosMin[0] > size[0]:
            posX = space
            posY += maxYInRow + space
            maxYInRow = 0
        posX -= cPosMin[0]
        maxYInRow = max(cPosMax[1] - cPosMin[1], maxYInRow)
        export_svg_svgwrite(v.addToAll([posX, posY - cPosMin[1]], cCoords), engrave=0)
        posX += cPosMax[0] + space
    dwg.save()