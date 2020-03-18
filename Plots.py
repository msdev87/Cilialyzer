import matplotlib.pyplot as plt


class plotxy:
    def __init__(self):
        self.fig=plt.figure()
        self.axes = self.fig.add_subplot(111)  
        self.xl = None 
        self.yl = None 
        self.lp = None 
        self.fs = None 
        self.xax = None 
        self.yax = None 


    def plot(self,xax,yax,xl='xlabel',yl='ylabel',lp=10,fs=12,xlims=(1,50)):
      
        #self.axes = plt.gca() 
        #axes.set_figure(figh)
        self.xl = xl 
        self.yl = yl 
        self.lp = lp 
        self.fs = fs
        self.xax = xax 
        self.yax = yax 
        plt.plot(xax,yax, color='0.2',lw=2)
        plt.ylabel(yl, labelpad=lp,fontsize=fs)
        plt.xlabel(xl,labelpad=lp,fontsize=fs) 
        #plt.ylabel('Relative Power Spectral Density',labelpad=15,fontsize=14)
        #plt.xlabel('Frequency [Hz]',labelpad=8,fontsize=14)
        plt.xlim(int(xlims[0]),int(xlims[1]))
        #plt.xticks(fontsize=14)
        #plt.yticks(fontsize=14)
        plt.grid()
        plt.tight_layout()
        plt.show() 
        



    def replot(self):
        plt.close(self.fig)
        self.plot(self.xax,self.yax,self.xl,self.yl,self.lp,self.fs) 







