"""-----------------------------------------------------------------------------
 Name: Landsat Destriper
 Purpose: Script is designed to visually remove dropped lines from Landsat 7

 Author:      Justin Rich (justin.rich@gi.alaska.edu)

 Created:     Feb. 10, 2011
 Copyright:   (c) glaciologist 2011
 Licence:     Although this application has been produced and tested
 successfully, no warranty expressed or implied is made regarding the
 reliablility and accuracy of the utility, or the data produced by it, on any
 other system or for general or scientific purposes, nor shall the act of
 distribution constitute any such warranty. It is also strongly recommended
 that careful attention be paid to the contents of the metadata / help file
 associated with these data to evaluate application limitations, restrictions
 or intended use. The creators and distributers of the application shall not
 be held liable for improper or incorrect use of the utiliity described and/
 or contained herein.
-----------------------------------------------------------------------------"""
import numpy

class Destripe ():

    def __init__ (self):
        pass

    def runDestripe (self, tile, columns, rows, windowSize, scallingTop, scallingBottom, iterations, noise, noiseH, noiseL):
        __tile = tile

        vFirstZero = True #First Nodata value within the column
        vReachedTopOfImage = False #Reached the first non-nodata pixel in a column
        vReachedBottomOfImage = False #Reached the last 'actual' image pixel in a column

        def getValue (__row, __col):
            value = 0
            try:
                value = __tile [__row, __col]
                if value > 255 or value < 0:
                    value = 0
            except:
                value = 0
            return value

        def getWindow (row, col, columns):
            window = numpy.array ([(0,0,0,0,0),
                                   (0,0,0,0,0),
                                   (0,0,0,0,0),
                                   (0,0,0,0,0),
                                   (0,0,0,0,0)])
            #First Column
            if col > 2:
                window [0,0] = getValue (row-2, col-2)
                window [1,0] = getValue (row-1, col-2)
                window [2,0] = getValue (row, col-2)
                window [3,0] = getValue (row+1, col-2)
                window [4,0] = getValue (row+2, col-2)

            #Second Column
            if col > 1:
                window [0,1] = getValue (row-2, col-1)
                window [1,1] = getValue(row-1,col-1)
                window [2,1] = getValue(row,col-1)
                window [3,1] = getValue(row+1,col-1)
                window [4,1] = getValue (row+2, col-1)

            #Third Column
            window [0,2] = getValue (row-2, col)
            window [1,2] = getValue(row-1,col)
            window [2,2] = getValue(row,col)
            window [3,2] = getValue(row+1,col)
            window [4,2] = getValue (row+2, col)

            #Fourth COlumn
            if col < (columns-1):
                window [0,3] = getValue (row-2, col+1)
                window [1,3] = getValue(row-1,col+1)
                window [2,3] = getValue(row,col+1)
                window [3,3] = getValue(row+1,col+1)
                window [4,3] = getValue (row+2, col+1)

            #Fifth Column
            if col < (columns):
                window [0,4] = getValue (row-2, col+2)
                window [1,4] = getValue (row-1, col+2)
                window [2,4] = getValue (row, col+2)
                window [3,4] = getValue (row+1, col+2)
                window [4,4] = getValue (row+2, col+2)

            return window

        #These two 'for' loops iterate over each pixel in the input image by column
        #and then by each pixel (row) within the column.
        for _iterations in range (0, iterations):
            for c in range(0, columns):

                for r in range(0, rows):

                    if vReachedBottomOfImage == True:
                        break #break the row loop if bottom of image has been reached

                    #Array's first place is ROW second place is COLUMN
                    if getValue(r,c) == 0:
                        if vReachedTopOfImage == True:
                            if vFirstZero == True:

                                #If the current pixel value is 0 and the top of the
                                #actual image has been reached. Check to see if the
                                #last data pixel has been reached
                                vBottomIsTrue = True
                                for q in range(r, rows):
                                    if getValue (q,c) <> 0:
                                        vBottomIsTrue = False
                                        break
                                #If it has been reached start next column
                                vReachedBottomOfImage = vBottomIsTrue

                                #If it is the first pixel in a stripe.
                                if vReachedBottomOfImage == False:

                                    window = getWindow (r,c, columns)

                                    #Multiply by scale factors
                                    window = window * scallingTop
                                    vWindowValues = 0
                                    for i in range (0,windowSize):
                                        for j in range (0,windowSize):
                                            if window [i,j] <> 0:
                                                vWindowValues+=1
                                                #Account for scaling if 'window value is not 0
                                                if scallingTop [i,j] > 1:
                                                    vWindowValues += scallingTop[i,j]-1

                                    if noise == 0: #Do not add noise to the stripes.
                                        __tile[r,c] = (numpy.sum(window) / vWindowValues)
                                    if noise == 1: #Add Noise to the stripes.
                                        randomFactor = int(numpy.random.randint(noiseL, noiseH))
                                        __tile[r,c] = (numpy.sum(window) / vWindowValues) + randomFactor

                                    vFirstZero = False
                                    del window
                    else:
                        if vReachedTopOfImage == True:
                            if vReachedBottomOfImage == False:

                                #If it is the bottom pixel in a stripe.
                                if vFirstZero == False:
                                    r -= 1 #Move row back to the last 0 value

                                    window = getWindow (r,c, columns)

                                    #Multiply by scale factors
                                    window = window * scallingBottom
                                    vWindowValues = 0
                                    for i in range (0, windowSize):
                                        for j in range (0, windowSize):
                                            if window [i,j] <> 0:
                                                vWindowValues+=1
                                                #Account for scaling if 'window value is not 0
                                                if scallingBottom [i,j] > 1:
                                                    vWindowValues += scallingBottom[i,j]-1

                                    if noise == 0: #Do not add noise to the stripes.
                                        __tile[r,c] = (numpy.sum(window) / vWindowValues)
                                    if noise == 1: #Add Noise to the stripes.
                                        randomFactor = int(numpy.random.randint(noiseL, noiseH))
                                        __tile[r,c] = (numpy.sum(window) / vWindowValues) + randomFactor

                                    vFirstZero = True
                                    del window
                        else:
                            vReachedTopOfImage = True


                #Resets the initial column variables and prepares for next column
                vFirstZero = True
                vReachedTopOfImage = False
                vReachedBottomOfImage = False

        return __tile
