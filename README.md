# cryoem
for cryo em data processing

******************************************

README

Cryo-EM data processing python program library
Ian Outhwaite
Long Lab, MSKCC 
May 22, 2019

******************************************

README Format
Program Name:
Program Summary:
Program input:
Example call:
Program flags / options:

******************************************

Contents
1. checkAutopick.py
2. renameMicrographs.py
3. rename_autopick_as_manpick.py
4. matchQueryToTarget.py
5. matchQueryToTargetTwoFactor.py
6. starSwiper.py
7. checkMicrographs.py
8. checkCtfRefine.py
9. choseBestCtf.py
10. checkParticleAngles.py
11. removeCtfDefocusOutliers.py
12. removeEdgeParticles.py
13. motionSelection.py
14. checkParticleDefocus.py
15. restoreOriginalCtfs.py

******************************************

1. 
Program name: 

	checkAutopick.py
	
Program summary: 
	Program gives user information about picked micrographs according to the FOM (figure-of-merit) scores for pickied particles on that micrograph.
Program input: 
	Either a star file of picked particle coordinates for a single micrograph, or a folder containing star files of picked coordinates 
Example call: 
	python checkAutopick.py -p myparticlefile 
Program flags / options: 
	-p Input is a single file of EXTRACTED particles; returns the distribution of FOM scores for particles in that file (min FOM, mean FOM, max FOM, standard deviation of FOM scores)
	-d Input is a directory containing particle files (ex: /tifs or /micrographs folder from WITHIN a RELION autopicking job); prints the micrographs in order from worst (top) to best (bottom) average FOM scores of their particles. Micrographs containing ice may have unusually high FOM scores; these micrographs may settle towards the bottom of the list.
	-pi Input is a single file of EXTRACTED particles; plots a frequency histogram of the FOM scores of the particles in a single starfile from a single micrograph
	-di Input is a directory containing EXTRACTED particle files; plots a frequency histogram of the average FOM scores for each micrograph referred to by the particle files. For example, if the directory contained 2000 files of picked coordinates, each file referring to a seperate micrograph, this would calculate the average FOM score for the particles from a single micrograph, and plot those average scores (2000 in total).
	-pn Input is a single file of EXTRACTED particles; creates a new file with the coordinates of particles with very high FOM scores: greater than (mean+(2.5*std)) given the FOM scores for particles in that file
	-dn Input is a directory containing EXTRACTED particle files; conducts "-pn" on each particle file and stores the new files in a new directory. That is, it creates a new directory with files, where each file contains particle coordinates for the FOM outliers (>(mean+(2.5std))) derived from the particles picked from a single micrograph in the original directory. 


******************************************

2.
Program name: 
	renameMicrographs.py
Program summary:
	Takes input of a folder, and renames all the files in that folder from _Stk.mrc to _stk.mrcs and _DW.mrc to .mrc
	uses a prefix input from the user, adding on the number afterwards for each type automatically (ex: 000001, 000002)
Program input:
	1. The folder with the files to rename
	2. The prefix to use for the files
Example call:
	python renameMicrographs.py /myMicrographs myprojectname_mydate
Program flags / options: 
	None

******************************************

3.
Program name: 
	rename_autopick_as_manpick.py
Program summary: 
	Takes input of a folder, and renames all the files in that folder from _autopick.star to _manualpick.star
	uses a prefix input from the user, adding on the number afterwards for each type automatically (ex: 000001, 000002)
	Useful to allow the manual pick program to open / view the results of autopicking, since it needs _manualpick.star files
Program input:
	1. The folder with the autopicked files
	2. The prefix to use
Example call:
	python renameAutopick.py /myAutopickedMicrographs myprojectname_mydate
Program flags / options: 
	None

******************************************

4. 
Program name: 
	matchQueryToTarget.py
Program summary: 
	Saves lines from first file that exist in second file (for a given column of data)
	Takes input of two files, compares the content from column x in each line of the query file and column y in target files, and prints out (to a new file) the lines from the first (query) file that matched at least one in the second (target) file for those respective columns. Ex: matches column 2 from the lines in the query file with column 5 in the target file, and prints out the lines that matched from the query file into a new file.
Program input:
	command line format:
	#1: file to compare (query)
	#2: file to compare to (target)
	#3: index, non-0 start (1, 2...) of first column to compare from query
	#4: index, non-0 start (1, 2...) of second column to compare from target
	#5: number of processes to use, can reset the default maximum number by changing the variable "maxprocs" in the script
