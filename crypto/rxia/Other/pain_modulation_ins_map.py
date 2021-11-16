import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from utilities import util

painmod_ins_str="""select   date, 

                case
                    when split_part(facility_id, '_', 1) = 'P' then 2*split_part(facility_id, '_', 2)::INT + 1
                    when split_part(facility_id, '_', 1) = 'M' then 2*split_part(facility_id, '_', 2)::INT
                end as facility_alias, 
                
                mfg_short_name, category_3, CATEGORY_4, 

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
                case when category_3 = 'INS' and category_4 ilike '%REPLACEMENT%' THEN 'REPLACEMENT'
                when category_4 ilike '%initial%' and category_3 = 'INS' then 'INITIAL' 
                else null end INS_TYPE, mfg_catalog,

                CASE WHEN category_3 = 'INS' and AVG_PRICE <2000 THEN 'FLAG' else null end flag, volume_raw, avg_price

                from temp.monitor2.PAINMOD_workbook_data
                where (date between '2019-01-01' and '2021-01-01') and category_2 ilike '%spinal%' 
                AND CATEGORY_3  IN ('INS')
                and flag is null
                group by 1,2,3,4,5,6,7,8,9,10,11
                order by 2, 5
                    """

painmod_ins = util.connect_snwflk(painmod_ins_str)
#painmod_ins = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin(big_4)]
painmod_ins['AVG_PRICE'] = painmod_ins['AVG_PRICE'].astype(float)

for i in painmod_ins['MFG_SHORT_NAME'].unique():
    print(i)
    temp = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([i])]
    fig_dims=(24,22)
    fig,ax = plt.subplots(figsize=fig_dims)
    sns.boxplot(data=temp, x='CATEGORY_4', y='AVG_PRICE', hue='CATEGORY_4')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

mfg_ipg = painmod_ins['MFG_SHORT_NAME'].unique().tolist()

#region medtronic
mdt_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[0]])]
mdt_price_cutoff = mdt_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.75,  interpolation='nearest')
# index 0 are all initials.
# index 1 are not all initials cut off at 75 quantile, greater or equal are initials
# index 2 all initials
# index 3 all replacement
# index 4 all replacement
# index 5 all replacement
# index 6 are all initial
# index 7 are all replacement
# index 8 are all initials
# index 9 are not all replacement, cut off at 75 quantile, not equal
# index 10 are all initials
# index 11 are all initials
mdt_category_4 = mdt_price_cutoff['CATEGORY_4'].unique().tolist()

IS_MDT_CAT_1 =  mdt_painmod['CATEGORY_4'].isin([mdt_category_4[1]]) 
mdt_prc_cat_cut_1 = mdt_painmod.loc[IS_MDT_CAT_1,'AVG_PRICE'].quantile(.1,interpolation='lower')
mdt_prc_cutoff_cat_1 = np.where(mdt_painmod.loc[IS_MDT_CAT_1,'AVG_PRICE'] >= mdt_prc_cat_cut_1, 'INITIAL', 'REPLACEMENT')
mdt_painmod.loc[mdt_painmod[IS_MDT_CAT_1].index,'INS_TYPE'] = mdt_prc_cutoff_cat_1

IS_MDT_CAT_4 = mdt_painmod['CATEGORY_4'].isin([mdt_category_4[4]]) 
mdt_painmod.loc[IS_MDT_CAT_4,'INS_TYPE'] = 'REPLACEMENT'

IS_MDT_CAT_6 = mdt_painmod['CATEGORY_4'].isin([mdt_category_4[6]])
mdt_painmod.loc[IS_MDT_CAT_6,'INS_TYPE'] = 'INITIAL'

IS_MDT_CAT_7 = mdt_painmod['CATEGORY_4'].isin([mdt_category_4[7]])
mdt_painmod.loc[IS_MDT_CAT_7,'INS_TYPE'] = 'REPLACEMENT'

