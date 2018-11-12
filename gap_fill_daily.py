import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

#gap_fill is used to fill daily gap fill data 
#Inputs: Dataframe with multiple stations to be gap filled, dataframe for confidence flags that correspond with gap filled data, and dataframe with instrumentation flags for gap filled data
def gap_fill(df,df_flags,df_inst):
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
        #Loop thorugh list of columns to build R^2 values between station that needs to get gap filled and the other 
        #stations. If data cannot be gap filled by the highest confidence station, the next highest station is used and so on
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

    #Get list of all unique stations 
    stnlist_uniques=stnlist.iloc[:,0].unique()

    #Proceed through all the stations in stnlist so that missing data can be gap filled 
    for stn in stnlist_uniques:
        #If no relationship with an R^2 above 0.5 exists, no gap fill can be done and this station-station relationship is passed
        if stn=="no stn":
            pass
        else:
            #Get the gap fill relationships that correspond with the given station 
            stnlist_sub=stnlist[stnlist.iloc[:,0]==stn]
            #Sort the values so that the highest R^2 value is first 
            stnlist_sub=stnlist_sub.sort_values(by='4',ascending=False)
            #Reset the index of the sorted values 
            stnlist_sub.reset_index(drop=True,inplace=True)
            #Loop through the number of relationships to other stations present for the given station 
            for i in range(len(stnlist_sub)):
                #Loop through the dataframe over a three day period (gaps between 1-3 days can be gap filled with linear interpolation)
                for j in range(0,len(df.iloc[:,1]),3):
                    #If there is a gap in the station that is to be gap filled and no gap in the relationship station...
                    if np.isnan(df[stnlist_sub.iloc[i,0]][j]) and ~np.isnan(df[stnlist_sub.iloc[i,1]][j]):
                        #If j is greater than or equal to 30 days before the end of the dataframe
                        if j>=(len(df)-30):
                            #Get the index value of j
                            beg=df.index[j]
                            #Get the index value of the end of the dataframe
                            end=df.index[-1]
                            #Create a new dataframe bounded by the index values 
                            newdf=df[beg:end]
                            #Use the linear relationship provided in stnlist to create new data that can be gap filled based on the regression equation
                            newdata=(newdf[stnlist_sub.iloc[i,1]]*np.array(stnlist_sub['2'][i]))+np.array(stnlist_sub['3'][i])
                            #If the newdata value is exactly the same as the y-intercept, it is reset back to 0
                            newdata=newdata.where(newdata != np.array(stnlist_sub['3'][i]), other=0, inplace=False, axis=None, level=None)
                            #If no new data can be created, pass to the next station 
                            if pd.isnull(newdata).all():
                                pass
                            #Use the pandas method 'fillna' to gap fill the station data with the new data 
                            else:
                                df[stnlist_sub.iloc[i,0]][beg:].fillna(value=newdata)
                        else: #If j is not greater than or equal to 30 days before the end of the dataframe 
                            #Get the index value of j
                            beg=df.index[j]
                            #Get the index value of j plus 30 days 
                            end=df.index[j+30]
                            #Create a new dataframe boudned by the index values 
                            newdf=df[beg:end]
                            #Use the linear relationship provided in stnlist to create new data that can be gap filled based on the regression equation
                            newdata=(newdf[stnlist_sub.iloc[i,1]]*np.array(stnlist_sub['2'][i]))+np.array(stnlist_sub['3'][i])
                            #If the newdata value is exactly the same as the y-intercept, it is reset back to 0
                            newdata=newdata.where(newdata != np.array(stnlist_sub['3'][i]), other=0, inplace=False, axis=None, level=None)
                            #If no new data can be created, pass to the next station 
                            if pd.isnull(newdata).all():
                                pass
                            else:
                                #Use the pandas method 'fillna' to gap fill the station data with the new data 
                                df[stnlist_sub.iloc[i,0]][beg:end]=df[stnlist_sub.iloc[i,0]][beg:end].fillna(value=newdata,inplace=False)
                                #Create flags for all filled values based on the confidence of the gap fill 
                                df_flags[stnlist_sub.iloc[i,0]][beg:end]=df_flags[stnlist_sub.iloc[i,0]][beg:end].fillna(value=stnlist_sub['5'][i],inplace=False)
                                #Create flags for instrumentation used for the gap fill
                                df_inst[stnlist_sub.iloc[i,0]][beg:end]=df_inst[stnlist_sub.iloc[i,0]][beg:end].fillna(value=stnlist_sub['1'][i],inplace=False)
    
    #Return a gap filled dataframe, a list of flags used for each gap fill, and a list of instrumentation used for each gap fill 
    return df,df_flags,df_inst
