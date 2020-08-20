#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2019

#for a CtfRefine "particles_ctf_refine.star" file: returns the estimated Ctf values to the original values from micrograph-wide Ctf estimation
#run using: python particles.star original_micrograph_ctfs.star

import sys, os
import string
import random
import numpy as np

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
def revert_Ctfs(starfile,original_ctf_file):
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
		sf.close()
	original_ctf_vals = {}
	with open(original_ctf_file) as ocf:
		lines = ocf.readlines()
		data = getHeader(lines)
		ctfs_header = data[2]
		file_body = data[1]
		original_DU_col = data[0][DU]-1
		original_DV_col = data[0][DV]-1
		micrograph_name_col = data[0][mic_name]-1
		for l in file_body:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []:
				original_ctf_vals[data[micrograph_name_col]] = (data[original_DU_col],data[original_DV_col])
		ocf.close()
	fixed_particles = []
	for mic in micrograph_names:
		original_DU_val = original_ctf_vals[mic][0]
		original_DV_val = original_ctf_vals[mic][1]
		for particle in micrograph_names[mic]:
			particle[DU_col] = original_DU_val
			particle[DV_col] = original_DV_val
			fixed_particles.append(particle)
	return (header,fixed_particles)
	
#main method wrtes data to new file with random partial extension to prevent accidental file overwriting
if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	original_ctfs = args[1]
	results = revert_Ctfs(starf,original_ctfs)
	filename = 'resultfile_' + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))
	newf = open(filename,'w')
	for l in results[0]: # the header
		newf.write(l)
	for p in results[1]: # the particles
		s = (' '.join(p))[:-1] + '\n'
		newf.write(s)
	print 'Changed ' + str(len(results[1])) + ' particles'
	print 'Resultfile named: ' + str(filename)

#eof
