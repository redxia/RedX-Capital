import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utilities import util
import statsmodels.api as sm

min_date = util.connect_snwflk("""select 
                        case 
                            when month(min(date)) != 1 then year(min(date))+1
                            else year(min(date))
                        end as min_date
                        from temp.monitor2.brainmodulation_workbook_data;""")['MIN_DATE'].values[0]


brain_mod_query="""select date, mfg_short_name, sum(total_spend_scaled)/1000000 as TS, sum(total_spend_raw)/1000000 as TR, TR / TS as capture, count(distinct facility_id)
                   from temp.monitor2.brainmodulation_workbook_data
                   where year >= {mindate}
                   group by 1,2
                   order by 2,1;""".format(mindate=min_date)

brain_mod = util.connect_snwflk(brain_mod_query)

brain_mod['TS_ROLL3_SUM'] = brain_mod.groupby('MFG_SHORT_NAME')['TS'].rolling(3).sum().values
brain_mod['TR_ROLL3_SUM'] = brain_mod.groupby('MFG_SHORT_NAME')['TR'].rolling(3).sum().values

tickers = brain_mod['MFG_SHORT_NAME'].unique()

temp = pd.DataFrame()
for i in tickers:
    df_idx_reset = brain_mod[brain_mod['MFG_SHORT_NAME'] == i].reset_index(drop=True)
    df_idx_reset.loc[df_idx_reset.index % 3 != 2,'TS_ROLL3_SUM'] = np.nan
    df_idx_reset.loc[df_idx_reset.index % 3 != 2,'TR_ROLL3_SUM'] = np.nan
    temp = pd.concat([temp, df_idx_reset], ignore_index=True)
brain_mod = temp

#mfg_short_name = brain_mod['MFG_SHORT_NAME']
brain_mod[['TS_ROLL3_SUM','TR_ROLL3_SUM']] = brain_mod.groupby('MFG_SHORT_NAME', as_index=False)[['TS_ROLL3_SUM','TR_ROLL3_SUM']].bfill()
#brain_mod['MFG_SHORT_NAME'] = mfg_short_name

brain_mod[['TR','TS']] = brain_mod[['TR','TS']].astype(float)

brain_mod['month_dist_TR'] = brain_mod['TR'] / brain_mod['TR_ROLL3_SUM']
brain_mod['month_dist_TS'] = brain_mod['TS'] / brain_mod['TS_ROLL3_SUM']

fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(x='DATE', y='month_dist_TR', data=brain_mod, hue='MFG_SHORT_NAME')
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.lineplot(x='DATE', y='month_dist_TS', data=brain_mod, hue='MFG_SHORT_NAME')

# for i in tickers:
#     brain_mod[brain_mod['MFG_SHORT_NAME']==i].plot(x='DATE', y='month_dist_TR', figsize=fig_dims, style='.-')

# month_dist
# brain_mod.loc[21:23,'month_dist_TR']
# (data.loc[:,'0'].sum() / data.loc[:,'0'].sum().sum()).astype(float).round(4)

brain_mod['TR_MoM_Growth'] = brain_mod.groupby('MFG_SHORT_NAME')['TR'].pct_change()

temp = pd.DataFrame()
for i in tickers:
    df_idx_reset = brain_mod[brain_mod['MFG_SHORT_NAME'] == i].reset_index(drop=True)
    df_idx_reset.loc[::3,'TR_MoM_Growth'] = df_idx_reset.loc[::3,'TR'].pct_change()# / df_idx_reset.loc[::3,'month_dist_TR'].mean() - 1
    #df_idx_reset.loc[1::3,'month_dist_TR_mean_pct'] = df_idx_reset.loc[1::3,'month_dist_TR'] / df_idx_reset.loc[1::3,'month_dist_TR'].mean() - 1
    #df_idx_reset.loc[2::3,'month_dist_TR_mean_pct'] = df_idx_reset.loc[2::3,'month_dist_TR'] / df_idx_reset.loc[2::3,'month_dist_TR'].mean() - 1
    temp = pd.concat([temp, df_idx_reset], ignore_index=True)
