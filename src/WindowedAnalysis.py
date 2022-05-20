from PIL import Image
import numpy as np
from numpy.fft import fftn
from numpy.fft import ifftn
import math
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit



class WinAnalysis:

    def __init__(self):

        # The windowed analysis is exclusively performed on the 
        # dynamically filtered ROI sequence 
        self.dyn_roiseq = [] # filtered ROI-sequence 

        # The window size defines the size of the areas, 
        # which we will examine separately
        self.total_windows = None # number of total windows 
        self.windowsize = None # window size 

        # we need the activity map to exclude areas (windows), 
        # which show too much variability (e.g. in CBF) 
        self.activitymap = []