Example call:
	python matchQueryToTarget.py queryfile targetfile column_x_in_query_file column_y_in_target_file number_of_processes_to_use
	python matchQueryToTarget.py myparticlesfile1.star myparticlesfile2.star 10 5 25
Program flags / options: 
	None

******************************************

5. 
Program name: 
	matchQueryToTargetTwoFactor.py
Program summary: 
	Saves lines from first file that exist in second file (for a given column of data). Useful for matching particles that have the same piece of information for one indentifier but are unique given that information for another indentifier - for example, particle may share the same x,y coordinates with particles picked from other micrographs, but they will not share the same x,y coordinate with particles from the same micrograph. This allows the user to find and match information from unique particles between two files.
	Takes input of two files, compares the content from column x1,x2 in each line of the query file and column y1,y2 in target files, and prints out (to a new file) the lines from the first (query) file that matched at least one in the second (target) file for those respective columns. Ex: matches columns 2 and 3 from the lines in the query file with columns 5 and 6 (respectively, x1->y1 and x2->y2) in the target file, and prints out the lines that matched from the query file into a new file.
Program input:
	command line format:
	#1: file to compare (query)
	#2: file to compare to (target)
	#3: index, non-0 start (1, 2...) of first column to compare from query (x1)
	#4: index, non-0 start (1, 2...) of first column to compare from target (y1)
	#5: index, non-0 start (1, 2...) of second column to compare from query (x2)
	#6: index, non-0 start (1, 2...) of second column to compare from target (y2)
	#7: number of processes to use, can reset the default maximum number by changing the variable "maxprocs" in the script
Example call:
	python matchQueryToTargetTwoFactor.py queryfile targetfile column_x1_in_query_file column_y1_in_target_file column_x2_in_query_file column_y2_in_target_file number_of_processes_to_use
	python matchQueryToTargetTwoFactor.py myparticlesfile1.star myparticlesfile2.star 2 5 3 6 25
Program flags / options: 
	None

******************************************

6.
Program name: 
	starSwiper.py
Program summary: 
	Finds the micrographs referred to in a star file using the "_rlnMicrographName" tag from the header
	Program opens each micrograph, and following a user command and the ENTER key (''=good image, only enter key & no imput needed or 'p'=poor image) sorts the data referred to by the line in the star file to a new star file, '' = good data (no input, just hit enter), 'p' = bad data, q quits the selection and prints out the starfiles, or if you work down the entire list, the new starfiles are printed at the very end. Output: two star files of micrographs, one with the data for those deemed "good" by the user and the other with the data for those deemed "poor." Useful for sorting through micrographs manually after curating good micrographs by estimated Ctf value.
Program input:
	1. The path to the micrograph star file listing all the micrographs and their locations (only use the ones from your "Import" section in relion)
	2. The path to the relion home directory (which should have the folder your micrographs came from originally)
	3. (optional) the number micrograph to start at, otherwise starts at 1
Example call:
	python starSwiper.py /pathtomicrographstarfile /pathtorelionfolder 593
	...would start at micrograph number 593