brain_mod = temp

for i in tickers:
    upper_quantile = brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TR_MoM_Growth'].quantile(.90, interpolation='linear')
    lower_quantile = brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TR_MoM_Growth'].quantile(.1, interpolation='linear')
    brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TR_MoM_Growth']=brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TR_MoM_Growth'].clip(lower=lower_quantile, upper=upper_quantile)

# TODO possibly transform into percentage greater than the mean that month dist.
# brain_mod['month_dist_TR_mean_pct'] = np.nan


# TODO winsorize the high MoM growth, if there is growth greater than 3 std.

# for i in tickers:
#     brain_mod[brain_mod['MFG_SHORT_NAME']==i].plot(x='DATE', y='TR_MoM_Growth', figsize=fig_dims, style='.-', title=i)

# TODO possbly dummy variable first month beceause the distribution is not dependent on previous months.
# TODO could set the every first month to zero to see if it improves
# for i in tickers:
#     brain_mod[brain_mod['MFG_SHORT_NAME']==i].plot(x='TR_MoM_Growth', y='month_dist_TR', figsize=fig_dims, style='.', title=i)

fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]])
correlations = []
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]][['TR_MoM_Growth','month_dist_TR']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]][['TR_MoM_Growth','month_dist_TR']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]][['TR_MoM_Growth','month_dist_TR']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]][['TR_MoM_Growth','month_dist_TR']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]][['TR_MoM_Growth','month_dist_TR']].corr())


residuals = []
y_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['month_dist_TR'].dropna()[1:].to_numpy()
X_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['TR_MoM_Growth'][1:(len(y_1)+1)]
X_1 = sm.add_constant(X_1).to_numpy()
model1 = sm.OLS(y_1,X_1).fit()
model1.summary()
residuals.append(np.std(y_1 - model1.fittedvalues) * 2) 

y_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['month_dist_TR'].dropna()[1:]
X_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['TR_MoM_Growth'][1:(len(y_2)+1)]
X_2 = sm.add_constant(X_2)
model2 = sm.OLS(y_2,X_2).fit()
model2.summary()
residuals.append(np.std(y_2 - model2.fittedvalues) * 2)

y_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['month_dist_TR'].dropna()[1:].to_numpy()
X_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['TR_MoM_Growth'][1:(len(y_3)+1)]
X_3 = sm.add_constant(X_3).to_numpy()
model3 = sm.OLS(y_3,X_3).fit()
model3.summary()
residuals.append(np.std(y_3 - model3.fittedvalues) * 2)

y_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['month_dist_TR'].dropna()[1:].to_numpy()
X_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['TR_MoM_Growth'][1:(len(y_4)+1)]
X_4 = sm.add_constant(X_4).to_numpy()
model4 = sm.OLS(y_4,X_4).fit()
model4.summary()
residuals.append(np.std(y_4 - model4.fittedvalues) * 2)

y_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['month_dist_TR'].dropna()[1:].to_numpy()
X_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['TR_MoM_Growth'][1:(len(y_5)+1)]
X_5 = sm.add_constant(X_5).to_numpy()
model5 = sm.OLS(y_5,X_5).fit()
model5.summary()
residuals.append(np.std(y_5 - model5.fittedvalues) * 2)

fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]])
model1.summary()
fig,ax = plt.subplots(figsize=fig_dims)
plt.plot(y_1, model1.fittedvalues, '.')
fig,ax = plt.subplots(figsize=fig_dims)
plt.plot(X_1[:,1],model1.fittedvalues-y_1, '.')

fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]])
model3.summary()
plt.plot(y_3, model3.fittedvalues, '.')
plt.plot(X_3[:,1],model3.fittedvalues-y_3, '.')

