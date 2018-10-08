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
import multiprocessing as mp
import time

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

def multi_Fmax(df,reffile,tISO,SW_removeIterations=True,SW_geomImperf=True,SW_probabMaterial=False):
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
	# handling: input tISO in [min]
	tISO*=60 # [s] dimension change

	## geometric imperfection handling ##
		# note: (forced) interpretation of 'average eccentricity', 'out of plumbness', 'out of straightness'; cfr. SAFIR input
		# average eccentricity handled through nodeline modification (*.tem)
		# out of plumbness and out of straightness handled through nodal position modification (*.in)
		# for out of plumbness, this must be revisited/confirmed
	# Switch applied to allow to disable calculation - geomImperf does not check whether Imperf data is provided
		# can be avoided by setting default values geomImperf input to zero within f[geomImperf]
	if SW_geomImperf: df=geomImperf(df)

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
		if SW_newfolder: 
			infile=reffolder+'\\'+simname+'\\'+simname+'.in'; SW_removeItem=True
		else: 
			infile=reffolder+'\\'+simname+'.in'; SW_removeItem=False
		sInfile[sim]=infile
		# run f[Fmax_SAFIR] for *.in realization
		Fmax_SAFIR(infile,P0,tISO,'custom',SW_removeIterations=SW_removeIterations,SW_removeItem=SW_removeItem,SW_probabMaterial=SW_probabMaterial)

	## remove comeback log ##
	comebackpath=os.getcwd()+'\\comeback'
	try: os.remove(comebackpath)
	except: pass

	## Collect results across simulations ##
	collectResults(df,sInfile,reffile)

def multi_FmaxParallel(df,reffile,tISO,SW_removeIterations=True,SW_geomImperf=True,SW_probabMaterial=False,n_proc=2):
	## local custom code for f[Fmax_SAFIR] on multiple realizations - parallel version
	# df: pd.DataFrame : realizations for which Fmax will be calculated
		# dimension variables conform SAFIR reqs
		# column names indicate variable pointers in reference *.in file

	## Switches and defaults
	SW_newfolder=True # necessary considering iteration result printing in Fmax_search.xlsx 
	SW_removeItem=False # do not remove *.tem file when moving dir in parallel computing
	SW_paralleldebug=False
	
	## initialization ## - possibly to be externalized
	## initial axial force
	P0=7*10**6 # [N]
	## target ISO 834 standard fire duration ##
	# handling: input tISO in [min
	tISO*=60 # [s] dimension change

	## geometric imperfection handling ##
		# note: (forced) interpretation of 'average eccentricity', 'out of plumbness', 'out of straightness'; cfr. SAFIR input
		# average eccentricity handled through nodeline modification (*.tem)
		# out of plumbness and out of straightness handled through nodal position modification (*.in)
		# for out of plumbness, this must be revisited/confirmed
	# Switch applied to allow to disable calculation - geomImperf does not check whether Imperf data is provided
		# can be avoided by setting default values geomImperf input to zero within f[geomImperf]
	if SW_geomImperf: df=geomImperf(df)

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
		# new folder and file
		newfolder=reffolder+'\\'+simname; infile=newfolder+'\\'+simname+'.in'
		sInfile[sim]=infile

	if SW_paralleldebug:

		for sim in df.index:

			infile=sInfile[sim]
			arg=(infile,P0,tISO,SW_removeIterations,SW_removeItem,SW_probabMaterial)
			parallelfunction(arg)

	else:

		## parallel processing for calculation jobs
		m_ = mp.Manager()
		p = mp.Pool(n_proc,maxtasksperchild=1)
		q = m_.Queue()
		jobs = p.map_async(parallelfunction, [(infile,P0,tISO,SW_removeIterations,SW_removeItem,SW_probabMaterial) for infile in sInfile])
		time_start = time.time()
		while True:
			if jobs.ready():
				print("Simulation completed in {} min.".format(str((time.time()-time_start)/60)))
				break
			else:
				print("{:25}{:<10.3f}{:10}".format("Simulation progress", q.qsize() * 100 / len(df.index), "%"))
				time.sleep(5)
		p.close()
		p.join()
		j=jobs.get() # introducing code as a random patch - cfr. issue not all entries run

	## Collect results across simulations ##
	collectResults(df,sInfile,reffile)

