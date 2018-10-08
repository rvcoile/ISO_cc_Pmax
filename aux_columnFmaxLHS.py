# __author__ = "RVC"
# __email__= "ruben.vancoile@gmail.com"
# __date__= "2018-10-03"

#
# support functions for masterfile for ISO column LHS calculation
# 

#####################
## REFERENCE PATHS ##
#####################

## python paths
rvcpyPath="C:/Users/rvcoile/Google Drive/Research/Codes/Python3.6/REF/rvcpy"

####################
## MODULE IMPORTS ##
####################

## standard module reads
import sys
import numpy as np
import pandas as pd
from copy import deepcopy

## local function reads
from columnFragility_shell import multi_FmaxParallel, multi_Fmax, collectResults

## distant function reads
directory=rvcpyPath
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame
from LatinHypercube import LHS_rand
from probabCalc_2018 import ParameterRealization_r, VarDict_to_df


##############
## FUNCTION ##
##############

def collectResults_subGroups(numList,reffile):
	# collect results from sub-folders - apply when SW_perform100
		# numList: list of startnumbers subcalcs
		# reffile: original *.in reffile - defines target directory

	## targetdir
	targetdir='\\'.join(reffile.split('\\')[0:-1])

	## collect for numList
	for i, num in enumerate(numList):
		## data collection
		subdir=targetdir+'\\{0}'.format(num).zfill(4)
		local_out=pd.read_excel(subdir+'\\output.xlsx','out') # local output
		xl = pd.ExcelFile(subdir+'\\LHS_SAFIRinput.xlsx') # *.xlsx with input values
		local_r=xl.parse("r") # r-values input
		local_Xref=xl.parse("Xref") # Xref-values input (original dimensions)
		local_X=xl.parse("X") # X-values input (SAFIR dimensions)

		## output printing
		if i==0: out=deepcopy(local_out); r=deepcopy(local_r); Xref=deepcopy(local_Xref); X=deepcopy(local_X)
		else:
			out=pd.concat([out,local_out])
			r=pd.concat([r,local_r])
			Xref=pd.concat([Xref,local_Xref])
			X=pd.concat([X,local_X])

	## print output
	Print_DataFrame([r,Xref,X,out],targetdir+'\\totaldata',['r','Xref','X','out'])
	Print_DataFrame([r,Xref,X],targetdir+'\\LHS_SAFIRinput',['r','Xref','X'])
	Print_DataFrame([out],targetdir+'\\out',['out'])


def localStochVar():
	# stochastic variable definition
	# returns varDict for calculation LHS realizations
	# usage: hardcoded input

	## key parameters ##
	fck=30. # [MPa] 20°C characteristic compressive strength
	Vfc=0.15 # [-] coefficient of variation
	sfy=30. # [MPa] standard deviation
	fyk=500. # [MPa] 20°C characteristic compressive strength
	l=4. # [m] column height

	## parameter dict ##
	# fc20 definition
	Vfc=Vfc # [-] coefficient of variation
	fck=fck # [MPa] 20°C characteristic compressive strength
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
	sfy=sfy # [MPa] standard deviation
	fyk=fyk # [MPa] 20°C characteristic compressive strength
	mfy=fyk+2*sfy # [MPa] mean value
	fy20={
	'name':'fy20',
	'Dist':'LN',
	'DIM':"[MPa]",
	'm':mfy,
	's':sfy,
	'info':''
	}

	# average eccentricity 'nodeline_Y'
	secc=l/1000 # [m] standard deviation
	mecc=0. # [m] 20°C characteristic compressive strength
	ecc={
	'name':'nodeline_Y',
	'Dist':'N',
	'DIM':"[m]",
	'm':mecc,
	's':secc,
	'info':''
	}

	# out of straightness 'oos'
	soos=l/1000 # [m] standard deviation
	moos=0. # [m] 20°C characteristic compressive strength
	oos={
	'name':'oos',
	'Dist':'N',
	'DIM':"[m]",
	'm':moos,
	's':soos,
	'info':''
	}

	# out of plumbness 'oop'
	soop=0.0015 # [rad] standard deviation
	moop=0. # [m] 20°C characteristic compressive strength
	oop={
	'name':'oop',
	'Dist':'N',
	'DIM':"[rad]",
	'm':moop,
	's':soop,
	'info':''
	}

	# kfy - eps logistic model Negar
	sepskfy=1. # [-] standard deviation standard normal variable
	mepskfy=0. # [-] mean value standard normal variable
	epskfy={
	'name':'epskfy',
	'Dist':'N',
	'DIM':"[-]",
	'm':mepskfy,
	's':sepskfy,
	'info':''
	}

	# varDict
	fullvarDict={
	'fc20':fc20,
	'fy20':fy20,
	'nodeline_Y':ecc,
	'oos':oos,
	'oop':oop,
	'epskfy':epskfy
	}

	return fullvarDict

