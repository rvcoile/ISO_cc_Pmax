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
import pandas as pd
from copy import deepcopy

## local function reads
from columnFragility_shell import multi_FmaxParallel, multi_Fmax

## distant function reads
directory=rvcpyPath
sys.path.append(directory)
from PrintAuxiliary import Print_DataFrame
from LatinHypercube import LHS_rand
from probabCalc_2018 import ParameterRealization_r, VarDict_to_df


##############
## FUNCTION ##
##############

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

def LHSFmax(SW_givenLHS,fixedLHSpath,start,nSim,nVar,totalvarDict,fullvarDict,reffile,SW_probabMaterial,nProc=1):

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
		multi_Fmax(X,reffile,SW_probabMaterial=SW_probabMaterial)
	else:
		multi_FmaxParallel(X,reffile,SW_probabMaterial=SW_probabMaterial,n_proc=nProc)

####################
## CONTROL CENTER ##
####################

if __name__ == "__main__": 

	totalvarDict=localStochVar()

	print(totalvarDict.keys())