def parallelfunction(arg):

	## unpack arguments
	infile,P0,tISO,SW_removeIterations,SW_removeItem,SW_probabMaterial=arg
	newfolder='\\'.join(infile.split('\\')[0:-1])
	
	## change directory
	os.chdir(newfolder)

	## run f[Fmax_SAFIR] for *.in realization
	Fmax_SAFIR(infile,P0,tISO,'custom',SW_removeIterations=SW_removeIterations,SW_removeItem=SW_removeItem,SW_probabMaterial=SW_probabMaterial)

	## remove comeback log ##
	comebackpath=os.getcwd()+'\\comeback'
	try: os.remove(comebackpath)
	except: pass

def collectResults(df,sInfile,reffile,SW_rerun=False,P0=None,tISO=None,SW_probabMaterial=None):

	## Collect results across simulations ##
	sFmax=pd.Series(index=df.index)
	stE=pd.Series(index=df.index)
	for sim in sFmax.index:

		# path to Fmax_search.xlsx
		infile=sInfile[sim]
		searchLog_path='\\'.join(infile.split('\\')[0:-1])+'\\Fmax_search.xlsx'
		# open logfile and select Pmax
		if SW_rerun:
			try: 
				searchLog=pd.read_excel(searchLog_path)
			except:
				# searchLog does not exist - redo calculation
				# default parameters - DANGER - USE WITH CAUTION
				SW_removeIterations=True
				SW_removeItem=True
				Fmax_SAFIR(infile,P0,tISO,'custom',SW_removeIterations=SW_removeIterations,SW_removeItem=SW_removeItem,SW_probabMaterial=SW_probabMaterial)				
				searchLog=pd.read_excel(searchLog_path)
		else: searchLog=pd.read_excel(searchLog_path)
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

def geomImperf(df):
	# takes df columns with imperfection input and add columns with nodal positions
	# uses hardcoded (and implicit) info on number of nodes, nodal order, column height etc.

	## hardcoded model parameters - column ##
	l=4.0 # [m] column height
	nNodes=21
	nodeList=np.linspace(0,l,nNodes) # nodes along length of column
	nodes=np.arange(nNodes) # note: does not correspond with SAFIR numbering: is natural Python numbering
	nSim=len(df.index)
	refPos=pd.DataFrame(0.,index=nodes,columns=['x','y']); refPos['y']=nodeList

	## initialize output ##
	xLabel=['x'+'{0}'.format(i).zfill(2) for i in nodes]
	yLabel=['y'+'{0}'.format(i).zfill(2) for i in nodes]
	Label=xLabel+yLabel
	out=pd.DataFrame(index=df.index,columns=Label)

	## out of straightness ##
	s_oos=df['oos']; amplitude=s_oos.values.reshape(1,nSim)
	angleList=np.linspace(0,np.pi,nNodes); sin_oos=np.sin(angleList)
	sin=np.reshape(sin_oos,(nNodes,1))
	xlist_oos=np.dot(sin,amplitude) # local lateral out of straightness
	xlist_oos=pd.DataFrame(xlist_oos,columns=df.index,index=nodes)

	## out of plumbness ##
		# # depreciated : out of plumbness calculation neglecting out of straightness
		# s_oop=df['oop']
		# sin_oop=np.sin(s_oop)
		# cos_oop=np.cos(s_oop)
		# # reshape for matrix multiplication
		# nodeL=np.reshape(nodeList,(nNodes,1))
		# sin=sin_oop.values.reshape((1,nSim)); cos=cos_oop.values.reshape((1,nSim))
		# Xlist_oop=np.dot(nodeL,sin); Ylist_oop=np.dot(nodeL,cos) # global positions considering out of plumbness
	# new version
	# effect out of plumbness, taking into account effect out of straightness
	s_oop=df['oop'] 
	sin_oop=np.sin(s_oop); cos_oop=np.cos(s_oop)
	# apply rotation effect per realization
	for sim in df.index:
		startPos=deepcopy(refPos); startPos['x']+=xlist_oos[sim].values
		rotation=np.array([[cos_oop[sim],-sin_oop[sim]],[sin_oop[sim],cos_oop[sim]]])
		newPos=np.dot(startPos,rotation)
		flatnewPos=newPos.flatten('F')
		out.loc[sim]=flatnewPos

	## append DataFrame
	df=pd.concat([df,out],axis=1)

	## return extended df of pointers and substitutes
	return df

