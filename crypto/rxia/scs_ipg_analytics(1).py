import pandas as pd
from utilities import util
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import seaborn as sns

painmod_ipg_str="""select   date, FACILITY_ID, mfg_short_name, category_3,

                    CASE WHEN CATEGORY_3 = 'LEAD' and category_4 ilike '%surgical%' and mfg_short_name = 'BOSTON SCIENTIFIC' then 'PADDLE' 
                    when CATEGORY_3 = 'LEAD' and category_4 ilike '%trial%'  and mfg_short_name = 'BOSTON SCIENTIFIC' then 'TRIAL'
                    when CATEGORY_3 = 'LEAD' and (category_4 not ilike '%surgical%' and category_4 not ilike '%TRIAL%') and mfg_short_name = 'BOSTON SCIENTIFIC' then 'PERC' 
                    WHEN CATEGORY_3 = 'LEAD' and category_4 ilike '%surgical%' and mfg_short_name = 'MEDTRONIC' then 'PADDLE' 
                    when CATEGORY_3 = 'LEAD' and category_4 ilike '%trial%' and mfg_short_name = 'MEDTRONIC' then 'TRIAL'
                    when CATEGORY_3 = 'LEAD' and (category_4 not ilike '%surgical%' and category_4 not ilike '%TRIAL%') and mfg_short_name = 'MEDTRONIC' then 'PERC'
                    
                    WHEN CATEGORY_3 = 'LEAD' and category_4 IN ('EXCLAIM LEAD', 'LAMITRODE',  'PENTA LEAD', 'TRIPOLE 16C LEAD', 'S-4 LEAD') and mfg_short_name ILIKE '%ABBOTT%' then 'PADDLE' 
                    when CATEGORY_3 = 'LEAD' and category_4 ilike '%trial%' and mfg_short_name ILIKE '%ABBOTT%' then 'TRIAL'
                    when CATEGORY_3 = 'LEAD' and (category_4 IN ('OCTRODE', 'QUATTRODE')) and mfg_short_name ILIKE '%ABBOTT%' then 'PERC'

                    WHEN CATEGORY_3 = 'LEAD' and category_4 ilike '%surgical%' and mfg_short_name ILIKE '%NEVRO%' then 'PADDLE' 
                    when CATEGORY_3 = 'LEAD' and category_4 ilike '%trial%' and mfg_short_name ILIKE '%NEVRO%' then 'TRIAL'
                    when CATEGORY_3 = 'LEAD' and (category_4 not ilike '%surgical%' and category_4 not ilike '%TRIAL%') and mfg_short_name ILIKE '%NEVRO%' then 'PERC'

                    else 'N/A' end LEAD_TYPE,   

                    CASE WHEN category_3 = 'INS' and AVG_PRICE <2000 THEN 'FLAG' else null end flag,
                    sum(volume_raw) as VR, sum(total_spend_raw) as TOTAL_SPEND, sum(AVG_PRICE * VOLUME_RAW) / sum(volume_raw) as AVG_PRC

                    from RESEARCH.KDOLGIN.PAINMOD_FINAL_TABLE_FEB_2021_KEEP
                    where (date between '2010-01-01' and '2021-01-01') and category_2 ilike '%spinal%' 
                    AND CATEGORY_3  IN ('INS', 'LEAD', 'ADAPTER')
                    and lead_type not in ('TRIAL')
                    and flag is null

                    group by 1,2,3,4,5,6
                    order by 1,3,4,5;
                    """

painmod_ipg = util.connect_snwflk(painmod_ipg_str)
painmod_ipg['AVG_PRC'] = painmod_ipg['AVG_PRC'].astype(float) # this should be weighted average
big_4 = ['ABBOTT LABORATORIES', 'BOSTON SCIENTIFIC', 'MEDTRONIC','NEVRO']

#region category 3 volume
category_3_VR = painmod_ipg.groupby(['DATE','MFG_SHORT_NAME','CATEGORY_3','LEAD_TYPE'], as_index=False)['VR'].sum()

IS_LEAD_PERC = np.logical_and(category_3_VR['CATEGORY_3']=='LEAD',category_3_VR['LEAD_TYPE']=='PERC')
category_3_VR.loc[IS_LEAD_PERC,'VR'] = category_3_VR.loc[IS_LEAD_PERC,'VR']/2

