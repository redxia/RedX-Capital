import os
import snowflake.connector
import pandas as pd
import numpy as np
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import LassoCV

# connects to database then querys it. Returns PD Dataframe
def connect_snwflk(str_query):
    cnx = snowflake.connector.connect( 
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
    cur = cnx.cursor()
    cur.execute(str_query)
    cols = [c[0] for c in cur.description]
    result = cur.fetchall()
    df = pd.DataFrame(data=result, columns=cols) 
    cur.close() # ending the connection
    return df

def linear_roll_fwd(df, start_idx):
    lambdas=lambdas=np.arange(0.01,10,.02)
    df['LR']=np.repeat(np.nan,len(df))
    df['LR_CON']=np.repeat(np.nan,len(df))
    df['LR_CON_PROJ']=np.repeat(np.nan,len(df))
    df['RIDGE']=np.repeat(np.nan,len(df))
    df['LASSO']=np.repeat(np.nan,len(df))
    df['RIDGE_CON']=np.repeat(np.nan,len(df))
    df['LASSO_CON']=np.repeat(np.nan,len(df))
    
    for i in range(start_idx, len(df)-1):
        # Features
        y_shrink=df.loc[0:i,'REVENUE'].to_numpy().reshape(-1,1).ravel()
        y_LR=df.loc[0:i,'REVENUE'].to_numpy().reshape(-1,1)
        X=sm.add_constant(df.loc[0:i,'PROJ'])
        X_con_proj=sm.add_constant(df[['CONSENSUS','PROJ']].loc[0:i])
        X1=df.loc[0:i, 'PROJ'].to_numpy().reshape(-1,1)
        X4_CON_proj=df.loc[0:i,['PROJ','CONSENSUS']]
        X_next=np.array(df.loc[i+1,'PROJ']).reshape(-1,1)
        X_con=sm.add_constant(df['CONSENSUS'].loc[0:i])
        X_next_con=np.array(df.loc[i+1,['PROJ','CONSENSUS']]).reshape(1,-1)

        # models
        ridge_model=RidgeCV(alphas=lambdas).fit(X1,y_shrink)
        lasso_model=LassoCV(cv=2, alphas=lambdas).fit(X1,y_shrink)
        lr_model=sm.OLS(y_LR, X).fit()
        lr_model_con=sm.OLS(y_LR, X_con).fit()
        lr_model_con_proj=sm.OLS(y_LR, X_con_proj).fit()
        ridge_con_model=RidgeCV(alphas=lambdas).fit(X4_CON_proj, y_shrink)
        lasso_con_model=LassoCV(cv=2, alphas=lambdas).fit(X4_CON_proj, y_shrink)

        # storing the predicted models
        df.loc[i+1,"LR"]=lr_model.predict(sm.add_constant(df['PROJ']).loc[i+1].values)
        df.loc[i+1,"LR_CON"]=lr_model_con.predict(sm.add_constant(df['CONSENSUS']).loc[i+1].values)
        df.loc[i+1,"LR_CON_PROJ"]=lr_model_con_proj.predict(sm.add_constant(df[['CONSENSUS','PROJ']]).loc[i+1].values)        
        df.loc[i+1,"RIDGE"]=ridge_model.predict(X_next)
        df.loc[i+1,"LASSO"]=lasso_model.predict(X_next)
        df.loc[i+1,"RIDGE_CON"]=ridge_con_model.predict(X_next_con)
        df.loc[i+1,"LASSO_CON"]=lasso_con_model.predict(X_next_con)
    # accuracy
    df['acc_CON']=np.repeat(np.nan,len(df))
    df.loc[(start_idx+1):,'acc_CON']=(df['CONSENSUS']/df['REVENUE'] - 1)[(start_idx+1):]
    df['acc_PROJ']=np.repeat(np.nan,len(df))
    df.loc[(start_idx+1):,'acc_PROJ']=(df['PROJ']/df['REVENUE'] - 1)[(start_idx+1):]
    df['acc_LR']=df['LR']/df['REVENUE'] - 1
    df['acc_LR_CON']=df['LR_CON']/df['REVENUE'] - 1
    df['acc_LR_CON_PROJ']=df['LR_CON_PROJ']/df['REVENUE'] - 1
    df['acc_RIDGE']=df['RIDGE']/df['REVENUE'] - 1
    df['acc_LASSO']=df['LASSO']/df['REVENUE'] - 1
    df['acc_RIDGE_CON']=df['RIDGE_CON']/df['REVENUE'] - 1
    df['acc_LASSO_CON']=df['LASSO_CON']/df['REVENUE'] - 1

    
    def avg_std(df, column, type='avg'):
        if type=='avg':
            return np.nansum(np.abs(df[column])) / np.count_nonzero(~np.isnan(df[column]))
        elif type=='std':
            return (np.nansum(df[column]**2) / np.count_nonzero(~np.isnan(df[column])))**0.5
        elif type=='median':
            return np.nanmedian(df[column])

    # storing the results overall accuracy
    summary=pd.DataFrame({'CONSENSUS':[avg_std(df, 'acc_CON'), avg_std(df, 'acc_CON', 'std'), avg_std(df, 'acc_CON', 'median')],
                          'PROJ':[avg_std(df, 'acc_PROJ'), avg_std(df, 'acc_PROJ', 'std'), avg_std(df, 'acc_PROJ', 'median')],
                          'LR':[avg_std(df, 'acc_LR'), avg_std(df, 'acc_LR', 'std'), avg_std(df, 'acc_LR', 'median')],
                          'LR_CON':[avg_std(df, 'acc_LR_CON'), avg_std(df, 'acc_LR_CON', 'std'), avg_std(df, 'acc_LR_CON', 'median')],
                          'LR_CON_PROJ':[avg_std(df, 'acc_LR_CON_PROJ'), avg_std(df, 'acc_LR_CON_PROJ', 'std'),avg_std(df, 'acc_LR_CON_PROJ', 'median')],
                          'RIDGE':[avg_std(df, 'acc_RIDGE'), avg_std(df, 'acc_RIDGE', 'std'),avg_std(df, 'acc_RIDGE', 'median')],
                          'LASSO':[avg_std(df, 'acc_LASSO'), avg_std(df, 'acc_LASSO', 'std'),avg_std(df, 'acc_LASSO', 'median')],
                          'RIDGE_CON':[avg_std(df, 'acc_RIDGE_CON'), avg_std(df, 'acc_RIDGE_CON', 'std'), avg_std(df, 'acc_RIDGE_CON', 'median')],
                          'LASSO_CON':[avg_std(df, 'acc_LASSO_CON'), avg_std(df, 'acc_LASSO_CON', 'std'), avg_std(df, 'acc_LASSO_CON', 'median')]}, index=['AVG', "STD", "MEDIAN"])
    return df, summary # Possibly TODO, under overshoot adjustment
        
def plot_lr_splines(df, fig_dims=(12,8)):
    X=sm.add_constant(df['PROJ'])
    X_con=sm.add_constant(df[['CONSENSUS','PROJ']])
    y=df['REVENUE']
    X2=PolynomialFeatures(2).fit_transform(df['PROJ'].to_numpy().reshape(-1,1))
    X3=PolynomialFeatures(3).fit_transform(df['PROJ'].to_numpy().reshape(-1,1))
    model=sm.OLS(y,X).fit()
    print('Linear Regression Model\n',model.summary(), '\n','Residual MSE\n',model.mse_resid,'\n\n')
    plt.figure(1,figsize=fig_dims)
    sns.regplot(x='PROJ', y='REVENUE', data=df)

    lr_model_con=sm.OLS(y, X_con).fit()
    print('Multi Linear Regression Model\n', lr_model_con.summary(), '\n','Residual MSE\n',lr_model_con.mse_resid,
          '\n Residual standard deviation\n ', np.nanstd(lr_model_con.mse_resid), '\n\n')
    plt.figure(2,figsize=fig_dims)
    plt.scatter(range(0,len(y)), lr_model_con.resid)

    model2=sm.OLS(y,X2).fit()
    print('Qudratic Regression Model\n',model2.summary(),'\n','Residual MSE\n',model2.mse_resid,'\n\n')
    plt.figure(3,figsize=fig_dims)
    plt.scatter(df['PROJ'], y)
    plt.plot(df['PROJ'].sort_values(), model2.fittedvalues.sort_values())        

    model3=sm.OLS(y,X3).fit()
    print('Cubic Regression Model\n',model3.summary(),'\n','Residual MSE\n',model3.mse_resid,'\n\n')
    plt.figure(4,figsize=fig_dims)
    plt.scatter(df['PROJ'], y)
    plt.plot(df['PROJ'].sort_values(), model3.fittedvalues.sort_values())   



# IGNORE this generates the whole alpha process
class ALPHA_PROCESS:
    #Class attribute
    ticker = ''
    def __init__(self, ticker):
        self.ticker = ticker

# TODO. INCOMPELTE MAPS THE PROCESS
class MAPPING(ALPHA_PROCESS):
    __ticker=''
    __mapping_str= """SELECT * 
                      FROM research.kdolgin.{symbol}_MAPPING_BUILD_FILE_KEEP;""".format(symbol=__ticker) # file to map
    __df=pd.DataFrame() # the data frame
    __category='' # category value to replace

    def __init__(self, ticker, category, mapping_str):
        self.__ticker=ticker
        self.__category=category
        self.__mapping_str=mapping_str
        self.__df=connect_snwflk(mapping_str)
        
    def set_category(self, category):
        self.__category=category

    def set_mapping_str(self, mapping_str):
        self.__mapping_str=mapping_str
        self.__df=connect_snwflk(mapping_str)

    def get_dataframe(self):
        return self.__df

    def get_members(self):
        return {"TICKER":self.__ticker, "MAPPING_STR":self.__mapping_str, "Data":self.__df, "CATEGORY":self.__category}

    # Used to map the values in the category. df is passed py reference
    # maps the only null values
    def mapping(self, str_filter, value, search_column='MAX_DESCRIPTION', second_str=False, str_filter2='', negation_2nd=False, 
                third_str=False, str_filter3='', negation_3rd=False):
        DSCRPT_NULLS = self.__df.loc[self.__df[self.__category].isnull(), search_column]
        MASK = DSCRPT_NULLS.str.contains(str_filter, case=False, regex=True)
        MASK = MASK[MASK == True]
        if second_str: # does not contain second string
            if third_str:
                if negation_2nd:
                    if negation_3rd:
                        MASK = MASK & ~self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                    case=False, regex=True) & \
                                      ~self.__df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                        case=False, regex=True)
                    else:
                        MASK = MASK & ~self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                    case=False, regex=True) & \
                                       self.__df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                    case=False, regex=True)
                else:
                    if negation_3rd:
                        MASK = MASK & self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                    case=False, regex=True) & \
                                     ~self.__df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                    case=False, regex=True)
                    else:
                        MASK = MASK & self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                        case=False, regex=True) & \
                                      self.__df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                        case=False, regex=True)
            else:
                if negation_2nd:
                    MASK = MASK & ~self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                case=False, regex=True)
                else:
                    MASK = MASK & self.__df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                case=False, regex=True)

            MASK = MASK[MASK == True]
        self.__df.loc[MASK.index, self.__category] = value

