import pandas as pd
import numpy as np
import os
from datetime import datetime
from numpy import random
import snowflake.connector
from utilities import util
import statsmodels.api as sm

cnx = snowflake.connector.connect(  
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
cur = cnx.cursor()

bootstraps = 129
random.seed(1)

print(f""" select * from TEMP.MONITOR2.painmod_cuts;""")

# Get all data from Snowflake table
cur.execute(f"""
                select * from TEMP.MONITOR2.painmod_cuts;
            """)

# Get column names
cols = [c[0] for c in cur.description]
# Assign results to var
result = cur.fetchall()

# Create a dataframe object from results, set column names  
cuts = pd.DataFrame(data=result, columns=cols)

# Get all data from Snowflake table
cur.execute(f"""
                select * from TEMP.MONITOR2.painmod_financials;
            """)

# Get column names
cols = [c[0] for c in cur.description]
# Assign results to var
result = cur.fetchall()
# Create another dataframe with the results from the latest query
financials = pd.DataFrame(data=result, columns=cols)

# Rename the column "QUARTER_DATE" to "PROJECTIONS_Q1_START_DATE"
financials = financials.rename(columns={'QUARTER_DATE': 'PROJECTIONS_Q1_START_DATE'})
q_data = financials.merge(cuts[['PROJECTIONS_Q0_START_DATE', 'PROJECTIONS_Q0_END_DATE', 'PROJECTIONS_Q1_START_DATE',
                                'PROJECTIONS_Q1_END_DATE', 'MOA_PROJECTIONS_TABLE', 'PETREL_PROJECTIONS_TABLE']],
                        how='left', left_on='PROJECTIONS_Q1_START_DATE', right_on='PROJECTIONS_Q1_START_DATE')

# Convert the data types of REVENUE, REVENUE_PREV, PROJECTION to floats
q_data[['REVENUE', 'REVENUE_PREV', 'PROJECTION']] = q_data[['REVENUE', 'REVENUE_PREV', 'PROJECTION']].astype(float)

# q_data['PROJECTION_SMOOTH'] = np.nan
# q_data['PROJECTION_HIGH_SMOOTH'] = np.nan
# q_data['PROJECTION_LOW_SMOOTH'] = np.nan
q_data['PROJECTION_STDEV'] = np.nan
q_data['PROJECTION_HIGH'] = np.nan 
q_data['PROJECTION_LOW'] = np.nan

# Columns are initialized here as NULL (0) 
q_data['PROJECTION_FILL_FACTOR'] = np.nan
q_data['PROJECTION_SCALE_FACTOR'] = np.nan
q_data['PROJECTION_ADJUSTED_SPEND'] = np.nan
q_data['PROJECTION_MONTH_1'] = np.nan
q_data['PROJECTION_MONTH_2'] = np.nan
q_data['PROJECTION_MONTH_3'] = np.nan

q_data['PROJECTION_SCALE_FACTOR_MA'] = np.nan
q_data['BS'] = np.nan

# Convert the column BS to an object type
# Objects are used for "Text or mixed numeric and non-numeric values"
# https://pbpython.com/pandas_dtypes.html
q_data['BS'] = q_data['BS'].astype(object)
q_data = q_data.sort_values(['TICKER', 'REVENUE_DIVISION', 'PROJECTIONS_Q1_START_DATE'])

workbook = os.path.join(os.path.normpath(r"C:\Users\redmond.xia\Guidepoint\Data - Data Products\Monitor\Mapping\Segments\Neuromodulation\Pain Modulation"), "painmod_master.xlsx")
wb_company_key = pd.read_excel(workbook, sheet_name='COMPANY_KEY')
wb_company_key = wb_company_key[['MFG_TICKER', 'MFG_SHORT_NAME']].dropna(how='any')

current_date=datetime(datetime.today().year, datetime.today().month, 1)

def bootstrap_projection():
    mfg_shortname = wb_company_key.loc[wb_company_key['MFG_TICKER']==q['TICKER'],'MFG_SHORT_NAME'].values[0]
    cur.execute("""select 
                    case 
                        when month(min(date)) <> 1 then year(min(date))+1
                        else year(min(date))
                    end as min_date
                    from research.kdolgin.painmod_workbook_data_KEEP
                    where mfg_short_name = '{mfg_name}';""".format(mfg_name=mfg_shortname))
    # Get the headers
    cols = [c[0] for c in cur.description]
    # Get the results
    result = cur.fetchall()
    min_date = pd.DataFrame(data=result, columns=cols)['MIN_DATE'].values[0]
    #q_month_dist = prev_dist[prev_dist['MFG_SHORT_NAME']==mfg_shortname]
    cur.execute("""select date, mfg_short_name, sum(total_spend_scaled)/1000000 as TS, sum(total_spend_raw)/1000000 as TR
                from research.kdolgin.painmod_workbook_data_KEEP
                where year >= {mindate} and mfg_short_name = '{mfg_name}'
                group by 1,2
                order by 2,1;""".format(mindate=min_date, mfg_name=mfg_shortname))

    # Get the headers
    cols = [c[0] for c in cur.description]
    # Get the results
    result = cur.fetchall()
    # Create a dataframe "panel" using the results and headers
    prev_dist = pd.DataFrame(data=result, columns=cols)

    #tickers = prev_dist['MFG_SHORT_NAME'].unique()
    prev_dist['TS_ROLL3_SUM'] = prev_dist['TS'].rolling(3).sum().values
    prev_dist['TR_ROLL3_SUM'] = prev_dist['TR'].rolling(3).sum().values
    prev_dist.loc[prev_dist.index % 3 != 2,'TS_ROLL3_SUM'] = np.nan
    prev_dist.loc[prev_dist.index % 3 != 2,'TR_ROLL3_SUM'] = np.nan
    prev_dist[['TS_ROLL3_SUM','TR_ROLL3_SUM']] = prev_dist[['TS_ROLL3_SUM','TR_ROLL3_SUM']].bfill()
    prev_dist[['TR','TS']] = prev_dist[['TR','TS']].astype(float)
    prev_dist['month_dist_TR'] = prev_dist['TR'] / prev_dist['TR_ROLL3_SUM']
    prev_dist['month_dist_TS'] = prev_dist['TS'] / prev_dist['TS_ROLL3_SUM']
    prev_dist['TR_MoM_Growth'] = prev_dist['TR'].pct_change()     
    upper_quantile = prev_dist['TR_MoM_Growth'].quantile(.95, interpolation='linear')
    lower_quantile = prev_dist['TR_MoM_Growth'].quantile(.05, interpolation='linear')
    prev_dist.loc[:,'TR_MoM_Growth']=prev_dist['TR_MoM_Growth'].clip(lower=lower_quantile, upper=upper_quantile)
    #prev_dist.loc[::3,'TR_MoM_Growth'] = prev_dist.loc[::3,'TR_MoM_Growth'] - (prev_dist.loc[::3,'TR_MoM_Growth'].abs().mean()/4)
    # prev_dist[['month_dist_TR','TR_MoM_Growth']].corr()
    y = prev_dist['month_dist_TR'].dropna()[1:]
    X = prev_dist['TR_MoM_Growth'][1:(len(y)+1)]
    X = sm.add_constant(X)
    growth_month_dist_lm = sm.OLS(y,X).fit()
    # np.std(y - growth_month_dist_lm.fittedvalues) * 2
    #growth_month_dist_lm.summary()

    # Run this query --'{q['PETREL_PROJECTIONS_TABLE']}'
    cur.execute(f"""
                    with x as
                        (select 
                            date, facility_id, sum(total_spend) spend
                        from TEMP.MONITOR2.painmod_projections_panel_final
                        where source_table in 
                            ('{q['MOA_PROJECTIONS_TABLE']}', '{q['PETREL_PROJECTIONS_TABLE']}')
                        and (
                                (date >= '{q['PROJECTIONS_Q0_START_DATE']}' 
                                and date <= '{q['PROJECTIONS_Q0_END_DATE']}') 
                            or 
                                (date >= '{q['PROJECTIONS_Q1_START_DATE']}' 
                                and date <= '{q['PROJECTIONS_Q1_END_DATE']}')
                            )
                        and trim(upper(ticker_adj)) = trim(upper('{q['TICKER']}'))
                        and trim(upper(category_1)) = trim(upper('{q['REVENUE_DIVISION']}'))
                        group by date, facility_id),
                    y as
                        (select date, facility_id, spend, date_from_parts(year(date), 3*quarter(date) -2, 1) q from x),
                    z as
                        (select date, facility_id, spend, dense_rank() over (order by q) - 1 quarter from y)  
                    select date, quarter,
                        case
                            when mod(month(date), 3) = 1 then 1
                            when mod(month(date), 3) = 2 then 2
                            else 3 
                        end as quarter_month, 
                        facility_id, spend
                    from z
                """)
                
    # Get the headers
    cols = [c[0] for c in cur.description]
    # Get the results
    result = cur.fetchall()
    # Create a dataframe "panel" using the results and headers
    panel = pd.DataFrame(data=result, columns=cols)
    
    # Then, execute this query --'{q['PETREL_PROJECTIONS_TABLE']}'
    cur.execute(f"""
                    with x as
                        (select distinct 
                            date, 
                            date_from_parts(year(date), 3*quarter(date) -2, 1) q,
                            facility_id 
                        from
                        TEMP.MONITOR2.painmod_projections_panel_membership 
                        where source_table in 
                            ('{q['MOA_PROJECTIONS_TABLE']}', '{q['PETREL_PROJECTIONS_TABLE']}')
                        and (
                                (date >= '{q['PROJECTIONS_Q0_START_DATE']}' 
                                and date <= '{q['PROJECTIONS_Q0_END_DATE']}')
                            or
                                (date >= '{q['PROJECTIONS_Q1_START_DATE']}' 
                                and date <= '{q['PROJECTIONS_Q1_END_DATE']}')
                            )
                        ),
                    y as
                        (select date, facility_id, dense_rank() over (order by q) - 1 quarter from x)
                    select date, quarter, 
                    case
                        when mod(month(date), 3) = 1 then 1
                        when mod(month(date), 3) = 2 then 2
                        else 3 
                    end as quarter_month,
                    facility_id
                    from y
                """)
    
    # Get the headers
    cols = [c[0] for c in cur.description]
    # Get the results
    result = cur.fetchall()
    # Create another dataframe called `membership` with the results and headers
    membership = pd.DataFrame(data=result, columns=cols)
    membership = membership[membership['FACILITY_ID'].isin(list(panel['FACILITY_ID'].unique()))]    
    panel = membership.merge(panel, how='left', left_on=['DATE', 'QUARTER', 'QUARTER_MONTH', 'FACILITY_ID'], 
                            right_on=['DATE', 'QUARTER', 'QUARTER_MONTH', 'FACILITY_ID'])      
    panel = panel.fillna(0)
    # Set the data types of columns QUARTER and QUARTER_MONTH to strings 
    panel[['QUARTER', 'QUARTER_MONTH']] = panel[['QUARTER', 'QUARTER_MONTH']].astype(str)

    
    # if len(panel) == 0:
    #     continue
    data = panel.pivot_table(index=['QUARTER', 'QUARTER_MONTH'], columns='FACILITY_ID', values='SPEND', aggfunc=np.sum)
    
    if not ('0', '1') in data.index:
        data.loc[('0', '1'), :] = np.nan
    if not ('0', '2') in data.index:
        data.loc[('0', '2'), :] = np.nan
    if not ('0', '3') in data.index:
        data.loc[('0', '3'), :] = np.nan
    if not ('1', '1') in data.index:
        data.loc[('1', '1'), :] = np.nan
    if not ('1', '2') in data.index:
        data.loc[('1', '2'), :] = np.nan
    if not ('1', '3') in data.index:
        data.loc[('1', '3'), :] = np.nan
    data = data.T
    
    # Candidate to dig into
    weights = (~data.loc[:, '1'].isnull()).sum(axis=1).astype(float)
    weights = weights/sum(weights)
    # Inspect this, compare to the full DF 'data'
    choices = np.linspace(0, len(data)-1, len(data)).astype(int)

    proj = []
    # Runs through 10 times; up to to 10 values
    fill_factor = []
    adjusted_spend = []
    month_dist_1 = []
    month_dist_2 = []
    month_dist_3 = []

    print((data.loc[:, '1'].isnull().sum(axis=0).values).astype(float)) # bb
    print(len(data)) # cc boot strap the current growth
    # TODO can
    for b in range(bootstraps):
        # Candidate to dig into
        bs_ix = random.choice(choices, size=int(0.7*len(choices)), replace=True, p=weights)
        data_bs = data.iloc[bs_ix, :]
        month_dist = (data_bs.loc[:, '0'].sum(axis=0).values).astype(float)

        # If the sum if 0.... move on to the next item in bootstrap (e.g., 1 of 10, 2 of 10 etc.)
        # if sum(month_dist) == 0:
        #     continue
        
        q1_spend_raw = float(np.nansum(data_bs.loc[:, '1'].values))
        
        # If the result is greater than 0....
        if (q1_spend_raw > 0):
            '''
            Set the var 'aa' to q1_spend_raw, but as a float 
            - NOTE: This is redundant and can probably be removed
            '''
            aa = float(np.nansum(data_bs.loc[:, '1'].values))
            bb = (data_bs.loc[:, '1'].isnull().sum(axis=0).values).astype(float) 
            cc = len(data_bs)
            ee = data_bs.loc[:,'1'].sum().astype(float) # current spendings
            ff = (ee / (1-(bb/cc))).replace(0, np.nan).values # scaled spending #
            gg = data_bs.sum().astype(float)
            gg['1'] = ff
            hh = gg.pct_change().replace(0, np.nan)
            pred_X = sm.add_constant(hh['1'].values)
            month_dist = np.nan_to_num(growth_month_dist_lm.predict(pred_X), nan=0) 
            dd = month_dist
            # TODO imput mean month distribution if it doesn't exists
            assert (len(dd) == 3), "Monthly distribution is not 3 months long"
            # assumes first month of aa to be non-nulls. # possible improvement -- longer lookback
            # Set var 'q1_spend_adj' to output of the formula. Denominator is capture rate
            if bb[1] < (.6*cc) and bb[2] < (.6*cc): # when the other two months are non-nulls
                ##assert (sum(dd) == 1), "TODO different cut dates, sum of distribution is not 1, all months"
                dd = (gg['1'] / gg['1'].sum()).values
                q1_spend_adj = aa * (1 + sum((bb / cc) * dd)) # original adj formula. Good for small amt of nulls & full data
                
            elif bb[1] >= (.6*cc) and bb[2] >= (.6*cc): # when the second and 3rd month is all nulls
                #assert (sum(dd) == 1), "TODO different cut dates, sum of distribution is not 1, first month"
                adj_factor = aa * (1 + bb[0]/cc) # adjust the first month of nulls
                q1_spend_adj = adj_factor / dd[0] # scale to full quarter
                #TODO Need to figure out some projections of other two months
            elif bb[1] < (.6*cc) and bb[2] >= (.6*cc): # second month is not null but last month is
                dd[2]  = 1.0 - dd[0] - dd[1]
                adj_factor = aa * (1 + sum((bb[0:2] / cc) * dd[0:2]/sum(dd[0:2]))) # adj 1st 2mo nulls 
                q1_spend_adj = adj_factor /  (dd[0] + dd[1]) # scale to full quarter

            elif bb[1] >= (.6*cc) and bb[2] < (.6*cc): # when 2nd month is null but last month is not null, not usual
                #assert (sum(dd) == 1), "TODO different cut dates, sum of distribution is not 1, second month"
                adj_factor = aa * (1 + sum(np.array([bb[0]/cc,bb[2]/cc]) *  
                                            np.array([dd[0]/sum([dd[0],dd[2]]),dd[2]/sum([dd[0],dd[2]])]))) # only 3rd mo are nulls
                q1_spend_adj = adj_factor / (dd[0] + dd[2]) 
                

            # Add the value of 'q1_spend_adj' to the list 'adjusted_spend'
            '''
            Inputs:
                q1_spend_adj
            '''
            adjusted_spend.append(q1_spend_adj)
            month_dist_1.append(dd[0])
            month_dist_2.append(dd[1])
            month_dist_3.append(dd[2])

            '''
            If the column 'REVENUE_PREV' from the dataframe 'q' is NOT NULL....

            Remember: 'q' comes from:
            q = q_data.loc[ix]
            '''
            if not np.isnan(q['REVENUE_PREV']):
                
                '''
                Calculate a growth rate and add results to the lists that were initialized above:
                '''
                # Adjusted spend / sum of: all rows in col '0' of data_bs DF ==> convert to float
                growth = q1_spend_adj / float(np.nansum(data_bs.loc[:, '0'].values))
                # Add value of: col REVENUE_PREV in dataframe 'q' * growth to the list 'proj' 
                proj.append(float(q['REVENUE_PREV']) * (growth))
                # Add output of equation to the list 'fill_factor'
                
                '''
                Inputs:
                    q1_spend_adj
                    q1_spend_raw
                '''
                fill_factor.append(q1_spend_adj/q1_spend_raw)
    return fill_factor, adjusted_spend, proj, month_dist_1, month_dist_2, month_dist_3
    


for ix in q_data.index:
    #ix =139 #bioness
    q = q_data.loc[ix]
    print(f"   ...Working on {q['TICKER']}:{q['REVENUE_DIVISION']} {q['PROJECTIONS_Q1_START_DATE']}")
    
    # To look at the most recent quarter projection 
    q_proj_date=q['PROJECTIONS_Q1_START_DATE']
    # If the column PROJECTION is null for that row....
    if np.isnan(q['PROJECTION']) and ~np.isnan(q['REVENUE_PREV']):
        fill_factor, adjusted_spend, proj, month_dist_1, month_dist_2, month_dist_3 = bootstrap_projection()
        q_data.loc[ix, 'PROJECTION_FILL_FACTOR'] = np.nanmedian(fill_factor)
        q_data.loc[ix, 'PROJECTION_ADJUSTED_SPEND'] = np.nanmedian(adjusted_spend)
        q_data.loc[ix, 'PROJECTION_ADJUSTED_SPEND_STDEV'] = np.nanstd(adjusted_spend)

        if not np.isnan(q['REVENUE_PREV']) and q['REVENUE_PREV'] > 0:
            q_data.at[ix, 'BS'] = sorted(proj)
            q_data.loc[ix, 'PROJECTION'] = np.nanmedian(proj)
            q_data.loc[ix, 'PROJECTION_MONTH_1'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_1)
            q_data.loc[ix, 'PROJECTION_MONTH_2'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_2)
            q_data.loc[ix, 'PROJECTION_MONTH_3'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_3)
            q_data.loc[ix, 'PROJECTION_STDEV'] = np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_HIGH'] = np.nanmedian(proj) + 3 * np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_LOW'] = np.nanmedian(proj) - 3 * np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_SCALE_FACTOR'] = (np.nanmedian(proj) + 3 * np.nanstd(proj))/np.nanmedian(adjusted_spend)

    elif (not np.isnan(q['PROJECTION'])) and ((current_date==q_proj_date) or ((current_date-pd.DateOffset(months=1))==q_proj_date) or ((current_date-pd.DateOffset(months=1))==q_proj_date) or ((current_date-pd.DateOffset(months=3))==q_proj_date) or ((current_date-pd.DateOffset(months=4))==q_proj_date) or ((current_date-pd.DateOffset(months=5))==q_proj_date)): 
        fill_factor, adjusted_spend, proj, month_dist_1, month_dist_2, month_dist_3 = bootstrap_projection()
        scaling_factor=(q_data.loc[ix, 'PROJECTION'] / np.nanmedian(proj))
        proj=[i*scaling_factor for i in proj]
        fill_factor=[i*scaling_factor for i in fill_factor]
        adjusted_spend=[i*scaling_factor for i in adjusted_spend]
        q_data.loc[ix, 'PROJECTION_FILL_FACTOR'] = np.nanmedian(fill_factor)
        q_data.loc[ix, 'PROJECTION_ADJUSTED_SPEND'] = np.nanmedian(adjusted_spend)
        q_data.loc[ix, 'PROJECTION_ADJUSTED_SPEND_STDEV'] = np.nanstd(adjusted_spend)
        if not np.isnan(q['REVENUE_PREV']) and q['REVENUE_PREV'] > 0:
            q_data.at[ix, 'BS'] = sorted(proj)
            q_data.loc[ix, 'PROJECTION_MONTH_1'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_1)
            q_data.loc[ix, 'PROJECTION_MONTH_2'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_2)
            q_data.loc[ix, 'PROJECTION_MONTH_3'] = q_data.loc[ix, 'PROJECTION'] * np.nanmean(month_dist_3)
            q_data.loc[ix, 'PROJECTION_STDEV'] = np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_HIGH'] = np.nanmedian(proj) + 3 * np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_LOW'] = np.nanmedian(proj) - 3 * np.nanstd(proj)
            q_data.loc[ix, 'PROJECTION_SCALE_FACTOR'] = (np.nanmedian(proj) + 3 * np.nanstd(proj))/np.nanmedian(adjusted_spend)


        
