import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
import matplotlib.pyplot as plt
import numpy
import math
import re
import os
import datetime

class TkPowerspecPlot:

    def __init__(self,tkframe):
        self.tkframe = tkframe
        # calculate the figure size (in inches) 
        #print('test',self.tkframe.winfo_height())

        dpi = 100
        figh = round(0.95*tkframe.winfo_height() / dpi)
        figw = round(1.2 * figh)
        #print('figh', figh, 'figw', figw) 

        self.fig = Figure(figsize=(figw,figh), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.xlabel = None
        self.ylabel = None
        self.labelpad = None
        self.fontsize = None
        self.xax = None
        self.yax = None

        self.canvas = None
        self.meancbf = None
        self.CBFtxt = None
        self.cbfSD = None


    def plot(self,xax,yax,xl='xlabel',yl='ylabel',lp=10,fs=15,xlims=(0.1,50)):

        self.xlabel = xl
        self.ylabel = yl
        self.labelpad = lp
        self.fontsize = fs
        self.xax = xax
        self.yax = yax

        self.axes.plot(self.xax,self.yax,linewidth=2)

        #plt.xlim(int(xlims[0]),int(xlims[1]))
        self.axes.set_xlim(left=xlims[0], right=xlims[1])
        self.axes.set_xlabel(self.xlabel,labelpad=self.labelpad,fontsize=self.fontsize)
        self.axes.set_ylabel(self.ylabel,labelpad=self.labelpad,fontsize=self.fontsize)
        self.axes.tick_params(labelsize=self.fontsize)
        self.axes.set_ylim(bottom=0, top=1.3*numpy.amax(self.yax[2:])) 

        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, self.tkframe) # hand over the fig and the tkinter frame 

        # shaded area between 5 and 15 Hertz initially
        ind = numpy.sum((numpy.array(self.xax) <= 15.0).astype(int))
        self.axes.fill_between(self.xax[0:ind+1], self.yax[0:ind+1],facecolor='gray',alpha=0.5)

        ind = numpy.sum((numpy.array(self.xax) <= 5.0).astype(int))
        self.axes.fill_between(self.xax[0:ind+1], self.yax[0:ind+1],facecolor='white',alpha=1.0)

        self.canvas.draw()

        self.canvas.get_tk_widget().place( relwidth=0.95, relheight=0.95)
        self.canvas._tkcanvas.place(relwidth=0.95, relheight=0.95)

    def get_cbf(self, minf, maxf, FPS):

        peakheight = max(self.yax[1:])

        low, high = minf, maxf

        nimgs = len(self.xax)

        top = numpy.sum((numpy.array(self.xax) <= maxf).astype(int))
        bot = numpy.sum((numpy.array(self.xax) <= minf).astype(int))

        weights = self.yax[bot:top].copy()

        normfac = numpy.sum(weights)
        for i in range(bot,top):
                weights[i-bot] = weights[i-bot] / normfac

        freqs = self.xax[bot:top]
        mean, mean_square = 0, 0

        for c in range(bot,top):
                mean = mean + weights[c-bot] * freqs[c-bot]
                mean_square = mean_square + (weights[c-bot] * (freqs[c-bot] * freqs[c-bot]))

        stddev = math.sqrt(mean_square - (mean*mean))

        self.meancbf = mean
        self.cbfSD = stddev

        xpos = 0.42
        ypos = 0.82

        str1 = "CBF = "
        str2 = "$%.1f$" %mean
        str3 = "$\pm$"
        str4 = "$%.2f$" %stddev
        str5 = " [Hz]"

        if (self.CBFtxt is None):
            self.CBFtxt = self.axes.text(xpos,ypos,str1+str2+str3+str4+str5,fontsize=14,transform=self.axes.transAxes)
        else:
            self.CBFtxt.set_text(str1+str2+str3+str4+str5)
        self.canvas.draw()



    def save_plot(self, dirname):

        datetime_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_directory = os.path.join(os.getcwd(),
            'Cilialyzer_output_' + datetime_string)
        try:
            os.mkdir(output_directory)
        except FileExistsError:
            pass
        fname = re.sub(r'[^A-Za-z0-9 ]', "_", dirname)
        fname = os.path.join(output_directory, fname + '_POWERSPECTRUM.png')
        self.fig.savefig(fname,format='png',dpi=200)