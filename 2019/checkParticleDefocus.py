#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2019

#Plots the number of particles per micrograph versus the average defocus value for particles from that micrograph. Also plots a histogram of the average micrograph defocus values (average of all particles from said micrograph). Useful to evaluate whether or not you have collected enough low-defocus information, and how many particles have been picked accross different defocus thresholds.

import sys, os
import string
import random
import numpy as np
import matplotlib
from scipy import stats
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

DU = '_rlnDefocusU'
DV = '_rlnDefocusV'
mic_name = '_rlnMicrographName'
attributes = [DU,DV,mic_name]

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
	
#returns the header and good particles from a CtfRefine output starfile	
def getData(starfile):
	DU_col = 0
	DV_col = 0
	micrograph_names = {}
	header = []
	with open(starfile) as sf:
		lines = sf.readlines()
		data = getHeader(lines)
		header = data[2]
		file_body = data[1]
		DU_col = data[0][DU]-1
		DV_col = data[0][DV]-1
		micrograph_name_col = data[0][mic_name]-1
		for l in file_body:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []:
				if data[micrograph_name_col] in micrograph_names:
					micrograph_names[data[micrograph_name_col]].append(data)
				else:
					micrograph_names[data[micrograph_name_col]] = [data]
	plotCtfdata(micrograph_names,DU_col,DV_col)

#plots particle number per group versus std for those paricles
def plotCtfdata(micrograph_names,DU_col,DV_col):
	numparticles = []
	particlesstd = []
	micrograph_defocus = []
	overall_average = 0.0
	total_counter = 0.0
	for mic in micrograph_names:
		particles=micrograph_names[mic]
		numparticles.append(len(particles))
		vals = []
		counter = 0
		for p in particles:
			counter += 1
			total_counter += 1
			vals.append((float(p[DU_col]) + float(p[DV_col]))/2.0)
		micrograph_defocus.append(np.average(vals))
		overall_average += ((np.average(vals)) * counter)
	print "Average defocus: " + str(overall_average / total_counter)

	plt.subplot(211)
	n, bins, patches = plt.hist(micrograph_defocus, bins=80)
	plt.ylabel('Frequency')
	plt.xlabel('Average micrograph defocus from per-particle Ctf estimation')
	xaxis = plt.xlim()


	plt.subplot(212)
	plt.axis([0,max(numparticles), min(micrograph_defocus), max(micrograph_defocus)])
	plt.plot(numparticles,micrograph_defocus, 'g^')
	plt.ylabel('Average of particle defocus')
	plt.xlabel('Number of particles per micrograph')

	plt.subplots_adjust(wspace=0.7)
	
	plt.show()

if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	results = getData(starf)

#eof