'''
Steps:
1) Gets all unique values in the column 'PROJECTIONS_Q1_START_DATE'
2) Loop through each value

NOTE: This concludes the loop started way way way above:
    for ix in q_data.index:
'''
for d in q_data['PROJECTIONS_Q1_START_DATE'].unique():
    
    # Create a new dataframe 'q' that contains all rows in DF 'q_data' where PROJECTIONS_Q1_START_DATE is equal to 0
    q = q_data[q_data['PROJECTIONS_Q1_START_DATE'] == d]
    '''
    Create a new dataframe 'sf' where:
    1) Gets the values in column 'PROJECTION_SCALE_FACTOR'
    2) Filter to all rows in column 'PROJECTION_SCALE_FACTOR' that are NOT NULL
    '''
    sf = q['PROJECTION_SCALE_FACTOR'][~q['PROJECTION_SCALE_FACTOR'].isnull()]
    if len(sf) == 0:
        continue

    # Reassign value of 'sf' to the median of current values, ignoring nulls 
    sf = np.nanmedian(sf.values)
    
    '''
    Sets 'sf' to the values in column 'PROJECTION_SCALE_FACTOR' in the dataframe 'q_data' that meet the following conditions:
    1) Column 'PROJECTIONS_Q1_START_DATE' equals 'd'
    2) Column 'PROJECTIONS_SCALE_FACTOR' IS NULL
    '''
    q_data.loc[(q_data['PROJECTIONS_Q1_START_DATE'] == d) & (q_data['PROJECTION_SCALE_FACTOR'].isnull()), 'PROJECTION_SCALE_FACTOR'] = sf

