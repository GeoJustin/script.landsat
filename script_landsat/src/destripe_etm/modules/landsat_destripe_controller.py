"""-----------------------------------------------------------------------------
 Name: Landsat Destriping Controller
 Purpose: Script is designed to visually remove dropped lines from Landsat 7

 Author:      Justin Rich (justin.rich@gi.alaska.edu)

 Created:     Feb. 10, 2011
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
import os
import glob
import math
import numpy
import pp
import image as IMAGE
import stop_watch as SW
import landsat_destripe

class Controller ():
    """Class to remove horizontal stripes from landsat ETM+ Images. This should
    only be used to visual enhance images and is not intended to be used with
    computational analysis."""

    def __init__ (self, folder, output, iterations, tiles, processors, noise, noiseH, noiseL):

        __sw = SW.StopWatch() #Start the Stop watch

        #Get a list of files to process and then process 'Destriping for each.
        for __file in glob.glob (os.path.join (folder, '*.TIF')):
            imageName = os.path.basename(__file)

            #Weighting for the moving window and variable to define window size.
            window_size = 5
            window_scaling_top = numpy.array ([(1,1,1,1,1),
                                             (0,1,2,1,0),
                                             (0,0,1,1,0),
                                             (0,1,2,1,0),
                                             (1,1,1,1,1)])

            window_scaling_bot = numpy.array ([(1,1,1,1,1),
                                             (0,0,2,1,0),
                                             (0,0,1,0,0),
                                             (0,1,2,1,0),
                                             (1,1,1,1,1)])

            print '-------------------------------------'
            print 'Image:' , os.path.basename(__file)
            print 'Output Folder:' , output
            print 'Job started at:' , __sw.get_time()
            print '   Number of Iterations:' , iterations
            print '   Number of Tiles:', tiles
            print '   Number of Processors:', processors
            if noise == 1:
                print '   Noise Added - Yes (scaling ', noiseL, 'to', noiseH, ')'
            else:
                print '   Noise Added - No (scaling ', noiseL, 'to', noiseH, ')'
            print 'Scaling factors for the moving window'
            print 'Top of stripe scaling:'
            print window_scaling_top
            print ''
            print 'Bottom of stripe scaling:'
            print window_scaling_bot
            print '-------------------------------------'


            __image = IMAGE.Image(__file) #Create and 'Image' From the input file
            rows = __image.get_rows() #Find the number of rows in the image.
            cols = __image.get_columns() #Find the number of rows in the image.

            tile_size = int(math.ceil(float(cols) / float(tiles)))

            # Call back to start a tile for destriping. This will be sent out as
            # a package to a processor when one is available.
            def __callback_destripe (CB_currentTile, CB_tileSize, CB_rows, CB_windowSize, CB_windowScalingTop, CB_windowScalingBot, CB_iterations, CB_noise, CB_noiseH, CB_noiseL):
                result = landsat_destripe.Destripe().runDestripe(CB_currentTile, CB_tileSize, CB_rows,  CB_windowSize, CB_windowScalingTop, CB_windowScalingBot, CB_iterations, CB_noise, CB_noiseH, CB_noiseL)
                return result

            ppservers = () #Start the job server.
            job_server = pp.Server(ppservers=ppservers,ncpus=processors) # Creates job server with automatically detected number of workers

            # For each tile, send out a new job for destriping.
            jobs = [] #List to keep the results of a job.
            jobID = 0
            tile = range (0, cols, tile_size);

            while 1:
                if len(jobs) < (processors*2) and jobID < tiles:
                    try:    # Send new tiles out to the job server.
                        current_tile = __image.get_tile(tile[jobID], tile_size)
                        jobs.append((job_server.submit(__callback_destripe, (current_tile, tile_size, rows, window_size, window_scaling_top, window_scaling_bot, iterations, noise, noiseH, noiseL,), (), ("numpy", "landsat_destripe",)), jobID))
                        print '     ', jobID, '- Tile segment', tile[jobID] , '-' , tile[jobID]+tile_size, 'started at:' , __sw.get_elapsed_time()
                    except: print 'ERROR Retrieving Tile'
                    jobID += 1

                if len(jobs) >= (processors*2): # Wait for tiles to return before sending more out
                    for job in jobs:
                        if job[0].finished:
                            popped = jobs.pop(jobs.index(job))
                            __image.return_tile(popped[0](), tile[popped[1]], tile_size)
                            print '          Returned tile ', popped[1], 'at' , __sw.get_elapsed_time()

                if jobID == tiles:  # Wait for all tiles to return after they are all sent out.
                    while jobs:
                        for job in jobs:
                            if job[0].finished:
                                popped = jobs.pop(jobs.index(job))
                                __image.return_tile(popped[0](), tile[popped[1]], tile_size)
                                print '          Returned tile ', popped[1], 'at' , __sw.get_elapsed_time()
                    break

            print ''
            job_server.print_stats() # Print job server statistics.
            __image.save_tiff(output + '\\' + imageName) #Saves the new image.

            # Delete variables and clean workspace
            del jobs, jobID, tile, __image, cols, rows, tile_size, imageName,
            job_server.destroy()

            print 'Job completed at:', __sw.get_time()
            print 'Elapsed time:', __sw.get_elapsed_time()

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
