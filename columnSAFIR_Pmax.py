# __author__ = "RVC"
# __email__= "ruben.vancoile@gmail.com"
# __date__= "2018-09-26"

#
# search for Pmax SAFIR column calculation
#


####################
## MODULE IMPORTS ##
####################

## standard module reads
import sys
from copy import deepcopy

## local function reads
# NONE

## distant function reads
directory="C:/Users/rvcoile/Google Drive/Research/Codes/Python3.6/REF/rvcpy"
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame

directory="C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\Python3.6\\SAFIRpy"
sys.path.append(directory)
from modSAFIR import mod_inSAFIR
from runSAFIR import SAFIR_run
from postprocessSAFIR import SAFIR_maxTIME


##############
## FUNCTION ##
##############

def Fmax_SAFIR(filein,fileout,modDict):
	# iteratively searches for SAFIR maximum load value
	#	load value to be modified indicated as "Fsearch" in *.in file
	#	pay attention to load direction ==> link with sign in *.in file


	


	## Single load evaluation ##
	############################
	# update *.in file
	# run calculation
	# obtain last converged timestep

	# create new *.in file ##
	mod_inSAFIR(filein,fileout,modDict)

	## run new *.in file ##
	SAFIR_run(fileout)

	## maxTime in *.out file ##
	outfile=deepcopy(fileout); outfile=outfile[0:-2]; outfile+='out'
	maxTime=SAFIR_maxTIME(outfile) # last converged timestep in [s]

	## output for feedback ##
	print("maxTime = %iseconds", maxTime)






#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__": 

	########################
	## SWITCH FOR TESTING ##
	########################

	SW_testcase=3
	SW_debug=False

	## SWITCH ##
	if not SW_debug:

	###############
	## EXECUTION ##
	###############

		## *.in file to be modified ##
		reffile="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\modfileTest\\Fsearch_N.in"

		## target *.in path ##
		outfile="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\modfileTest\\mod_02.in"

		## Variables to be modified ##
		# variable 00
		ref00='Fsearch'
		sub00=str(6*10**6)
		# combination into Dict
		modDict={
		ref00:sub00
		}

		## execution ##
		Pmax=Fmax_SAFIR(reffile,outfile,modDict)

	###########
	## DEBUG ##
	###########

	else:

		pass