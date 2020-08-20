#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

# motionSelection.py is a program designed to allow a user to remove a subset of micrographs (or particles) from a dataset.
#
# Required files:
# 1. MotionCor path to logfile
# 2. The prefix of the micrographs (Ex: "IO26A_" for IO26A_0001, IO26A_0002 etc.)
#
# Program flags. Use all flags sequentially after the prefix parameter, as the third argument. The order does not matter.
#
# "-t" flag will set the maximum threshold of movement (in A) for output from the program at the argument following the flag
# ex: "-t 100" will set the threshold to 100A. The program default is 50A.
# 
# "-o" flag will tell the program to output the names of the micrographs with less than the threshold limit of movement to a new text file. 
# This file will be named "Good_micrograph_names_****" Where "*" represents a random alphanumeric character. 
# Each micrograph name will be listed on a new line. 
#
# "-h" flag will tell the program to output histograms and dot plots of the data in a single figure
#
# "-a" flag will tell the program to calculate movement for the micrographs based upon the absolute total difference between the first and last frames. 
# This is not reccomended since it can hide micrographs with lots of movement that end up near the same start position.
# The program default is to calculate movement for micrographs based upon the sum of the differences in position between each frame (stepwise-total movement).
#
# IN PROGRESS: "-s" flag will print out a dot plot with the average stepwise-total movement between that frame and the frame previous (so for 3 frames ABC, only frames B and C will have values)
#
# IMPORTANT: You MUST input the number of frames as the third argument. Flags MUST be the fourth argument, and changes to the movement threshold (after -t) must be the fifth argument.
#
# Example program input: 
# python motionSelection.py logfile prefix 46 -tho 75
# python motionSelection.py logfile prefix 46
#


import glob, os, sys, numpy, shutil, tempfile, random, string
import matplotlib
from scipy import stats
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

# Single method from stackoverflow: 
# https://stackoverflow.com/questions/4847615/copying-a-symbolic-link-in-python
def copy(src, dst):
    if os.path.islink(src):
        linkto = os.readlink(src)
        os.symlink(linkto, dst)
    else:
        shutil.copy(src,dst)

#returns the lines in a file, as well as a list of the line components that are seperated by whitespace on the line
def parsefilelines(file):
	data = []
	lines = file.readlines()
	for l in lines:
		val = l.strip().split(' ')
		entry_no_whitespace = [x.strip() for x in val if x] 
		data.append((l,entry_no_whitespace))
	return data

#plots a histogram of the distribution of total movement for the micrographs according to absolute total movement (last frame - first frame) and stepwise totals (differences between sequential frames summed iteratively for all frames)
#also plots a dot plot of the ranks for each micrograph relative to all other micrographs. Data that skews a linnear relationship between the ranks represents micrographs with lots of movement where the first and last frames are not relatively distant.
def plotDistances(absolute_distances,total_distances,rank_data):

	fig = plt.figure(facecolor='white')

	plt.subplot(311)
	n, bins, patches = plt.hist(absolute_distances, bins=80)
	plt.ylabel('Frequency')
	plt.xlabel('Absolute-Total Movement of Global Frame Alignments')
	xaxis = plt.xlim()

	plt.subplot(312)
	n, bins, patches = plt.hist(total_distances, bins=80)
	plt.ylabel('Frequency')
	plt.xlabel('Stepwise-Total Movement of Global Frame Alignments')
	xaxis = plt.xlim()

	plt.subplot(313)
	x_absolute_data = []
	y_step_data = []
	limit = len(rank_data)
	for entry in rank_data:
		x_absolute_data.append(entry[0])
		y_step_data.append(entry[1])
	plt.axis([-20,limit+20,-20,limit+20])
	plt.plot(x_absolute_data,y_step_data, 'g^')

	correlation = stats.linregress(x_absolute_data,y_step_data)
	rsq = correlation[2]**2

	x = numpy.arange(min(x_absolute_data)-0.2,max(x_absolute_data)+0.2,0.001)
	ycoords = [correlation[0] * i + correlation[1] for i in x]
	plt.plot(x, ycoords, 'b', label = 'R-squared: ' + str(rsq))
	plt.legend(bbox_to_anchor=(1, 1))
	plt.xlabel('Absolute-Total Rank')
	plt.ylabel('Stepwise-Total Rank')

	plt.tight_layout()

	plt.show()