class PROJECTION(ALPHA_PROCESS):
    #region private member variables
    __FY_QTR = 'YYYYQQ' #Year and the quarter, pandas default ex. 2020Q1
    __ticker = '' # The ticker symbol
    __cutdate = 'YYYYMMDD' # the week before report
    __prev_15mo = "'YYYY-MM-DD'" # 15 months before the cut date
    __projection_str=""  # SQL string for projection table
    __summary_str="" # SQL string for summary table
    __facility_str="" # SQL string for facility table
    __exclude_id=''
    #endregion private member variables

    def __init__(self, FY_QTR, ticker, cutdate, prev_15mo, exclude_id=''):    
        self.__FY_QTR=FY_QTR
        self.__ticker=ticker
        self.__cutdate=cutdate
        self.__prev_15mo=prev_15mo # used in facility str table
        self.__exclude_id=exclude_id
        self.__projection_str="""SELECT YEAR, QUARTER, QUARTERLY_ESTIMATE/1000000 as RAW_SPEND,
                                 OFFICIAL_REVENUE/1000000 AS REPORTED, FACTOR,
                                 SCALED_QUARTERLY_ESTIMATE/1000000 AS PROJECTIONS 
                                 FROM moa.build_kd_{cutdate}.estimator_12_12_{symbol}_scaled_estimate_{cutdate}_rx
                                 WHERE year >= '2018' ORDER BY 1,2;
                              """.format(cutdate=self.__cutdate, symbol=self.__ticker) 
        self.__summary_str= """SELECT GP_TRANSACTION_DATE, PANEL_FACILITY_CNT, FACILITY_FACTOR, AVG_FACILITY_SPEND, COMPANY_FACILITY_COUNT, TOTAL_SPEND 
                              FROM moa.build_kd_{cutdate}.estimator_12_03_{symbol}_factor_{cutdate}_rx ORDER BY 1 ASC;
                            """.format(cutdate=self.__cutdate, symbol=self.__ticker) 
        if exclude_id:
            self.__facility_str= """SELECT TRANSACTION_DATE, FACILITYID, SUM(TOTAL_SPEND) AS SPEND
                                    FROM moa.BUILD_kd_{cutdate}.runner_11_05_{symbol}_aggregation_{cutdate}
                                    WHERE TRANSACTION_DATE >= {rolling15_month} AND 
                                    facilityid IN (SELECT FACILITY_ID FROM moa.BUILD_kd_{cutdate}.estimator_12_00_all_moa_same_store_{cutdate})
                                    AND facilityid not in ({exclude_id})
                                    GROUP BY 1,2
                                    ORDER BY 1 DESC;
                                """.format(cutdate=self.__cutdate, symbol=self.__ticker, rolling15_month=self.__prev_15mo, exclude_id=self.__exclude_id) 
        else:
            self.__facility_str= """SELECT TRANSACTION_DATE, FACILITYID, SUM(TOTAL_SPEND) AS SPEND
                                    FROM moa.BUILD_kd_{cutdate}.runner_11_05_{symbol}_aggregation_{cutdate}
                                    WHERE TRANSACTION_DATE >= {rolling15_month} AND 
                                    facilityid IN (SELECT FACILITY_ID FROM moa.BUILD_kd_{cutdate}.estimator_12_00_all_moa_same_store_{cutdate})
                                    GROUP BY 1,2
                                    ORDER BY 1 DESC;
                                """.format(cutdate=self.__cutdate, symbol=self.__ticker, rolling15_month=self.__prev_15mo) 

    #region starndard member functions
    def set_projection_str(self, projection_str):
        self.__projection_str = projection_str

    def set_summary_str(self, summary_str):
        self.__summary_str = summary_str

    def set_facility_str(self, facility_str):
        self.__facility_str = facility_str

    def get_members(self):
        return {"FY_QTR":self.__FY_QTR, "TICKER":self.__ticker, "CUTDATE":self.__cutdate, 
                "PREV_15MO":self.__prev_15mo, "PROJECTION_STR":self.__projection_str, 
                "SUMMARY_STR":self.__summary_str, "FACILITY_STR":self.__facility_str}
    #endregion standard member functions

    # USED FOR OUTLIER CHECK EXCEL GENERATION and PROJECTIONS
    def summary_qtr_projection_facility(self, remove_covid=False):
        #region Projection, Summary, Facility tables
        PROJECTION = connect_snwflk(self.__projection_str)
        SUMMARY = connect_snwflk(self.__summary_str)
        FACILILTY = connect_snwflk(self.__facility_str)
        #endregion Projection, Summary, Facility tables

        #region Projection adjustments and cleaning, 12_12 table
        PROJECTION['CALENDAR'] = PROJECTION['YEAR'].astype(str) + "Q" + PROJECTION['QUARTER'].astype(str)
        PROJECTION = PROJECTION.drop(columns=['YEAR','QUARTER']) # reordering the columns
        PROJECTION_COLUMNS = PROJECTION.columns.to_list()
        LAST_COLUMN = [PROJECTION_COLUMNS.pop()]
        LAST_COLUMN.extend(PROJECTION_COLUMNS)
        PROJECTION = PROJECTION[LAST_COLUMN]
        PROJECTION['QoQ'] = PROJECTION['REPORTED'].pct_change() #.round(2) building variables
        PROJECTION['Est_QoQ'] = PROJECTION['PROJECTIONS'].pct_change() #.round(2)
        PROJECTION['ACCURACY'] = (PROJECTION['PROJECTIONS'] / PROJECTION['REPORTED'] - 1) #.round(4)
        PROJECTION['PROJECTIONS'] = PROJECTION['PROJECTIONS'] #.round(1)
        PROJECTION['RAW_SPEND'] = PROJECTION['RAW_SPEND'] #.round(1)
        PROJECTION['FACTOR'] = PROJECTION['FACTOR'] #.round(2)
        #endregion Projection adjustements

        #region summary adjustment and cleaning, 12_03 table
        SUMMARY['FACILITY_FACTOR'] = SUMMARY['FACILITY_FACTOR'].astype(float) #.round(2)
        SUMMARY["AVG_FACILITY_SPEND"] = SUMMARY["AVG_FACILITY_SPEND"].astype(float) #.round(2)
        SUMMARY['COMPANY_Factor_Est'] = (SUMMARY["COMPANY_FACILITY_COUNT"] * SUMMARY['FACILITY_FACTOR']) #.round(2)
        SUMMARY['Estimate'] = (SUMMARY["AVG_FACILITY_SPEND"] * SUMMARY["COMPANY_Factor_Est"]) #.round(2)
        SUMMARY['TOTAL_SPEND'] = SUMMARY['TOTAL_SPEND'].astype(float) #.round(2)
        #endregion summary adjustment

        #region making quarterly revenues
        # group by the date to sum quarterly estimates
        SUMMARY_QTR = SUMMARY.copy()
        SUMMARY_QTR['GP_TRANSACTION_DATE'] = pd.PeriodIndex(SUMMARY_QTR['GP_TRANSACTION_DATE'], freq='Q')
        SUMMARY_QTR = SUMMARY_QTR.groupby("GP_TRANSACTION_DATE", as_index=False)["TOTAL_SPEND"].sum()
        SUMMARY_QTR['TOTAL_SPEND']  = SUMMARY_QTR['TOTAL_SPEND'].astype(float) #.round(2)
        SUMMARY_QTR = SUMMARY_QTR.rename(columns={"GP_TRANSACTION_DATE":'Calendar', "TOTAL_SPEND":"EST"})
        #endregion quarterly revenues

        #region raw projection tables
        # Similar process to projections, but we don't run the linear regression here
        RAW_PROJECTION = PROJECTION.copy()
        RAW_PROJECTION.loc[:,'RAW_SPEND'] = (SUMMARY_QTR.loc[SUMMARY_QTR['Calendar'].astype(str).isin(RAW_PROJECTION['CALENDAR']),'EST'].values / 1000000) #.round(1)
        RAW_PROJECTION.loc[:,'FACTOR'] = (RAW_PROJECTION['REPORTED'].rolling(4).sum() / RAW_PROJECTION['RAW_SPEND'].rolling(4).sum()) #.round(2)
        prev_qtr_index = RAW_PROJECTION[self.__FY_QTR==RAW_PROJECTION['CALENDAR']].index[0]-1
        RAW_PROJECTION['FACTOR'] = RAW_PROJECTION.loc[prev_qtr_index,'FACTOR']
        RAW_PROJECTION['PROJECTIONS'] = (RAW_PROJECTION['RAW_SPEND'] * RAW_PROJECTION['FACTOR']) #.round(1)
        RAW_PROJECTION['QoQ'] = RAW_PROJECTION['REPORTED'].pct_change() #.round(2)
        RAW_PROJECTION['Est_QoQ'] = RAW_PROJECTION['PROJECTIONS'].pct_change() #.round(2)
        RAW_PROJECTION['ACCURACY'] = (RAW_PROJECTION['PROJECTIONS'] / RAW_PROJECTION['REPORTED'] - 1) #.round(4)
        #endregion raw projection tables

        #region facility and pivot table, 11_03 and grannular facility tables
        # group by date and facility id. Creates the outliier check through standard deviations
        # orders by standard deviations
        FACILITY = FACILILTY.groupby(["FACILITYID","TRANSACTION_DATE"],as_index=False)["SPEND"].sum()
        FACILITY["SPEND"] = FACILITY["SPEND"].astype(float)
        FACILITY_PIVOT = pd.pivot_table(FACILITY, values="SPEND", index="FACILITYID", columns="TRANSACTION_DATE")

        FACTILITY_PIVOT_STD = FACILITY_PIVOT.rolling(window=12, min_periods=3, axis=1).std().copy()
        FACILITY_COMPARE = pd.concat([FACILITY_PIVOT, FACTILITY_PIVOT_STD], axis=1)
        LAST_COLUMN = FACILITY_COMPARE.columns[-1]
        FACILITY_COMPARE.columns = [*FACILITY_COMPARE.columns[:-1],'TO_SORT']
        FACILITY_COMPARE = FACILITY_COMPARE.sort_values(by=[FACILITY_COMPARE.columns[-1]], ascending=False)
        FACILITY_COMPARE.columns = [*FACILITY_COMPARE.columns[:-1], LAST_COLUMN]
        #endregion facility and pivot table

        #region Linear regression
        # Produces a new quarterly sum
        linear_regression = SUMMARY.copy()
        if remove_covid: # This remove the covid months in the linear regression projections
            mar_apr = np.logical_and(linear_regression['GP_TRANSACTION_DATE'].astype(str) != '2020-04-01', linear_regression['GP_TRANSACTION_DATE'].astype(str) != '2020-05-01')
            linear_regression = linear_regression[mar_apr]
            len_summary = len(linear_regression.loc[mar_apr,'COMPANY_Factor_Est'])
            y = linear_regression.loc[mar_apr,'COMPANY_Factor_Est'][(len_summary - 21):(len_summary - 3)].reset_index(drop=True) 
        else:
            len_summary = len(linear_regression['COMPANY_Factor_Est'])
            y = linear_regression['COMPANY_Factor_Est'][(len_summary - 21):(len_summary - 3)].reset_index(drop=True) 

        # The linear regression of facility based on time or index
        X = (y.index + 1) # start index from 1
        X = sm.add_constant(X)
        model = sm.OLS(y,X).fit()
        pred_X = sm.add_constant(range(19,22))
        prediction = model.predict(pred_X) #.round(2)
        
        # Aggregating the results into the quarterlys
        linear_regression.iloc[-3:,6]  = prediction #6 for the company factor estimate update
        linear_regression['Estimate'] = (linear_regression["AVG_FACILITY_SPEND"] * linear_regression["COMPANY_Factor_Est"]) #.round(2)
        # updating the quarterly spendings.
        linear_regression['GP_TRANSACTION_DATE'] = pd.PeriodIndex(linear_regression['GP_TRANSACTION_DATE'], freq='Q')
        linear_regression = linear_regression.groupby("GP_TRANSACTION_DATE", as_index=False)["Estimate"].sum()

        # This produces the projection tables similar to 12_12
        LR_PROJECTION = PROJECTION.copy()
        is_in_PROJ = LR_PROJECTION['CALENDAR'].isin(linear_regression['GP_TRANSACTION_DATE'].astype(str))
        is_in_LR = linear_regression['GP_TRANSACTION_DATE'].astype(str).isin(LR_PROJECTION['CALENDAR'])
        LR_PROJECTION.loc[is_in_PROJ, 'PROJECTIONS'] = (linear_regression.loc[is_in_LR,'Estimate'] / 1000000).to_numpy() # .round(1)
        LR_PROJECTION['SCALE_ADJUST'] = (LR_PROJECTION['REPORTED'].rolling(4).sum() / LR_PROJECTION['PROJECTIONS'].rolling(4).sum()) #.round(2)
        prev_qtr_index = LR_PROJECTION[self.__FY_QTR==LR_PROJECTION['CALENDAR']].index[0]-1
        LR_PROJECTION['SCALE_ADJUST'] = LR_PROJECTION.iloc[prev_qtr_index, 8] # 8 for the scale adjust
        LR_PROJECTION['ADJ_PROJECTIONS'] = (LR_PROJECTION['SCALE_ADJUST'] * LR_PROJECTION['PROJECTIONS']) #.round(1)
        LR_PROJECTION['ACCURACY'] = (LR_PROJECTION['ADJ_PROJECTIONS'] / LR_PROJECTION['REPORTED'] - 1) #.round(4)
        #endregion Linear regression

        with pd.ExcelWriter("Alphas\\"+self.__ticker.split('_')[0]+"\\"+self.__ticker+"_" + self.__FY_QTR + "_Estimate_"+self.__cutdate+".xlsx") as writer:
            SUMMARY.to_excel(writer, sheet_name=self.__ticker + "_SUMMARY", index=False)
            SUMMARY_QTR.to_excel(writer, sheet_name=self.__ticker + "_QTR", index=False)
            RAW_PROJECTION.to_excel(writer, sheet_name=self.__ticker + "_RAW_PROJECTIONS", index=False)
            PROJECTION.to_excel(writer, sheet_name=self.__ticker + "_PROJECTIONS", index=False)
            FACILITY_COMPARE.to_excel(writer, sheet_name=self.__ticker+"_OUTLIER_CHECK")
            linear_regression.to_excel(writer, sheet_name=self.__ticker+"EST_QTR_SUM", index=False)
            LR_PROJECTION.to_excel(writer, sheet_name="LR_PROJECTION", index=False)
        return RAW_PROJECTION, PROJECTION, LR_PROJECTION

