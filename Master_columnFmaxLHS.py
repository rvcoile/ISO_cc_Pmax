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

####################
## MODULE IMPORTS ##
####################

## standard module reads
import pandas as pd
import numpy as np

## local function reads
from columnFragility_shell import multi_FmaxParallel

####################
## CONTROL CENTER ##
####################

if __name__ == "__main__": 

	## Switch ##
	############

	# user input reference file and stoch variables
	SW_userInput=False # [boolean] user input vs. hardcoded input
	SW_probabMaterial=True # [boolean] use probabSAFIR *.exe - default = True - should be fully compatible when no probab material models are used - to be confirmed

	# debug control
	SW_debug=False

	## Execution ##
	###############

	if not SW_debug:
		if SW_userInput:

			pass

		else: 

			## reffile ##
			reffile="C:\\Users\\rvcoile\\Documents\\Workers\\ProbabMaterial\\reffileMaterialconc.in"

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

	## Debug ##
	###########
	# temporary hardcoded tests - debug code

	else:

		## reffile ##
		reffile="C:\\Users\\rvcoile\\Documents\\Workers\\ProbabMaterial\\reffileMaterialconc.in"

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