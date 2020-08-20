#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

#Takes input of a star file
#Finds the micrographs referred to in the star file using the "_rlnMicrographName" tag from the header
#Program opens each micrograph, and following a user command and the ENTER key ('['=good or 'p'=bad keys) sorts the data referred to by the line in the star file to a new star file, [ (Right) = good data, p (Left) = poor data, q quits the selection and prints out the starfiles, or if you work down the entire list, the new starfiles are printed at the very end.

#example command: python starSwiper.py /pathtomicrographstarfile /pathtorelionfolder

#HOWEVER don't run this when you're looking at other images using imod, this will cause those programs to exit.

#GOOD = '[' (or just hit enter)
#POOR = 'p'

import sys
import string
import random
import os
import subprocess
import signal
from subprocess import Popen

mgName = '_rlnMicrographName'

#gets the header of a .star file, and returns all the lines following the header as well
def getHeader(file):
	header = []
	lines = file.readlines()
	inUnderscores = 0
	i = 0
	while i<len(lines):
		if lines[i][0] == '_':
			if inUnderscores == 0:
				inUnderscores = 1
		else:
			if inUnderscores == 1:
				header = lines[:i]
				break
		i+=1
	restoffile = lines[i:]
	return header, restoffile	

#parses lines split by any number of whitespace characters
def parsefilelines(lines):
	data = []
	for l in lines:
		val = l.strip().split(' ')
		entry_no_whitespace = [x.strip() for x in val if x] 
		data.append((l,entry_no_whitespace))
	return data

#finds the correct column that the information for the micrograph locations are stored in
def getMicrographColumn(header):
	for entry in header:
		val = entry.strip().split(' ')
		entry_no_whitespace = [x.strip() for x in val if x] 
		if len(entry_no_whitespace) > 1:
			if entry_no_whitespace[0] == mgName:
				return int(entry_no_whitespace[1][1:])-1
		elif len(entry_no_whitespace) == 1:
			if entry_no_whitespace[0] == mgName:
				return 0
	
if __name__ == '__main__':

	inttostart = 0
	#user commands, starfile is the first, path to the original relion directory is second.
	args = sys.argv[1:]
	starfilename = args[0]
	relionPath = args[1]
	if len(args) > 2:
		inttostart = int(args[2])-1
	originalDirectory = os.getcwd() #save the path for the directory we're in for future reference

	goodlines = [] #the lines referring to good micrographs from the original starfile
	poorlines = [] #the lines referring to poor micrographs from the original starfile
	header = [] #the original starfile header

	print '\nProgram commands: enter for good micrographs, p and then enter for poor micrographs, and q to quit the program\n'
	
	with open(starfilename) as sf:

		#get the header of the original file, as well as all the data lines under the header
		header, filelines = getHeader(sf)

		#find out which column refers to the path to the original micrographs
		mgCol = getMicrographColumn(header)

		#parse the data lines to remove whitespace
		lines = parsefilelines(filelines)
		i = 0
		if inttostart != 0:
			i = int(inttostart)

		#for every bit of data in the starfile...
		while i<len(lines):

			print 'Looking at micrograph: ' + str(i+1) + ' of ' + str(len(lines)+1)
			line = lines[i][0] #the data in the line
			pathToMic = lines[i][1][mgCol] #the path to the micrograph referred to in the line
			folder = '/'.join(pathToMic.split('/')[:-1])+'/' #the folder the micrograph is in
			print folder
			filename = pathToMic.split('/')[-1] #the name of the micrograph file
			fullpath = relionPath + '/' + folder #the fullpath to the folder
			os.chdir(fullpath)
			print 'Micrograph name: ' + str(filename)
		
			#open up a new 3dmod process to visualize the micrograph
			p = subprocess.Popen(['/programs/x86_64-linux/imod/4.7.15/bin/imod',filename])
			x = raw_input("Enter a Command: ")
			print 'Input was: ' + str(x)

			#if we want to quit the program prematurely
			if x=='q':
				os.system('pkill -f /programs/x86_64-linux/imod/4.7.15/')
				p.kill()
				print '\nQuitting micrograph selection\n'
				break

			#if we don't like the micrograph, add the data referring to it from the starfile to our colelction of good lines
			elif x=='p':
				print 'Sent to poor micrographs\n'
				poorlines.append(line)

			#if we like the micrograph, add the data referring to it from the starfile to our colelction of good lines
			else:
				print 'Sent to good micrographs\n'
				goodlines.append(line)

			#quit all processes of imod to get rid of extra windows every 5 images
			if i%5 == 0:
				os.system('pkill 3dmod')
				p.kill()

			#go back to the original directory we started from
			os.chdir(originalDirectory)
			i+=1

	#make sure we're in the right place
	os.chdir(originalDirectory)

	#make a random four-character alpha-numeric indentifier for our output to make sure it doesn't get overwritten by accident
	suffix = ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))

	#name our output files
	gname = 'Good_Micrographs_' + suffix
	pname = 'Poor_Micrographs_' + suffix
	goodsf = open(gname,'w')
	poorsf = open(pname,'w')

	#write the header to both files
	for l in header:
		goodsf.write(l)
		poorsf.write(l)

	#write the good lines (micrograph data from the original star file) to the goodline file
	for l in goodlines:
		goodsf.write(l)

	#write the poor lines (micrograph data from the original star file) to the poorline file
	for l in poorlines:
		poorsf.write(l)

	#let the user know what their output is called
	print 'Name of output files:\n' + gname + '\n' + pname + '\n'
		 
		
		


