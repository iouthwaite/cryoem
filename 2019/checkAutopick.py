#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

#for a single micrograph: prints out a plot describing the distribtion of merit for picked particles, with breakdown by the classes those particles were assigned to, following 2D classification

import sys, os
import string
import random
import numpy
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
#matplotlib.rcParams['interactive'] = True

xcord = '_rlnCoordinateX'
ycord = '_rlnCoordinateY'
classNum = '_rlnClassNumber'
merit = '_rlnAutopickFigureOfMerit'
psi = '_rlnAnglePsi'
attributes = [xcord,ycord,classNum,merit,psi]

#gets the header of a star file, returns the columns in the file that the xcor,ycor,classNum and merit fall into in dictionary form
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
		
#input: a star file of an autopicked micrograph
#output: a list of particles, format [xcor,ycord,classNum,merit]
def importStarfile(starfile):
	particles = []
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
				xcor = data[columns['_rlnCoordinateX']-1]
				ycor = data[columns['_rlnCoordinateY']-1]
				cNum = data[columns['_rlnClassNumber']-1]
				mert = data[columns['_rlnAutopickFigureOfMerit']-1]
				ps = data[columns['_rlnAnglePsi']-1]
				particles.append([xcor,ycor,cNum,mert])
	return particles

#calculates the min, mean, max and std of merit for a list of particles from a picked micrograph
def calcMeritDistribution(particles):
	numbers = []
	for p in particles:
		numbers.append(float(p[3]))
	std = numpy.std(numbers)
	return (min(numbers),numpy.mean(numbers),max(numbers),std)

#orders micrographs from worst to best according to average merit score of picked particles.
#output = a list of [micrograph name, z-score, average merit of picked particles] for all micrographs
def compareMicrographs(micrographs):
	mscores = []
	for m in micrographs:
		particles = importStarfile(m)
		if particles != []:
			data = calcMeritDistribution(particles)
			mscores.append((str(m), data[1]))
	output = sorted(mscores, key=lambda x: x[1])
	return output
	
#plots the distrbution of merit scores for all particles accross all micrographs
def plotMeritOfAllParticles(micrographs):
	mscores = []
	for m in micrographs:
		particles = importStarfile(m)
		for p in particles:
			mscores.append(float(p[3]))
	n, bins, patches = plt.hist(mscores, bins=30)
	plt.xlabel('Particle Merit Score')
	plt.ylabel('Frequency')
	plt.title('Histogram of particle merit scores')
	plt.show()

#plots the distribution of merit scores for a single micrograph
def plotMeritOfParticles(micrograph):
	mscores = []
	particles = importStarfile(micrograph)
	for p in particles:
		mscores.append(float(p[3]))
	n, bins, patches = plt.hist(mscores, bins=30)
	plt.xlabel('Particle Merit Score')
	plt.ylabel('Frequency')
	title = 'Histogram of particle merit scores: ' + str(micrograph)
	plt.title(title)
	plt.show()
	
#creates a new file with the coordinates of particles with very high merit scores (potentially ice)
def newHighMFile(micrograph):

	mscores = []
	particles = importStarfile(micrograph)
	for p in particles:
		mscores.append(float(p[3]))
	mean = numpy.mean(mscores)
	std = numpy.std(mscores)
	thresh = mean + (2.5*std)
	print mean, std, thresh

	output = []

	with open(micrograph) as f:
		lines = f.readlines()
		fileparse = getHeader(lines)
		datalines = fileparse[1]
		header = fileparse[2]
		for temp in header:
			output.append(temp)
		columns = fileparse[0]
		for l in datalines:
			dat = l.strip().split(' ')
			data = [x.strip() for x in dat if x] 
			if data != []:
				mert = data[columns['_rlnAutopickFigureOfMerit']-1]
				if (float(mert) > thresh):
					output.append(l)
	print output
	return output
	
if __name__ == '__main__':
	args = sys.argv[1:]

	if args[0] == '-p': #if first agrument is -p we are checking a particles file, if -d then we're going to compare all the particle files in a given directory
		particles = importStarfile(args[1]) #second argument is the particles file
		print 'Micrograph name: ' + str(args[1])
		print calcMeritDistribution(particles)

	elif args[0] == '-pi': #we are going to image the distribution of merit scores for particles in a single micrograph
		plotMeritOfParticles(str(args[1]))

	elif args[0] == '-pn': #create a new file with the coordinates of particles with very high merit scores
		output = newHighMFile(args[1])
		newfname = 'poorParticles_'+str(args[1])
		newf = open(newfname,'w')
		for line in output:
			newf.write(line)
		newf.close()

	elif args[0] == '-d': #we are going to find the worst micrographs in a given directory
		os.chdir('./'+str(args[1]))
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		results = compareMicrographs(files)
		for o in results:
			print o

	elif args[0] == '-di': #image the distribution of merit scores for all micrographs
		os.chdir('./'+str(args[1]))
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		plotMeritOfAllParticles(files)

	

	elif args[0] == '-dn': #makes a new folder and puts in the files of the lists of particles with very high merit scores
		datafolder = args[1]
		cwd = os.getcwd()
		newdirname = 'Micrographs_' + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))
		newfiles = []
		os.chdir('./'+datafolder)
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		print files
		for f in files:
			print f
			newfiles.append((str(f),newHighMFile(f)))
		os.chdir('./..')
		os.mkdir(newdirname)
		os.chdir('./'+newdirname)
		for f in newfiles:
			newf = open(f[0],'w')
			for l in f[1]:
				newf.write(l)
			newf.close()
		os.chdir('./..')

#eof
		
			
		
	
