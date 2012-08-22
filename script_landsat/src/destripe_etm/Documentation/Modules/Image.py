"""-----------------------------------------------------------------------------
 Name: Image Processor: Image Handler
 Purpose: Script is designed to produce several products that can be derived
   from Landsat images.

 Author:      Justin Rich (justin.rich@gi.alaska.edu)

 Created:     Feb. 23, 2011
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
import arcpy, numpy
import os

class Image ():
    """Class that deals with geoTiff I/O"""

    #Global Variables
    __image__ = numpy.zeros ((1,1))
    __rows__ = 0
    __columns__ = 0
    __xCellSize__ = 0
    __yCellSize__ = 0
    __spatialRef__ = ''
    __location__ = arcpy.Point()
    __tiff__ = ''

    def __init__(self, tiff):
        """Imports a single tiff file and returns an array. Takes in a file name
        (this includes the directory path)"""
        global __image__,  __rows__, __columns__, __xCellSize__
        global __yCellSize__, __tiff__, __spatialRef__, __location__

        try:
            import arcinfo
            print "ArcInfo license available"
        except:
            print "ArcInfo license not available"
            sys.exit()

        if arcpy.CheckExtension("spatial") == "Available":
            arcpy.CheckOutExtension("spatial")
            print "Spatial Analyist license available"
        else:
            print "Spatial Analyist license not available"
            sys.exit()

        __tiff__ = tiff
        __location__ = arcpy.Point()
        __location__.X = str(arcpy.GetRasterProperties_management(__tiff__, "LEFT"))
        __location__.Y = str(arcpy.GetRasterProperties_management(__tiff__, "BOTTOM"))

        __rows__ = arcpy.GetRasterProperties_management(tiff, 'ROWCOUNT')
        __columns__ = arcpy.GetRasterProperties_management(tiff, 'COLUMNCOUNT')
        __xCellSize__ = arcpy.GetRasterProperties_management(tiff, 'CELLSIZEX')
        __yCellSize__ = arcpy.GetRasterProperties_management(tiff, 'CELLSIZEY')
        __spatialRef__ = arcpy.Describe(__tiff__).spatialReference

        __image__ = arcpy.RasterToNumPyArray(__tiff__)

    #---------------------------------------------------------------------------
    def getTile (self, x, width):
        """Returns a numpy array created from the image based on the column X and
        the size of width."""
        rows = int(str(__rows__))
        xd = x
        tile = numpy.zeros((rows ,width))

        for c in range(0, width):
            for r in range(0, rows):
                tile[r , c] = self.getValue (r, xd)
            xd +=1
        return tile

    #---------------------------------------------------------------------------
    def returnTile (self, tile, x, width):
        """Takes in a numpy array and places it in the image based on the
        column X and the size in based on width."""
        rows = int(str(__rows__))
        xd = x

        for c in range(0, width):
            for r in range(0, rows):
                self.setValue(r, xd, (tile [r, c]))
            xd +=1

    #---------------------------------------------------------------------------
    def saveTiff (self, output):
        """Save image as a geotiff."""
        try:
            from arcpy import env
            env.workspace = os.path.dirname (output)

            #Output the calculated array to a geotiff
            raster = arcpy.NumPyArrayToRaster(__image__, __location__, __tiff__,
             __tiff__, 0)
            arcpy.DefineProjection_management(raster, __spatialRef__)
            raster.save (output)
        except:
            return False
        return True

    #---------------------------------------------------------------------------
    def getValue (self, row, column):
        """Returns the value of a pixel at the specified row and column.The
            #functions purpose is to handle exceptions where they exist such as
            'out of bounds' / 'out of range' that occure when the moving window
            is at an edge."""
        value = 0
        try:
            value = __image__ [row, column]
            if value > 255 or value < 0:
                value = 0
        except:
            value = 0
        return value

    #---------------------------------------------------------------------------
    def setValue (self, row, column, value):
        """Sets the value of a pixel at the specified row and column."""
        try:
            global __image__
            __image__[row, column] = value
        except:
            return False
        return True

    #---------------------------------------------------------------------------
    def getRows (self):
        """Returns the number of rows in the image."""
        return int(str(__rows__))

    #---------------------------------------------------------------------------
    def getColumns (self):
        """Returns the number of columns in the image"""
        return int(str(__columns__))

    #---------------------------------------------------------------------------
    def getXCellSize (self):
        """Returns the size of image pixels in the X direction"""
        return __xCellSize__

    #---------------------------------------------------------------------------
    def getYCellSize (self):
        """Returns the size of image pixels in the y direction"""
        return __yCellSize__

    #---------------------------------------------------------------------------
    def getSpatialReference (self):
        """Returns the spatial reference for the image"""
        return __spatialRef__.name