def dimCorrSAFIR(varDictDict):
	# modify dimension and parameter values of varDicts to SAFIR input

	# deepcopy if input DictDict
	varDictDictout=deepcopy(varDictDict)

	# iterate over variables and check dim
	for var in varDictDictout.keys():
		# read dimension
		dim=varDictDictout[var]['DIM']
		# correct dimension
		if dim=='[MPa]':
			varDictDictout[var]['DIM']=['N/m2']
			varDictDictout[var]['m']*=10**6
			varDictDictout[var]['s']*=10**6
		if dim=='[mm]':
			varDictDictout[var]['DIM']=['m']
			varDictDictout[var]['m']/=10**3
			varDictDictout[var]['s']/=10**3
	return varDictDictout

def LHSFmax(SW_givenLHS,fixedLHSpath,start,nSim,nVar,totalvarDict,fullvarDict,reffile,SW_probabMaterial,tISO,nProc=1):

	# r-values
	if SW_givenLHS:
		# fixedLHSpath defined as reference path
		r=pd.read_excel(fixedLHSpath); r=r.iloc[start:start+nSim,:]
		print(r)
	else: 
		r=LHS_rand(nSim,nVar,'Center')
	# parameter realization
	r.columns=list(fullvarDict.keys()) # r-value assignment to variables
	X=deepcopy(r); Xref=deepcopy(r)
	for key in fullvarDict.keys(): # variable realization
		X[key]=ParameterRealization_r(fullvarDict[key],X[key])
		Xref[key]=ParameterRealization_r(totalvarDict[key],Xref[key])
	# printing
	LHSprintPath='\\'.join(reffile.split('\\')[0:-1])+'\\LHS_SAFIRinput'
	Print_DataFrame([r,Xref,X],LHSprintPath,['r','Xref','X'])

	## run multi_Fmax
	if nProc==1:
		multi_Fmax(X,reffile,tISO,SW_probabMaterial=SW_probabMaterial)
	else:
		multi_FmaxParallel(X,reffile,tISO,SW_probabMaterial=SW_probabMaterial,n_proc=nProc)

def collectRealizations_postFail(reffile,fixedLHSpath,start,nSim,P0,tISO,SW_probabMaterial):
	## collect results from individual realizations after glitch ##
	print("Reconstructing")

	# functions of initialization
	totalvarDict=localStochVar() # varDict with original dimensions
	fullvarDict=dimCorrSAFIR(totalvarDict)

	## df reconstruction ##
	# df == X in current *.py
	r=pd.read_excel(fixedLHSpath); r=r.iloc[start:start+nSim,:]
	r.columns=list(fullvarDict.keys()) # r-value assignment to variables
	X=deepcopy(r)
	for key in fullvarDict.keys(): # variable realization
		X[key]=ParameterRealization_r(fullvarDict[key],X[key])
	df=X # assign df

	## sInfile reconstruction ##
	sInfile=pd.Series(index=df.index)
	for sim in df.index:
		# determine *.in file location
		reffolder='\\'.join(reffile.split('\\')[0:-1])
		if not isinstance(sim,str): simname='{0}'.format(sim).zfill(5) # assumes index is (integer) number
		else: simname=sim
		infile=reffolder+'\\'+simname+'\\'+simname+'.in'
		sInfile[sim]=infile

	## collect results from realization subfolders ##
	SW_rerun=True # [boolean] try to open file and rerun calc if failure
	collectResults(df,sInfile,reffile,SW_rerun,P0,tISO,SW_probabMaterial)

