
def query_snflk(str_query):
    import gp.snowflake
    import pandas as pd
    cnx = gp.snowflake.connect()
    cur = cnx.cursor()
    cur.execute(str_query)
    cols = [c[0] for c in cur.description]
    result = cur.fetchall()
    df = pd.DataFrame(data=result, columns=cols) 
    cur.close() # ending the connection
    return df

class PROJECTION():
    #region private member variables
    __FY_QTR = 'YYYYQQ' #Year and the quarter, pandas default ex. 2020Q1
    __ticker = '' # The ticker symbol
    __cutdate = 'YYYYMMDD' # the week before report
    __prev_18mo = "'YYYY-MM-DD'" # 18 months before the FY_QTR
    __projection_str=""  # SQL string for projection table
    __summary_str="" # SQL string for summary table
    __facility_str="" # SQL string for facility table
    __same_store=True
    __exclude_id=''
    #endregion private member variables

    def __init__(self, FY_QTR, ticker, cutdate, prev_18mo, exclude_id, same_store):    
        self.__FY_QTR=FY_QTR
        self.__ticker=ticker
        self.__cutdate=cutdate
        self.__prev_18mo=prev_18mo # used in facility str table
        self.__same_store=same_store
        if same_store:
            self.__projection_str="""SELECT YEAR, QUARTER, QUARTERLY_ESTIMATE/1000000 as RAW_SPEND,
                                    OFFICIAL_REVENUE/1000000 AS REPORTED, FACTOR,
                                    SCALED_QUARTERLY_ESTIMATE/1000000 AS PROJECTIONS 
                                    FROM moa.build_kd_{cutdate}.estimator_12_12_{symbol}_scaled_estimate_{cutdate}_rx
                                    WHERE year >= '2016' 
                                    ORDER BY 1,2;
                                """.format(cutdate=self.__cutdate, symbol=self.__ticker) 
            self.__summary_str= """SELECT GP_TRANSACTION_DATE, PANEL_FACILITY_CNT, FACILITY_FACTOR, AVG_FACILITY_SPEND, COMPANY_FACILITY_COUNT, TOTAL_SPEND 
                        FROM moa.build_kd_{cutdate}.estimator_12_03_{symbol}_factor_{cutdate}_rx ORDER BY 1 ASC;
                    """.format(cutdate=self.__cutdate, symbol=self.__ticker) 
        else:
            self.__projection_str="""SELECT YEAR, QUARTER, QUARTERLY_ESTIMATE/1000000 as RAW_SPEND,
                        OFFICIAL_REVENUE/1000000 AS REPORTED, FACTOR,
                        SCALED_QUARTERLY_ESTIMATE/1000000 AS PROJECTIONS 
                        FROM moa.build_kd_{cutdate}.estimator_12_12_{symbol}_scaled_estimate_{cutdate}_non_SS_rx
                        WHERE year >= '2016' 
                        ORDER BY 1,2;
                    """.format(cutdate=self.__cutdate, symbol=self.__ticker) 
            self.__summary_str= """SELECT GP_TRANSACTION_DATE, PANEL_FACILITY_CNT, FACILITY_FACTOR, AVG_FACILITY_SPEND, COMPANY_FACILITY_COUNT, TOTAL_SPEND 
                        FROM moa.build_kd_{cutdate}.estimator_12_03_{symbol}_factor_{cutdate}_non_SS_rx ORDER BY 1 ASC;
                    """.format(cutdate=self.__cutdate, symbol=self.__ticker) 

        if exclude_id:
            self.__facility_str= """SELECT TRANSACTION_DATE, FACILITYID, SUM(TOTAL_SPEND) AS SPEND
                                    FROM moa.BUILD_kd_{cutdate}.runner_11_05_{symbol}_aggregation_{cutdate}
                                    WHERE TRANSACTION_DATE >= {rolling18_month} AND 
                                    facilityid IN (SELECT FACILITY_ID FROM moa.BUILD_kd_{cutdate}.estimator_12_00_all_moa_same_store_{cutdate})
                                    AND facilityid not in ({exclude_id})
                                    GROUP BY 1,2
                                    ORDER BY 1 DESC;
                                """.format(cutdate=self.__cutdate, symbol=self.__ticker, rolling18_month=self.__prev_18mo, exclude_id=self.__exclude_id) 
        else:
            self.__facility_str= """SELECT TRANSACTION_DATE, FACILITYID, SUM(TOTAL_SPEND) AS SPEND
                                    FROM moa.BUILD_kd_{cutdate}.runner_11_05_{symbol}_aggregation_{cutdate}
                                    WHERE TRANSACTION_DATE >= {rolling18_month} AND 
                                    facilityid IN (SELECT FACILITY_ID FROM moa.BUILD_kd_{cutdate}.estimator_12_00_all_moa_same_store_{cutdate})
                                    GROUP BY 1,2
                                    ORDER BY 1 DESC;
                                """.format(cutdate=self.__cutdate, symbol=self.__ticker, rolling18_month=self.__prev_18mo)



    def summary_qtr_projection_facility(self, remove_covid=False):
        import pandas as pd
        import numpy as np
        import statsmodels.api as sm

        #region Projection, Summary, Facility tables
        PROJECTION = query_snflk(self.__projection_str)
        SUMMARY = query_snflk(self.__summary_str)
        #endregion Projection, Summary

        #region Projection adjustments and cleaning, 12_12 table
        PROJECTION['CALENDAR'] = PROJECTION['YEAR'].astype(str) + "Q" + PROJECTION['QUARTER'].astype(str)
        PROJECTION = PROJECTION.drop(columns=['YEAR','QUARTER']) # reordering the columns
        PROJECTION_COLUMNS = PROJECTION.columns.to_list()
        LAST_COLUMN = [PROJECTION_COLUMNS.pop()]
        LAST_COLUMN.extend(PROJECTION_COLUMNS)
        PROJECTION = PROJECTION[LAST_COLUMN]
        PROJECTION['QoQ'] = PROJECTION['REPORTED'].pct_change() 
        PROJECTION['Est_QoQ'] = PROJECTION['PROJECTIONS'].pct_change() 
        PROJECTION['ACCURACY'] = (PROJECTION['PROJECTIONS'] / PROJECTION['REPORTED'] - 1) 
        #endregion Projection adjustements

        #region summary adjustment and cleaning, 12_03 table
        SUMMARY['FACILITY_FACTOR'] = SUMMARY['FACILITY_FACTOR'].astype(float) 
        SUMMARY["AVG_FACILITY_SPEND"] = SUMMARY["AVG_FACILITY_SPEND"].astype(float) 
        SUMMARY['COMPANY_Factor_Est'] = (SUMMARY["COMPANY_FACILITY_COUNT"] * SUMMARY['FACILITY_FACTOR']) 
        SUMMARY['Estimate'] = (SUMMARY["AVG_FACILITY_SPEND"] * SUMMARY["COMPANY_Factor_Est"]) 
        SUMMARY['TOTAL_SPEND'] = SUMMARY['TOTAL_SPEND'].astype(float) 
        #endregion summary adjustment

        #region making quarterly revenues
        # group by the date to sum quarterly estimates
        SUMMARY_QTR = SUMMARY.copy()
        SUMMARY_QTR['GP_TRANSACTION_DATE'] = pd.PeriodIndex(SUMMARY_QTR['GP_TRANSACTION_DATE'], freq='Q')
        SUMMARY_QTR = SUMMARY_QTR.groupby("GP_TRANSACTION_DATE", as_index=False)["TOTAL_SPEND"].sum()
        SUMMARY_QTR['TOTAL_SPEND']  = SUMMARY_QTR['TOTAL_SPEND'].astype(float) 
        SUMMARY_QTR = SUMMARY_QTR.rename(columns={"GP_TRANSACTION_DATE":'Calendar', "TOTAL_SPEND":"EST"})
        #endregion quarterly revenues

        #region raw projection tables
        # Similar process to projections, but we don't run the linear regression here
        RAW_PROJECTION = PROJECTION.copy()
        RAW_PROJECTION.loc[:,'RAW_SPEND'] = (SUMMARY_QTR.loc[SUMMARY_QTR['Calendar'].astype(str).isin(RAW_PROJECTION['CALENDAR']),'EST'].values / 1000000) 
        RAW_PROJECTION.loc[:,'FACTOR'] = (RAW_PROJECTION['REPORTED'].rolling(4).sum() / RAW_PROJECTION['RAW_SPEND'].rolling(4).sum()) 
        prev_qtr_index = RAW_PROJECTION[self.__FY_QTR==RAW_PROJECTION['CALENDAR']].index[0]-1
        RAW_PROJECTION['FACTOR'] = RAW_PROJECTION.loc[prev_qtr_index,'FACTOR']
        RAW_PROJECTION['PROJECTIONS'] = (RAW_PROJECTION['RAW_SPEND'] * RAW_PROJECTION['FACTOR']) 
        RAW_PROJECTION['QoQ'] = RAW_PROJECTION['REPORTED'].pct_change() 
        RAW_PROJECTION['Est_QoQ'] = RAW_PROJECTION['PROJECTIONS'].pct_change() 
        RAW_PROJECTION['ACCURACY'] = (RAW_PROJECTION['PROJECTIONS'] / RAW_PROJECTION['REPORTED'] - 1) 
        #endregion raw projection tables

        #region Linear regression
        # Produces a new quarterly sum
        linear_regression = SUMMARY.copy()
        if remove_covid: # This remove the covid months in the linear regression projections
            mar_apr = np.logical_and(linear_regression['GP_TRANSACTION_DATE'].astype(str) != '2020-04-01', linear_regression['GP_TRANSACTION_DATE'].astype(str) != '2020-05-01')
            #linear_regression = linear_regression[mar_apr]
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
        linear_regression['Estimate'] = (linear_regression["AVG_FACILITY_SPEND"] * linear_regression["COMPANY_Factor_Est"]) 
        # updating the quarterly spendings.
        linear_regression['GP_TRANSACTION_DATE'] = pd.PeriodIndex(linear_regression['GP_TRANSACTION_DATE'], freq='Q')
        linear_regression = linear_regression.groupby("GP_TRANSACTION_DATE", as_index=False)["Estimate"].sum()

        # This produces the projection tables similar to 12_12
        LR_PROJECTION = PROJECTION.copy()
        is_in_PROJ = LR_PROJECTION['CALENDAR'].isin(linear_regression['GP_TRANSACTION_DATE'].astype(str))
        is_in_LR = linear_regression['GP_TRANSACTION_DATE'].astype(str).isin(LR_PROJECTION['CALENDAR'])
        LR_PROJECTION.loc[is_in_PROJ, 'PROJECTIONS'] = (linear_regression.loc[is_in_LR,'Estimate'] / 1000000).to_numpy() 
        LR_PROJECTION['SCALE_ADJUST'] = (LR_PROJECTION['REPORTED'].rolling(4).sum() / LR_PROJECTION['PROJECTIONS'].rolling(4).sum()) 
        prev_qtr_index = LR_PROJECTION[self.__FY_QTR==LR_PROJECTION['CALENDAR']].index[0]-1
        LR_PROJECTION['SCALE_ADJUST'] = LR_PROJECTION.iloc[prev_qtr_index, 8] # 8 for the scale adjust
        LR_PROJECTION['ADJ_PROJECTIONS'] = (LR_PROJECTION['SCALE_ADJUST'] * LR_PROJECTION['PROJECTIONS']) 
        LR_PROJECTION['ACCURACY'] = (LR_PROJECTION['ADJ_PROJECTIONS'] / LR_PROJECTION['REPORTED'] - 1) 
        #endregion Linear regression
        return RAW_PROJECTION, PROJECTION, LR_PROJECTION

    def facility_check(self):
        import pandas as pd
        FACILILTY = query_snflk(self.__facility_str)
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
        return FACILITY_COMPARE
