# __author__ = "RVC"
# __email__= "ruben.vancoile@gmail.com"
# __date__= "2018-09-30"

#
# shell for fragility curve calculation Pmax SAFIR column calculation
#


####################
## MODULE IMPORTS ##
####################

## standard module reads
import sys
import pandas as pd
import numpy as np
# from copy import deepcopy
# import time

## local function reads
from columnSAFIR_Pmax import Fmax_SAFIR

## distant function reads
directory="C:/Users/rvcoile/Google Drive/Research/Codes/Python3.6/REF/rvcpy"
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame

directory="C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\Python3.6\\SAFIRpy"
sys.path.append(directory)
from modSAFIR import mod_inSAFIR_multifile


##############
## FUNCTION ##
##############

def multi_Fmax(df,reffile,SW_newfolder=True):
	## local custom code for f[Fmax_SAFIR] on multiple realizations
	# df: pd.DataFrame : realizations for which Fmax will be calculated
		# dimension variables conform SAFIR reqs
		# column names indicate variable pointers in reference *.in file

	## initialization ## - possibly to be externalized
	## initial axial force
	P0=7*10**6 # [N]
	## target ISO 834 standard fire duration ##
	tISO=120 # [min]
	## handling ##
	tISO*=60 # [s] dimension change

	## *.in file realization ##
	mod_inSAFIR_multifile(df,reffile,SW_newfolder)

	## Pmax search for each of the generated *.in files - f[Fmax_SAFIR]
		# can be parallellized
	for sim in df.index:
		# determine *.in file location
		reffolder='\\'.join(reffile.split('\\')[0:-1])
		if not isinstance(sim,str): simname='{0}'.format(sim).zfill(5) # assumes index is (integer) number
		else: simname=sim
		if SW_newfolder: infile=reffolder+'\\'+simname+'\\'+simname+'.in'
		else: infile=reffolder+'\\'+simname+'.in'
		# run f[Fmax_SAFIR] for *.in realization
		Fmax_SAFIR(infile,P0,tISO,'custom')



#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__": 

	########################
	## SWITCH FOR TESTING ##
	########################

	SW_debug=False

	## SWITCH ##
	if not SW_debug:

	###############
	## EXECUTION ##
	###############

		## *.in file to be modified ##
		reffile="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\reffile.in"

		## (stoch) variable realizations ##
		# realizations of variables to be substituted
		# for each column realization, Pmax will be calculated
		fc=[25.2,30.7,30.] # [MPa] 20°C concrete compressive strength realization
		fy=[512.0,420.6,500.] # [MPa] 20°C steel yield stress realization
		nR=len(fc)
		X=pd.DataFrame([fc,fy],index=['fc [MPa]','fy [MPa]'],columns=np.arange(nR))
		X=X.T # transpose(X)

		## create input file for each realization and perform Pmax search ##
			# dimension variables conform SAFIR reqs
			# column names indicate variable pointers in reference *.in file
		df=X*10**6; df.columns=['fc20', 'fy20']
		multi_Fmax(df,reffile)



		## testing ##
		# print(df)

	###########
	## DEBUG ##
	###########

	else:

		## data-path ##
		filein="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\PmaxSearch\\Fsearch_ref.in"