# GROWTH is used for analytical and exploratory checking of the process
class GROWTH(ALPHA_PROCESS):
    __ticker=''
    __cutdate=''
    __sql_qry="""select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                 from moa_live.stage.{symbol}_data_{date} 
                 group by 1,2,3,4,5,6,7,8
                 order by 4;""".format(symbol=__ticker, date=__cutdate) # data to analyze
    __df=pd.DataFrame()
    __df_rev=pd.DataFrame()
    __SPEND=pd.DataFrame()
    __QTR_SPEND=pd.DataFrame()
    __MOA_REV=pd.DataFrame()
    __MOA_REV_PROP=pd.DataFrame()
    __PRODUCT_FAMILY=pd.DataFrame()
    __PRODUCT_CATEGORY=pd.DataFrame()
    __REVENUE_DIVISION=pd.DataFrame()

    #TODO PLOTTING FUNCTIONS together.

    def __init__(self, ticker, cutdate, sql_qry, rev_dict):
        self.__ticker=ticker
        self.__cutdate=cutdate
        self.__sql_qry=sql_qry
        self.__df=connect_snwflk(sql_qry)
        self.__df_rev=pd.DataFrame(rev_dict)
    def set_sql_qry(self, sql_query):
        self.__sql_qry=sql_query
    def set_cutdate(self, date):
        self.__cutdate=date
    def set_df(self):
        self.__df=connect_snwflk(self.__sql_qry)
    def set_df_rev(self, rev_dict):
        self.__df_rev=pd.DataFrame(rev_dict)
    def get_members(self):
        return {'Ticker':self.__ticker, 'Cutdate':self.__cutdate, 'SQL_QUERY':self.__sql_qry, 'RAW_DATA':self.__df, 'Reported_Revenue':self.__df_rev, 'SPEND_DATA':self.__SPEND, 'QTR_SPEND':self.__QTR_SPEND, 'MOA_REV':self.__MOA_REV, 'MOA_REV_PROP':self.__MOA_REV_PROP, 'PRODUCT_FAMILY':self.__PRODUCT_FAMILY, 'PRODUCT_CATEGORY':self.__PRODUCT_CATEGORY, 'REVENUE_DIVISION':self.__REVENUE_DIVISION}

    def spend_growth_rate(self):
        # TODO MAYBE PUT UPPER LOWER ESTIMATES for next quarter
        #raw data spendings
        self.__PRODUCT_FAMILY = self.__df.groupby(['TRANSACTION_DATE','PRODUCT_FAMILY'], as_index=False)['SPEND'].sum().round(2)
        self.__PRODUCT_CATEGORY = self.__df.groupby(['TRANSACTION_DATE','PRODUCT_CATEGORY'], as_index=False)['SPEND'].sum().round(2)
        self.__REVENUE_DIVISION = self.__df.groupby(['TRANSACTION_DATE','REVENUE_DIVISION'], as_index=False)['SPEND'].sum().round(2)

        # TODO possibly monthly spending
        # Regular spending and quarterly
        self.__SPEND = self.__df.groupby(['TRANSACTION_DATE'], as_index=False)['SPEND'].sum()
        self.__SPEND['SPEND'] = self.__SPEND['SPEND'].astype(float)
        self.__SPEND['SEQ_GROWTH'] = (self.__SPEND['SPEND'] / self.__SPEND['SPEND'].shift(3) - 1).round(4).replace([np.inf,-np.inf], np.nan)
        self.__SPEND['MoM_GROWTH'] = self.__SPEND['SPEND'].pct_change()

        self.__QTR_SPEND = self.__SPEND.copy()
        self.__QTR_SPEND['DATE'] = pd.PeriodIndex(self.__QTR_SPEND['TRANSACTION_DATE'], freq='Q').astype(str)
        self.__QTR_SPEND = self.__QTR_SPEND.groupby('DATE', as_index=False)['SPEND'].sum().round(2)

        # Actual Revenue 
        # TODO get the revenue directly from sql
        self.__df_rev['QoQ_GROWTH'] = (self.__df_rev['SPEND'] / self.__df_rev['SPEND'].shift() - 1).round(4).replace([np.inf,-np.inf], np.nan)
        self.__df_rev['YoY_GROWTH'] = (self.__df_rev['SPEND'] / self.__df_rev['SPEND'].shift(4) - 1).round(4).replace([np.inf,-np.inf], np.nan)
        self.__df_rev['Color'] = 'Actual'
        self.__QTR_SPEND['QoQ_GROWTH'] = (self.__QTR_SPEND['SPEND'] / self.__QTR_SPEND['SPEND'].shift() - 1).round(4).replace([np.inf,-np.inf], np.nan)
        self.__QTR_SPEND['YoY_GROWTH'] = (self.__QTR_SPEND['SPEND'] / self.__QTR_SPEND['SPEND'].shift(4) - 1).round(4).replace([np.inf,-np.inf], np.nan)
        self.__QTR_SPEND['Color'] = 'MOA'
        self.__MOA_REV = pd.concat([self.__df_rev, self.__QTR_SPEND], ignore_index=True)
        self.__MOA_REV_PROP = self.__df_rev.merge(self.__QTR_SPEND, how='left', on='DATE')
        self.__MOA_REV_PROP['PROPORTION'] = (self.__MOA_REV_PROP['SPEND_y'] / self.__MOA_REV_PROP['SPEND_x']).round(4) # x is actual
        # TODO proportion might be a good estimator for next period growth.
        # do some kind of regression for next period growth
        return self.__df, self.__SPEND, self.__QTR_SPEND, self.__df_rev, self.__MOA_REV, self.__MOA_REV_PROP, self.__PRODUCT_FAMILY, self.__PRODUCT_CATEGORY, self.__REVENUE_DIVISION

    # TODO maybe make it all contained variables
    # Two months is the missing arguments where we need the require growth of 2 months
    # month1_spend, month2_spend are the if case scenarios growth rates
    # TODO add the month over month growth, also add the growth from month over month
    def required_growth(self, two_months=True, month1_growth=0.0):
        if two_months:
            # Spend x is actual, spend y is moa adj. 
            residual_months = self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_x'] - self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_y']
            sum_prev_resid_months = self.__SPEND.iloc[-3:-1,1].sum().round(2) # Second and third months ago spendings
            total_growth = (residual_months / sum_prev_resid_months - 1).round(4)
            residual_last = (residual_months - self.__SPEND.iloc[-3,1] * (1 + month1_growth)).round(2)
            month2_growth = (residual_last / self.__SPEND.iloc[-2,1] - 1).round(4)
            if (self.__SPEND.iloc[-3,1] * (1 + month1_growth)).round(2) > residual_last:
                print('first month grows faster than second month')
            required_growth = {'residual_spend':residual_months, 'prev_seq_resid_spend': sum_prev_resid_months, 'growth_mo1':month1_growth, 'growth_mo2':month2_growth, 'total_growth':total_growth, 
            'middle_mo_spend':(self.__SPEND.iloc[-3,1] * (1 + month1_growth)).round(2), 'last_mo_spend':residual_last, 'QTR_REV': self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_x']}
        else:
            # Spend x is actual, spend y is moa adj. 
            residual_months = self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_x'] - self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_y']
            sum_prev_resid_months = self.__SPEND.iloc[-3:-2,1] # third months ago spendings
            growth_last = residual_months / sum_prev_resid_months - 1
            required_growth = {'residual_spend':residual_months.round(2), 'prev_seq_spend':sum_prev_resid_months.round(2).values[0], 'last_growth':growth_last.round(4).values[0], 'QTR_SPEND': self.__MOA_REV_PROP.loc[len(self.__MOA_REV_PROP)-1,'SPEND_x']}
        return required_growth

    def plot_categories(self, fig_dims=(12,8)):
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.lineplot(data=self.__PRODUCT_FAMILY, x='TRANSACTION_DATE', y='SPEND', hue='PRODUCT_FAMILY').set_title('Monthly Product Family Revenue')

        #product category
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.lineplot(data=self.__PRODUCT_CATEGORY, x='TRANSACTION_DATE', y='SPEND', hue='PRODUCT_CATEGORY').set_title('Monthly Product Category Revenue')

        #revenue division
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.lineplot(data=self.__REVENUE_DIVISION, x='TRANSACTION_DATE', y='SPEND', hue='REVENUE_DIVISION').set_title('Monthly Revenue Division')
        return None

    # possibly add boolean to cut or not
    def plot_rev_trend(self, date_cut, fig_dims=(12,8)):
        # Monthly Spending
        self.__SPEND.plot(x='TRANSACTION_DATE', y='SPEND', style='.-', title='Monthly Spending MOA', figsize=fig_dims)

        # MoM Growth
        SPEND = self.__SPEND.copy()
        SPEND.plot(x='TRANSACTION_DATE', y='MoM_GROWTH', style='.--', figsize=fig_dims, title='MoM Spending Growth')

        fig,ax = plt.subplots(figsize=fig_dims)
        sns.regplot(data=SPEND, x=(SPEND.index+1), y='MoM_GROWTH').set_title('MoM Spending Growth Regression')

        # Sequential growth
        self.__SPEND.plot(x='TRANSACTION_DATE', y='SEQ_GROWTH', style='.-', figsize=fig_dims, title='3 Month Sequential Growth')

        # Regression plot of sequential growth
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.regplot(data=self.__SPEND, x=(self.__SPEND.index+1), y='SEQ_GROWTH').set_title('Sequential Growth Monthly Spending MOA Regression')

        # QTR SPENDINGS
        QTR_SPEND = self.__QTR_SPEND[self.__QTR_SPEND['DATE'].astype(str) >= date_cut]
        QTR_SPEND.plot(x='DATE', y='SPEND', style='.-', title='MOA QTR SPENDING', figsize=fig_dims)
        
        # Compare QTR SPEND to Actual
        MOA_REV = self.__MOA_REV[self.__MOA_REV['DATE'].astype(str) >= date_cut]
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.lineplot(data=MOA_REV, x='DATE', y='SPEND', hue='Color').set_title('QTR SPENDING MOA vs. Actual')        

        # Plot the proportion and compare the spendings
        self.__MOA_REV_PROP.iloc[0:-1,:].plot(x='DATE', y='PROPORTION', style='.-', figsize=fig_dims, title='MOA to Actual Proportion')
        self.__MOA_REV_PROP.iloc[0:-1,:].plot(x='SPEND_y', y='SPEND_x', style='.', figsize=fig_dims, title='MOA (x-axis) vs Acutal (y-axis) Spending')

        # Compares the regression 
        fig,ax = plt.subplots(figsize=fig_dims)
        sns.regplot(x='SPEND_y', y='SPEND_x', data=self.__MOA_REV_PROP.iloc[0:-1,:]).set_title('MOA (x-axis) vs. Actual (y-axis) regression plot')

        # Regression summary
        X = self.__MOA_REV_PROP['SPEND_y'][0:-1]
        X = sm.add_constant(X)
        y = self.__MOA_REV_PROP['SPEND_x'][0:-1]
        model = sm.OLS(y,X).fit()
        print(model.summary())
        return None

    def plot_growth_adj(self, fig_dims=(12,8)):
        self.__df_rev.plot(x='DATE', y='YoY_GROWTH', style='.--', figsize=fig_dims, title='Actual Revenue YoY Growth Plot')
        self.__df_rev.plot(x='DATE', y='QoQ_GROWTH', style='.--', figsize=fig_dims, title='Actual Revenue QoQ Growth Plot')

        fig,ax = plt.subplots(figsize=fig_dims) # regression ignores 0 index
        sns.regplot(data=self.__df_rev, x=(self.__df_rev.index+1), y='YoY_GROWTH').set_title('Actual Revenue YoY Growth Regression')
        
        fig,ax = plt.subplots(figsize=fig_dims) # regression ignores 0 index
        sns.regplot(data=self.__df_rev, x=(self.__df_rev.index+1), y='QoQ_GROWTH').set_title('Actual Revenue QoQ Growth Regression')

        return None

    def LR_plots(self, fig_dims=(12,8)):
        # TODO maybe add the predicted plot
        # Compares the regression 
        #fig,ax = plt.subplots(figsize=fig_dims)
        y = self.__MOA_REV_PROP['SPEND_x'][0:-1]
        X1 = sm.add_constant(self.__MOA_REV_PROP['SPEND_y'][0:-1])
        X2 = PolynomialFeatures(2).fit_transform(self.__MOA_REV_PROP['SPEND_y'][0:-1].to_numpy().reshape(-1,1))
        X3 = PolynomialFeatures(3).fit_transform(self.__MOA_REV_PROP['SPEND_y'][0:-1].to_numpy().reshape(-1,1))

        model1 = sm.OLS(y,X1).fit()
        print('Linear Regression Model\n',model1.summary(), '\n','Residual MSE\n',model1.mse_resid,'\n\n')
        plt.figure(1,figsize=fig_dims)
        sns.regplot(x='SPEND_y', y='SPEND_x', data=self.__MOA_REV_PROP.iloc[0:-1,:]).set_title('MOA (x-axis) vs. Actual (y-axis) regression plot')

        model2 = sm.OLS(y,X2).fit()
        print('Qudratic Regression Model\n',model2.summary(),'\n','Residual MSE\n',model2.mse_resid,'\n\n')
        plt.figure(2,figsize=fig_dims)
        plt.scatter(self.__MOA_REV_PROP['SPEND_y'][0:-1], self.__MOA_REV_PROP['SPEND_x'][0:-1])
        plt.plot(self.__MOA_REV_PROP['SPEND_y'][0:-1].sort_values(), model2.fittedvalues.sort_values())        

        model3 = sm.OLS(y,X3).fit()
        print('Cubic Regression Model\n',model3.summary(),'\n','Residual MSE\n',model3.mse_resid,'\n\n')
        plt.figure(3,figsize=fig_dims)
        plt.scatter(self.__MOA_REV_PROP['SPEND_y'][0:-1], self.__MOA_REV_PROP['SPEND_x'][0:-1])
        plt.plot(self.__MOA_REV_PROP['SPEND_y'][0:-1].sort_values(), model3.fittedvalues.sort_values())

    def adjust_proj_qtr(self, moa_spend):
        pred = {'LR':0, 'Qudratic':0, 'Cubic':0, "Min":0, "Max":0, "Input":moa_spend}
        y = self.__MOA_REV_PROP['SPEND_x'][0:-1]
        X1 = sm.add_constant(self.__MOA_REV_PROP['SPEND_y'][0:-1])
        pred['Min'] = min(self.__MOA_REV_PROP['SPEND_y'][0:-1])
        pred['Max'] = max(self.__MOA_REV_PROP['SPEND_y'][0:-1])
        # TODO print out the ranges and the value to predict
        model1 = sm.OLS(y,X1).fit()
        pred['LR'] = [model1.params[0] + moa_spend * model1.params[1]]

        X2 = PolynomialFeatures(2).fit_transform(self.__MOA_REV_PROP['SPEND_y'][0:-1].to_numpy().reshape(-1,1))
        model2 = sm.OLS(y,X2).fit()
        pred['Qudratic'] = [model2.params[0] + moa_spend * model2.params[1] + moa_spend**2 * model2.params[2]]

        X3 = PolynomialFeatures(3).fit_transform(self.__MOA_REV_PROP['SPEND_y'][0:-1].to_numpy().reshape(-1,1))
        model3 = sm.OLS(y,X3).fit()
        pred['Cubic'] = [model3.params[0] + moa_spend * model3.params[1] + moa_spend**2 * model3.params[2] + moa_spend**3 * model3.params[3]]

        #X4 = sm.add_constant(np.log(self.__MOA_REV_PROP['SPEND_y'][0:-1]))
        #model4 = sm.OLS(y,X4).fit()
        return(pd.DataFrame(pred))

    def dist_model_qtr_adj(self):

        self.__df['REPORTED_MoM'] = self.__df['REPORTED'].pct_change()
        self.__df['SPEND_MoM'] = self.__df['SPEND'].pct_change()


# line chart growth, deprecated
# Used in NARI.py, converts monthly to quarterly spendings
def NARI_mon2qtr_spend(df, group, category_1=False):
    # adjusts the spend to float and int
    df['GP_TRANSACTION_DATE'] = pd.PeriodIndex(df['GP_TRANSACTION_DATE'], freq='Q') # convert to quarterly
    df = df.groupby(group, as_index=False)['TOTAL_SPEND'].sum()
    df['TOTAL_SPEND']  = df['TOTAL_SPEND'].astype(float).round(0).astype(int)

    # combining the string levels
    group.remove('GP_TRANSACTION_DATE')
    if not category_1: # remove category 1 level if it isn't relevant from boolean argument
        group.remove('CATEGORY_1')
    df['PRODUCT'] = df[group].apply(lambda row: '_'.join(row.values.astype(str)), axis = 1) # used for hue
    df = df.rename(columns={'GP_TRANSACTION_DATE':'YEAR_QTR','TOTAL_SPEND':'REPORTED_REVENUE'})
    df['YEAR_QTR'] = df['YEAR_QTR'].astype(str)
    return df

