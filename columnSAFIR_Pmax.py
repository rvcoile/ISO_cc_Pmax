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
import scipy.optimize as optim
import time

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

def Fmax_SAFIR(filein,P0,t_target,optmethod='Nelder-Mead',deltaPconvCrit=1000,deltaCostCrit=60**2):
	# iteratively searches for SAFIR maximum load value
	#	load value to be modified indicated as "Fsearch" in *.in file
	#	pay attention to load direction ==> link with sign in *.in file
	#	t_target in function of application
	#		- ISO 834: a specified ISO 834 duration
	#		- parametric fire: full fire duration

	## start ##
	###########
	starttime=time.gmtime()

	## control settings ##
	######################
	# convCrit = 20. # [s] convergence criterion (difference maxTime and t_target)

	## initialization ##
	####################
	name='' # name extension for generated *.in files
	targetfolder='\\'.join(filein.split('\\')[0:-1])
	dfpath=targetfolder+'\\Fmax_search'

	## output data ##
	data=pd.DataFrame(['seek',t_target/60.],columns=['target'],index=['P [kN]','tmax [min]'])
	Print_DataFrame([data],dfpath,['iterations']) # initial print
	
	## optimization ##
	##################
	costfunction([P0],filein,name,dfpath,t_target)
	if optmethod=='Nelder-Mead':
		optionsNM={'maxiter': None, 'maxfev': None, 'xatol': 0.0001, 'fatol': 0.0001} # default options
		optionsNM['xatol']=deltaPconvCrit
		optionsNM['fatol']=deltaCostCrit
		optim.minimize(costfunction,P0,args=(filein,name,dfpath,t_target),method='Nelder-Mead',options=optionsNM)

	## print calculation settings log ##
	###################################
	endtime=time.gmtime()
	totaltime=(time.mktime(endtime)-time.mktime(starttime))/60. # [min] total calculation duration
	calcSettingLog(dfpath,filein,optmethod,P0,starttime,endtime,totaltime)


def costfunction(Pi,*args):
	## costfunction for iteration
	# squared error (maxtime-t_target)

	## unpack args ##
	pi=Pi[0]
	filein,name,dfpath,t_target=args

	## read existing data ## - expected overkill - should be in memory to some extent - indicates iteration number
	data=pd.read_excel(dfpath+'.xlsx')
	sim=len(data.columns)-1

	## run SAFIR for Pi ##
	maxTime_i=Pi_SAFIR(pi,filein,name,sim)
	print(maxTime_i)

	## print iteration result ##
	data[sim]=[pi*10**-3,maxTime_i/60.]
	Print_DataFrame([data],dfpath,['iterations']) # print iteration result

	## return squared deviation maxTime_i-t_target ##
	# note: both in [s]
	return (maxTime_i-t_target)**2

def Pi_SAFIR(Pi,filein,name='',sim=0):
	## single iteration of SAFIR calculation

	## initialization ##
	####################

	## Variables to be modified ##
	ref00='Fsearch'
	sub00=str(Pi)
	# combination into Dict for f[mod_inSAFIR]
	modDict={
	ref00:sub00
	}

	## Single load evaluation ##
	############################
	# update *.in file
	# run calculation
	# obtain last converged timestep

	## create new *.in file ##
	simnummer=str(sim).zfill(4) # iteration number with leading zeros (total of 4 characters)
	fileout=filein[:-6]+name+simnummer+'.in'
	mod_inSAFIR(filein,fileout,modDict)

	## run new *.in file ##
	SAFIR_run(fileout)

	## maxTime in *.out file ##
	outfile=deepcopy(fileout); outfile=outfile[0:-2]; outfile+='out'
	maxTime=SAFIR_maxTIME(outfile) # last converged timestep in [s]

	return maxTime

