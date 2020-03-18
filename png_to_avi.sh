#!/bin/bash



#mencoder "mf://*.png" -mf type=png:fps=100 -ovc lavc -o output.avi


mencoder mf://*.png -mf w=320:h=240:fps=100:type=png -ovc copy -oac copy -o  messung02la_1.avi
