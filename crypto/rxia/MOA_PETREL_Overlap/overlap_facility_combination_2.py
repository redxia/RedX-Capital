import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import snowflake.connector
import os
import itertools



cnx = snowflake.connector.connect(
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
cur = cnx.cursor()


cur.execute("""
select * from facility_match_8 
where total_matches > 2 
and score > 1 
and (pct_all_moa_matches > 0.05 or pct_all_sarco_matches > 0.05) 
order by facility_id_moa, total_matches
""")

cols = [c[0] for c in cur.description]
result = cur.fetchall()
df = pd.DataFrame(data=result, columns=cols)

df_orig = df.copy()


def agg_fac_type(x):    
    if x['FACILITY_ID_SARCO'] == 'S_AGGREGATED': 
        y = f"{x['FACILITY_ID_SARCO']}_{x['DIVISION_SARCO']}_{x['FACILITY_TYPE_SARCO']}"
    else:
        y = x['FACILITY_ID_SARCO']
    return y
        
df['FACILITY_ID_SARCO'] = df.apply(lambda x: agg_fac_type(x), axis=1)

fac_group = []
for m in list(df['FACILITY_ID_MOA'].unique()):
    dfm = df[df['FACILITY_ID_MOA'] == m]
    if len(dfm) == 1:
        p = dfm.iloc[0]['FACILITY_ID_SARCO']
        dfp = df[df['FACILITY_ID_SARCO'] == p]
        m_list = list(dfp['FACILITY_ID_MOA'].unique())
        p_list = list(dfp['FACILITY_ID_SARCO'].unique())
    else:
        m_list = list(dfm['FACILITY_ID_MOA'].unique())
        p_list = list(dfm['FACILITY_ID_SARCO'].unique())
    fac_group.append((m_list, p_list))

for p in list(df['FACILITY_ID_SARCO'].unique()):
    dfp = df[df['FACILITY_ID_SARCO'] == p]
    if len(dfp) == 1:
        m = dfp.iloc[0]['FACILITY_ID_MOA']
        dfm = df[df['FACILITY_ID_MOA'] == m]
        p_list = list(dfm['FACILITY_ID_SARCO'].unique())
        m_list = list(dfm['FACILITY_ID_MOA'].unique())
    else:
        p_list = list(dfp['FACILITY_ID_SARCO'].unique())
        m_list = list(dfp['FACILITY_ID_MOA'].unique())
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
create or replace table temp.sarco_test.m_s_merge as
select date, mfg_ticker, mfg_catalog, total_spend,
iff(facility_id = 'S_AGGREGATED', facility_id || '_' || facility_type, facility_id) as facility_id
from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION;
""")   
    
    

fac_group_final = []
details = []
for ix, f in enumerate(fac_group_dedup):
    
    print(f'Working on group {str(int(ix + 1))} of {str(int(len(fac_group_dedup)))}')
    
    
    m_list = f[0].copy()
    p_list = f[1].copy()
    
    
    if (len(f[0]) == 1) and (len(f[1]) == 1):
        
        mstr = ', '.join(["'" + x + "'" for x in f[0]])
        pstr = ', '.join(["'" + x + "'" for x in f[1]])
        
        cur.execute(f"""
        select count(*) as matches from
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
             where facility_id in ({mstr}) group by 1, 2) as a
        inner join
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
            where facility_id in ({pstr}) group by 1, 2) as b
        on a.date = b.date
        and a.mfg_catalog = b.mfg_catalog
        and a.total_spend = b.total_spend;
        """)
        base = cur.fetchall()[0][0]
        
        details.append((f[0], f[1], mstr[1:-1], pstr[1:-1], base, 0, 'KEEP'))
        fac_group_final.append((f[0], f[1]))
        continue
    
    
    if (len(f[0]) > 1):
        
        mstr = ', '.join(["'" + x + "'" for x in f[0]])
        pstr = ', '.join(["'" + x + "'" for x in f[1]])
        
        cur.execute(f"""
        select count(*) as matches from
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
             where facility_id in ({mstr}) group by 1, 2) as a
        inner join
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
            where facility_id in ({pstr}) group by 1, 2) as b
        on a.date = b.date
        and a.mfg_catalog = b.mfg_catalog
        and a.total_spend = b.total_spend;
        """)
        base = cur.fetchall()[0][0]
        
        for ixx, m in enumerate(f[0]):
            
            m_list.remove(m)
            
            m_list_minus = f[0].copy()
            m_list_minus.remove(m)
            
            if len(m_list_minus) > 0:
                mstr = ', '.join(["'" + x + "'" for x in m_list_minus])
                pstr = ', '.join(["'" + x + "'" for x in f[1]])
                cur.execute(f"""
                select count(*) as matches from
                    (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge
                     where facility_id in ({mstr}) group by 1, 2) as a
                inner join
                    (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
                    where facility_id in ({pstr}) group by 1, 2) as b
                on a.date = b.date
                and a.mfg_catalog = b.mfg_catalog
                and a.total_spend = b.total_spend;
                """)
                
                comp = cur.fetchall()[0][0]
                
                if comp < base:
                    m_list.append(m)
                    print(f'      Keeping facility {m} in {pstr[1:-1]}')
                    details.append((f[0], f[1], m, pstr[1:-1], base, comp, 'KEEP'))
                else:
                    print(f'      Removing facility {m} from {pstr[1:-1]}')
                    details.append((f[0], f[1], m, pstr[1:-1], base, comp, 'REMOVE'))
            else:
                m_list.append(m)
                print(f'      Keeping facility {m} in {pstr[1:-1]}')
                details.append((f[0], f[1], m, pstr[1:-1], base, 0, 'KEEP'))
                
            
                
        fac_group_final.append((m_list, f[1]))
                
    else:
        
        mstr = ', '.join(["'" + x + "'" for x in f[0]])
        pstr = ', '.join(["'" + x + "'" for x in f[1]])
        
        cur.execute(f"""
        select count(*) as matches from
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
             where facility_id in ({mstr}) group by 1, 2) as a
        inner join
            (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
            where facility_id in ({pstr}) group by 1, 2) as b
        on a.date = b.date
        and a.mfg_catalog = b.mfg_catalog
        and a.total_spend = b.total_spend;
        """)
        base = cur.fetchall()[0][0]
        
        for ixx, p in enumerate(f[1]):
            
            p_list.remove(p)
            
            p_list_minus = f[1].copy()
            p_list_minus.remove(p)
            
            if len(p_list_minus) > 0:
                mstr = ', '.join(["'" + x + "'" for x in f[0]])
                pstr = ', '.join(["'" + x + "'" for x in p_list_minus])
                cur.execute(f"""
                select count(*) as matches from
                    (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge 
                     where facility_id in ({mstr}) group by 1, 2) as a
                inner join
                    (select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.m_s_merge
                    where facility_id in ({pstr}) group by 1, 2) as b
                on a.date = b.date
                and a.mfg_catalog = b.mfg_catalog
                and a.total_spend = b.total_spend;
                """)
                
                comp = cur.fetchall()[0][0]
                
                if comp < base:
                    p_list.append(p)
                    print(f'      Keeping facility {p} in {mstr[1:-1]}')
                    details.append((f[0], f[1], mstr[1:-1], p, base, comp, 'KEEP'))
                else:
                    print(f'      Removing facility {p} from {mstr[1:-1]}')
                    details.append((f[0], f[1], mstr[1:-1], p, base, comp, 'REMOVE'))
            else:
                p_list.append(p)
                print(f'      Keeping facility {p} in {mstr[1:-1]}')
                details.append((f[0], f[1], mstr[1:-1], p, base, 0, 'KEEP'))
                
                
                
        fac_group_final.append((f[0], p_list))
    

ix = 0
df_out = pd.DataFrame(columns=['FACILITY_ID_MOA', 'FACILITY_ID_SARCO'])
for f in fac_group_final:
    m = f[0]
    p = f[1]
    if (len(m) == 1) and (len(p) == 1): 
        df_out.loc[ix] = [m[0], p[0]]
        ix = ix + 1
    elif len(m) > 1:
        for mm in m:
            df_out.loc[ix] = [mm, p[0]]
            ix = ix + 1
    elif len(p) > 1:
        for pp in p:
            df_out.loc[ix] = [m[0], pp]
            ix = ix + 1

df_out = df_out.drop_duplicates()
            
df_out.to_csv(r'C:\dev\da.research\personal\rxia\MOA_PETREL_Overlap\overlap_facilities_rx.csv')
            
            
df_details = pd.DataFrame(columns=['FACILITY_IDS_MOA', 'FACILITY_IDS_SARCO', 'MOA_FACILITY_OF_INTEREST', 'SARCO_FACILITY_OF_INTEREST', 
                                   'MATCHES_WITH', 'MATCHES_WITHOUT', 'DECISION'], data=details)         
            
df_details['PCT'] = df_details.apply(lambda x: 100*(x['MATCHES_WITHOUT'])/x['MATCHES_WITH'], axis=1)        


df_orig['FACILITY_ID_SARCO'] = df_orig.apply(lambda x: agg_fac_type(x), axis=1)

df_orig = df_orig.rename(columns={'FACILITY_ID_MOA':'MOA_FACILITY_OF_INTEREST', 'FACILITY_ID_SARCO':'SARCO_FACILITY_OF_INTEREST'})


df = df_details.merge(df_orig, how='left', left_on=['MOA_FACILITY_OF_INTEREST', 'SARCO_FACILITY_OF_INTEREST'],
                      right_on=['MOA_FACILITY_OF_INTEREST', 'SARCO_FACILITY_OF_INTEREST'])


df[['PCT_ALL_SARCO_MATCHES', 'PCT_ALL_MOA_MATCHES', 'AVG_SKUS_PER_QUARTER', 'AVG_QUARTERS_PER_SKU', 'SCORE']] = df[['PCT_ALL_SARCO_MATCHES', 
  'PCT_ALL_MOA_MATCHES', 'AVG_SKUS_PER_QUARTER', 'AVG_QUARTERS_PER_SKU', 'SCORE']].apply(pd.to_numeric)
















            
            