#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__": 

	########################
	## SWITCH FOR TESTING ##
	########################

	## SWITCH ##
	SW_debug=False

	I_test=5 # test indicator

	###########
	## SETUP ##
	###########

	if not SW_debug:

	###############
	## EXECUTION ##
	###############

		if I_test==1:

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

		elif I_test==2:

			## *.in file to be modified ##
			reffile="C:\\Users\\rvcoile\\Documents\\Workers\\PmaxSearchShell\\reffile.in"

			## LHS input generation ##
			# LHS settings
			nLHS=2 # number LHS realizations
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
			LHSprintPath='\\'.join(reffile.split('\\')[0:-1])+'\\LHS_SAFIRinput'
			Print_DataFrame([r,X],LHSprintPath,['r','X'])

			## SAFIR simulation
			# dimension updating
			df=X*10**6
			# simulation run
			multi_Fmax(df,reffile)

		elif I_test==3:
			# test 1 + nodeline adjustment ##

			## *.in file to be modified ##
			reffile="C:\\Users\\rvcoile\\Documents\\Workers\\SAFIRshell\\reffile.in"

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

			# add 'nodeline_Y'
			df['nodeline_Y']=[0.0003,0.00002,0.0001]

			# run multi_Fmax
			multi_Fmax(df,reffile)

		elif I_test==4:

			# out of plumbness; out of straightness
			df=pd.DataFrame([[0.0015,0.0],[0.0,0.2]],columns=[0,1],index=['oop','oos']); df=df.transpose()

			# geomImperf test
			df=geomImperf(df)

			# test
			print(df)

		elif I_test==5:

			# combine I_test 3 and 4

			## *.in file to be modified ##
			## Switch probabSAFIR
			SW_probabMaterial=True

			if SW_probabMaterial: 
				# reffile="C:\\Users\\rvcoile\\Documents\\Workers\\ProbabMaterial\\reffileMaterial.in"
				reffile="C:\\Users\\rvcoile\\Documents\\Workers\\ProbabMaterial\\reffileMaterialconc.in"
			else: reffile="C:\\Users\\rvcoile\\Documents\\Workers\\Imperfection\\reffileGeom.in"

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

			# add 'nodeline_Y'
			df['nodeline_Y']=[0.0003,0.00002,0.0001]
			df['oop']=[0.0015,0.002,0.0]
			df['oos']=[0.004,0.003,0.0]

			# run multi_Fmax
			# multi_Fmax(df,reffile,SW_probabMaterial=SW_probabMaterial)
			multi_FmaxParallel(df,reffile,SW_probabMaterial=SW_probabMaterial)


			# test 1 + nodeline adjustment ##

			# ## *.in file to be modified ##
			# reffile="C:\\Users\\rvcoile\\Documents\\Workers\\Imperfection\\reffileGeom.in"

			# ## realizations pointers ##
			# # copy test 3
			# fc=[25.2,30.7,30.] # [MPa] 20°C concrete compressive strength realization
			# fy=[512.0,420.6,500.] # [MPa] 20°C steel yield stress realization
			# nR=len(fc)
			# X=pd.DataFrame([fc,fy],index=['fc [MPa]','fy [MPa]'],columns=np.arange(nR))
			# X=X.T # transpose(X)
			# df=X*10**6; df.columns=['fc20', 'fy20']
			# df['nodeline_Y']=[0.0003,0.00002,0.0001]
			# # geom imperfection 'out of plumbness', 'out of straightness'
			# df['oop']=[0.0015,0.003,0.0] # [rad] out of plumbness
			# df['oos']=[0.004,0.001,0.0] # [m] out of straightness

			# ## simulation run
			# multi_Fmax(df,reffile)

			

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

