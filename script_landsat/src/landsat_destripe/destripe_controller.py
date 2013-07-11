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

import multiprocessing       
import utilities.environment as ENV                  
import utilities.image as IMAGE

import landsat_destripe

class Controller ():
    """Class to remove horizontal stripes from landsat ETM+ Images. This should
    only be used to visual enhance images and is not intended to be used with
    computational analysis."""

    def __init__ (self, variables):

        # Setup working environment and start a log file
        environment = ENV.setup_arcgis(variables.read_variable('OUTPUT_FOLDER'))
        
        # Get input variables and assign them to a variable        
        input_folder = variables.read_variable('INPUT_FOLDER')
        input_type = variables.read_variable('INPUT_TYPE')
        output_Folder = variables.read_variable('OUTPUT_FOLDER')
        iterations = variables.read_variable('ITERATIONS')
        tiles = variables.read_variable('TILES')
        processors = variables.read_variable('PROCESSORS')
        noise = variables.read_variable('NOISE')
        noiseh = variables.read_variable('NOISEH')
        noisel = variables.read_variable('NOISEL')

        # Weighting for the moving window and variable to define window size.
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

        # Print input variables to the Log file
        __Log = environment.log
        __Log.print_line("Input Folder: " + input_folder)
        __Log.print_line("Output Folder: " + output_Folder)
        __Log.print_line("Number of Iterations: " + str(iterations))
        __Log.print_line("Number of Tiles: " + str(tiles))
        __Log.print_line("Number of Processors: " + str(processors))
        
        if noise == 1:  
            __Log.print_line("Noise Introduced: Yes")
            __Log.print_line("    Noise High: " + str(noiseh))
            __Log.print_line("    Noise Low: " + str(noisel))
        else:           __Log.print_line("Noise Introduced: No")
        
        __Log.print_line("Window Size: " + str(window_size))
        __Log.print_line("Window Top: ")
        __Log.print_line(str(window_scaling_top))
        __Log.print_line("Window Bottom: ")
        __Log.print_line(str(window_scaling_bot))
        __Log.print_break(1)
        
        #Get a list of files to process and then run 'Destriping' for each.
        for __file in glob.glob (os.path.join (input_folder, input_type)):
            
            imageName = os.path.basename(__file) # Get current image name
            __Log.print_line("Starting Image: " + imageName)

            __image = IMAGE.Image(__file) # Load current image 
            rows = __image.get_rows() # Get the number of rows in the image.
            cols = __image.get_columns() # Get the number of rows in the image.

            tile_size = int(math.ceil(float(cols) / float(tiles))) # Calculate tile size

            jobs_queue = [] # List to hold current jobs sent out for processing
            job_number = 0  # Tracks the number of jobs sent out
            jobs_returned = 0  # Tracks the number of jobs returned
            tile = range (0, cols, tile_size); # A list of tiles, their size and position
            result_queue = multiprocessing.Queue() # Queue to hold results until returned to image
              
            while (jobs_returned < tiles):
                if len(jobs_queue) < processors and job_number < tiles:
                    
                    try:
                        # Get a tile to run from the image
                        current_tile = __image.get_tile(tile[job_number], tile_size)
                        
                        # create a job / processing on a tile
                        process = multiprocessing.Process(target=landsat_destripe.run_destripe, args=(job_number, current_tile, tile_size, rows, window_size, window_scaling_top, window_scaling_bot, iterations, noise, noiseh, noisel,result_queue))
                        jobs_queue.append(process) # Add job to jobs list
                        process.start() # Start the job
                        job_number += 1 # Increase to the next job number
                        
                        __Log.print_line("  Loaded Tile - " + str(job_number))
                    except: 
                        __Log.print_line("ERROR Retrieving Tile - " + str(job_number))
                        
          
                while result_queue.empty() == False: # If a job has been completed return it
                    try:
                        return_value = result_queue.get() # Get a returned jobs
                        
                        # Return completed tile to image
                        __image.return_tile(return_value[1], tile[return_value[0]], tile_size)
                        __Log.print_line("      Returned Tile - " + str(return_value[0])) # Job Number returned
                        jobs_returned += 1
                        
                        for job in jobs_queue: # Remove any job from the job list that is complete
                            if job.is_alive() == False:
                                jobs_queue.pop(jobs_queue.index(job))
                    except: __Log.print_line("ERROR Returning Tile")
          
            
            __image.save_tiff(output_Folder + '\\' + imageName) #Saves the new image.
            __Log.print_line("Image Saved As: " + output_Folder + '\\' + imageName)
            __Log.print_break(1)
            
            # Delete variables and clean workspace
            del imageName, __image, jobs_queue, job_number, jobs_returned
            del rows, cols, tile_size, tile, result_queue

        # All Processing Complete
        environment.remove_workspace()
        __Log.print_break(1)
        __Log.print_line("Processing completed")


def driver():
    import utilities.variables as variable
    var = variable.Variables()
    
    Controller (var)

if __name__ == '__main__':
    driver()
