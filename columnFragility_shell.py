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
import os
import sys
import pandas as pd
import numpy as np
from copy import deepcopy
# import time

## local function reads
from columnSAFIR_Pmax import Fmax_SAFIR

## distant function reads
directory="C:/Users/rvcoile/Google Drive/Research/Codes/Python3.6/REF/rvcpy"
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame
from LatinHypercube import LHS_rand
from probabCalc_2018 import ParameterRealization_r

directory="C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\Python3.6\\SAFIRpy"
sys.path.append(directory)
from modSAFIR import mod_inSAFIR_multifile


##############
## FUNCTION ##
##############

def multi_Fmax(df,reffile,SW_removeIterations=True):
	## local custom code for f[Fmax_SAFIR] on multiple realizations
	# df: pd.DataFrame : realizations for which Fmax will be calculated
		# dimension variables conform SAFIR reqs
		# column names indicate variable pointers in reference *.in file

	## Switches and defaults
	SW_newfolder=True # necessary considering iteration result printing in Fmax_search.xlsx 

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
	sInfile=pd.Series(index=df.index)
	for sim in df.index:
		# determine *.in file location
		reffolder='\\'.join(reffile.split('\\')[0:-1])
		if not isinstance(sim,str): simname='{0}'.format(sim).zfill(5) # assumes index is (integer) number
		else: simname=sim
		if SW_newfolder: infile=reffolder+'\\'+simname+'\\'+simname+'.in'
		else: infile=reffolder+'\\'+simname+'.in'
		sInfile[sim]=infile
		# run f[Fmax_SAFIR] for *.in realization
		Fmax_SAFIR(infile,P0,tISO,'custom',SW_removeIterations=SW_removeIterations)

	## remove comeback log ##
	comebackpath=os.getcwd()+'\\comeback'
	os.remove(comebackpath)

	## Collect results across simulations ##
	collectResults(df,sInfile,reffile)

def collectResults(df,sInfile,reffile):

	## Collect results across simulations ##
	sFmax=pd.Series(index=df.index)
	stE=pd.Series(index=df.index)
	for sim in sFmax.index:

		# path to Fmax_search.xlsx
		infile=sInfile[sim]
		searchLog_path='\\'.join(infile.split('\\')[0:-1])+'\\Fmax_search.xlsx'
		# open logfile and select Pmax
		searchLog=pd.read_excel(searchLog_path)
		Pmax=searchLog.loc['P [kN]'].iloc[-1]
		tE=searchLog.loc['tmax [min]'].iloc[-1]
		# assign result
		sFmax[sim]=Pmax
		stE[sim]=tE

	## print output
	df['Pmax [kN]']=sFmax
	df['tmax [min]']=stE
	outpath='\\'.join(reffile.split('\\')[0:-1])+'\\output'
	Print_DataFrame([df],outpath,['out'])




#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__": 

	########################
	## SWITCH FOR TESTING ##
	########################

	## SWITCH ##
	SW_debug=False

	I_test=2 # test indicator

	###########
	## SETUP ##
	###########

	## *.in file to be modified ##
	reffile="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\reffile.in"

	if I_test==1:
		## (stoch) variable realizations ##
		# realizations of variables to be substituted
		# for each column realization, Pmax will be calculated
		fc=[25.2,30.7,30.] # [MPa] 20°C concrete compressive strength realization
		fy=[512.0,420.6,500.] # [MPa] 20°C steel yield stress realization
		nR=len(fc)
		X=pd.DataFrame([fc,fy],index=['fc [MPa]','fy [MPa]'],columns=np.arange(nR))
		X=X.T # transpose(X)

	if not SW_debug:

	###############
	## EXECUTION ##
	###############

		if I_test==1:

			## create input file for each realization and perform Pmax search ##
			# dimension variables conform SAFIR reqs
			# column names indicate variable pointers in reference *.in file
			df=X*10**6; df.columns=['fc20', 'fy20']
			multi_Fmax(df,reffile)

		elif I_test==2:

			## LHS input generation ##
			# LHS settings
			nLHS=10 # number LHS realizations
			nVar=2 # number of variables
			# r-values
			r=LHS_rand(nLHS,nVar,'Center')
			
			## stochastic variables

			# fc20 definition
			Vfc=0.15 # [-] coefficient of variation
			fck=30 # [MPa] 20°C characteristic compressive strength
			mfc=fck*1/(1-2*Vfc); sfc=mfc*Vfc # [MPa] mean value and standard deviation
			fc20={
			'name':'fc20',
			'Dist':'LN',
			'DIM':"[MPa]",
			'm':mfc,
			's':sfc,
			'info':''
			}

			# fy20 definition
			sfy=30 # [MPa] standard deviation
			fyk=500 # [MPa] 20°C characteristic compressive strength
			mfy=fyk+2*sfy # [MPa] mean value
			fy20={
			'name':'fy20',
			'Dist':'LN',
			'DIM':"[MPa]",
			'm':mfy,
			's':sfy,
			'info':''
			}

			# varDict
			fullvarDict={
			'fc20':fc20,
			'fy20':fy20
			}

			## parameter realization
			# assign r columns
			r.columns=['fc20','fy20']
			X=deepcopy(r)
			for key in fullvarDict.keys():
				X[key]=ParameterRealization_r(fullvarDict[key],X[key])

			## testing ##
			Print_DataFrame([r,X],'LHS_SAFIRinput',['r','X'])

			## SAFIR simulation
			# dimension updating
			df=X*10**6
			# simulation run
			multi_Fmax(df,reffile)

	###########
	## DEBUG ##
	###########

	else:

		## df as in code ##
		df=X*10**6; df.columns=['fc20', 'fy20']

		## sInfile ##
		sInfile=pd.Series(index=df.index)
		sInfile[0]="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\00000\\00000.in"
		sInfile[1]="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\00001\\00001.in"
		sInfile[2]="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\00002\\00002.in"

		## trial collectResults ##
		collectResults(df,sInfile,reffile)