#STEPWISE TOTAL DISTANCE OF MICROGRAPHS
#maxmvmnt is the maximum allowable movement in Angstroms for the micrographs; anything over this value will be excluded. Movement is calculated as sum of differences of steps in movemnet between each frame up to the maximum frame number
#Aka this calculates the step-wise total movement for the microgaphs (sum of differences in positions between sequential frames, for all frames)
def getLow_TOTAL_MvmntMicrographNames(data,prefix,maxmvmnt,framenumber):
	currentfile = ''
	prefix_len = len(prefix)
	good_micrographs = []
	poor_micrographs = []
	nummics = 0
	distances = []
	name_dist = []
	last_xcor = 0
	last_ycor = 0
	dist = 0
	for line in data:
		if line[0][:prefix_len] == prefix:
			current_micrograph = line[1][0]
			last_xcor = 0
			last_ycor = 0
			dist = 0
		if (line[0][:14] == '...... Frame ('):
			xcor = float(line[1][5])
			ycor = float(line[1][6])
			dx = xcor - last_xcor
			dy = ycor - last_ycor
			last_xcor = xcor
			last_ycor = ycor
			dist = dist + (((dx**2)+(dy**2))**0.5)
			if line[1][3][:2] == str(framenumber):
				distances.append(dist)
				name_dist.append((current_micrograph,dist))
				if dist <= maxmvmnt:
					nummics += 1
					good_micrographs.append(current_micrograph)
				else:
					poor_micrographs.append(current_micrograph)
	print 'num mices: ' + str(nummics)
	return [good_micrographs,poor_micrographs,distances,name_dist]

def getAverageFrameMvmnt(data,prefix):
	prefix_len = len(prefix)
	frames = {}
	last_xcor = 0
	last_ycor = 0
	for line in data:
		if line[0][:prefix_len] == prefix:
			last_xcor = 0
			last_ycor = 0
		if (line[0][:14] == '...... Frame ('):
			frame = str(line[1][3][:2])
			print 'Frame: ' + frame
			xcor = float(line[1][5])
			ycor = float(line[1][6])
			dx = xcor - last_xcor
			dy = ycor - last_ycor
			last_xcor = xcor
			last_ycor = ycor
			dist = dist + (((dx**2)+(dy**2))**0.5)
			frames[frame] = frames.get[frame, []].append(dist)
	return frames

#ABSOLUTE DISTANCE TOTAL TRAVELLED
#maxmvmnt is the maximum allowable movement in Angstroms for the micrographs; anything over this value will be excluded. Movement is calculated as total absolute distance for the given frame number.
#Aka this calculates the absolute total difference between the position of the first frame and the last frame. The first frame is assumed to be 0,0.
def getLowMvmntMicrographNames(data,prefix,maxmvmnt,framenumber):
	currentfile = ''
	prefix_len = len(prefix)
	good_micrographs = []
	poor_micrographs = []
	distances = []
	name_dist = []
	for line in data:
		if line[0][:prefix_len] == prefix:
			current_micrograph = line[1][0]
		if (line[0][:12] == '...... Frame') and (line[1][3][:2] == str(framenumber)):
			mvmnt_x = float(line[1][5])
			mvmnt_y = float(line[1][6])
			dist = ((mvmnt_x**2)+(mvmnt_y**2))**0.5
			distances.append(dist)
			name_dist.append((current_micrograph,dist))
			if dist <= maxmvmnt:
				good_micrographs.append(current_micrograph)
			else:
				poor_micrographs.append(current_micrograph)
	return [good_micrographs,poor_micrographs,distances,name_dist]


