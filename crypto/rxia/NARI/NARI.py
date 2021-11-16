# Author: Redmond Xia
# Date: 02/04/2021
# Description: Looking at the revenues in MOA of NARI - Inari Medical

#region importing libaries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from utilities import util
%load_ext autoreload
%autoreload 2
#endregion libraries

#region SQL connection and data collecting
# category 3 granular
cat3_query_NARI = """WITH A AS ( 
                        SELECT GP_TRANSACTION_DATE, MFG_CATALOG, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                        FROM moa.BUILD_kd_20210204.runner_10_cleaned_base_table
                        WHERE MFG_NAME_LONG ilike '%inari%' OR VENDOR_NAME_LONG ILIKE '%inari%'
                        GROUP BY 1, 2
                    ), B AS (
                        SELECT *
                        FROM research.kdolgin.foundations_NARI_ALPHA_mapping_FINAL_KEEP
                    )
                    SELECT A.GP_TRANSACTION_DATE, CATEGORY_1, CATEGORY_2, CATEGORY_3, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                    FROM A LEFT JOIN B ON A.MFG_CATALOG = B.MFG_CATALOG
                    GROUP BY 1,2,3,4
                    ORDER BY 1;"""
cat3_NARI = util.connect_snwflk(cat3_query_NARI)

# category 2 granular 
cat2_query_NARI = """WITH A AS ( 
                        SELECT GP_TRANSACTION_DATE, MFG_CATALOG, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                        FROM moa.BUILD_kd_20210204.runner_10_cleaned_base_table
                        WHERE MFG_NAME_LONG ilike '%inari%' OR VENDOR_NAME_LONG ILIKE '%inari%'
                        GROUP BY 1, 2
                    ), B AS (
                        SELECT *
                        FROM research.kdolgin.foundations_NARI_ALPHA_mapping_FINAL_KEEP
                    )
                    SELECT A.GP_TRANSACTION_DATE, CATEGORY_1, CATEGORY_2, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                    FROM A LEFT JOIN B ON A.MFG_CATALOG = B.MFG_CATALOG
                    GROUP BY 1,2,3
                    ORDER BY 1;"""
cat2_NARI = util.connect_snwflk(cat2_query_NARI)

# category 1 granular
cat1_query_NARI = """WITH A AS ( // use this to build the 
                        SELECT GP_TRANSACTION_DATE, MFG_CATALOG, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                        FROM moa.BUILD_kd_20210204.runner_10_cleaned_base_table
                        WHERE MFG_NAME_LONG ilike '%inari%' OR VENDOR_NAME_LONG ILIKE '%inari%'
                        GROUP BY 1, 2
                    ), B AS (
                        SELECT *
                        FROM research.kdolgin.foundations_NARI_ALPHA_mapping_FINAL_KEEP
                    )
                    SELECT A.GP_TRANSACTION_DATE, CATEGORY_1, SUM(TOTAL_SPEND) AS TOTAL_SPEND
                    FROM A LEFT JOIN B ON A.MFG_CATALOG = B.MFG_CATALOG
                    GROUP BY 1,2
                    ORDER BY 1;"""
cat1_NARI = util.connect_snwflk(cat1_query_NARI)
#endregion SQL Connection

#region Inari Medical Unaudited quarterly revenue
## Found on the 10Qs, 2019Q4 & 2020Q4 are averaged and approximate
NARI_rev_FY19_20 = {'YEAR_QTR' : ['2019Q1','2019Q2','2019Q3','2019Q4', 
                                  '2020Q1','2020Q2','2020Q3', '2020Q4'], # units are in thousands
                    'REPORTED_REVENUE': [6945, 10072, 14225, 22580, 
                                         26953, 25392, 38715, 48400]}
df_NARI_rev_FY19_20 = pd.DataFrame(data=NARI_rev_FY19_20)
df_NARI_rev_FY19_20['Color'] = 'Actual'
#endregion Inari Medical Unaudited Quarterly Revenues

#region MOA Inari Medical Revenues
cols = ['GP_TRANSACTION_DATE','CATEGORY_1','CATEGORY_2','CATEGORY_3']
# want the dates after 2019 b/c NARI recently IPO from 2020
cat3_rev_NARI = util.NARI_mon2qtr_spend(cat3_NARI[np.logical_and(cat3_NARI["GP_TRANSACTION_DATE"] >= datetime.date(2019,1,1),
                                                                 cat3_NARI["GP_TRANSACTION_DATE"] <= datetime.date(2020,12,31))], 
                                        group=cols, category_1=False)

