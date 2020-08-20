#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2019

#Takes input of two files, compares the content from column x in each line of the query file and column y in target files, and prints out (to a new file) the lines from the first file that matched at least one in the second file for those respective columns. Ex: matches column 2 from the lines in the query file with column 5 in the target file, and prints out the lines that matched from the query file into a new file. Only does this for things that match in the first of the two entries given - ex, only match particles with the same original position if they came from the same micrograph name.

#Can also be used to sort entries in one file according to the order of a second file, since it iterates through the order of the entries in the second file.

#command line format:
#1: file to compare (query) (prints lines and the header from this file)
#2: file to compare to (target) (iterates through the data entries in this file)
#3: index, non-0 start (1, 2...) of first column to compare from query
#4: index, non-0 start (1, 2...) of second column to compare from target
#5  index of first column from query for second criteria
#6  index of second column from target for second criteria
#7: number of processes to use, can reset the maximum number by changing the variable "maxprocs" below

#the header comes from f1
#the printed lines come from f1

maxprocs = 30

#exampleformat = python matchQueryToTarget.py queryfile targetfile startcolumn endcolumn 25

import sys
import string
import random
import multiprocessing as mp
import os
from datetime import datetime

percentdone = {}

#obtains the header for a starfile - will work with RELION starfiles, but if you change the header (adding in empty lines between the header descriptions, for example) it won't grab the entire thing
def getHeader(lines):
	header = []
	inUnderscores = False
	i = 0
	while i<len(lines):
		if lines[i][0][0] == '_':
			if not inUnderscores:
				inUnderscores = True
		else:
			if inUnderscores:
				for j in lines[:i]:
					header.append(j[0])
				break
		i+=1
	return header	

#parses through a data file and reads the lines into lists without spaces
def parsefilelines(file):
	data = []
	lines = file.readlines()
	for l in lines:
		val = l.strip().split(' ')
		entry_no_whitespace = [x.strip() for x in val if x] 
		data.append((l,entry_no_whitespace))
	return data

#iterates through the data in file2, and if column # 'end' in file2 matches any entry in file1 at column # 'start' it will add the entry from file1 to a list
def compareData(f2,f1,results,start,end,start2,end2,processnum):
	processname = 'process_' + str(processnum)
	percentdone[processnum] = 0
	result = []
	i = 0
	counter = 0
	for f2_entry in f2:

		i+=1
		if i % 1000 == 0:
			print processname + ('   %.2f' % (((i+0.0) / len(f2))*100)) + '% completed, entries done: ' + str(i) + ' / ' + str(len(f2))
			percentdone[processnum] = (((i+0.0) / len(f2))*100)
		if len(f2_entry[1]) >= end+1:
			temp = f2_entry[1][end]
			temp_criteria_two = f2_entry[1][end2]
			for f1_entry in f1:
				if len(f1_entry[1]) >= start+1:
					if f1_entry[1][start] == temp:
						if f1_entry[1][start2] == temp_criteria_two:
							result.append(f1_entry[0])
							counter+=1
							break
	print processname + ' COMPLETE'
	results.append((processnum,result,counter))

def comparefiles(file1,file2,start,end,start2,end2,numprocs):

	f1 = [] #the list for data entries from file1
	f2 = [] #the list for data entries from file2

	headerlines = [] #the list for the header from file1
	headerlines2 = [] #the list for the header from file2

	#the output name for the program's result file
	filename = 'resultfile_' + ''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(4))

	#the output file the program will be writing data to
	newf = open(filename,'w')

	with open(file1) as f:
		f1 = parsefilelines(f) #pull out the data from file1 into a list
		headerlines = getHeader(f1) #get just the header data from file1

	with open(file2) as k:
		f2 = parsefilelines(k) #pull out the data from file2 into a list
		headerlines2 = getHeader(f2) #get just the header data from file2

	#write the header to the output file
	for line in headerlines: 
		newf.write(line)

	#set the number of processors that will be used, max = maxprocs, min = 1
	if (numprocs > maxprocs+1):
		numprocs = maxprocs
	elif (numprocs < 1):
		numprocs = 1

	#define the number of pieces of data per chunk that our data is going to be broken up into
	#ex: 1000 data pieces over 10 processors will require datachunk to equal 100
	datachunks = ((len(f2)-len(headerlines2)) / (numprocs))
	if datachunks < 1:
		datachunks = 1

	#define the lists of data, each equal in size to 'datachunk,' that will each be split over a different process
	#if the data doesn't divide up evenly, add the excess at the end to the last chunk to preserve the order
	chunks = [f2[x:x+datachunks] for x in xrange(len(headerlines2), len(f2), datachunks)]
	if len(chunks) > numprocs:
		chunks[len(chunks)-2]+=chunks.pop(len(chunks)-1)

	#set up our process manager
	manager = mp.Manager()
	results = manager.list()
	jobs = []

	#for each process we are going to use, start a new process using the portion of data from f2 that we want to compare to f1
	#since we would normally iterate through the data in f2, by noting the order of the processes we can recompile the results in the correct order
	for i in range(numprocs):
		print 'Starting Process: ' + str(i) + ' with ' + str(len(chunks[i])) + ' particles'
		if i>(len(chunks)-1):
			break
		p = mp.Process(target = compareData, args=(chunks[i],f1,results,start,end,start2,end2,i))
		jobs.append(p)
		p.start()

	#resolve each process
	for proc in jobs:
		proc.join()

	#counter for the number of data entries matched between the files
	counter = 0

	#sort the results based upon the process number to preserve the correct order
	results_sorted = sorted(results, key=lambda result: result[0])

	#write out the results to the new file in the correct order, and note the number of data entries written out
	for r in results_sorted:
		for entry in r[1]:
			newf.write(entry)
		counter += r[2]

	#remove whitespace at the end of the files to engender accurate counts of the file sizes
	if f1[len(f1)-1][0] == ' \n':
		f1.pop(len(f1)-1)
	if f2[len(f2)-1][0] == ' \n':
		f2.pop(len(f2)-1)

	#print out the data output to the command line
	output = '\nOutput for: ' + str(file1) + ' ' + str(file2) + ' ' + str(start+1) + ' ' + str(end+1) + ' ' + str(numprocs) + '\nInput file data entries: \n' + str(file1) + ': ' + str(len(f1)-len(headerlines)) + '\n' + str(file2) + ': ' + str(len(f2)-len(headerlines2)) + '\n\nmoved: ' + str(counter) + ' data entries' + '\nResultfile named: ' + str(filename)
	newf.close()
	return output

if __name__ == '__main__':
	print
	starttime = datetime.now() #keep track of how long the program takes to run
	args = sys.argv[1:] #get arguments from the command line into the program
	print comparefiles(args[0],args[1],int(args[2])-1,int(args[3])-1,int(args[4])-1,int(args[5])-1,int(args[6])) #run the program
	print 'Total runtime: ' + str( datetime.now() - starttime) + '\n' #note the runtime 


#eof
