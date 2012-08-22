"""-----------------------------------------------------------------------------
 Name: Landsat Destriping Controller
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
import os, glob, sys, math
import numpy, pp
import Image, StopWatch, LandsatDestripe

class Controller ():
    """Class to remove horizontal stripes from landsat ETM+ Images. This should
    only be used to visual enhance images and is not intended to be used with
    computational analysis."""

    def __init__ (self, folder, output, iterations, tiles, processors, noise, noiseH, noiseL):

        stopWatch = StopWatch.stopWatch() #Start the Stopwatch

        #Get a list of files to process and then process 'Destriping for each.
        for __file in glob.glob (os.path.join (folder, '*.TIF')):
            imageName = os.path.basename(__file)

            #Weighting for the moving window and variable to define window size.
            windowSize = 5
            windowScalingTop = numpy.array ([(1,1,1,1,1),
                                             (0,1,2,1,0),
                                             (0,0,1,1,0),
                                             (0,1,2,1,0),
                                             (1,1,1,1,1)])

            windowScalingBot = numpy.array ([(1,1,1,1,1),
                                             (0,0,2,1,0),
                                             (0,0,1,0,0),
                                             (0,1,2,1,0),
                                             (1,1,1,1,1)])

            print '-------------------------------------'
            print 'Image:' , os.path.basename(__file)
            print 'Output Folder:' , output
            print 'Job started at:' , stopWatch.getCurrentTime()
            print '   Number of Iterations:' , iterations
            print '   Number of Tiles:', tiles
            print '   Number of Processors:', processors
            if noise == 1:
                print '   Noise Added - Yes (scaling ', noiseL, 'to', noiseH, ')'
            else:
                print '   Noise Added - No (scaling ', noiseL, 'to', noiseH, ')'
            print 'Scaling factors for the moving window'
            print 'Top of stripe scaling:'
            print windowScalingTop
            print ''
            print 'Bottom of stripe scaling:'
            print windowScalingBot
            print '-------------------------------------'


            __image__ = Image.Image(__file) #Create and 'Image' From the input file
            rows = __image__.getRows() #Find the number of rows in the image.
            cols = __image__.getColumns() #Find the number of rows in the image.

            tileSize = int(math.ceil(float(cols) / float(tiles)))

            # Call back to start a tile for destriping. This will be sent out as
            # a package to a processer when one is available.
            def __callbackDestripe (CB_currentTile, CB_tileSize, CB_rows, CB_windowSize, CB_windowScalingTop, CB_windowScalingBot, CB_iterations, CB_noise, CB_noiseH, CB_noiseL):
                result = LandsatDestripe.Destripe().runDestripe(CB_currentTile, CB_tileSize, CB_rows,  CB_windowSize, CB_windowScalingTop, CB_windowScalingBot, CB_iterations, CB_noise, CB_noiseH, CB_noiseL)
                return result

            ppservers = () #Start the job server.
            job_server = pp.Server(ppservers=ppservers,ncpus=processors) # Creates jobserver with automatically detected number of workers

            # For each tile, send out a new job for destriping.
            jobs = [] #List to keep the results of a job.
            jobID = 0
            tile = range (0, cols, tileSize);

            while 1:
                if len(jobs) < (processors*2) and jobID < tiles:
                    try:
                        currentTile = __image__.getTile(tile[jobID], tileSize)
                        jobs.append((job_server.submit(__callbackDestripe, (currentTile, tileSize, rows, windowSize, windowScalingTop, windowScalingBot, iterations, noise, noiseH, noiseL,), (), ("numpy", "LandsatDestripe",)), jobID))
                        print '     ', jobID, '- Tile segment', tile[jobID] , '-' , tile[jobID]+tileSize, 'started at:' , stopWatch.getEllapsedTime()
                    except: print 'ERROR Retrieving Tile'
                    jobID += 1

                if len(jobs) >= (processors*2):
                    for job in jobs:
                        if job[0].finished:
                            popped = jobs.pop(jobs.index(job))
                            __image__.returnTile(popped[0](), tile[popped[1]], tileSize)
                            print '          Returned tile ', popped[1], 'at' , stopWatch.getEllapsedTime()

                if jobID == tiles:
                    while jobs:
                        for job in jobs:
                            if job[0].finished:
                                popped = jobs.pop(jobs.index(job))
                                __image__.returnTile(popped[0](), tile[popped[1]], tileSize)
                                print '          Returned tile ', popped[1], 'at' , stopWatch.getEllapsedTime()
                    break

            print ''
            job_server.print_stats()

            __image__.saveTiff(output + '\\' + imageName) #Saves the new image.

            del jobs, jobID, tile, __image__, cols, rows, tileSize, imageName,
            job_server.destroy()

            print 'Job completed at:', stopWatch.getCurrentTime()
            print 'Elapsed time:', stopWatch.getEllapsedTime()

        raw_input ("Processing Complete. Press Any Key.")



def driver():
    folder = 'C:\\Users\\glaciologist\\Desktop\\Pans'
    output = 'C:\\Users\\glaciologist\\Desktop\\PanOut'
    iterations = 15
    tiles = 250
    processors = 5
    noise = 1
    noiseH = 3
    noiseL = -1
    Controller (folder, output, iterations, tiles, processors, noise, noiseH, noiseL)

if __name__ == '__main__':
    driver()