def calcSettingLog(targetfolder,reffile,optmethod,P0,starttime,endtime,duration):

    with open(targetfolder+'.txt','w') as f:
    
	    f.write('LOG OF CALCULATION SETTINGS\n\n')
	    f.write('reference file:\n%s\n' % (reffile))
	    f.write('\nOptimization algorithm: %s\nwith starting value = %d\n' %(optmethod,P0))
	    f.write('\nStart time: %s' % time.strftime("%Y-%m-%d %H:%M:%S", starttime))
	    f.write('\nEnd time: %s' % time.strftime("%Y-%m-%d %H:%M:%S", endtime))
	    f.write('\nDuration: {:.{}f} min'.format(duration,2))


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
		reffile="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\PmaxSearch\\Fsearch_ref.in"

		## initial axial force ##
		P0=6*10**6 # [N]

		## target ISO 834 standard fire duration ##
		tISO=120 # [min]

		## handling ##
		tISO*=60 # [s] dimension change

		# convergence criterion in force - not active
		deltaPconvCrit=1000 # [N]
		deltaCostCrit=60**2 # [s2]

		## execution ##
		# maxTime=Pi_SAFIR(P0,reffile)
		Fmax_SAFIR(reffile,P0,tISO)




	###########
	## DEBUG ##
	###########

	else:

		filein="C:\\Users\\rvcoile\\Documents\\SAFIR\\SAFIRpyTest\\PmaxSearch\\Fsearch_ref.in"
		dfpath='\\'.join(filein.split('\\')[0:-1])+'\\Fmax_search'
		data=pd.read_excel(dfpath+'.xlsx')
		print(data)

		# trial
		sim=0; Pi=6000000; maxTime_i=7200
		data[sim]=[Pi*10**-3,maxTime_i/60.]
		Print_DataFrame([data],dfpath,['iterations']) # print iteration result



# def Fmax_SAFIR(filein,P0,t_target):
# 	# iteratively searches for SAFIR maximum load value
# 	#	load value to be modified indicated as "Fsearch" in *.in file
# 	#	pay attention to load direction ==> link with sign in *.in file
# 	#	t_target in function of application
# 	#		- ISO 834: a specified ISO 834 duration
# 	#		- parametric fire: full fire duration

# 	## control settings ##
# 	######################
# 	convCrit = 20. # [s] convergence criterion (difference maxTime and t_target)

# 	## initialization ##
# 	####################
# 	## calculation parameters ##
# 	P=P0 # axial force
# 	name='' # name extension for generated *.in files
# 	sim=0 # number of iteration
# 	SW_nonConverged=True # Switch indicating if maxLoad converged

# 	## Variables to be modified ##
# 	ref00='Fsearch'
# 	sub00=str(P)
# 	# combination into Dict for f[mod_inSAFIR]
# 	modDict={
# 	ref00:sub00
# 	}

# 	## output data ##
# 	data=pd.DataFrame(index=['P [kN]','tmax [min]'])

# 	while SW_nonConverged:

# 		## Single load evaluation ##
# 		############################
# 		# update *.in file
# 		# run calculation
# 		# obtain last converged timestep

# 		## update P under consideration ##
# 		modDict[ref00]=str(P)

# 		## create new *.in file ##
# 		simnummer=str(sim).zfill(4) # iteration number with leading zeros (total of 4 characters)
# 		fileout=filein[:-6]+name+simnummer+'.in'
# 		mod_inSAFIR(filein,fileout,modDict)

# 		## run new *.in file ##
# 		SAFIR_run(fileout)

# 		## maxTime in *.out file ##
# 		outfile=deepcopy(fileout); outfile=outfile[0:-2]; outfile+='out'
# 		maxTime=SAFIR_maxTIME(outfile) # last converged timestep in [s]

# 		## output for feedback ##
# 		print("maxTime = %iseconds" % maxTime)
# 		data[sim]=[P*10**-3,maxTime/60.]

# 		## Convergence check ##
# 		#######################

# 		if np.abs(maxTime-t_target)<convCrit:
# 			SW_nonConverged=False
# 		else:
# 			sim+=1 # go to next iteration
# 			if sim==1:
# 				if maxTime>t_target: P*=1.1 # P0 to low => add 10%
# 				else: P*=0.9 # P0 to low => reduce with 10%
# 			else:
# 				P=P_iterate(data)
# 				# abort for testing
# 				SW_nonConverged=False

# 	return P,data

# def P_iterate(data,t_target):
# 	# returns next iteration for P
# 	# note: difference in time dimension data and t_target

# 	## note1: possibility to use optimization package or other ##
# 	## note2: possibility to take advantage of deflection information ##

# 	return 8*10**6