category_3_VR = (category_3_VR.groupby(['DATE','MFG_SHORT_NAME','CATEGORY_3'], as_index=False)['VR'].sum().round(0))
category_3_VR= category_3_VR[category_3_VR['MFG_SHORT_NAME'].isin(big_4)]# big 4
fig_dims=(14,12)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(data=category_3_VR,x='DATE',y='VR',style='CATEGORY_3',hue='MFG_SHORT_NAME', ax=ax, palette='dark')

# category_3_VR = category_3_VR.pivot(index=['DATE','MFG_SHORT_NAME'], columns='CATEGORY_3' ,values='VR').fillna(0)
# category_3_VR.columns = ['ADAPTER_VR','INS_VR','LEAD_VR']
#category_3_VR['NET_LEAD_INS'] = category_3_VR['LEAD'] - category_3_VR['INS']
#category_3_VR['PCT_SURG'] = (category_3_VR['ADAPTER'] / category_3_VR['NET_LEAD_INS']).round(4)
# category_3_VR.plot(y='PCT_SURG', figsize=(12,6), style='.--')
# category_3_VR.plot(x='DATE',figsize=(12,6), style='.--')
# category_3_VR['PCT_SURG'].hist(bins=15)
# category_3_VR['PCT_SURG'].describe()

df_LEAD = category_3_VR[category_3_VR['CATEGORY_3']=='LEAD']
df_INS = category_3_VR[category_3_VR['CATEGORY_3']=='INS']
df_NET_INS_LEAD = df_INS.merge(df_LEAD, how='left', on=['DATE','MFG_SHORT_NAME']).fillna(0)
df_NET_INS_LEAD['NET_INS_LEAD'] = df_NET_INS_LEAD['VR_x'] - df_NET_INS_LEAD['VR_y']
df_NET_INS_LEAD=df_NET_INS_LEAD.rename(columns={'VR_x':'VR_INS','VR_y':'VR_LEAD','CATEGORY_3_x':'CATEGORY_3_INS','CATEGORY_3_y':'CATEGORY_3_LEAD'})
fig_dims=(14,12)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(data=df_NET_INS_LEAD, x='DATE', y='NET_INS_LEAD', hue='MFG_SHORT_NAME')
#endregion category 3 volume

#region category 3 spend 
category_spend = painmod_ipg.groupby(['DATE','MFG_SHORT_NAME','CATEGORY_3'], as_index=False)['TOTAL_SPEND'].sum()
# only abbot bsx, medtronic, nevro
category_spend=category_spend[category_spend['MFG_SHORT_NAME'].isin(big_4)]
fig_dims=(14,12)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(data=category_spend,x='DATE',y='TOTAL_SPEND',style='CATEGORY_3',hue='MFG_SHORT_NAME', ax=ax, palette='dark')

# category_spend = category_spend.pivot(index='DATE', columns='CATEGORY_3', values='TOTAL_SPEND').astype(float)
# category_spend.columns = ['ADAPTER_SPD','INS_SPD','LEAD_SPD']
# category_spend.plot()
# category_spend['NET_LEAD_INS_SPD'] = category_spend['LEAD_SPD'] - category_spend['INS_SPD']
# category_spend['NET_LEAD_INS_SPD'].plot()

category_spend_trend = (category_spend / category_spend.iloc[0,:]).round(2)
category_spend_trend.plot()
#endregion category 3 spend

#region category 3 price

# by lead type
category_VR_SPEND = painmod_ipg.groupby(['DATE','MFG_SHORT_NAME','CATEGORY_3','LEAD_TYPE'], as_index=False).agg(volume=('VR',sum),spend=('TOTAL_SPEND', sum))
category_VR_SPEND['AVG_PRC'] = (category_VR_SPEND['spend'] / category_VR_SPEND['volume']).astype(float).round(2)
category_VR_SPEND.loc[category_VR_SPEND['LEAD_TYPE']=='N/A','LEAD_TYPE'] = np.nan
category_VR_SPEND['LEAD_TYPE'] = category_VR_SPEND['LEAD_TYPE'].fillna(category_VR_SPEND['CATEGORY_3'])
fig_dims=(14,12)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(data=category_VR_SPEND,x='DATE',y='AVG_PRC',style='LEAD_TYPE',hue='MFG_SHORT_NAME', ax=ax, palette='dark')

