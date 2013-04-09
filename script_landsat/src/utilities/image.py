"""-----------------------------------------------------------------------------
 Name: Image Processor: Image Handler
 Purpose: Script is designed to produce several products that can be derived
   from Landsat images.

 Author:      Justin Rich (justin.rich@gi.alaska.edu)

 Created:     Feb. 23, 2011
 Copyright:   (c) glaciologist 2011
 License:     Although this application has been produced and tested
 successfully, no warranty expressed or implied is made regarding the
 reliability and accuracy of the utility, or the data produced by it, on any
 other system or for general or scientific purposes, nor shall the act of
 distribution constitute any such warranty. It is also strongly recommended
 that careful attention be paid to the contents of the metadata / help file
 associated with these data to evaluate application limitations, restrictions
 or intended use. The creators and distributors of the application shall not
 be held liable for improper or incorrect use of the utility described and/
 or contained herein.
-----------------------------------------------------------------------------"""
import arcpy                                                 #@UnresolvedImport
import numpy 
import os

class Image ():
    """Class that deals with image I/O by holding and storing raster information.
    This class works by becoming an 'image', storing data in a numpy array in order 
    to facilitate raster manipulation. The 'image' can be manipulated by changing
    grid cell values or by checking in and out sections of the raster for use in 
    other modules."""

    __IMAGE = numpy.zeros ((1,1))   # Holds the images as numpy grid
    __ROWS = 0                      # Number of Rows
    __COLUMNS = 0                   # Number of Columns
    __XCELLSIZE = 0                 # X cell size
    __YCELLSIZE = 0                 # Y cell size
    __SPATIALREF = ''               # Hold spatial reference info
    __LOCATION = arcpy.Point()      # Hold location anchor point
    __TIFF = ''                     # Hold original file name / location

    def __init__(self, tiff):
        """Imports a single tiff file and returns an array. Takes in a file name
        (this includes the directory path)"""
        global __IMAGE,  __ROWS, __COLUMNS, __XCELLSIZE         # Global Variable
        global __YCELLSIZE, __TIFF, __SPATIALREF, __LOCATION    # Global Variable

        try: # Look for and check out 'ArcInfo' License.
            import arcinfo                      #@UnresolvedImport @UnusedImport
        except:
            sys.exit()                                      #@UndefinedVariable

        # Look for and check out 'Spatial' extension.
        if arcpy.CheckExtension("spatial") == "Available":
            arcpy.CheckOutExtension("spatial")
        else:
            sys.exit()                                      #@UndefinedVariable

        # Get / Set the images and populate variables.
        __TIFF = tiff
        __LOCATION = arcpy.Point()
        __LOCATION.X = str(arcpy.GetRasterProperties_management(__TIFF, "LEFT"))
        __LOCATION.Y = str(arcpy.GetRasterProperties_management(__TIFF, "BOTTOM"))
        __ROWS = arcpy.GetRasterProperties_management(tiff, 'ROWCOUNT')
        __COLUMNS = arcpy.GetRasterProperties_management(tiff, 'COLUMNCOUNT')
        __XCELLSIZE = arcpy.GetRasterProperties_management(tiff, 'CELLSIZEX')
        __YCELLSIZE = arcpy.GetRasterProperties_management(tiff, 'CELLSIZEY')
        __SPATIALREF = arcpy.Describe(__TIFF).spatialReference

        __IMAGE = arcpy.RasterToNumPyArray(__TIFF)

    def get_tile (self, x, width):
        """Returns a numpy array created from the image based on the column X and
        the size of width."""         
        xd = x # Tile Width
        tile = numpy.zeros((self.get_rows() ,width)) # Empty grid to fill
        for c in range(0, width): # Iterate through array and get values
            for r in range(0, self.get_rows()):
                tile[r , c] = self.get_value (r, xd)
            xd +=1
        return tile  # Pass grid

    def return_tile (self, tile, x, width):
        """Takes in a numpy array and places it in the image based on the
        column X and the size in based on width."""
        xd = x # Tile Width
        for c in range(0, width): # Iterate through array and set values
            for r in range(0, self.get_rows()):
                self.set_value(r, xd, (tile [r, c]))
            xd +=1

    def save_tiff (self, output):
        """Save image as a geotiff."""
        try:
            from arcpy import env                           #@UnresolvedImport
            env.workspace = os.path.dirname (output)

            #Output the calculated array to a geotiff
            raster = arcpy.NumPyArrayToRaster(__IMAGE, __LOCATION, __TIFF, __TIFF, 0)
            arcpy.DefineProjection_management(raster, __SPATIALREF)
            raster.save (output)
        except:
            return False
        return True

    def get_value (self, row, column):
        """Returns the value of a pixel at the specified row and column.The
            #functions purpose is to handle exceptions where they exist such as
            'out of bounds' / 'out of range' that occurs when the moving window
            is at an edge."""
        value = 0   # Value to return
        try: # Try and get the value from the image.
            value = __IMAGE [row, column]
            if value > 255 or value < 0:
                value = 0
        except:
            value = 0 # If value can't be obtained return 0
        return value # Return Value

    def set_value (self, row, column, value):
        """Sets the value of a pixel at the specified row and column."""
        try: # Try and set value in the image
            global __IMAGE
            __IMAGE[row, column] = value
        except:
            return False # If value is not set, return false
        return True # If value is set, return true

    def get_rows (self):
        """Returns the number of rows in the image."""
        return int(str(__ROWS))

    def get_columns (self):
        """Returns the number of columns in the image"""
        return int(str(__COLUMNS))

    def get_x_cell_size (self):
        """Returns the size of image pixels in the X direction"""
        return __XCELLSIZE

    def get_y_cell_size (self):
        """Returns the size of image pixels in the y direction"""
        return __YCELLSIZE

    def get_spatial_reference (self):
        """Returns the spatial reference for the image"""
        return __SPATIALREF.name
