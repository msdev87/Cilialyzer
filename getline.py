from matplotlib import pyplot as plt
import numpy 

class GetLine:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())

        # connection ID (=cid):  
        self.cid = line.figure.canvas.mpl_connect('button_press_event', onclick) 

    def onclick(self, event):


        #print "TEST1" 

        if event.inaxes!=self.line.axes: return
         
        if (len(self.xs) < 2):
            # substitue first point -> first point is always xdata,0
            #print('self.xs')
            #print(self.xs)
            #print type(self.xs) 
            self.xs.append(event.xdata)
            #print('type von xdata :') 
            #print type(event.xdata)
            self.ys.append(numpy.float64(0))
            self.xs.pop(0)
            self.ys.pop(0) 
            self.xs.append(event.xdata)
            self.ys.append(numpy.float64(1))
        else:

            self.xs.pop(0)
            self.ys.pop(0)
            self.xs.insert(0,event.xdata)
            self.ys.insert(0,numpy.float64(0))

 
            self.xs.insert(1,event.xdata)
            self.ys.insert(1,numpy.float64(1))
            self.xs.pop()
            self.ys.pop()

            #print "TEST" 
            if (len(self.xs) == 2): return
	
        self.line.set_data(self.xs, self.ys)
        self.line.set_color('r')
        self.line.figure.canvas.draw()
        if (len(self.xs) == 2): return
    
"""
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('click to build line segments')
line, = ax.plot([0], [0])  # empty line


linebuilder = GetLine(line)
print(linebuilder)

print(linebuilder.line)
print(linebuilder.xs)
print(linebuilder.cid)
plt.show()
"""