category_VR_SPEND = painmod_ipg.groupby(['DATE','MFG_SHORT_NAME','CATEGORY_3'], as_index=False).agg(volume=('VR',sum),spend=('TOTAL_SPEND', sum))
category_VR_SPEND['AVG_PRC'] = (category_VR_SPEND['spend'] / category_VR_SPEND['volume']).astype(float).round(2)
category_VR_SPEND = category_VR_SPEND[category_VR_SPEND['MFG_SHORT_NAME'].isin(big_4)]
fig_dims=(14,12)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(data=category_VR_SPEND,x='DATE',y='AVG_PRC',style='CATEGORY_3',hue='MFG_SHORT_NAME', ax=ax, palette='dark')

# category_avg_prc = category_VR_SPEND.pivot(index='DATE', columns='CATEGORY_3', values='AVG_PRC')
# category_avg_prc.columns = ['ADAPTER_PRC','INS_PRC','LEAD_PRC']
# category_avg_prc.plot()
# category_avg_prc.corr()
# category_avg_prc_trend = (category_avg_prc / category_avg_prc.iloc[0,:]).round(4)
# category_avg_prc_trend.plot(figsize=(12,6))
# category_avg_prc_trend
#endregion category 3 price



# mlr with adapter and ins prices, total spend linear regression
# linear regression on the bottoms up to get aggrgate spending. 
final_df = pd.concat([category_3_VR,category_avg_prc,category_spend], axis=1)
final_df['TOTAL_SPEND'] = final_df['ADAPTER_SPD'] + final_df['INS_SPD'] + final_df['LEAD_SPD']
final_df['NET_INS_LEAD_SPD'] = final_df['INS_SPD']  - final_df['LEAD_SPD']
final_df['PCT_ADPT_NETINSLEAD'] = final_df['ADAPTER_SPD'] / final_df['NET_INS_LEAD_SPD']
final_df['PCT_ADPT_NETINSLEAD'].plot(figsize=(12,6))
final_df['PCT_ADPT_TOTSPD'] = final_df['ADAPTER_SPD'] / final_df['TOTAL_SPEND']
(final_df['PCT_ADPT_TOTSPD'] / final_df['PCT_ADPT_TOTSPD'][0]).plot()
pct_price = pd.concat([category_3_VR['PCT_SURG'],price],axis=1)
pct_price_trend = pct_price / pct_price.iloc[0,:]
pct_price_trend.plot()


#region overall plot
painmod_ipg_vr_spend = painmod_ipg.groupby('DATE').agg(volume=('VR', sum), spend=('TOTAL_SPEND', sum))
painmod_ipg_vr_spend = painmod_ipg_vr_spend.astype(float)
painmod_ipg_vr_spend['avg_prc'] = (painmod_ipg_vr_spend['spend'] / painmod_ipg_vr_spend['volume']).round(2)
painmod_ipg_vr_spend = painmod_ipg_vr_spend.round(2)
painmod_ipg_vr_spend['avg_prc'].plot()
painmod_ipg_vr_spend['volume'].plot()
painmod_ipg_vr_spend['spend'].plot()
#endregion overall plot

#region overall trend plots
painmod_ipg_trend = painmod_ipg[["DATE","VR","TOTAL_SPEND"]]
painmod_ipg_trend = painmod_ipg_trend.groupby('DATE').agg(volume=('VR', sum), spend=('TOTAL_SPEND', sum))
painmod_ipg_trend = painmod_ipg_trend.astype(np.float64)
painmod_ipg_trend['avg_prc'] = (painmod_ipg_trend['spend'] / painmod_ipg_trend['volume']).round(2)
painmod_ipg_trend = painmod_ipg_trend / painmod_ipg_trend.iloc[0,:]
painmod_ipg_trend.plot(grid=True, figsize=(12,6), style='.-')
#endregion overall trend plots

#region overall volume ma
volume = painmod_ipg.groupby("DATE")["VR"].sum()
volume.plot() # original plotting
volume_ma = volume.rolling(2).mean().round(0)
volume_ma.plot(figsize=(10,6), style='.-')
#endregion painmod_ipg overall volume

#region total spend ma
spend = painmod_ipg.groupby("DATE")["TOTAL_SPEND"].sum().astype(int)
spend_ma = spend.rolling(2).mean().round(2)
spend_ma.plot(figsize=(10,6), style='.-')
#endregion painmod_ipg total spend

#region price ma
price = painmod_ipg.groupby('DATE').agg(volume=('VR', sum), spend=('TOTAL_SPEND', sum)).astype(float)
price['price'] = (price['spend'] / price['volume']).round(2)
price = price['price']
price_ma = price.rolling(2).mean().round(2)
price_ma.plot()
#endregion painmod_ipg price


# TODO knn classification, based off price and volume