#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

#Takes input of a folder, and renames all the files in that folder from 
# _autopick.star to _manualpick.star
#uses a prefix input from the user, adding on the number afterwards for each type. 

import glob, os, sys

if __name__ == '__main__':
	args = sys.argv[1:]
	folder = args[0] #the folder is the first argument
	cwd = os.getcwd()
	print cwd
	for file in os.listdir(cwd+'/'+folder):
		os.chdir(cwd+'/'+folder)
		if file[-13:] == 'autopick.star':
			print file[:-13]
			os.rename(file,file[:-13]+'manualpick.star')
