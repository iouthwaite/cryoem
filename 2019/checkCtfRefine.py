#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2019

#for a CtfRefine "particles_ctf_refine.star" file: plots number of particles per micrograph versus standard deviation of defocus values, per micrograph
#Particle defocus is defined in this script as ( ( _rlnDefocusU + _rlnDefocusV ) / 2 )

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
	
#getData
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
	for mic in micrograph_names:
		particles=micrograph_names[mic]
		numparticles.append(len(particles))
		vals = []
		for p in particles:
			vals.append((float(p[DU_col]) + float(p[DV_col]))/2.0)
		particlesstd.append(np.std(vals))
	plt.subplot(111)
	plt.axis([0,max(numparticles), min(particlesstd), max(particlesstd)])
	plt.plot(numparticles,particlesstd, 'g^')
	plt.ylabel('Std of particle defocus')
	plt.xlabel('Number of particles per micrograph')
	plt.show()

if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	results = getData(starf)

#eof
