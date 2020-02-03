import cv2
import numpy
from skimage.color import deltaE_cie76
import json
import scipy.spatial


#Specify how many cubes you have
#rowTotal is how many cubes per row, same with columnTotal
#cubesRequired is the final amount

pruningTable = {}


def main():

    cubeTotal = 900

    
    imagePath = "C://Users//isopr//Desktop//input.png"    
    loadedImage = cv2.imread( imagePath )


    print("original shape")

    print(loadedImage.shape)
    
    imageRows = loadedImage.shape[0]
    imageColumns = loadedImage.shape[1]

    rowTotal = 0
    columnTotal = 0

    #resize by 10% until the image fits
    #each cube is 9 pixels

    totalPixelsAllocated = cubeTotal * 9
    totalImagePixels = imageRows * imageColumns

    while totalImagePixels > totalPixelsAllocated:
        loadedImage = cv2.resize( loadedImage, (int(0.9 * imageColumns), int(0.9 * imageRows)) , interpolation = cv2.INTER_CUBIC )
        imageRows = loadedImage.shape[0]
        imageColumns = loadedImage.shape[1]
        totalImagePixels = imageRows * imageColumns

 
    print("shape after iterative resizing")
    print(loadedImage.shape)
    

    rowTotal = int(imageRows / 3)
    columnTotal = int(imageColumns / 3)
    cubesRequired = rowTotal * columnTotal

    finalResized = cv2.resize(loadedImage, (3*columnTotal, 3*rowTotal))
    #finalResized = loadedImage

    #Thresh the resized image

        
    listedPixels = finalResized.tolist()

    thresholdedPixels = []

    for x in listedPixels:
        fixedRow = []

        for y in x:
        
            fixedPixels = [0,0,0]


            if y[0] > 125:
                fixedPixels[0] = 255

            if y[1] > 85:
                fixedPixels[1] = 125
            if y[1] > 170:
                fixedPixels[1] = 255

            if y[2] > 125:
                fixedPixels[2] = 255

            fixedRow.append(fixedPixels)

        thresholdedPixels.append(fixedRow)


    testArray = numpy.asarray(thresholdedPixels)
    cv2.imwrite('threshedImage.png', testArray)

    #Need to convert the thresholdedPixels to cube colours

    print("first pixel")
    print(thresholdedPixels[0][0])

    cubeConvertedPixels = []

    for x in thresholdedPixels:
        cubeRow = []

        for y in x:
            cubeRow.append(colourMatcher(y))
            
        cubeConvertedPixels.append(cubeRow)


        
   
    threshedArray = numpy.asarray(cubeConvertedPixels)



    print("new shape")
    print(threshedArray.shape)





    finalResized = threshedArray


    
    
    cv2.imwrite('resizedImage.png', threshedArray)
    
    print(rowTotal)
    print(columnTotal)
    print(cubesRequired)

    cubeList = []

    cubeCounter = 0

    iteratingSliceX = 0
    iteratingSliceY = 0
 

    while cubeCounter < cubesRequired:
        
        if iteratingSliceX == finalResized.shape[1]:
            iteratingSliceX = 0
            iteratingSliceY +=3

            
        subArray = finalResized[ iteratingSliceY:iteratingSliceY+3, iteratingSliceX:iteratingSliceX+3]
        
        cubeList.append( subArray.tolist() )
        cubeCounter +=1
        iteratingSliceX +=3
  

    #cubeList now contains the pixel values, it needs to be converted to colour values with colour distance

    colourList = []

    for x in cubeList:
        convertedCube = []

        listedCube = []
        for j in x:
            for k in j:
                listedCube.append(k)
        
        
        for sticker in listedCube:
            convertedCube.append(colourFinder(sticker))
            
        colourList.append(convertedCube)

    #colourlist contains a bunch of cubes which are all the required colours

    movesForCube = []

    for j in colourList:
        movesForCube.append( minimise(j))


    #{cube Number: ["row number", "column number", colourList[], movesForCube[]] }
    outputJson = {}

    cubeCounter = 1
    rowCounter = 1
    columnCounter = 1

    
    for x in movesForCube:
        
        if columnCounter > columnTotal:
            columnCounter = 1
            rowCounter += 1

            
        outputPage = { cubeCounter : [rowCounter, columnCounter, colourList[cubeCounter-1], x] }
        outputJson.update(outputPage)
        
        cubeCounter += 1
        columnCounter +=1
        

    with open('computedMosaic.json', 'w') as computedResult:
        computedResult.write(json.dumps(outputJson)) 


def loadFiles():
    global pruningTable
    with open("C:/Users/isopr/Desktop/Project Mosaic/pruningTable.txt") as file:
        pruningTable = json.load(file)
        