#region pct deviations
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR_mean_pct', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR_mean_pct', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR_mean_pct', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR_mean_pct', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TR_MoM_Growth', y='month_dist_TR_mean_pct', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]])
correlations = []
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]][['TR_MoM_Growth','month_dist_TR_mean_pct']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]][['TR_MoM_Growth','month_dist_TR_mean_pct']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]][['TR_MoM_Growth','month_dist_TR_mean_pct']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]][['TR_MoM_Growth','month_dist_TR_mean_pct']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]][['TR_MoM_Growth','month_dist_TR_mean_pct']].corr())


residuals = []
y_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['month_dist_TR_mean_pct'].dropna()[1:].to_numpy()
X_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['TR_MoM_Growth'][1:(len(y_1)+1)]
X_1 = sm.add_constant(X_1).to_numpy()
model1 = sm.OLS(y_1,X_1).fit()
model1.summary()
residuals.append(np.std(y_1 - model1.fittedvalues) * 2) 

y_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['month_dist_TR_mean_pct'].dropna()[1:]
X_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['TR_MoM_Growth'][1:(len(y_2)+1)]
X_2 = sm.add_constant(X_2)
model2 = sm.OLS(y_2,X_2).fit()
model2.summary()
residuals.append(np.std(y_2 - model2.fittedvalues) * 2)

y_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['month_dist_TR_mean_pct'].dropna()[1:].to_numpy()
X_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['TR_MoM_Growth'][1:(len(y_3)+1)]
X_3 = sm.add_constant(X_3).to_numpy()
model3 = sm.OLS(y_3,X_3).fit()
model3.summary()
residuals.append(np.std(y_3 - model3.fittedvalues) * 2)

y_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['month_dist_TR_mean_pct'].dropna()[1:].to_numpy()
X_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['TR_MoM_Growth'][1:(len(y_4)+1)]
X_4 = sm.add_constant(X_4).to_numpy()
model4 = sm.OLS(y_4,X_4).fit()
model4.summary()
residuals.append(np.std(y_4 - model4.fittedvalues) * 2)

y_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['month_dist_TR_mean_pct'].dropna()[1:].to_numpy()
X_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['TR_MoM_Growth'][1:(len(y_5)+1)]
X_5 = sm.add_constant(X_5).to_numpy()
model5 = sm.OLS(y_5,X_5).fit()
model5.summary()
residuals.append(np.std(y_5 - model5.fittedvalues) * 2)
#endregion pct deviations

# TODO dummy variable is first month, see if it improves
# TODO 










# region TS
brain_mod['TS_MoM_Growth'] = brain_mod.groupby('MFG_SHORT_NAME')['TS'].pct_change()

# TODO winsorize the high MoM growth, if there is growth greater than 3 std.
for i in tickers:
    upper_quantile = brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TS_MoM_Growth'].quantile(.95, interpolation='linear')
    lower_quantile = brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TS_MoM_Growth'].quantile(.05, interpolation='linear')
    brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TS_MoM_Growth']=brain_mod.loc[brain_mod['MFG_SHORT_NAME']==i,'TS_MoM_Growth'].clip(lower=lower_quantile, upper=upper_quantile)

for i in tickers:
    brain_mod[brain_mod['MFG_SHORT_NAME']==i].plot(x='DATE', y='TS_MoM_Growth', figsize=fig_dims, style='.-', title=i)

# TODO possbly dummy variable first month beceause the disTSibution is not dependent on previous months.
# TODO could set the every first month to zero to see if it improves
for i in tickers:
    brain_mod[brain_mod['MFG_SHORT_NAME']==i].plot(x='TS_MoM_Growth', y='month_dist_TS', figsize=fig_dims, style='.', title=i)

fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TS_MoM_Growth', y='month_dist_TS', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TS_MoM_Growth', y='month_dist_TS', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TS_MoM_Growth', y='month_dist_TS', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TS_MoM_Growth', y='month_dist_TS', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]])
fig_dims=(12,8)
fig,ax = plt.subplots(figsize=fig_dims)
sns.regplot(x='TS_MoM_Growth', y='month_dist_TS', data=brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]])
correlations = []
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]][['TS_MoM_Growth','month_dist_TS']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]][['TS_MoM_Growth','month_dist_TS']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]][['TS_MoM_Growth','month_dist_TS']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]][['TS_MoM_Growth','month_dist_TS']].corr())
correlations.append(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]][['TS_MoM_Growth','month_dist_TS']].corr())