def runSpecificCases(reffile,fixedLHSpath,simList,P0,tISO,SW_probabMaterial,nProc=1):
	## run specific cases on demand ##
	print("Specific calculation runs")

	# hardcoded defaults
	SW_removeIterations=True

	# functions of initialization
	totalvarDict=localStochVar() # varDict with original dimensions
	fullvarDict=dimCorrSAFIR(totalvarDict)

	## df reconstruction ##
	# df == X in current *.py
	r=pd.read_excel(fixedLHSpath); r=r.loc[simList,:]
	r.columns=list(fullvarDict.keys()) # r-value assignment to variables
	X=deepcopy(r); Xref=deepcopy(X)
	for key in fullvarDict.keys(): # variable realization
		X[key]=ParameterRealization_r(fullvarDict[key],X[key])
		Xref[key]=ParameterRealization_r(totalvarDict[key],Xref[key])
	df=X # assign df

	## sInfile construction ##
	sInfile=pd.Series(index=df.index)
	for sim in df.index:
		# determine *.in file location
		reffolder='\\'.join(reffile.split('\\')[0:-1])
		if not isinstance(sim,str): simname='{0}'.format(sim).zfill(5) # assumes index is (integer) number
		else: simname=sim
		infile=reffolder+'\\'+simname+'\\'+simname+'.in'; SW_removeItem=True
		sInfile[sim]=infile
	LHSprintPath='\\'.join(reffile.split('\\')[0:-1])+'\\LHS_SAFIRinput'
	Print_DataFrame([r,Xref,X],LHSprintPath,['r','Xref','X'])

	## calculation of simulations ##
	if nProc==1:
		multi_Fmax(df,reffile,tISO/60,SW_removeIterations=SW_removeItem,SW_probabMaterial=SW_probabMaterial,P0=P0)		
	else:
		multi_FmaxParallel(df,reffile,tISO/60,SW_removeIterations=SW_removeItem,SW_probabMaterial=SW_probabMaterial,n_proc=nProc,P0=P0)

####################
## CONTROL CENTER ##
####################

if __name__ == "__main__":

	####################
	## LOCAL SWITCHES ##
	####################

	Action='specificCases' # 'collectPostFail'; 'specificCases'

	if Action == 'collectPostFail':
		## collecting results post run failure, including rerun of non-calculated realizations

		# main reffile path and LHS data path
		reffile="C:\\Users\\rvcoile\\Documents\\Workers\\Probab\\reffileFull.in"	
		fixedLHSpath='C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\refValues\\LHScenter_10000_6var.xlsx'

		# sim parameters
		start=0
		nSim=300
		P0=7*10**6 # [N]
		tISO=240*60 # [s]
		SW_probabMaterial=True

		# reffile
		# reffile='\\'.join(reffile.split('\\')[0:-1])+'\\'+str(start)+'\\'+reffile.split('\\')[-1]
		reffile='\\'.join(reffile.split('\\')[0:-1])+'\\0000\\'+reffile.split('\\')[-1]

		print(reffile)
		# collect realizations
		collectRealizations_postFail(reffile,fixedLHSpath,start,nSim,P0,tISO,SW_probabMaterial)
		
	elif Action == 'specificCases':
		## caclulation of specific cases - e.g. known issues

		# main reffile path and LHS data path
		reffile="C:\\Users\\rvcoile\\Documents\\Workers\\Probab2\\reffileFull.in"	
		fixedLHSpath='C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\refValues\\LHScenter_10000_6var.xlsx'

		## simulations
		# simSeries=[306]
		filepath="C:\\Users\\rvcoile\\OneDrive - UGent\\CalcCenter\\Results\\ISOcc120min\\outputFull.xlsx"
		simSeries=pd.read_excel(filepath,'issueList'); simSeries=simSeries['sim'].values
		print(simSeries)

		## calculation parameters
		P0=10*10**6 # [N]
		tISO=120*60 # [s]
		SW_probabMaterial=True

		# specific realization calculations
		runSpecificCases(reffile,fixedLHSpath,simSeries,P0,tISO,SW_probabMaterial,nProc=1)		