def ff1(x):
    '''
    If the column 'PROJECTION' is null:
        - Set y to the output of: projected scale factor * projected adjusted spend
    Else:
        - Set y to 'PROJECTION'
    '''
    if np.isnan(x['PROJECTION']): 
        y = x['PROJECTION_SCALE_FACTOR'] * x['PROJECTION_ADJUSTED_SPEND']
    else:
        y = x['PROJECTION']
    return y


def ff2(x):
    '''
    If the column 'PROJECTION' is null:
        - Set y to the output of SCALE_FACTOR * (adj. spend + 3 * spend standard deviation)
    Else:
        - Set y to the PROJECTION_HIGH
    '''
    if np.isnan(x['PROJECTION']): 
        y = x['PROJECTION_SCALE_FACTOR'] * (x['PROJECTION_ADJUSTED_SPEND'] + 3 * x['PROJECTION_ADJUSTED_SPEND_STDEV'])
    else:
        y = x['PROJECTION_HIGH']
    return y

def ff3(x):
    '''
    If the column 'PROJECTION' is null:
        - Set y to the output of SCALE_FACTOR * (adj. spend - 3 * spend standard deviation)
    Else:
        - Set y to the PROJECTION_LOW
    '''
    if np.isnan(x['PROJECTION']): 
        y = x['PROJECTION_SCALE_FACTOR'] * (x['PROJECTION_ADJUSTED_SPEND'] - 3 * x['PROJECTION_ADJUSTED_SPEND_STDEV'])
    else:
        y = x['PROJECTION_LOW']
    return y


