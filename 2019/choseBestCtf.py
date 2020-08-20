#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

#for a group of micrographs.star files: prints out best estimated resolution lines, using header from the first file

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
micname = "_rlnMicrographName"
Ctfvalue = "_rlnCtfMaxResolution"
attributes = [maxres,meritnum,DU,DV,DA,micname,Ctfvalue]

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

def getBestCtf(files):
	micrographs = {}
	header = []
	for f in files:
		with open(f) as sf:
			lines = sf.readlines()
			headerparse = getHeader(lines)
			datalines = headerparse[1]
			columns = headerparse[0]
			header = headerparse[2]
			micnamecol = int(columns["_rlnMicrographName"]) - 1
			Ctfval = int(columns["_rlnCtfMaxResolution"]) - 1
			for l in datalines:
				ldat = filter(lambda a: a != '', (l.split(' ')))
				if len(ldat) > 2:
					if ldat[micnamecol] in micrographs:
						if ldat[Ctfval] < micrographs[ldat[micnamecol]][1][Ctfval]:
							#print 'REPLACING HERE'
							#print 'OLD CTF: ' + str(micrographs[ldat[micnamecol]][1][Ctfval])
							#print 'NEW CTF: ' + str(ldat[Ctfval]) 
							micrographs[ldat[micnamecol]] = [l,ldat]
							#print micrographs[ldat[micnamecol]]
					else:
						micrographs[ldat[micnamecol]] = [l,ldat]
	return (header,micrographs)
	
if __name__ == '__main__':
	args = sys.argv[1:]
	values = getBestCtf(args)
	newf = open("micrographs_ctf.star_best","wr+")
	for l in values[0]:
		newf.write(l)
	for v in values[1]:
		newf.write(values[1][v][0])
	newf.close()
