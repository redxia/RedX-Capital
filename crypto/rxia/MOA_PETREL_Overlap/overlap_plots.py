import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import snowflake.connector
import os



cnx = snowflake.connector.connect(
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
cur = cnx.cursor()


cur.execute("""
select facility_id_moa, facility_id_sarco from research.rxia.facility_match_6 where pct > 0.5 and facility_id_sarco not like 'S_AGG%' and matches > 100;
""")

cols = [c[0] for c in cur.description]
result = cur.fetchall()
df_fac = pd.DataFrame(data=result, columns=cols)


cur.execute("""
select distinct date from petrel_live.merged.v_petrel_moa_current where date >= '2012-01-01' order by 1;
""")

cols = [c[0] for c in cur.description]
result = cur.fetchall()
df_date = pd.DataFrame(data=result, columns=cols)



for ix in range(len(df_fac)):
    print(f'Working on pair {ix + 1} of {len(df_fac)}')
    
    plt.close('all')
    
    m_fac = df_fac.loc[ix, 'FACILITY_ID_MOA']
    p_fac = df_fac.loc[ix, 'FACILITY_ID_PETREL']

    cur.execute(f"""
    create or replace table top_skus_m as
    with a as
    (select facility_id, date, mfg_ticker, mfg_catalog, sum(total_spend) spend 
    from petrel_live.merged.v_petrel_moa_current where facility_id = '{m_fac}' and mfg_ticker is not null 
    and date >= '2012-01-01'
    group by 1, 2, 3, 4)
    select facility_id, mfg_ticker, mfg_catalog, count(spend) top_skus from a group by 1, 2, 3
    """)
    
    
    cur.execute(f"""
    create or replace table top_skus_p as
    with a as
    (select facility_id, date, mfg_ticker, mfg_catalog, sum(total_spend) spend 
    from petrel_live.merged.v_petrel_moa_current where facility_id = '{p_fac}' and mfg_ticker is not null 
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
    (select * from petrel_live.merged.v_petrel_moa_current where facility_id in ('{m_fac}', '{p_fac}')) as b
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
    
    
    dfm = df[df['FACILITY_ID'] == m_fac]
    dfp = df[df['FACILITY_ID'] == p_fac]
    
    
    
    dfm = df_cross.merge(dfm, how='left', left_on=['DATE', 'MFG_TICKER_CATALOG'], right_on=['DATE', 'MFG_TICKER_CATALOG'])
    dfp = df_cross.merge(dfp, how='left', left_on=['DATE', 'MFG_TICKER_CATALOG'], right_on=['DATE', 'MFG_TICKER_CATALOG'])   
    
    
    fig, axes = plt.subplots(10, 1)
    
    
    pltnum = 0
    for s in list(dfm['MFG_TICKER_CATALOG'].unique()):
        
        dfmm = dfm[dfm['MFG_TICKER_CATALOG'] == s]
        dfpp = dfp[dfp['MFG_TICKER_CATALOG'] == s]
        
        if (len(dfmm[~np.isnan(dfmm['TOTAL_SPEND'])]) == 0) or (len(dfpp[~np.isnan(dfpp['TOTAL_SPEND'])]) == 0):
            continue
        
        
        if (pltnum > 9):
            continue
        
        axes[pltnum].plot(dfmm['DATE'], dfmm['TOTAL_SPEND'], '-r')
        axes[pltnum].plot(dfpp['DATE'], dfpp['TOTAL_SPEND'], ':k')
        axes[pltnum].grid()
        axes[pltnum].set_ylabel(s)
        if pltnum < 9:
            axes[pltnum].set_xticklabels([])
       
            
        pltnum = pltnum + 1
        
        
    plt.xlabel(f'MOA facility {m_fac[2:]} / PETREL facility {p_fac[2:]}')
    
    fig = plt.gcf()
    fig.set_size_inches(24, 12)
    
    
    plt.savefig(f'T:\Personal Folders\Andrew\Overlap Figures\{m_fac[0]}{m_fac[2:]}_{p_fac[0]}{p_fac[2:]}.png')
    