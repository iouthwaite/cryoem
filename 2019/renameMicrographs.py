#!/bin/python2.7
#Ian Outhwaite, Long Lab, MSKCC 2017

#Takes input of a folder, and renames all the files in that folder from 
# _Stk.mrc to _stk.mrcs
# _DW.mrc to .mrc
#uses a prefix input from the user, adding on the number afterwards for each type. 

import glob, os, sys

if __name__ == '__main__':
	args = sys.argv[1:]
	folder = args[0] #the folder is the first argument
	prefix = args[1] #the prefix to use for the file names is the second argument
	cwd = os.getcwd()
	print cwd
	i, j = 0, 0
	for file in os.listdir(cwd+'/'+folder):
		os.chdir(cwd+'/'+folder)
		if file[-8:] == '_Stk.mrc':
			namenum = str(i)
			os.rename(file,prefix+'_'+(namenum.zfill(6))+'_stk.mrcs')
			i += 1
		if file[-7:] == '_DW.mrc':
			namenum = str(j)
			os.rename(file,prefix+'_'+(namenum.zfill(6))+'.mrc')
			j += 1