'''
Apply each of the above functions to every row in the specified column
- 'lambda' is an "anonymous" function - here it lets us run the function for each row, "x"

Meaning:
- Apply this function (e.g., ff2) to every row ("x") in the column (axis=1)

What it does:
- Sets values for high/low/expected projections for each row in dataframe
'''
q_data['PROJECTION_HIGH'] = q_data.apply(lambda x: ff2(x), axis=1)
q_data['PROJECTION_LOW'] = q_data.apply(lambda x: ff3(x), axis=1)
q_data['PROJECTION'] = q_data.apply(lambda x: ff1(x), axis=1)

# For each unique value in the 'TICKER' column of q_data (i.e. each ticker):
for t in q_data['TICKER'].unique():
    # For each revenue division....
    for rd in q_data['REVENUE_DIVISION'].unique():
        '''
        Set 'q' to a subset of dataframe 'q_data' whose columns meet the following conditions:
        1) Column 'TICKER' = t
        2) Column 'REVENUE_DIVISION' = rd 

        ==> i.e., get the data pertaining only to that ticker + revenue division 
        '''
        q = q_data[(q_data['TICKER'] == t) & (q_data['REVENUE_DIVISION'] == rd)]
        # If there are no results... skip!
        if len(q) == 0:
            continue
        
        '''
        Steps: 
        1) Produces a rolling window of the column 'PROJECTION_SCALE_FACTOR' in dataframe 'q'
        2) Calculates the mean of the rolling window, assigns to 'sf_rolling'

        Arguments:
        - arg 1 (window)        ==> Size of the moving window. This is the number of observations used for calculating the statistic.
        - arg 2 (min_periods)   ==> Minimum number of observations in window required to have a value (otherwise result is NA).
        
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
        ''' 
        sf_rolling = q['PROJECTION_SCALE_FACTOR'].rolling(4, min_periods=1).mean()
        
        '''
        Fill missing values of the dataframe
        'ffill == forward fill' ==> propagates last valid observation forward

        https://www.geeksforgeeks.org/python-pandas-dataframe-ffill/
        '''
        sf_rolling = sf_rolling.ffill()
        
        '''
        Sets 'sf_rolling' to the values in column 'PROJECTION_SCALE_FACTOR_MA' in the dataframe 'q_data' that meet the following conditions:
        1) Ticker is the ticker for the iteration of the current loop
        2) Revenue Division is the rd for the iteration of the current loop

        i.e. ==> Sets value for a projection scale moving average for that ticker/revenue division  
        '''
        q_data.loc[(q_data['TICKER'] == t) & (q_data['REVENUE_DIVISION'] == rd), 'PROJECTION_SCALE_FACTOR_MA'] = sf_rolling