#Legacy method that copies data from a micrograph folder to a new folder based upon good micrograph names. Not used in program but kept around in case it is needed someday.
def copyGoodMicrographsToNewFolder(good_micrograph_names,cwd,original_micrographs):
	#first make a folder for the good micrographs
	directory = cwd + '/Good_Micrographs_' + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))
	if not os.path.exists(directory):
		os.makedirs(directory)
	c = 0 #where c is the number of files copied
	#copy the .mrc and _stk.mrcs files to the new directory
	for f in os.listdir(cwd+'/'+original_micrographs):
		fname = f
		if f[-9:] == '_stk.mrcs': #if it is the stack, we need to change the last part of the name to make sure it gets matched currectly
			fname = f[:-9] + '.mrc'
		if fname in good_micrograph_names:
			src = cwd+'/'+original_micrographs+'/'+f
			copy(src,directory+'/'+f)
			c+=1
	return (directory+'/', c)

#formats the data so that the plotDistances method can access it easilly. Also ranks the micrographs based upon the two movement metrics.
def generateDotPlotData(name_dist_absolute,name_dist_stepwise):
	rank_absolute = []
	rank_step = []
	tuples_rankAbsolute_rankStep = []
	absolute_sorted = sorted(name_dist_absolute, key=lambda tup: tup[1])
	step_sorted = sorted(name_dist_stepwise, key=lambda tup: tup[1])
	c  = 0
	while c<len(absolute_sorted):
		rank_absolute.append((c,absolute_sorted[c]))
		c+=1
	c = 0
	while c<len(step_sorted):
		rank_step.append((c,step_sorted[c]))
		c+=1
	for i in rank_absolute:
		match = [j for j in rank_step if j[1][0] == i[1][0]]
		tuples_rankAbsolute_rankStep.append((i[0],match[0][0]))
	return tuples_rankAbsolute_rankStep

#write the names of micrographs to a text file
def writeGoodNamesToFile(gnames):
	name = "Good_micrograph_names_" + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))
	f = open(name, 'w')
	for name in gnames:
		f.write(name + '\n')
	f.close

#main portion of program
if __name__ == '__main__':

	output = 0
	mvmnt_thresh = 50
	hist = 0
	step_total = 1
	calc_steps = False

	args = sys.argv[1:]
	logfile = args[0] #the logfile is the first argument
	micrograph_prefix = args[1] #the prefix used for micrograph names is the second argument
	frames = args[2]
	if len(args) > 2:
		flags = list(args[3])
		if flags[0] == '-':
			for flag in flags:
				if flag == 'o':
					output = 1
				if flag == 'h':
					hist = 1
				if flag == 't':
					mvmnt_thresh = float(args[4])
				if flag == 'a':
					step_total = 0
				if flag == 's':
					calc_steps = True
	
	lfile = open(logfile,'rw+')
	logfile_data = parsefilelines(lfile)

	print
	print 'Number of frames in movies: ' + str(frames)
	print 'Threshold to use: ' + str(mvmnt_thresh)
	print

	#format: goodnames, poornames, distances, rank_data
	data_stepwise = getLow_TOTAL_MvmntMicrographNames(logfile_data,micrograph_prefix,mvmnt_thresh,frames)
	data_absolute = getLowMvmntMicrographNames(logfile_data,micrograph_prefix,mvmnt_thresh,frames)

	if calc_steps:
		frames = getAverageFrameMvmnt(logfile_data,micrograph_prefix)
		print frames

	total_mics_step = len(data_stepwise[2])
	total_mics_absolute = len(data_absolute[2])

	name_dist_absolute = data_absolute[3]
	name_dist_stepwise = data_stepwise[3]

	if hist == 1:
		rank_data = generateDotPlotData(name_dist_absolute,name_dist_stepwise)
		plotDistances(data_absolute[2],data_stepwise[2],rank_data)

	if output == 1:
		fc = 0
		if step_total == 1:
			fc = len(data_stepwise[0])
			writeGoodNamesToFile(data_stepwise[0])
		else:
			fc = len(data_absolute[0])
			writeGoodNamesToFile(data_absolute[0])
		print 'New file contains names of: ' + str(fc) + ' micrographs'
#EOF