def minimise( currentCube ):
    global pruningTable
    cubeFaces ={ "b" : {'b' : 'U', 'g' : 'D', 'r' : 'R', 'o' : 'L', 'w' : 'F','y' : 'B' },
                 "g" : {'b' : 'D', 'g' : 'U', 'r' : 'R', 'o' : 'L', 'w' : 'B','y' : 'F' },
                 "w" : {'b' : 'F', 'g' : 'B', 'r' : 'L', 'o' : 'R', 'w' : 'U','y' : 'D' },
                 "y" : {'b' : 'F', 'g' : 'B', 'r' : 'R', 'o' : 'L', 'w' : 'D','y' : 'U' },
                 "r" : {'b' : 'F', 'g' : 'B', 'r' : 'U', 'o' : 'D', 'w' : 'R','y' : 'L' },
                 "o" : {'b' : 'F', 'g' : 'B', 'r' : 'D', 'o' : 'U', 'w' : 'L','y' : 'R' }}

    
    #create the currentKey, match to the center, which is index 4
    #change colours to UDLFFB

    colours = { 'b' : 'Blue',
                'g' : 'Green',
                'r' : 'Red',
                'o' : 'Orange',
                'w' : 'White',
                'y' : 'Yellow'}
    
    currentKey = []
    
    topColour = currentCube[4]

    #this is the current dictionary for the current cube
    colourSpace = cubeFaces[topColour]
    
    for x in currentCube:
        currentKey.append(colourSpace[x])

    del currentKey[4]

    key1 = currentKey  
    key2 = [ key1[5], key1[3], key1[0], key1[6], key1[1], key1[7], key1[4], key1[2] ]
    key3 = [ key1[7], key1[6], key1[5], key1[4], key1[3], key1[2], key1[1], key1[0] ]
    key4 = [ key1[2], key1[4], key1[7], key1[1], key1[6], key1[0], key1[3], key1[5] ]

    textKey1 = ''.join(key1)
    textKey2 = ''.join(key2)
    textKey3 = ''.join(key3)
    textKey4 = ''.join(key4)
    
    

    currentTopColour = colours[topColour]
    frontColourString = ''

    if textKey1 == "UUUUUUUU":
        outputString = ("Grey:{} side up".format(currentTopColour))
        return outputString


    #print(currentCube)
    

    keysToCheck = [ textKey1, textKey2, textKey3, textKey4 ]
    lengths = []
    sequences = []


    for keys in keysToCheck:
        if keys in pruningTable:
            sequence = pruningTable[keys]
            lengths.append(len(sequence))
            sequences.append(sequence)
        if keys not in pruningTable:
            sequences.append("null")
            lengths.append(100)

    minimumMoves = min(lengths)
    minimumIndex = lengths.index(minimumMoves)
    outputSequence = sequences[minimumIndex]

    
    #needs to return top colour and front colour
    #index 0 means default front, 1 is right, 2 is back, 3 is left
    faceDict = { 0 : "F", 1 : "L", 2 : "B", 3 : "R" }
    currentFrontSide = faceDict[minimumIndex]


    #needs to apply transformation if index is different

    outputSequence = transformation( outputSequence, minimumIndex ) 
    

    currentFrontColour = ''


    for key, value in colourSpace.items():
        if value == currentFrontSide:
            currentFrontColour = colours[key]
    
    
    outputString = ("{}:{}".format( currentFrontColour, ((outputSequence).replace("'", "")).replace(",", "") ))

    return( outputString )
            
    

def transformation( inputSequence, rotationIndex ):

    transformedSequence = str(inputSequence)
    
    if rotationIndex == 0:
        return  (transformedSequence.replace('i', "&#8242;"))
    if rotationIndex == 1:
        YiCompliment = {ord("R") : "B", ord("L") : "F", ord("F") : "R", ord("B") : "L"}
        transformedSequence = transformedSequence.translate(YiCompliment)
        return  (transformedSequence.replace('i', "&#8242;"))
    if rotationIndex == 2:
        Y2Compliment = {ord("R") : "L", ord("L") : "R", ord("F") : "B", ord("B") : "F"}
        transformedSequence = transformedSequence.translate(Y2Compliment)
        return  (transformedSequence.replace('i', "&#8242;"))
    if rotationIndex == 3:
        YCompliment = {ord("R") : "F", ord("L") : "B", ord("F") : "L", ord("B") : "R"}
        transformedSequence = transformedSequence.translate(YCompliment)
        return  (transformedSequence.replace('i', "&#8242;"))
        

#Colours are flipped for BGR, not RGB

def colourFinder( colourTuple ):
    colours = { 'b': [0,0,250],
                'g': [0,255,0],
                'r': [255,0,0],
                'o': [255,125,0],
                'w': [255,255,255],
                'y': [255,255,0]}

    outputColour = 'w'
    lowestDistance = 3000

    colourList = [ colourTuple[2], colourTuple[1], colourTuple[0] ]
    colourArray = numpy.asarray(colourList)



    for key in colours:
        testColour = numpy.asarray(colours[key])
        testDistance = scipy.spatial.distance.euclidean(colourArray, testColour)

        if testDistance < lowestDistance:
            outputColour = key
            lowestDistance = testDistance
                         

    return(outputColour)


def colourMatcher(colourTuple):
    colours = { 'b': [0,0,250],
                'g': [0,255,0],
                'r': [255,0,0],
                'o': [255,125,0],
                'w': [255,255,255],
                'y': [255,255,0]}

    colourOutput = { 'b': [255,0,0],
                    'g': [0,255,0],
                    'r': [0,0,255],
                    'o': [0,125,255],
                    'w': [255,255,255],
                    'y': [0,255,255]}


    outputColour = 'w'
    lowestDistance = 3000

    colourList = [ colourTuple[2], colourTuple[1], colourTuple[0] ]
    colourArray = numpy.asarray(colourList)



    for key in colours:

        testColour = numpy.asarray(colours[key])
        testDistance = scipy.spatial.distance.euclidean(colourArray, testColour)

        if testDistance < lowestDistance:
            outputColour = key
            lowestDistance = testDistance
                         
    

    return(colourOutput[outputColour])


loadFiles() 
main()





