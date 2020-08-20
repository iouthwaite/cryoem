#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2018

#for a CtfRefine "particles_ctf_refine.star" file: returns the "good" particles that are not deviant from statistical norms
#User can enter the number of standard deviations away from the mean that they want to retain particles within, for the defocus values of a single micrograph
#Particle defocus is defined in this script as ( ( _rlnDefocusU + _rlnDefocusV ) / 2 )

'''
Users need to hard-set certain values in the program
* NUM_STANDARD_DEVIATIONS refers to the number of standard deviations of per-particle defocus values for a given micrograph, outside of which outliers will be removed. Ex: a micrograph with a defocus standard deviation (calculated from the particles for that micrograph) greater or less than than 1.75 standard deviation from the average of other micrographs' defocus standard deviations will be excluded. Basically, getting rid of micrographs with a high amount of defocus variance.
* min_particles refers to the minimum number of particles needed to apply this deviation method - if there are too few particles a micrograph will naturally have higher statistical deviance and you may want to exclude it and keep all the data
* maximum_allowed_defocus_deviation refers to a hard cutoff applied to all micrographs; if the standard deviation of defocus values for a micrograph is higher than this value, no particles from that micrograph will be included (basically saying there is something wrong with too much of the data to let it pass)

How to use:
If you want to remove outliers from single micrographs, set min_particles to 0, NUM_STANDARD_DEVIATIONS to your desired value, and the maximum_allowed_defocus_deviation very high
If you want to remove outlier micrographs of "worse data," set min_particles very high and the maximum_allowed_defocus_deviation to your desired threshold
'''

import sys, os
import string
import random
import numpy as np

DU = '_rlnDefocusU'
DV = '_rlnDefocusV'
mic_name = '_rlnMicrographName'
attributes = [DU,DV,mic_name]

#user can hard-set this value as desired
NUM_STANDARD_DEVIATIONS = 1.75 #minimum numer of standard deviations
min_particles = 50000000 #minimum particles per micrograph to remove outliers
maximum_allowed_defocus_deviation = 600

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

#returns the "good" particles from a group of particles
def getGood(particles,DU,DV):
	good_p = []
	vals = []
	for p in particles:
		vals.append((float(p[DU]) + float(p[DV]))/2.0)
	m = np.mean(vals)
	sd = np.std(vals)
	for p in particles:

		#### THIS IS WHERE PER PARTICLE DEFOCUS COMPARISONS COME FROM
		defocus = ((float(p[DU]) + float(p[DV]))/2.0) 
		if (np.abs(defocus - m) < (NUM_STANDARD_DEVIATIONS*sd)):
			good_p.append(p)

	return good_p

def checkAverageDefocus(particles,max_std,DU,DV):
	defocus_vals = []
	for p in particles:
		defocus_vals.append(((float(p[DU]) + float(p[DV]))/2.0))
	standard_dev = np.std(defocus_vals)
	average = np.average(defocus_vals)
	if (standard_dev >= max_std): 
		return False
	else:
		return True
	
#returns the header and good particles from a CtfRefine output starfile	
def remove_outliers(starfile):
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
	good_particles = []
	for f in micrograph_names:
		#if a micrograph has more than "min_particles" particles, apply a cutoff
		l = len(micrograph_names[f])
		if l > min_particles:
			good_particles+=(getGood(micrograph_names[f],DU_col,DV_col))
		else: #else remove if the standard deviation for the particles is too high
			if checkAverageDefocus(micrograph_names[f],maximum_allowed_defocus_deviation,DU_col,DV_col) == True:
				good_particles+=(micrograph_names[f])
	return (header,good_particles)
	
#main method wrtes data to new file with random partial extension to prevent accidental file overwriting
if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	results = remove_outliers(starf)
	filename = 'resultfile_' + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))
	newf = open(filename,'w')
	for l in results[0]: # the header
		newf.write(l)
	for p in results[1]: # the particles
		s = (' '.join(p))[:-1] + '\n'
		newf.write(s)
	print 'Retained ' + str(len(results[1])) + ' particles'
	print 'Resultfile named: ' + str(filename)

#eof