residuals = []
y_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['month_dist_TS'].dropna()[1:].to_numpy()
X_1 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['TS_MoM_Growth'][1:(len(y_1)+1)]
X_1 = sm.add_constant(X_1).to_numpy()
model1 = sm.OLS(y_1,X_1).fit()
model1.summary()
residuals.append(np.std(y_1 - model1.fittedvalues) * 2) 

y_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['month_dist_TS'].dropna()[1:]
X_2 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]]['TS_MoM_Growth'][1:(len(y_2)+1)]
X_2 = sm.add_constant(X_2)
model2 = sm.OLS(y_2,X_2).fit()
model2.summary()
residuals.append(np.std(y_2 - model2.fittedvalues) * 2)

y_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['month_dist_TS'].dropna()[1:].to_numpy()
X_3 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]]['TS_MoM_Growth'][1:(len(y_3)+1)]
X_3 = sm.add_constant(X_3).to_numpy()
model3 = sm.OLS(y_3,X_3).fit()
model3.summary()
residuals.append(np.std(y_3 - model3.fittedvalues) * 2)

y_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['month_dist_TS'].dropna()[1:].to_numpy()
X_4 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]]['TS_MoM_Growth'][1:(len(y_4)+1)]
X_4 = sm.add_constant(X_4).to_numpy()
model4 = sm.OLS(y_4,X_4).fit()
model4.summary()
residuals.append(np.std(y_4 - model4.fittedvalues) * 2)

y_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['month_dist_TS'].dropna()[1:].to_numpy()
X_5 = brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]]['TS_MoM_Growth'][1:(len(y_5)+1)]
X_5 = sm.add_constant(X_5).to_numpy()
model5 = sm.OLS(y_5,X_5).fit()
model5.summary()
residuals.append(np.std(y_5 - model5.fittedvalues) * 2)

# TODO dummy variable is first month, see if it improves
# TODO 
brain_mod['month_dist_TS_QoQ_Growth'] = brain_mod['month_dist_TS'].pct_change(3)
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]].plot(x='DATE', y='month_dist_TS_QoQ_Growth', figsize=fig_dims, style='.-', title=tickers[0])
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[1]].plot(x='DATE', y='month_dist_TS_QoQ_Growth', figsize=fig_dims, style='.-', title=tickers[1])
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[2]].plot(x='DATE', y='month_dist_TS_QoQ_Growth', figsize=fig_dims, style='.-', title=tickers[2])
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[3]].plot(x='DATE', y='month_dist_TS_QoQ_Growth', figsize=fig_dims, style='.-', title=tickers[3])
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[4]].plot(x='DATE', y='month_dist_TS_QoQ_Growth', figsize=fig_dims, style='.-', title=tickers[4])
#endregion new section












plot_acf(brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]]['month_dist_TR'].dropna())
# average every 3.
brain_mod['adj_factor'] = brain_mod['TS'] / brain_mod['TR']
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]].plot(x='DATE', y='adj_factor', title=tickers[0], style='.-', figsize=fig_dims)
brain_mod[brain_mod['MFG_SHORT_NAME']==tickers[0]].plot(x='adj_factor', y='month_dist_TR', title=tickers[0], style='.', figsize=fig_dims)

# TODO models
# Take a look at the adjustment factor
# Times Series Model
# Distribution averages.
# TODO ask kenny if he would know that every first quarter month that usually have lower spends
# TODO random forrest approach or check out the adjustment kind of random forrest
# TODO random forrest kind of approach see what level of distribution based on growth rate.
# TODO linear interpolate QoQ growth rate. see if those growth rates  are predictive of distribution
# TODO or do a weighted average weight of distribution. or regular for 1st month, second month, third month.
# first month distribution should theoreteically be lower