cat3_product_NARI = cat3_rev_NARI['CATEGORY_3'].unique()
sns.set_palette('dark')

sns.lineplot(data=cat3_rev_NARI[cat3_rev_NARI['CATEGORY_3'] == cat3_product_NARI[0]], 
                x='YEAR_QTR', y='REPORTED_REVENUE', hue='PRODUCT')
sns.lineplot(data=cat3_rev_NARI[cat3_rev_NARI['CATEGORY_3'] == cat3_product_NARI[1]], 
                x='YEAR_QTR', y='REPORTED_REVENUE', hue='PRODUCT')
sns.lineplot(data=cat3_rev_NARI[cat3_rev_NARI['CATEGORY_3'] == cat3_product_NARI[2]], 
                x='YEAR_QTR', y='REPORTED_REVENUE', hue='PRODUCT')
sns.lineplot(data=cat3_rev_NARI[cat3_rev_NARI['CATEGORY_3'] == cat3_product_NARI[3]], 
                x='YEAR_QTR', y='REPORTED_REVENUE', hue='PRODUCT')

cols = cols = ['GP_TRANSACTION_DATE','CATEGORY_1','CATEGORY_2']
cat2_rev_NARI = util.NARI_mon2qtr_spend(cat2_NARI[np.logical_and(cat2_NARI["GP_TRANSACTION_DATE"] >= datetime.date(2019,1,1),
                                                                 cat2_NARI["GP_TRANSACTION_DATE"] <= datetime.date(2020,12,31))], 
                                        group=cols, category_1=False)

sns.lineplot(data=cat2_rev_NARI, x='YEAR_QTR', y='REPORTED_REVENUE', hue='PRODUCT')

# since there is only 1 category, this is already total revenue
cols = cols = ['GP_TRANSACTION_DATE','CATEGORY_1']
cat1_NARI['TOTAL_SPEND'] = cat1_NARI['TOTAL_SPEND'] / 1000 # change the units into thousands
cat1_rev_NARI = util.NARI_mon2qtr_spend(cat1_NARI[np.logical_and(cat1_NARI["GP_TRANSACTION_DATE"] >= datetime.date(2019,1,1),
                                                                 cat1_NARI["GP_TRANSACTION_DATE"] <= datetime.date(2020,12,31))], 
                                        group=cols, category_1=False)

sns.lineplot(data=cat1_rev_NARI, x='YEAR_QTR', y='REPORTED_REVENUE').set_title('Quarterly Revenue')
#endregion MOA Inari Medical Revenues

#region Revenue trend graph of Actual vs. MOA
cat1_rev_NARI['Color'] = 'MOA'
NARI_rev_trend = pd.concat([df_NARI_rev_FY19_20, cat1_rev_NARI[['YEAR_QTR','REPORTED_REVENUE','Color']]], ignore_index=True)
sns.lineplot(data=NARI_rev_trend, x='YEAR_QTR', y='REPORTED_REVENUE', hue='Color')
#endregion Revenue trend graph

#region Comment
# #region Revenue Growth graph
# df_NARI_rev_FY19_20_growth = df_NARI_rev_FY19_20.copy()
# df_NARI_rev_FY19_20_growth.REPORTED_REVENUE = df_NARI_rev_FY19_20_growth.REPORTED_REVENUE / df_NARI_rev_FY19_20_growth.REPORTED_REVENUE[0] - 1

# NARI_rev_qtr_growth = NARI_rev_qtr.copy()
# NARI_rev_qtr_growth['REPORTED_REVENUE'] = NARI_rev_qtr_growth['REPORTED_REVENUE'] / NARI_rev_qtr_growth['REPORTED_REVENUE'][0] - 1

# NARI_rev_trend_growth = pd.concat([df_NARI_rev_FY19_20_growth, NARI_rev_qtr_growth], ignore_index=True)

# # the plot
# sns.lineplot(data=NARI_rev_trend_growth, x='YEAR_QTR', y='REPORTED_REVENUE', hue='Color')
# #endregion Revenue Growth graph

# #region yoy
# NARI_rev_qtr["REPORTED_REVENUE"] / NARI_rev_qtr["REPORTED_REVENUE"].shift(4)
# df_NARI_rev_FY19_20['REPORTED_REVENUE'] / df_NARI_rev_FY19_20['REPORTED_REVENUE'].shift(4)
# #endregion yoy
#endregion comment