# __author__ = "RVC"
# __email__= "ruben.vancoile@gmail.com"
# __date__= "2018-10-03"

#
# masterfile for ISO column LHS calculation
# status 2018/10/03
#		- ISO 834 standard fire exposure
# not included:
#		- concrete cover variability
#		- concrete retention factor uncertainty

#####################
## REFERENCE PATHS ##
#####################

## python paths
rvcpyPath="C:/Users/rvcoile/Google Drive/Research/Codes/Python3.6/REF/rvcpy"
SAFIRpyPath="C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\Python3.6\\SAFIRpy"

## reference files
reffile="C:\\Users\\rvcoile\\Documents\\Workers\\Probab\\reffileFull.in"
fixedLHSpath='C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\refValues\\LHScenter_10000_6var.xlsx'

####################
## MODULE IMPORTS ##
####################

## standard module reads
import sys
import os
import shutil
import pandas as pd
import numpy as np
from copy import deepcopy

## local function reads
from aux_columnFmaxLHS import localStochVar, dimCorrSAFIR, LHSFmax, collectResults

## distant function reads
directory=rvcpyPath
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame
from LatinHypercube import LHS_rand

directory=SAFIRpyPath
sys.path.append(directory)
from runSAFIR import SAFIR_TEMinIN

####################
## CONTROL CENTER ##
####################

if __name__ == "__main__": 

	## Switch ##
	############

	## user input reference file and stoch variables ##
	SW_userInput=False # [boolean] user input vs. hardcoded input
	SW_probabMaterial=True # [boolean] use probabSAFIR *.exe - default = True - should be fully compatible when no probab material models are used - to be confirmed
	SW_perform100=True # [boolean] perform calculation per 100 LHS sim in subdirectory

	## fixed LHS sampling scheme ##
	SW_givenLHS=True # [boolean] use precalculated LHS scheme - benefit for repeatability
	start=2500 # start number simulation
	nSim=1000 # number of simulations to run

	## number of processors ##
	nProc=3

	## debug control ##
	SW_debug=False
	Itest=3

	## Execution ##
	###############

	if not SW_debug:
		if SW_userInput:

			pass

		else:

			## initialization ##
			# reffile defined at reference paths

			## (stoch) variable realizations ##
			totalvarDict=localStochVar() # varDict with original dimensions
			# df=varDict_to_df(totalvarDict) # printing of varDict df for reference purposes - not completed yet
			fullvarDict=dimCorrSAFIR(totalvarDict)

			## LHS input generation ##
			nVar=len(fullvarDict.keys())

			## perform per 100 - or full calculation
			if SW_perform100:
				# perform LHS calculation per 100 for ease of follow up and calculation interruptions
				startList=np.arange(start,start+nSim,100)
				for starter in startList:
					# create new subfolder and copy *.in and *.tem to subfolder
					subdir='\\'.join(reffile.split('\\')[0:-1])+'\\{0}'.format(starter).zfill(4)
					os.mkdir(subdir) # WIP - error raised if directory already exists
					subreffile=subdir+'\\'+reffile.split('\\')[-1]
					shutil.copy(reffile,subreffile) # copy reffile to subdir - overhead which may be removed
					temfilepath,temname=SAFIR_TEMinIN(reffile) # determine *.tem file (full path - *.in directory assumed)
					temtargetpath=subdir+'\\'+temname # path for *.tem in subdir
					shutil.copy(temfilepath,temtargetpath) # copy reffile to subdir - overhead which may be removed					
					# perform LHS calculation for 100 sim
					LHSFmax(SW_givenLHS,fixedLHSpath,starter,100,nVar,totalvarDict,fullvarDict,subreffile,SW_probabMaterial,nProc)
				collectResults(startList,reffile)
			else:
				LHSFmax(SW_givenLHS,fixedLHSpath,start,nSim,nVar,totalvarDict,fullvarDict,reffile,SW_probabMaterial,nProc)


	## Debug ##
	###########
	# temporary hardcoded tests - debug code

	else:

		if Itest==1:
			# reference test from columnFragility_shell.py

			## reffile ##
			reffile="C:\\Users\\rvcoile\\Documents\\Workers\\ProbabMaterial\\reffileFull.in"

			## (stoch) variable realizations ##
			# realizations of variables to be substituted
			# for each column realization, Pmax will be calculated
			fc=[25.2,30.7,30.] # [MPa] 20°C concrete compressive strength realization
			fy=[512.0,420.6,500.] # [MPa] 20°C steel yield stress realization
			nR=len(fc)
			X=pd.DataFrame([fc,fy],index=['fc [MPa]','fy [MPa]'],columns=np.arange(nR))
			X=X.T # transpose(X)
			# test 1 df
			df=X*10**6; df.columns=['fc20', 'fy20']
			# add geometric imperfections
			df['nodeline_Y']=[0.0003,0.00002,0.0001]
			df['oop']=[0.0015,0.002,0.0]
			df['oos']=[0.004,0.003,0.0]

			## print input df
			print(df)

			# run multi_Fmax
			# multi_Fmax(df,reffile,SW_probabMaterial=SW_probabMaterial)
			multi_FmaxParallel(df,reffile,SW_probabMaterial=SW_probabMaterial)

		elif Itest==2:
			# LHS input generation - to be used for generating input r-sets for repeatability

			nLHS=10000; nVar=6
		
			r=LHS_rand(nLHS,nVar,'Center')
			# Print_DataFrame([r],'LHS_{0}_{1}var'.format(nLhS,nVar),['{0}'.format(nVar).zfill(2)])
			Print_DataFrame([r],'LHS_{0}_{1}var'.format(nLHS,nVar),['r'])

		elif Itest==3:
			# LHS input generation - to be used for generating input r-sets for repeatability

			nLHS=10000; nVar=6
		
			r=LHS_rand(nLHS,nVar,'Center')
			# Print_DataFrame([r],'LHS_{0}_{1}var'.format(nLhS,nVar),['{0}'.format(nVar).zfill(2)])
			Print_DataFrame([r],'LHS_{0}_{1}var'.format(nLHS,nVar),['r'])