Program flags / options:
	In program: ''' = good file, 'p' = poorfile, and use q to quit and save the results you have gone through so far. 

*****************************************

7.
Program name:
	checkMicrographs.py
Program summary:
	Creates a plot of the information from a .star file of micrographs after Ctf estimation. Includes a histogram of Ctf estimated max resolution, and a series of linear correlation plots between max res and a) FOM score, b) defocus angle and c) the RMS value for defocus U and V coordinates (aka the magnitude of the vector that describes the U and V coordinates).
Program input:
	The name of the micrograph star file with your Ctf-corrected micrographs (aka the output from Ctf estimation/Ctffind4 in your Ctf folder in relion)
Example call:
	python checkMicrographs.py micrographs_ctf.star
Program flags / options:
	None, but you can resize the window of the generated plot, and you should save the plot as a .png file since the plot is dismissed when the program closes

*****************************************

8. 
Program Name: 
	checkCtfRefine.py
Program Summary:
	For CtfRefine output .star file, plots the number of particles per micrograph against the standard deviation of defocus values for those particles, from that single micrograph. Each point represents a micrograph.
Program input:
	A .star file that is the output of CtfRefine from RELION, or any .star file with that information and the same header entries
Example call:
	python checkCtfRefine.py particles_refine_ctf.star
Program flags / options:
	None

******************************************

9.
Program Name:
	choseBestCtf.py
Program Summary:
	For a group of CtfFind output files, returns one .star file with the maximum resolution Ctf values for a given micrograph. Useful for combining the results of multiple CtfFind runs conducted with different maximum resolution cutoffs (aka 3.5A, 4A and 5A as typical values)
Program input:
	A series of .star files (usually named micrographs_ctf.star)
Example call:
	python choseBestCtf.py  micrographs_ctf_3p5.star micrographs_ctf_4.star micrographs_ctf_5.star
Program flags / options:
	None

******************************************

10.
Program Name:
	checkParticleAngles.py
Program Summary:
	for refined particles file (.star, either from Refine3D or converted from a cryosparc refinment): prints plots of the three refinment angle distributions
Program input:
	.star file of refined particles
Example call:
	python checkParticleAngles.py my_refined_particles.star 100
Program flags / options:
	Last number represents the number of bins for the histograms the program creates, try different values to get a sense of what is going on with your data

******************************************

11.
Program Name:
	removeCtfDefocusOutliers.py
Program Summary:
	For a CtfRefine "particles_ctf_refine.star" file: returns the "good" particles that are not deviant from statistical norms
	User can enter the number of standard deviations away from the mean that they want to retain particles within, for the defocus values of a single micrograph
	Particle defocus is defined in this script as ( ( _rlnDefocusU + _rlnDefocusV ) / 2 )
	Users need to hard-set certain values in the program
	* NUM_STANDARD_DEVIATIONS refers to the number of standard deviations of per-particle defocus values for a given micrograph, outside of which outliers will be removed. Ex: a micrograph with a defocus standard deviation (calculated from the particles for that micrograph) greater or less than than 1.75 standard deviation from the average of other micrographs' defocus standard deviations will be excluded. Basically, getting rid of micrographs with a high amount of defocus variance.
	* min_particles refers to the minimum number of particles needed to apply this deviation method - if there are too few particles a micrograph will naturally have higher statistical deviance and you may want to exclude it and keep all the data
	* maximum_allowed_defocus_deviation refers to a hard cutoff applied to all micrographs; if the standard deviation of defocus values for a micrograph is higher than this value, no particles from that micrograph will be included (basically saying there is something wrong with too much of the data to let it pass)
	How to use:
	If you want to remove outliers from single micrographs, set min_particles to 0, NUM_STANDARD_DEVIATIONS to your desired value, and the maximum_allowed_defocus_deviation very high
	If you want to remove outlier micrographs of "worse data," set min_particles very high and the maximum_allowed_defocus_deviation to your desired threshold	
Program input:
	A .star file that is the output of CtfRefine from RELION, or any .star file with that information and the same header entries
Example call:
	python removeCtfDefocusOutliers.py particles_refine_ctf.star
Program flags / options:
	See above, set the hard vales in the actual script. Write down what values you use.

******************************************

12.
Program Name:
	removeEdgeParticles.py
Program Summary:
	Removes particles picked near the edges of micrographs
	Defaults (based upon 2x binning of super resolution micrographs, check the dimensions of your image files)
	max_xcor = 3710
	max_ycor = 3838
Program input:
	A .star file with ycor and xcor positions of picked particles
Example call:
	python removeEdgeParticles.py my_particles.star 100
Program flags / options:
	After the file name, include the distance from the edge (in pixels, according to image dimensions) that you want to use

******************************************

13.
Program Name:
	motionSelection.py
Program Summary:
	Now basically defunct, was useful to remove micrographs with lots of movement. Designed when processing was done not from .tif files, which makes this code obsolete. Particle polishing seems to fix the movement issue. Needs output logfile from motioncor processing.
Program input:
	See script
Example call:
	See script
Program flags / options:
	See script

******************************************

14.
Program Name:
	checkParticleDefocus.py
Program Summary:
	Plots the number of particles per micrograph versus the average defocus value for particles from that micrograph. Also plots a histogram of the average micrograph defocus values (average of all particles from said micrograph). Useful to evaluate whether or not you have collected enough low-defocus information, and how many particles have been picked accross different defocus thresholds.
Program input:
	A particles.star file, useful after extracting picked particles, or following Ctf refinment
Example call:
	python checkParticleDefocus.py my_particles.star
Program flags / options:
	None

******************************************

15.
Program Name:
	restoreOriginalCtfs.py
Program Summary:
	for a CtfRefine "particles_ctf_refine.star" file: returns the estimated defocus values to the original values from a .star file (a CtfFind .star file). Note, the names of the micrographs referred to in the .star files must match, otherwise the program will be unable to locate the original defocus information.
Program input:
	A .star file of particles that have undergone per-particle Ctf estimation and have different defocus values
	A .star file of micrographs from CtfFind, with the original DU and DV values
Example call:
	python restoreOriginalCtfs.py my_refined_particles.star micrographs_ctf.star
Program flags / options:
	None

******************************************

#eof