IS_MDT_CAT_9 = mdt_painmod['CATEGORY_4'].isin([mdt_category_4[9]])
mdt_prc_cutoff_cat_9 = np.where(mdt_painmod.loc[IS_MDT_CAT_9,'AVG_PRICE'] > mdt_price_cutoff.iloc[9,1], 'INITIAL', 'REPLACEMENT')
mdt_painmod.loc[mdt_painmod[IS_MDT_CAT_9].index,'INS_TYPE'] = mdt_prc_cutoff_cat_9

IS_MDT_CAT_11 = mdt_painmod['CATEGORY_4'].isin([mdt_category_4[11]])
mdt_painmod.loc[IS_MDT_CAT_11,'INS_TYPE'] = 'INITIAL'
#endregion medtronic

#region BSX
bsx_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[1]])]
bsx_price_cutoff = bsx_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.25,  interpolation='nearest')
bsx_category_4 = bsx_price_cutoff['CATEGORY_4'].unique().tolist()
# index 0 not all are initials, cutoff 25 quantile, greater than and equal
# index 1 are all initials
# index 2 not all are initials, cutoff 25 quantile, greater than
# index 3 are all initials
# index 4 not all are initials, cutoff 25 quantile, greater than
# index 5 not all are initials, cutoff 25 quantile, greater than
# index 6 are all initials
# index 7 not all are initials, cutoff 25 quantile, greater than
# index 8 are all initials
IS_BSX_CAT_0 = bsx_painmod['CATEGORY_4'].isin([bsx_category_4[0]])
bsx_prc_cutoff_cat_0 = np.where(bsx_painmod.loc[IS_BSX_CAT_0,'AVG_PRICE'] >= bsx_price_cutoff.iloc[0,1], 'INITIAL', 'REPLACEMENT')
bsx_painmod.loc[bsx_painmod[IS_BSX_CAT_0].index,'INS_TYPE'] = bsx_prc_cutoff_cat_0

IS_BSX_CAT_2 = bsx_painmod['CATEGORY_4'].isin([bsx_category_4[2]])
bsx_prc_cutoff_cat_2 = np.where(bsx_painmod.loc[IS_BSX_CAT_2,'AVG_PRICE'] > bsx_price_cutoff.iloc[2,1], 'INITIAL', 'REPLACEMENT')
bsx_painmod.loc[bsx_painmod[IS_BSX_CAT_2].index,'INS_TYPE'] = bsx_prc_cutoff_cat_2

IS_BSX_CAT_4 = bsx_painmod['CATEGORY_4'].isin([bsx_category_4[4]])
bsx_prc_cutoff_cat_4 = np.where(bsx_painmod.loc[IS_BSX_CAT_4,'AVG_PRICE'] > bsx_price_cutoff.iloc[4,1], 'INITIAL', 'REPLACEMENT')
bsx_painmod.loc[bsx_painmod[IS_BSX_CAT_4].index,'INS_TYPE'] = bsx_prc_cutoff_cat_4

IS_BSX_CAT_5 = bsx_painmod['CATEGORY_4'].isin([bsx_category_4[5]])
bsx_prc_cutoff_cat_5 = np.where(bsx_painmod.loc[IS_BSX_CAT_5,'AVG_PRICE'] > bsx_price_cutoff.iloc[5,1], 'INITIAL', 'REPLACEMENT')
bsx_painmod.loc[bsx_painmod[IS_BSX_CAT_5].index,'INS_TYPE'] = bsx_prc_cutoff_cat_5

IS_BSX_CAT_7 = bsx_painmod['CATEGORY_4'].isin([bsx_category_4[7]])
bsx_prc_cat_cut_7 = bsx_painmod.loc[IS_BSX_CAT_7,'AVG_PRICE'].quantile(.15, interpolation='lower')
bsx_prc_cutoff_cat_7 = np.where(bsx_painmod.loc[IS_BSX_CAT_7,'AVG_PRICE'] >= bsx_prc_cat_cut_7, 'INITIAL', 'REPLACEMENT')
bsx_painmod.loc[bsx_painmod[IS_BSX_CAT_7].index,'INS_TYPE'] = bsx_prc_cutoff_cat_7
#endregion BSX