# Create a column 'PROJECTION_SMOOTH' and set as the output of the formula
q_data['PROJECTION_SMOOTH'] = q_data['PROJECTION_ADJUSTED_SPEND'] * q_data['PROJECTION_SCALE_FACTOR_MA']

# Create a column 'PROJECTION_SMOOTH_HIGH' and set as the output of the formula - 3 standard deviations above the moving average
q_data['PROJECTION_SMOOTH_HIGH'] = (q_data['PROJECTION_ADJUSTED_SPEND'] 
                                    + 3 * q_data['PROJECTION_ADJUSTED_SPEND_STDEV']) * q_data['PROJECTION_SCALE_FACTOR_MA']

# Create a column 'PROJECTION_SMOOTH_LOW' and set as the output of the formula - 3 standard deviations below the moving average
q_data['PROJECTION_SMOOTH_LOW'] = (q_data['PROJECTION_ADJUSTED_SPEND'] 
                                    - 3 * q_data['PROJECTION_ADJUSTED_SPEND_STDEV']) * q_data['PROJECTION_SCALE_FACTOR_MA']

# Filter the dataframe q_data to the specified columns
q_data = q_data[['TICKER', 'REVENUE_DIVISION', 'PROJECTIONS_Q0_START_DATE',
                'PROJECTIONS_Q0_END_DATE', 'PROJECTIONS_Q1_START_DATE', 'PROJECTIONS_Q1_END_DATE',
                'REVENUE', 'REVENUE_PREV', 'PROJECTION', 'PROJECTION_HIGH', 'PROJECTION_LOW', 'PROJECTION_STDEV','PROJECTION_MONTH_1',
                'PROJECTION_MONTH_2','PROJECTION_MONTH_3', 'PROJECTION_FILL_FACTOR', 'PROJECTION_SCALE_FACTOR', 'PROJECTION_ADJUSTED_SPEND', 
                'PROJECTION_ADJUSTED_SPEND_STDEV', 'PROJECTION_SMOOTH', 'PROJECTION_SMOOTH_HIGH', 
                'PROJECTION_SMOOTH_LOW', 'PROJECTION_SCALE_FACTOR_MA', 'MOA_PROJECTIONS_TABLE', 'PETREL_PROJECTIONS_TABLE']]