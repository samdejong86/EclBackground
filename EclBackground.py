#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from basf2 import *

# this prevents the creaton of Belle2FileCatalog.xml.
os.environ["BELLE2_FILECATALOG"] = "NONE"

# get location, sample, and campaign name from command line
location = sys.argv[1]
sampletype = sys.argv[2]
HERLER = sys.argv[3]
campaignName = sys.argv[4]


# length of each file, in us (nearly always 1)
timePerFile = 1000


# Input location set at command line
#inputs = location + "output_" + sampletype + "_" + HERLER + "_study_*.root"
if HERLER != "N":
    inputs = location + sampletype+"_"+HERLER+"_1ms.root"
    outfile = "./rootFiles/" + sampletype + "_" + HERLER + "_" + campaignName + ".root"
else:
    inputs = location+sampletype+"_100us.root"
    outfile = "./rootFiles/" + sampletype + "_" + campaignName + ".root"

print(inputs)

# set the sample time based on the number of files that will be opened.
sampletime = timePerFile * int(subprocess.check_output('ls ' + inputs + ' | wc -l',
                                                       shell=True))
print('The sampletime is ', str(sampletime), 'us')

# Output filename will be based on sample, eg RBB_HER_12thCamp.root

print('The output will written to ', outfile)

# The background module can produce some ARICH plots for shielding studies. To do this, set this to True
ARICH = False

# Register necessary modules
main = create_path()

# RootInput takes the Monte Carlo events and fills the datastore, so they can be accessed by other modules
simpleinput = register_module('RootInput')
simpleinput.param('inputFileNames', inputs)
main.add_module(simpleinput)

gearbox = register_module('Gearbox')
main.add_module(gearbox)

# If you want the ARICH plots, you need to load the geometry.
if ARICH:
    geometry = register_module('Geometry')
    geometry.logging.log_level = LogLevel.WARNING
    main.add_module(geometry)

# The ecl background module is a HistoModule. Any histogram registered in it will be written to file by the HistoManager module
histo = register_module('HistoManager')  # Histogram Manager
histo.param('histoFileName', outfile)
main.add_module(histo)

# ecl Background study module
eclBg = register_module('ECLBackground')
eclBg.param('sampleTime', sampletime)
eclBg.param('doARICH', ARICH)
eclBg.param('crystalsOfInterest', [318, 625, 107])  # If you want the dose for specific crystals, put the cell ID here

# other ECL modules...
eclDigi = register_module('ECLDigitizer')
eclRecShower = register_module('ECLCRFinderAndSplitter')

main.add_module(eclDigi)
main.add_module(eclRecShower)
main.add_module(eclBg)

# run it
process(main)

print(statistics)