#region ABBOTT LABORATORIES
abt_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[2]])]
abt_price_cutoff = abt_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.25,  interpolation='nearest')
abt_category_4 = abt_price_cutoff['CATEGORY_4'].unique().tolist()
# index 0 not all are initials, greater than or equal quantile 25 are initials
# index 1 are all replacement
# index 2 are all replacement
# index 3 are all initials
# index 4 not all are initials, greater than or equal quantile 25 are initials
# index 5 are all initials
# index 6 not all are initials, greater than or equal quantile 25 are initials
# index 7 are all initials
# index 8 not all are initials, greater than quantile 25 are initials
# index 9 are all replacement
# index 10 are all initials

IS_ABT_CAT_0 = abt_painmod['CATEGORY_4'].isin([abt_category_4[0]])
abt_prc_cutoff_cat_0 = np.where(abt_painmod.loc[IS_ABT_CAT_0,'AVG_PRICE'] >= abt_price_cutoff.iloc[0,1], 'INITIAL', 'REPLACEMENT')
abt_painmod.loc[abt_painmod[IS_ABT_CAT_0].index,'INS_TYPE'] = abt_prc_cutoff_cat_0

IS_ABT_CAT_2 = abt_painmod['CATEGORY_4'].isin([abt_category_4[2]])
abt_painmod.loc[abt_painmod[IS_ABT_CAT_2].index,'INS_TYPE'] = 'REPLACEMENT'

IS_ABT_CAT_4 = abt_painmod['CATEGORY_4'].isin([abt_category_4[4]])
abt_prc_cat_cut_4 = abt_painmod.loc[IS_ABT_CAT_4,'AVG_PRICE'].quantile(.10, interpolation='lower')
abt_prc_cutoff_cat_4 = np.where(abt_painmod.loc[IS_ABT_CAT_4,'AVG_PRICE'] >= abt_prc_cat_cut_4, 'INITIAL', 'REPLACEMENT')
abt_painmod.loc[abt_painmod[IS_ABT_CAT_4].index,'INS_TYPE'] = abt_prc_cutoff_cat_4

IS_ABT_CAT_6 = abt_painmod['CATEGORY_4'].isin([abt_category_4[6]])
abt_prc_cat_cut_6 = abt_painmod.loc[IS_ABT_CAT_6,'AVG_PRICE'].quantile(.10, interpolation='lower')
abt_prc_cutoff_cat_6 = np.where(abt_painmod.loc[IS_ABT_CAT_6,'AVG_PRICE'] >= abt_prc_cat_cut_6, 'INITIAL', 'REPLACEMENT')
abt_painmod.loc[abt_painmod[IS_ABT_CAT_6].index,'INS_TYPE'] = abt_prc_cutoff_cat_6

IS_ABT_CAT_8 = abt_painmod['CATEGORY_4'].isin([abt_category_4[8]])
abt_prc_cutoff_cat_8 = np.where(abt_painmod.loc[IS_ABT_CAT_8,'AVG_PRICE'] > abt_price_cutoff.iloc[8,1], 'INITIAL', 'REPLACEMENT')
abt_painmod.loc[abt_painmod[IS_ABT_CAT_8].index,'INS_TYPE'] = abt_prc_cutoff_cat_8

IS_ABT_CAT_9 = abt_painmod['CATEGORY_4'].isin([abt_category_4[9]])
abt_painmod.loc[abt_painmod[IS_ABT_CAT_9].index,'INS_TYPE'] = 'REPLACEMENT'
#endregion ABBOTT LABORTORIES

# region NUVECTRA
nvtr_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[3]])]
nvtr_price_cutoff = nvtr_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.75,  interpolation='nearest')
nvtr_category_4 = nvtr_price_cutoff['CATEGORY_4'].unique().tolist()

IS_NVTR_CAT_0 = nvtr_painmod['CATEGORY_4'].isin([nvtr_category_4[0]])
nvtr_prc_cutoff_cat_0 = np.where(nvtr_painmod.loc[IS_NVTR_CAT_0,'AVG_PRICE'] > nvtr_price_cutoff.iloc[0,1], 'INITIAL', 'REPLACEMENT')
nvtr_painmod.loc[nvtr_painmod[IS_NVTR_CAT_0].index,'INS_TYPE'] = nvtr_prc_cutoff_cat_0
#endregion NUVECTRA

