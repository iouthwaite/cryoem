#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2019

#for refined particles file: prints plots of the refinment angle distributions

#python checkParticleAngles.py starfile.star num_bins

import sys, os
import string
import random
import numpy as np
import matplotlib
from scipy import stats
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

psi = '_rlnAnglePsi'
rot = '_rlnAngleRot'
tilt = '_rlnAngleTilt'
attributes = [psi,rot,tilt]

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

def get_angles(starfile,bin_num):

	psi_angles = []
	rot_angles = []
	tilt_angles = []
	all_particles = []

	with open(starfile) as sf:
		lines = sf.readlines()
		header_info = getHeader(lines)
		columns = header_info[0]
		psi_col = int(columns[psi])-1
		rot_col = int(columns[rot])-1
		tilt_col = int(columns[tilt])-1

		file_body = header_info[1]
		for l in file_body:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []: #is a particle
				p_psi = float(data[psi_col]) 
				p_rot = float(data[rot_col])
				p_tilt = float(data[tilt_col])
				psi_angles.append(p_psi)
				rot_angles.append(p_rot)
				tilt_angles.append(p_tilt)
				all_particles.append((p_psi,p_rot,p_tilt))

	plt.subplot(311)
	n, bins, patches = plt.hist(psi_angles, bins=bin_num)
	plt.ylabel('Frequency')
	xaxis = plt.xlim()

	plt.subplot(312)
	n, bins, patches = plt.hist(rot_angles, bins=bin_num)
	plt.ylabel('Frequency')
	xaxis = plt.xlim()

	plt.subplot(313)
	n, bins, patches = plt.hist(tilt_angles, bins=bin_num)
	plt.ylabel('Frequency')
	plt.xlabel('top: PSI, middle: ROT, bottom: TILT')
	xaxis = plt.xlim()

	plt.show()

#main method wrtes data to new file with random partial extension to prevent accidental file overwriting
if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	bins = int(args[1])
	results = get_angles(starf,bins)

#eof
