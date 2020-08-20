#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2019

#for a micrographs.star file: prints out a plot describing the distribtion of Ctf-estimated resolution of micrographs

import sys, os
import string
import random
import numpy
import matplotlib
from scipy import stats
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

meritnum = '_rlnCtfFigureOfMerit'
maxres = '_rlnCtfMaxResolution'
DU = '_rlnDefocusU'
DV = '_rlnDefocusV'
DA = '_rlnDefocusAngle'
attributes = [maxres,meritnum,DU,DV,DA]

#gets the header of a star file, returns the columns in the file that the attributes fall into in dictionary form
def getHeader(lines):
	restoffile = []
	header = []
	inUnderscores = 0
	i = 0
	while i<len(lines):
		if lines[i][0] == '_':
			if inUnderscores == 0:
				inUnderscores = 1
		else:
			if inUnderscores == 1:
				header = lines[:i]
				restoffile = lines[i:]
				break
		i+=1
	columns = {}
	for line in header:
		if (line[0] == '_'):
			atr = line.split(' ')[0]
			colnum = int(line.split(' ')[1].split('#')[1])
			if atr in attributes:
				columns[atr] = colnum
	return (columns,restoffile,header)
		
def importStarfile(starfile):
	resscores = []
	with open(starfile) as sf:
		lines = sf.readlines()
		headerparse = getHeader(lines)
		datalines = headerparse[1]
		columns = headerparse[0]
		particles = []
		for l in datalines:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []:
				mres = data[columns[maxres]-1]
				merit = data[columns[meritnum]-1]
				du = data[columns[DU]-1]
				dv = data[columns[DV]-1]
				da = data[columns[DA]-1]
				resscores.append((mres,merit,du,dv,da))
	return resscores

#This method isn't normally useful, but it compares the DU and DV coordinates to measure the distortion on the basis of where micrographs are collected. If the entire collection isn't done using 2x2 or 3x3 focusing then this method won't work, since it averages the distortion for every 4th or 9th micrograph. Also won't work if micrographs are removed ahead of time (ex: through manual removal) so generally it isn't useful to call it. 
def computeIterativity(particles):
	du = []
	dv = []
	for p in particles:
		du.append(float(p[2]))
		dv.append(float(p[3]))
	la = []
	lb = [[],[],[],[]]
	lc = [[],[],[],[],[],[],[],[],[]]
	x = 0
	counter4 = 0
	counter9 = 0
	while x<len(du)-1:
		value = (abs(du[x] - dv[x])) / ((du[x]+dv[x])/2)
		if x % 4 == 0:
			counter4 = 0
		if x % 9 == 0:
			counter9 = 0
		la.append(value)
		lb[counter4].append(value)
		lc[counter9].append(value)
		x+=1
		counter4+=1
		counter9+=1
	a2 = round(((sum(la)/len(la))*100),4)
	b2 = []
	c2 = []
	for entry in lb:
		b2.append( round(((sum(entry) / len(entry))*100),4) )
	for entry in lc:
		c2.append( round(((sum(entry) / len(entry))*100),4) )
	return (a2, b2, c2)
		
#plots the distribution of assorted scores for a single starfile of micrographs
def plotMeritOfParticles(micrograph):

	ctfscores = []
	meritscores = []
	Du = []
	Dv = []
	Da = []
	particles = importStarfile(micrograph)
	
	j = 0
	for p in particles:
		ctfscores.append(float(p[0]))
		meritscores.append(float(p[1]))
		Du.append(float(p[2]))
		Dv.append(float(p[3]))
		Da.append(float(p[4]))
		j+= 1
	plt.subplot(411)
	n, bins, patches = plt.hist(ctfscores, bins=80)
	plt.ylabel('Frequency')
	title = 'checkMicrographs.py output: ' + str(micrograph) + ', ' + str(j) + ' micrographs'
	plt.title(title)
	xaxis = plt.xlim()

	plt.subplot(412)
	plt.axis([xaxis[0],xaxis[1], min(meritscores), max(meritscores)])
	plt.plot(ctfscores,meritscores, 'g^')

	correlation = stats.linregress(ctfscores,meritscores)
	rsq = correlation[2]**2

	x = numpy.arange(min(ctfscores)-0.2,max(ctfscores)+0.2,0.001)
	ycoords = [correlation[0] * i + correlation[1] for i in x]
	plt.plot(x, ycoords, 'b', label = 'R-squared: ' + str(rsq))
	plt.legend(bbox_to_anchor=(1, 1))
	#plt.xlabel('Micrograph estimated resolution')
	plt.ylabel('Micrograph FOM')

	plt.subplot(413)
	plt.axis([xaxis[0],xaxis[1], min(Da), max(Da)])
	plt.plot(ctfscores,Da, 'g^')

	correlation = stats.linregress(ctfscores,Da)
	rsq = correlation[2]**2

	x = numpy.arange(min(ctfscores)-0.2,max(ctfscores)+0.2,0.001)
	ycoords = [correlation[0] * i + correlation[1] for i in x]
	plt.plot(x, ycoords, 'b', label = 'R-squared: ' + str(rsq))
	plt.legend(bbox_to_anchor=(1, 1))
	#plt.xlabel('Micrograph estimated resolution')
	plt.ylabel('Defocus angle')

	plt.subplot(414)
	rmsDistVals = []
	t = 0
	while t<len(Du):
		rmsv = (((Du[t])**2) + ((Dv[t])**2))**0.5
		rmsDistVals.append(rmsv)
		t+=1

	plt.axis([xaxis[0],xaxis[1], min(rmsDistVals), max(rmsDistVals)])
	plt.plot(ctfscores,rmsDistVals, 'g^')

	correlation = stats.linregress(ctfscores,rmsDistVals)
	rsq = correlation[2]**2

	x = numpy.arange(min(ctfscores)-0.2,max(ctfscores)+0.2,0.001)
	ycoords = [correlation[0] * i + correlation[1] for i in x]
	plt.plot(x, ycoords, 'b', label = 'R-squared: ' + str(rsq))
	plt.legend(bbox_to_anchor=(1, 1))
	plt.xlabel('Micrograph estimated resolution')
	plt.ylabel('RMS of defocus U/V')

	'''
	Don't use this normally - see the text above "compute iterativity" above for why. Also set the subplots above to 511,512,513,and 514 if you are using this)
	axs = plt.subplot(515)
	axs.axis('off')
	row_label = ("Average distortion","Distortion 2x2","Distortion 3x3")
	data = computeIterativity(particles)
	nd = []
	nd.append([data[0]] + ([0]*8))
	nd.append(data[1] + ([0]*5))
	nd.append(data[2])
		
	print nd
	table = axs.table(cellText = nd, loc = 'center', rowLabels=row_label)#, #colLabels=col_label, loc='center')
	table.auto_set_font_size(False)
	table.set_fontsize(12)
	'''

	plt.show()
	
if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	plotMeritOfParticles(starf)


