"""-----------------------------------------------------------------------------
 Name: Landsat Destriping
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
#Add the current directory to python search path.
import sys, os
sys.path.append (os.path.dirname(os.path.abspath(__file__)) + '\\Modules')

import Tkinter, pp

class GUI ():

    def __init__ (self, main):

        Tk = Tkinter #Just to Shorten Things.
#_______________________________________________________________________________
#*******Menu Bar****************************************************************
        def __callback_Help (): #This is also used by 'Help' button.
            import webbrowser
            helpfile = os.path.dirname(os.path.abspath(__file__)) + '\\Help.html'
            webbrowser.open(helpfile)

        def __callback_Exit (): #This is also used by 'Exit' button
            main.destroy()
            try: self.root.destroy()
            except: pass
            sys.exit()

        #File Menu
        menubar = Tk.Menu(main)

        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=__callback_Exit)
        menubar.add_cascade(label="File", menu=filemenu)

        #Help Menu
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Files", command=__callback_Help)
        menubar.add_cascade(label="Help", menu=helpmenu)

        main.config(menu=menubar)

#_______________________________________________________________________________
#*******Select Input Frame******************************************************
        #MAIN FRAME
        InputFrame = Tk.Frame (main)
        InputFrame.grid (row =0, column =0, columnspan = 1, pady = 6)

        InputPath = Tk.Label (InputFrame, text='Select Input')
        InputPath.grid(row=0, column = 0, sticky = Tk.W, padx = 6)

        def callback_SelectedI ():
            self.getDirectory (InputString)
        InputString = Tk.StringVar()
        InputEntry = Tk.Entry (InputFrame, textvariable = InputString, width = 50)
        InputEntry.grid(row=0, column = 1, padx = 6)

        inputFile = Tk.Button(InputFrame, text = 'Select', height = 1, width = 8,
         command = callback_SelectedI)
        inputFile.grid(row=0, column = 2, padx = (0,6), pady = (0,6))

#_______________________________________________________________________________
#*******Select Output Frame*****************************************************

        InputPath = Tk.Label (InputFrame, text='Select Output')
        InputPath.grid(row=1, column = 0, sticky = Tk.W, padx = 6, pady = (6,6))

        def callback_SelectedO ():
            self.getDirectory (outputString)
        outputString = Tk.StringVar()
        outputEntry = Tk.Entry (InputFrame, textvariable = outputString, width = 50)
        outputEntry.grid(row=1, column = 1, padx = 6, pady = (6,6))

        outputFile = Tk.Button(InputFrame, text = 'Select', height = 1, width = 8,
         command = callback_SelectedO)
        outputFile.grid(row=1, column = 2, padx = (0,6), pady = (0,6))


#_______________________________________________________________________________
#*******Add Noise **************************************************************

        OptionsFrame = Tk.LabelFrame(main, text= 'Parameters')
        OptionsFrame.grid (row =2, column =0, columnspan = 2, padx =6, pady = 6)

        NoiseFrame = Tk.Frame (OptionsFrame, relief = Tk.RIDGE, bd = 1)
        NoiseFrame.grid (row =2, column =0, columnspan = 2, padx = 20, pady = (6,6))

        checkNoise = Tk.IntVar ()

        def __callback_Noise ():
            if checkNoise.get() == 1: #Noise is selected.
                NoiseLEntry.configure (state=Tk.NORMAL)
                NoiseHEntry.configure (state=Tk.NORMAL)
            if checkNoise.get() == 0: #Noise is not selected.
                NoiseLEntry.configure (state=Tk.DISABLED)
                NoiseHEntry.configure (state=Tk.DISABLED)

        checkBox = Tk.Checkbutton(NoiseFrame, text = "Add Noise", variable = checkNoise, onvalue = 1, offvalue = 0, command=__callback_Noise)
        checkBox.pack(side=Tk.LEFT, padx = (50,3))
        checkBox.select()

        labelNoiseL = Tk.Label(NoiseFrame, text='(Low')
        labelNoiseL.pack(side=Tk.LEFT)

        NoiseLString = Tk.StringVar()
        NoiseLEntry = Tk.Entry (NoiseFrame, textvariable = NoiseLString, width = 3, justify = Tk.CENTER)
        NoiseLEntry.pack(side=Tk.LEFT, padx = 3)
        NoiseLString.set(-1)

        labelNoiseH = Tk.Label(NoiseFrame, text=' - High')
        labelNoiseH.pack(side=Tk.LEFT)

        NoiseHString = Tk.StringVar()
        NoiseHEntry = Tk.Entry (NoiseFrame, textvariable = NoiseHString, width = 3, justify = Tk.CENTER)
        NoiseHEntry.pack(side=Tk.LEFT, padx = 3)
        NoiseHString.set(3)

        labelNoiseH2 = Tk.Label(NoiseFrame, text=')')
        labelNoiseH2.pack(side=Tk.LEFT, padx = (3,50))


#_______________________________________________________________________________
#*******Interation Spiner*******************************************************

        iteratorFrame = Tk.Frame (OptionsFrame)
        iteratorFrame.grid (row =3, column =0, columnspan = 2, padx = 20, pady = (6,12))

        iterFrame = Tk.Frame (iteratorFrame, relief = Tk.RIDGE, bd = 1)
        iterFrame.pack(side=Tk.LEFT)

        labelIterat = Tk.Label(iterFrame, text='Iterations')
        labelIterat.pack(side=Tk.LEFT, padx = (6,0))

        IterationString = Tk.StringVar()
        IterationEntry = Tk.Entry (iterFrame, textvariable = IterationString, width = 3, justify = Tk.CENTER)
        IterationEntry.pack(side=Tk.LEFT, padx = (6,6), pady= 3)
        IterationString.set("7")

        ppservers = ()
        job_server = pp.Server(ppservers=ppservers) # Creates jobserver with automatically detected number of workers

        ProcFrame = Tk.Frame (iteratorFrame, relief = Tk.RIDGE, bd = 1)
        ProcFrame.pack(side=Tk.LEFT, padx = (20,0))

        labelProc = Tk.Label(ProcFrame, text='Processors')
        labelProc.pack(side=Tk.LEFT, padx = (6,0))

        ProcString = Tk.StringVar()
        ProcEntry = Tk.Entry (ProcFrame, textvariable = ProcString, width = 3, justify = Tk.CENTER)
        ProcEntry.pack(side=Tk.LEFT, padx = (6,0), pady= 3)
        ProcString.set(str(int(job_server.get_ncpus() * .75)))

        labelProcTotal = Tk.Label(ProcFrame, text='of ' + str(job_server.get_ncpus()))
        labelProcTotal.pack(side=Tk.LEFT, padx = (0, 6))

        tileFrame = Tk.Frame (iteratorFrame, relief = Tk.RIDGE, bd = 1)
        tileFrame.pack(side=Tk.LEFT, padx = (20,0))

        labeltile = Tk.Label(tileFrame, text='Tiles')
        labeltile.pack(side=Tk.LEFT, padx = (6,0))

        tileString = Tk.StringVar()
        tileEntry = Tk.Entry (tileFrame, textvariable = tileString, width = 3, justify = Tk.CENTER)
        tileEntry.pack(side=Tk.LEFT, padx = (6,6), pady= 3)
        tileString.set(100)


#_______________________________________________________________________________
#*******Modules Available Input Frame*******************************************
        arcpyModule = 'NOT FOUND'
        numpyModule = 'NOT FOUND'

        try:
            import arcpy #@UnresolvedImport @UnusedImport
            arcpyModule = 'AVAILABLE'
        except: pass

        try:
            import numpy #@UnusedImport
            numpyModule = 'AVAILABLE'
        except: pass

        foundFrame = Tk.Frame(main)
        foundFrame.grid(row=4, column=0, columnspan = 3, pady = 6)

        arcpyLabel = Tk.Label (foundFrame, text= "Arcpy Module - ")
        arcpyLabel.pack(side=Tk.LEFT, padx = (6,0))

        arcpyLabelResult = Tk.Label (foundFrame, text= arcpyModule, fg = "#008000")
        if arcpyModule == 'NOT FOUND':
            arcpyLabelResult.configure(fg = "#ff0000")
        arcpyLabelResult.pack(side=Tk.LEFT, padx = (0,12))

        numpyLabel = Tk.Label (foundFrame, text="Numpy Module - ")
        numpyLabel.pack(side=Tk.LEFT, padx = (6,0))

        numpyLabelResult = Tk.Label (foundFrame, text=numpyModule, fg = "#008000")
        if numpyModule == 'NOT FOUND':
            numpyLabelResult.configure(fg = "#ff0000")
        numpyLabelResult.pack(side=Tk.LEFT, padx = (0,12))

#_______________________________________________________________________________
#*******#Button Frame***********************************************************
        buttonFrame = Tk.Frame(main)
        buttonFrame.grid(row=5, column=0, columnspan = 3, pady = 6)

        #Help Button
        helpButton = Tk.Button(buttonFrame, text = "Help", height = 1,
         width = 12, command=__callback_Help)
        helpButton.pack(side=Tk.LEFT, padx = (6,12))

        #Exit Program Button
        exitButton = Tk.Button(buttonFrame, text = "Exit", height = 1,
         width = 12, command=__callback_Exit)
        exitButton.pack(side=Tk.LEFT, padx = (6,12))

        #Run Program Button
        def callback_runImport ():
            import landsat_destripe_controller #@UnresolvedImport
            if InputString.get() <> '' and outputString.get() <> '' and IterationString.get() <> '':
                main.destroy()
                try: root.destroy() #@UndefinedVariable
                except: pass
                landsat_destripe_controller.Controller (InputString.get(), outputString.get(), int(IterationString.get()), int(tileString.get()), int(ProcString.get()), checkNoise.get(), int(NoiseHString.get()), int(NoiseLString.get()))
            else: #, , noiseH, noiseL
                import tkMessageBox
                tkMessageBox.showwarning ('Warning', 'You must select a folder containing images to destripe, a folder to output the results (different from the input) and the number of iterations to complete.')
        run = Tk.Button(buttonFrame, text = "Run", height = 1,
         width = 12, command= callback_runImport)
        run.pack(side=Tk.LEFT, padx = 6)


#_______________________________________________________________________________
#***FUNCTIONS*******************************************************************
    def getDirectory (self, string):
        """Method: Get directory
        Purpose - An extension of the tkFileDialog module to be used internally."""
        import tkFileDialog
        vDirectory = tkFileDialog.askdirectory(title='Please select a directory')
        if len(vDirectory) > 0:
            string.set (vDirectory)
            return vDirectory




def driver():
    main = Tkinter.Tk()
    main.title ('Destripinator - V.2.0')
    GUI (main)
    main.mainloop()

if __name__ == '__main__':
    driver()
