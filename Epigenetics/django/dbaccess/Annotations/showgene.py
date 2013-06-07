'''
Created on 2013-05-16

@author: sperez

'''


from svgwrite.shapes import Rect
from svgwrite.text import Text
from svgwrite.drawing import Drawing


# We get coordinates from querying ensembl normally but that takes time
# so here is the coordinates of the exons for the huntington gene:
# from query_ensembl import coordinates
# from query_ensembl import name, location
name = "Huntington"
location = "Chr 4: 3076407-3245676"
coordinates = [[3076407.0, 3076815.0], [3088665.0, 3088749.0], [3101000.0, 3101121.0], [3105550.0, 3105610.0], [3107083.0, 3107163.0], [3109011.0, 3109150.0], [3117030.0, 3117172.0], [3117811.0, 3117990.0], [3122954.0, 3123159.0], [3124615.0, 3124663.0], [3127275.0, 3127356.0], [3128990.0, 3129331.0], [3131650.0, 3131774.0], [3132031.0, 3132150.0], [3133012.0, 3133124.0], [3133364.0, 3133502.0], [3134288.0, 3134447.0], [3134540.0, 3134638.0], [3136127.0, 3136267.0], [3137630.0, 3137694.0], [3137952.0, 3138053.0], [3142236.0, 3142383.0], [3144492.0, 3144613.0], [3146878.0, 3146955.0], [3148523.0, 3148675.0], [3149731.0, 3149934.0], [3156019.0, 3156146.0], [3158798.0, 3158926.0], [3162008.0, 3162119.0], [3174046.0, 3174124.0], [3174634.0, 3174858.0], [3176447.0, 3176526.0], [3176672.0, 3176834.0], [3179058.0, 3179114.0], [3180024.0, 3180173.0], [3182241.0, 3182378.0], [3184080.0, 3184197.0], [3188323.0, 3188446.0], [3189377.0, 3189613.0], [3190677.0, 3190820.0], [3201458.0, 3201666.0], [3205733.0, 3205875.0], [3208222.0, 3208402.0], [3208533.0, 3208710.0], [3209007.0, 3209084.0], [3210499.0, 3210638.0], [3211553.0, 3211676.0], [3213655.0, 3213869.0], [3214290.0, 3214436.0], [3215684.0, 3215862.0], [3216836.0, 3216938.0], [3219491.0, 3219679.0], [3221908.0, 3222035.0], [3224113.0, 3224214.0], [3225132.0, 3225287.0], [3225718.0, 3225858.0], [3227387.0, 3227470.0], [3230341.0, 3230472.0], [3230606.0, 3230736.0], [3231613.0, 3231769.0], [3234889.0, 3235080.0], [3237010.0, 3237125.0], [3237291.0, 3237505.0], [3237875.0, 3237981.0], [3240173.0, 3240336.0], [3240544.0, 3240705.0], [3241572.0, 3245676.0]]
# We scale down the coordinates and calculate the length of the gene:
offset = coordinates[0][0]
coordinates = [[(value - offset) / 100 for value in pair] for pair in coordinates]
length = (coordinates[-1][1] - coordinates[0][0])


# We draw the gene
height = 70
x, y = 30, 30
position = (x, y)
gene = Drawing("SVGs/gene.svg", debug = True)    # , size=('200mm', '150mm'), viewBox=('0 0 200 150'))
gene.add(Rect(insert = position, size = (length, height), fill = "dodgerblue"))

# We add the exons
for i, pair in enumerate(coordinates):
    start, end = pair[0], pair[1]
    newposition = (position[0] + start, position[1])
    gene.add(Rect(insert = newposition, size = (end - start, height), fill = "slateblue"))


# We add legends
gene.add(Text(name, insert = (40, 20), fill = "black"))
gene.add(Text(location, insert = (150, 20), fill = "grey"))
gene.add(Text("Intron", insert = (40, 130), fill = "dodgerblue"))
gene.add(Text("Exon", insert = (40, 150), fill = "slateblue"))


def svgcode():
    return gene.tostring()

# Uncomment below to create the .svg file
# gene.save()
print "The", name, "gene is ready to be viewed."
