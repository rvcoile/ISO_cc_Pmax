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
import pandas as pd
import numpy as np

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

def Fmax_SAFIR(filein,P0,t_target):
	# iteratively searches for SAFIR maximum load value
	#	load value to be modified indicated as "Fsearch" in *.in file
	#	pay attention to load direction ==> link with sign in *.in file
	#	t_target in function of application
	#		- ISO 834: a specified ISO 834 duration
	#		- parametric fire: full fire duration

	## control settings ##
	######################
	convCrit = 20. # [s] convergence criterion (difference maxTime and t_target)

	## initialization ##
	####################
	## calculation parameters ##
	P=P0 # axial force
	name='' # name extension for generated *.in files
	sim=0 # number of iteration
	SW_nonConverged=True # Switch indicating if maxLoad converged

	## Variables to be modified ##
	ref00='Fsearch'
	sub00=str(P)
	# combination into Dict for f[mod_inSAFIR]
	modDict={
	ref00:sub00
	}

	## output data ##
	data=pd.DataFrame(index=['P [kN]','tmax [min]'])

	while SW_nonConverged:

		## Single load evaluation ##
		############################
		# update *.in file
		# run calculation
		# obtain last converged timestep

		## update P under consideration ##
		modDict[ref00]=str(P)

		## create new *.in file ##
		simnummer=str(sim).zfill(4) # iteration number with leading zeros (total of 4 characters)
		fileout=filein[:-6]+name+simnummer+'.in'
		mod_inSAFIR(filein,fileout,modDict)

		## run new *.in file ##
		SAFIR_run(fileout)

		## maxTime in *.out file ##
		outfile=deepcopy(fileout); outfile=outfile[0:-2]; outfile+='out'
		maxTime=SAFIR_maxTIME(outfile) # last converged timestep in [s]

		## output for feedback ##
		print("maxTime = %iseconds" % maxTime)
		data[sim]=[P*10**-3,maxTime/60.]

		## Convergence check ##
		#######################

		if np.abs(maxTime-t_target)<convCrit:
			SW_nonConverged=False
		else:
			sim+=1 # go to next iteration
			## note1: possibility to use optimization package or other ##
			## note2: possibility to take advantage of deflection information ##
			

			if sim==1:
				if maxTime>t_target: P*=1.1 # P0 to low => add 10%
				else: P*=0.9 # P0 to low => reduce with 10%
			else:
				P=P_iterate(data)
				# abort for testing
				SW_nonConverged=False

	return P,data

def P_iterate(data,t_target):
	# returns next iteration for P
	# note: difference in time dimension data and t_target



	return 8*10**6






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
		reffile="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\modfileTest\\Fsearch_ref.in"

		## initial axial force ##
		P0=6*10**6 # [N]

		## target ISO 834 standard fire duration ##
		tISO=120 # [min]

		## handling ##
		tISO*=60 # [s] dimension change

		## execution ##
		Pmax,df=Fmax_SAFIR(reffile,P0,tISO)

		print(df)

	###########
	## DEBUG ##
	###########

	else:

		pass