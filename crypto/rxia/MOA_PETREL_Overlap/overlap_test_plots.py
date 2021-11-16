import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import snowflake.connector
import os
import re





cnx = snowflake.connector.connect(
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
cur = cnx.cursor()


df_rev = pd.read_excel(r'C:\dev\da.research\personal\afontanella\MOA_PETREL_Overlap\overlap_facilities_review_dedupe.xlsx', 
                   sheet_name='overlap_facilities_review_yeses')


df_rev = df_rev[['DIVISION_MOA', 'DIVISION_PETREL', 'MOA_FACILITY', 'PETREL_FACILITY', 'FACILITY_TYPE_MOA', 
         'FACILITY_TYPE_PETREL', 'BED_SIZE_MOA', 'BED_SIZE_PETREL']]


df_rev.to_csv(r'C:\\dev\\da.research\\personal\\afontanella\\MOA_PETREL_Overlap\\overlap_results.csv', index=False)

cur.execute("""
create or replace table temp.af.fac (
    DIVISION_MOA varchar, 
    DIVISION_PETREL varchar,
    MOA_FACILITY varchar,
    PETREL_FACILITY varchar,
    FACILITY_TYPE_MOA varchar,
    FACILITY_TYPE_PETREL varchar,
    BED_SIZE_MOA varchar,
    BED_SIZE_PETREL varchar
    )
""")

cur.execute("""
put 'file://C://dev//da.research//personal//afontanella//MOA_PETREL_Overlap//overlap_results.csv' @~/temp/ source_compression=none auto_compress=true;
""")

cur.execute("""
truncate temp.af.fac;
""")

cur.execute("""
copy into temp.af.fac from  @~/temp/overlap_results.csv.gz
file_format = (type='CSV' compression=gzip field_delimiter=',' skip_header=1 field_optionally_enclosed_by='"')
enforce_length = false 
purge = true 
force = true;
""")



fac_group = []
for m in list(df_rev['MOA_FACILITY'].unique()):
    df1 = df_rev[df_rev['MOA_FACILITY'] == m]
    p = list(df1['PETREL_FACILITY'].unique())
    df2 = df_rev[df_rev['PETREL_FACILITY'].isin(p)]
    m = list(df2['MOA_FACILITY'].unique())
    df3 = df_rev[df_rev['MOA_FACILITY'].isin(m)]

    m_list = list(df3['MOA_FACILITY'].unique())
    p_list = list(df3['PETREL_FACILITY'].unique())
    
    fac_group.append((m_list, p_list))
    
    

    
fac_group = sorted(fac_group)
s = [', '.join(x[0]) + ', ' + ', '.join(x[1]) for x in fac_group]
ixx = []
for ix, ss in enumerate(s):
    if ss not in s[:ix]:
        ixx.append(ix)
    
fac_group_dedup = []
for ix, f in enumerate(fac_group):
    if ix in ixx:
        fac_group_dedup.append(f)


cur.execute("""
create table if not exists temp.af.m_p_merge as
select date, mfg_ticker, mfg_catalog, total_spend,
iff(facility_id = 'P_AGGREGATED', facility_id || '_' || division || '_' || facility_type, facility_id) as facility_id
from petrel_live.merged.v_petrel_moa_current
""")   


cur.execute("""
select distinct date from petrel_live.merged.v_petrel_moa_current where date >= '2012-01-01' order by 1;
""")

cols = [c[0] for c in cur.description]
result = cur.fetchall()
df_date = pd.DataFrame(data=result, columns=cols)
    
    

for ix, f in enumerate(fac_group_dedup):
    
    
    
    print(f'Working on group {str(int(ix + 1))} of {str(int(len(fac_group_dedup)))}')
    
    m_list = f[0]
    p_list = f[1]
    
    
    m_str = ', '.join([f"'{x}'" for x in m_list])
    p_str = ', '.join([f"'{x}'" for x in p_list])
    
    m_str2 = ', '.join([x for x in m_list])
    p_str2 = ', '.join([x for x in p_list])
    
    mp_str = m_str + ', ' + p_str
    
    
    cur.execute(f"""
    create or replace table top_skus_m as
    with a as
    (select facility_id, date, mfg_ticker, mfg_catalog, sum(total_spend) spend 
    from temp.af.m_p_merge where facility_id in ({m_str}) and mfg_ticker is not null 
    and date >= '2012-01-01'
    group by 1, 2, 3, 4)
    select facility_id, mfg_ticker, mfg_catalog, count(spend) top_skus from a group by 1, 2, 3
    """)
    
    
    cur.execute(f"""
    create or replace table top_skus_p as
    with a as
    (select facility_id, date, mfg_ticker, mfg_catalog, sum(total_spend) spend 
    from temp.af.m_p_merge where facility_id in ({p_str}) and mfg_ticker is not null 
    and date >= '2012-01-01'
    group by 1, 2, 3, 4)
    select facility_id, mfg_ticker, mfg_catalog, count(spend) top_skus from a group by 1, 2, 3
    """)
    
    
    cur.execute(f"""
    create or replace table top_skus as
    select a.mfg_ticker, a.mfg_catalog, a.top_skus skus_m, b.top_skus skus_p, a.top_skus*b.top_skus as prod
    from top_skus_m as a
    inner join
    top_skus_p as b
    on a.mfg_ticker = b.mfg_ticker
    and a.mfg_catalog = b.mfg_catalog
    order by prod desc
    limit 10
    """)
    
    
    cur.execute(f"""
    select date, facility_id, mfg_ticker, mfg_catalog, sum(total_spend) total_spend from
    (select b.* from
    top_skus as a
    left join
    (select * from temp.af.m_p_merge where facility_id in ({mp_str})) as b
    on a.mfg_ticker = b.mfg_ticker
    and a.mfg_catalog = b.mfg_catalog)
    group by 1, 2, 3, 4
    order by 1, 2, 3, 4;
    """)
    
            
            
    
    cols = [c[0] for c in cur.description]
    result = cur.fetchall()
    df = pd.DataFrame(data=result, columns=cols)
    
    
    df['TOTAL_SPEND'] = pd.to_numeric(df['TOTAL_SPEND'])
    
    df['MFG_TICKER_CATALOG'] = df.apply(lambda x: x['MFG_TICKER'] + '_' + x['MFG_CATALOG'], axis=1)
    
    
    df_cross = pd.DataFrame(columns=['DATE', 'MFG_TICKER_CATALOG'])
    ixx = 0
    for a in list(df['MFG_TICKER_CATALOG'].unique()):
        for b in list(df_date['DATE'].unique()):
            df_cross.loc[ixx, ['DATE', 'MFG_TICKER_CATALOG']] = (b, a)
            ixx = ixx + 1
    
    
    
    dfm_all = df[df['FACILITY_ID'].isin(m_list)]
    dfp_all = df[df['FACILITY_ID'].isin(p_list)]
    dfm_all = df_cross.merge(dfm_all, how='left', left_on=['DATE', 'MFG_TICKER_CATALOG'], right_on=['DATE', 'MFG_TICKER_CATALOG'])
    dfp_all = df_cross.merge(dfp_all, how='left', left_on=['DATE', 'MFG_TICKER_CATALOG'], right_on=['DATE', 'MFG_TICKER_CATALOG'])   
    
    plt.close('all')
    
    fig, axes = plt.subplots(10, 1)
    
    
    pltnum = 0
    for s in list(df['MFG_TICKER_CATALOG'].unique()):
        
        dfmm = dfm_all[dfm_all['MFG_TICKER_CATALOG'] == s]
        dfpp = dfp_all[dfp_all['MFG_TICKER_CATALOG'] == s]
        
        
        dfm_group = dfmm.groupby(['DATE'])['DATE','TOTAL_SPEND'].sum().reset_index()
        dfp_group = dfpp.groupby(['DATE'])['DATE','TOTAL_SPEND'].sum().reset_index()
        
        
        if (len(dfmm[~np.isnan(dfmm['TOTAL_SPEND'])]) == 0) or (len(dfpp[~np.isnan(dfpp['TOTAL_SPEND'])]) == 0):
            continue
        
        
        if (pltnum > 9):
            continue
        
        axes[pltnum].plot(dfm_group['DATE'], dfm_group['TOTAL_SPEND'], '-r')
        axes[pltnum].plot(dfp_group['DATE'], dfp_group['TOTAL_SPEND'], ':b')
        axes[pltnum].grid()
        axes[pltnum].set_ylabel(s)
        
        
        m_unique = list(dfmm['FACILITY_ID'].unique())
        m_unique = [x for x in m_unique if type(x) == str]
        if len(m_unique) > 1:
            for m in m_unique:
                dfmmm = dfmm[dfmm['FACILITY_ID'] == m]
                
                dfmmm = df_date.merge(dfmmm, how='left', left_on=['DATE'], right_on=['DATE'])
                
                axes[pltnum].plot(dfmmm['DATE'], dfmmm['TOTAL_SPEND'], '-r', linewidth=0.5, alpha = 0.8)
        
        
        p_unique = list(dfpp['FACILITY_ID'].unique())
        p_unique = [x for x in p_unique if type(x) == str]
        if len(p_unique) > 1:
            for p in p_unique:
                dfppp = dfpp[dfpp['FACILITY_ID'] == p]
                
                dfppp = df_date.merge(dfppp, how='left', left_on=['DATE'], right_on=['DATE'])
                
                axes[pltnum].plot(dfppp['DATE'], dfppp['TOTAL_SPEND'], '-b', linewidth=0.5, alpha=0.8)
        
               
            
        pltnum = pltnum + 1
        
        
    plt.xlabel(f'MOA facilities {m_str2} / PETREL facility {p_str2}')
    
    fig = plt.gcf()
    fig.set_size_inches(24, 12)
    
    
    plt.savefig(f'T:\Personal Folders\Andrew\Overlap Figures\grouping\group_{str(ix + 1)}.png')
    
            
            
            
            
            
            
    
    
    
    
    
    