#region STIMWAVE
stimwv_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[4]])]
stimwv_price_cutoff = stimwv_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.15, interpolation='lower') #,  interpolation='nearest'
stimwv_category_4 = stimwv_price_cutoff['CATEGORY_4'].unique().tolist()

IS_STIMWV_CAT_0 = stimwv_painmod['CATEGORY_4'].isin([stimwv_category_4[0]])
stimwv_painmod.loc[stimwv_painmod[IS_STIMWV_CAT_0].index,'INS_TYPE'] = 'REPLACEMENT'

IS_STIMWV_CAT_1 = stimwv_painmod['CATEGORY_4'].isin([stimwv_category_4[1]])
stimwv_prc_cutoff_cat_1 = np.where(stimwv_painmod.loc[IS_STIMWV_CAT_1,'AVG_PRICE'] >= stimwv_price_cutoff.iloc[1,1], 'INITIAL', 'REPLACEMENT')
stimwv_painmod.loc[stimwv_painmod[IS_STIMWV_CAT_1].index,'INS_TYPE'] = stimwv_prc_cutoff_cat_1
#endregion stimwave

#region NEVRO
nvro_painmod = painmod_ins[painmod_ins['MFG_SHORT_NAME'].isin([mfg_ipg[5]])]
nvro_price_cutoff = nvro_painmod.groupby('CATEGORY_4',as_index=False)['AVG_PRICE'].quantile(.04, interpolation='lower') #,  interpolation='nearest'
nvro_category_4 = nvro_price_cutoff['CATEGORY_4'].unique().tolist()

IS_NVRO_CAT_0 = nvro_painmod['CATEGORY_4'].isin([nvro_category_4[0]])
nvro_cat_0_prc_cut = nvro_painmod.loc[IS_NVRO_CAT_0,'AVG_PRICE'].quantile(.04,interpolation='lower')
nvro_prc_cutoff_cat_0 = np.where(nvro_painmod.loc[IS_NVRO_CAT_0,'AVG_PRICE'] > nvro_cat_0_prc_cut, 'INITIAL', 'REPLACEMENT')
nvro_painmod.loc[nvro_painmod[IS_NVRO_CAT_0].index,'INS_TYPE'] = nvro_prc_cutoff_cat_0

IS_NVRO_CAT_1 = nvro_painmod['CATEGORY_4'].isin([nvro_category_4[1]])
nvro_cat_1_prc_cut = nvro_painmod.loc[IS_NVRO_CAT_1,'AVG_PRICE'].quantile(.3,interpolation='lower')
nvro_prc_cutoff_cat_1 = np.where(nvro_painmod.loc[IS_NVRO_CAT_1,'AVG_PRICE'] > nvro_cat_1_prc_cut, 'INITIAL', 'REPLACEMENT')
nvro_painmod.loc[nvro_painmod[IS_NVRO_CAT_1].index,'INS_TYPE'] = nvro_prc_cutoff_cat_1

IS_NVRO_CAT_2 = nvro_painmod['CATEGORY_4'].isin([nvro_category_4[2]])
nvro_cat_2_prc_cut = nvro_painmod.loc[IS_NVRO_CAT_2,'AVG_PRICE'].quantile(.02,interpolation='lower')
nvro_prc_cutoff_cat_2 = np.where(nvro_painmod.loc[IS_NVRO_CAT_2,'AVG_PRICE'] >= nvro_cat_2_prc_cut, 'INITIAL', 'REPLACEMENT')
nvro_painmod.loc[nvro_painmod[IS_NVRO_CAT_2].index,'INS_TYPE'] = nvro_prc_cutoff_cat_2
#endregion NEVRO

temp = pd.concat([mdt_painmod, bsx_painmod, abt_painmod, nvtr_painmod, stimwv_painmod, nvro_painmod], axis=0)

temp.to_excel('PAINMOD_INS_MAPPING.xlsx', index=False)