#!/bin/python2.7
#(C)Ian Outhwaite, Long Lab, MSKCC 2018

#Removes particles near edge of micrograph, distance defined by user in command line (in pixels)
#Ex: python removeEdgeParticles picked_particles.star 200

import sys, os
import string
import random
import numpy as np

xcor = '_rlnCoordinateX'
ycor = '_rlnCoordinateY'
attributes = [xcor,ycor]

max_xcor = 3710 #MAY NEED TO BE CHANGED BY USER
max_ycor = 3838 #MAY NEED TO BE CHANGED BY USER

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
def remove_outliers(starfile,edge_dist):
	xcorcol = 0
	ycorcol = 0
	num_particles = 0.0
	num_bad_particles = 0.0
	good_particles = []
	header = []
	with open(starfile) as sf:
		lines = sf.readlines()
		data = getHeader(lines)
		header = data[2]
		file_body = data[1]
		xcorcol = data[0][xcor]-1
		ycorcol = data[0][ycor]-1
		for l in file_body:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []:
				num_particles += 1
				particle_xcor = float(data[xcorcol])
				particle_ycor = float(data[ycorcol])
				if ((particle_xcor < edge_dist or particle_xcor > (max_xcor-edge_dist)) or (particle_ycor < edge_dist or particle_ycor > (max_ycor-edge_dist))):
					num_bad_particles +=1
				else:
					good_particles.append(data)
	return (header,good_particles)
	
#main method wrtes data to new file with random partial extension to prevent accidental file overwriting
if __name__ == '__main__':
	args = sys.argv[1:]
	starf = args[0]
	distance = args[1]
	results = remove_outliers(starf,distance)
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
