"""-----------------------------------------------------------------------------
 Name: Stop Watch
 Purpose: Prints a message to the console or ArcGIS processing window

 Author:      Justin Rich (justin.rich@gi.alaska.edu)

 Created:     March 8, 2011
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
import time

class stopWatch ():
    """Extends the time module for personal use."""

    __startTime__ = float(0) #Hold start time.

    def __init__(self):
        global __startTime__
        __startTime__ = time.clock()

    def resetStartTime (self):
        """Resets the Start time held internally."""
        global __startTime__
        __startTime__ = time.clock()

    def getStartTime (self):
        """Returns the start time currently being held internally."""
        #problem with gmTime. Returns 1970, 1 , 1, 0 , ...
        t = time.strftime ('%H:%M:%S', time.gmtime(__startTime__))
        return t

    def getEllapsedTime (self):
        """Returns the difference between the Start time and the Current time."""
        t = time.strftime ('%H:%M:%S', time.gmtime(time.clock() - __startTime__))
        return t

    def pause (self, seconds):
        """Causes a pause for X seconds before resuming."""
        time.sleep(seconds)

    def getCurrentTime (self):
        """Returns the current time."""
        localtime = time.strftime('%H:%M:%S')
        return localtime

    def getCurrentDay (self):
        """Returns the current day of the week."""
        day = time.strftime('%d')
        return day

    def getCurrentMonth (self):
        """Returns the current month number (i.e 1 = Jan., 2 = Feb... etc."""
        month = time.strftime('%m')
        return month

    def getCurrentMonthName (self):
        """Returns the current month name (i.e. January, February... etc."""
        monthName = time.strftime('%B')
        return monthName

    def getCurrentYear (self):
        """Returns the current year"""
        year = time.strftime('%Y')
        return year
