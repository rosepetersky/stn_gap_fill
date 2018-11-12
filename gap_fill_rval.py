
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

#gap_fill_rval(): Function for getting linear regression values ONLY, not any gap filling or flags  
#Inputs: Dataframe with station information 

def gap_fill_rval(df):
    #Create a list of columns
    col_list=df.columns
    #Create an empty list for R^2 values
    rlist=[]
    #Create an empty dataframe for stations 
    stnlist= pd.DataFrame(0, index=range(1), columns=range(4))
    for column in col_list:
        #Drop all columns but the one that will be gap filled 
        df_drop=df.drop(column,axis=1)
        #Get list of columns that were not dropped
        col_list2=df_drop.columns
        #Loop thorugh list of columns to build R^2 values between station that needs to get gap filled and the other stations
        for i in range(len(col_list2)):
            #Create a dataframe with just the column that needs to be gap filled and the given station that could be used to gap fill it
            rdf=pd.DataFrame(data=[df[column],df_drop[col_list2[i]]])
            #Transpose the dataframe
            rdf=rdf.T
            #Get list of columns for dataframe
            rdf.columns=[column,col_list2[i]]
            #Drop all nan values in the dataframe
            rdf=rdf.dropna()
            if len(rdf)==0: #If the dataframe is empty without the nan values
                #Add to the station dataframe that no relationship exists between these stations 
                stnlist=stnlist.append(pd.DataFrame(data=['no stn','no stn',np.nan,np.nan,np.nan,np.nan]).T)
            else: #If the dataframe is not empty without the nan values 
                #Get the slope, intercept, R^2 value, p value, and standard error of a linear regression relationship between
                #The given station (independent variable) and the station that will be gap filled (dependent variable)
                slope, intercept, r_value, p_value, std_err = stats.linregress(rdf.iloc[:,1],rdf.iloc[:,0])
                if r_value>=0.9: #If the R^2 value is greater than 0.9
                    #Create a row for stndf with the station to be gap filled, the station used for gap filling, the slope
                    #the intercept, the R^2 value, and a flag saying that there is high confidence between the given station and the station to be gap-filed
                    rlist=[column,col_list2[i],slope,intercept,r_value,'EHC']
                    #Transpose the row so it can be appended to stnlist
                    rlistdf=pd.DataFrame(rlist).T
                    #Append the row to stnlist
                    stnlist=stnlist.append(rlistdf)
                elif r_value>=0.75 and r_value<0.9: #If the R^2 value is greater than 0.75 but less than 0.9
                    #Create a row for stndf with the station to be gap filled, the station used for gap filling, the slope
                    #the intercept, the R^2 value, and a flag saying that there is medium confidence between the given station and the station to be gap-filed
                    rlist=[column,col_list2[i],slope,intercept,r_value,'EMC']
                    #Transpose the row so it can be appended to stnlist
                    rlistdf=pd.DataFrame(rlist).T
                    #Append the row to stnlist
                    stnlist=stnlist.append(rlistdf)
                elif r_value>=0.5 and r_value<0.75: #If the R^2 value is greater than 0.5 but less than 0.75
                    #Create a row for stndf with the station to be gap filled, the station used for gap filling, the slope
                    #the intercept, the R^2 value, and a flag saying that there is low confidence between the given station and the station to be gap-filed
                    rlist=[column,col_list2[i],slope,intercept,r_value,'ELC']
                    #Transpose the row so it can be appended to stnlist
                    rlistdf=pd.DataFrame(rlist).T
                    #Append the row to stnlist
                    stnlist=stnlist.append(rlistdf)
                else:
                    #Add to the station dataframe that no R^2 greater than or equal to 0.5 exists between these stations 
                    stnlist=stnlist.append(pd.DataFrame(data=['no stn','no stn',np.nan,np.nan,np.nan,np.nan]).T)

    stnlist=stnlist.iloc[1:,:]
    #Name the columns in stnlist
    stnlist.columns=['0','1','2','3','4','5']
    #Drop all duplicated columns
    stnlist=stnlist.drop_duplicates()
    #Reset the index in stnlist to 0
    stnlist.reset_index(drop=True,inplace=True)

    #Only use unique rows in stnlist 
    stnlist_uniques=stnlist.iloc[:,0].unique()
    #Return list of stations along with linear regression information 
    return stnlist
