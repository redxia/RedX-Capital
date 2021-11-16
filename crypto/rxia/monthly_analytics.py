# Author: Redmond Xia
# Date: 03/17/2021
# Description: Looking at the monthly revenues in MOA and ploting most of them

#region importing libaries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from utilities import util
import statsmodels.api as sm
%load_ext autoreload
%autoreload 2
cutdate='20210722' # 20210429 20210304 20210318
#endregion libraries
sns.set_palette('dark')

# TODO Build a function for regression of moa spend adjustment
# TODO format query.
#region ABMD
"""
Consensus: 4/8/2021 2021Q1 177.5
"""
ABMD_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ABMD_data_20210729 
                where company_name ilike 'ABIOMED Inc' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""
# forecast range 9%-14%
ABMD_Q1_GROWTH = 1.48 # 2017Q2 cut date, in-sample
# ABMD fiscal quarter is two quarters ahead
ABMD_REV_15_20 = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4', # live estimates Q2 2017
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1','2021Q2'], 
                  'SPEND': [57.7, 63.7, 66.7, 75,
                            81.8, 89.6, 89.3, 100.3,
                            108.2, 114.7, 113.6, 130.7,
                            146.2, 151.7, 152.2, 165.7,
                            169.7, 168.3, 164.2, 177.1,
                            164, 126.2, 163.2, 179.6,
                            186.1, 189.1]} # units are in millions
# consensus 165.8, used yoy growth
ABMD = util.GROWTH('ABMD', cutdate, ABMD_QUERY, ABMD_REV_15_20)

#ABMD.spend_growth_rate()
ABMD_RAW, ABMD_SPEND, ABMD_QTR_SPEND, df_ABMD_REV_15_20, ABMD_rev_trend, ABMD_MOA_ACTUAL_PROP, ABMD_PRODUCT_FAMILY, ABMD_PRODUCT_CATEGORY, ABMD_REVENUE_DIVISION  = ABMD.spend_growth_rate()

#product family, category, revenue division
ABMD.plot_categories(fig_dims=(12,8))

#Exploratory
ABMD.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
ABMD.plot_growth_adj()
ABMD_REQ_GROWTH = ABMD.required_growth(two_months=False)
ABMD.LR_plots()
ABMD.adjust_proj_qtr(ABMD_QTR_SPEND['SPEND'].iloc[-1]) 
#ABMD.adjust_proj_qtr(58) # 193.8052836864597 For them to beat they will need to make 
#endregion ABMD

#region ATEC 
"""
Consensus: 4/7/2021 2021Q1 38.9
2021Q2 45.1
"""
ATEC_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ATEC_data_20210729
                where year >= 2017 and company_name = 'ALPHATEC SPINE'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ATEC_Q1_GROWTH = 1.4 # previously 1.4, 1.6-1.65
ATEC_REV_17_20 = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                            '2018Q1','2018Q2','2018Q3','2018Q4', 
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [23.4, 21.9, 20.7, 20.9,
                            19.2, 20.4, 21, 23.1,
                            23, 26.1, 28.1, 31.1,
                            29.1, 28.8, 40.1, 43.1,
                            43.7, 45.1]} # units are in millions

ATEC = util.GROWTH('ATEC', cutdate, ATEC_QUERY, ATEC_REV_17_20)

ATEC_RAW, ATEC_SPEND, ATEC_QTR_SPEND, df_ATEC_REV_17_20, ATEC_rev_trend, ATEC_MOA_ACTUAL_PROP, ATEC_PRODUCT_FAMILY, ATEC_PRODUCT_CATEGORY, ATEC_REVENUE_DIVISION = ATEC.spend_growth_rate()

#Spendings
#product family
ATEC.plot_categories(fig_dims=(14,12))

#exploratory
ATEC.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
ATEC.plot_growth_adj()
ATEC_REQ_GROWTH = ATEC.required_growth(two_months=False, month1_growth=.304551)

ATEC.LR_plots()
#ATEC.adjust_proj_qtr(29.1*ATEC_Q1_GROWTH)
ATEC.adjust_proj_qtr(ATEC_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion ATEC

#region ATRC 
"""
Consensus: 4/7/2021 2021Q1 46
# growth yoy roughly 25%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.ATRC_data_20210429
ATRC_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ATRC_data_20210729
                where year >= 2014 and company_name = 'Atricure Inc'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ATRC_Q1_GROWTH = 1.11 # 
ATRC_REV = {'DATE' : ['2014Q1','2014Q2','2014Q3','2014Q4', 
                      '2015Q1','2015Q2','2015Q3','2015Q4', 
                      '2016Q1','2016Q2','2016Q3','2016Q4', 
                      '2017Q1','2017Q2','2017Q3','2017Q4', 
                      '2018Q1','2018Q2','2018Q3','2018Q4', 
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3','2020Q4',
                      '2021Q1', '2021Q2'], 
                  'SPEND': [18.1, 19.9, 20.1, 22.1,
                            22.9, 25.7, 24.7, 28.9,
                            28.3, 30.9, 30.6, 32.7,
                            33.3, 35.5, 33.4, 36.2,
                            38.4, 40.8, 39.8, 43.1,
                            43, 47.2, 46.1, 49.5,
                            43.5, 33.7, 44.7, 47.4,
                            50.3, 50.4]} # units are in millions

ATRC = util.GROWTH('ATRC', cutdate, ATRC_QUERY, ATRC_REV)

ATRC_RAW, ATRC_SPEND, ATRC_QTR_SPEND, df_ATRC_REV, ATRC_rev_trend, ATRC_MOA_ACTUAL_PROP, ATRC_PRODUCT_FAMILY, ATRC_PRODUCT_CATEGORY, ATRC_REVENUE_DIVISION = ATRC.spend_growth_rate()

#Spendings
#product family
ATRC.plot_categories(fig_dims=(14,12))

#exploratory
ATRC.plot_rev_trend(date_cut='2014Q1',fig_dims=(16,8))

#growth adjustment
ATRC.plot_growth_adj()
ATRC_REQ_GROWTH = ATRC.required_growth(two_months=False, month1_growth=.304551)

ATRC.LR_plots()
ATRC.adjust_proj_qtr(ATRC_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion ATRC

#region BSX_CARDIO 
"""
Consensus: 4/7/2021 2021Q1 518.6
# Guidedance -3% - 3%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.BSX_CARDIO_data_20210429
BSX_CARDIO_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                      from moa_live.stage.BSX_data_20210722
                      where company_name = 'Boston Scientific' and revenue_division ilike '%CARDIO%' and year >= 2013
                      group by 1,2,3,4,5,6,7,8
                      order by 4;"""

BSX_CARDIO_Q1_GROWTH = 1.0 
BSX_CARDIO_REV_13_20 = {'DATE' : ['2013Q1','2013Q2','2013Q3','2013Q4', 
                                  '2014Q1','2014Q2','2014Q3','2014Q4', 
                                  '2015Q1','2015Q2','2015Q3','2015Q4', 
                                  '2016Q1','2016Q2','2016Q3','2016Q4', 
                                  '2017Q1','2017Q2','2017Q3','2017Q4', 
                                  '2018Q1','2018Q2','2018Q3','2018Q4', 
                                  '2019Q1','2019Q2','2019Q3','2019Q4',
                                  '2020Q1','2020Q2','2020Q3','2020Q4',
                                  '2021Q1', '2021Q2'], 
                        'SPEND': [283, 285, 272, 277,
                                  281, 298, 303, 319,
                                  315, 347, 342, 356,
                                  373, 391, 400, 401,
                                  420, 424, 412, 438,
                                  426, 448, 434.5, 453,
                                  452, 473, 525.2, 587,
                                  521, 378, 491, 479,
                                  521, 603.7]} # units are in millions

BSX_CARDIO = util.GROWTH('BSX_CARDIO', cutdate, BSX_CARDIO_QUERY, BSX_CARDIO_REV_13_20)

BSX_CARDIO_RAW, BSX_CARDIO_SPEND, BSX_CARDIO_QTR_SPEND, df_BSX_CARDIO_REV_13_20, BSX_CARDIO_rev_trend, BSX_CARDIO_MOA_ACTUAL_PROP, BSX_CARDIO_PRODUCT_FAMILY, BSX_CARDIO_PRODUCT_CATEGORY, BSX_CARDIO_REVENUE_DIVISION = BSX_CARDIO.spend_growth_rate()

#Spendings
#product family
BSX_CARDIO.plot_categories(fig_dims=(14,12))

#exploratory
BSX_CARDIO.plot_rev_trend(date_cut='2013Q1',fig_dims=(16,8))

#growth adjustment
BSX_CARDIO.plot_growth_adj()
BSX_CARDIO_REQ_GROWTH = BSX_CARDIO.required_growth(two_months=False, month1_growth=.304551)

BSX_CARDIO.LR_plots()
#BSX_CARDIO.adjust_proj_qtr(29.1*BSX_CARDIO_Q1_GROWTH)
BSX_CARDIO.adjust_proj_qtr(BSX_CARDIO_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion BSX_CARDIO

#region BSX_MEDSURG 
"""
Consensus: 4/7/2021 2021Q1 517.7
# Guidedance -3% - 3%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.BSX_MEDSURG_data_20210429
BSX_MEDSURG_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                      from moa_live.stage.BSX_data_20210722
                      where company_name = 'Boston Scientific' and revenue_division ilike '%Medsurg%' and year >= 2017
                      group by 1,2,3,4,5,6,7,8
                      order by 4;"""

BSX_MEDSURG_Q1_GROWTH = 1.0 
BSX_MEDSURG_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                             '2018Q1','2018Q2','2018Q3','2018Q4', 
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2','2020Q3','2020Q4',
                             '2021Q1', '2021Q2'], 
                        'SPEND': [398, 421, 410, 449.5,
                                  428, 458, 461, 498, 
                                  484, 518, 534, 548, 
                                  493, 352, 521, 553,
                                  493, 577.3]} # units are in millions

BSX_MEDSURG = util.GROWTH('BSX_MEDSURG', cutdate, BSX_MEDSURG_QUERY, BSX_MEDSURG_REV)

BSX_MEDSURG_RAW, BSX_MEDSURG_SPEND, BSX_MEDSURG_QTR_SPEND, df_BSX_MEDSURG_REV, BSX_MEDSURG_rev_trend, BSX_MEDSURG_MOA_ACTUAL_PROP, BSX_MEDSURG_PRODUCT_FAMILY, BSX_MEDSURG_PRODUCT_CATEGORY, BSX_MEDSURG_REVENUE_DIVISION = BSX_MEDSURG.spend_growth_rate()

#Spendings
#product family
BSX_MEDSURG.plot_categories(fig_dims=(14,12))

#exploratory
BSX_MEDSURG.plot_rev_trend(date_cut='2013Q1',fig_dims=(16,8))

#growth adjustment
BSX_MEDSURG.plot_growth_adj()
BSX_MEDSURG_REQ_GROWTH = BSX_MEDSURG.required_growth(two_months=False, month1_growth=.304551)

BSX_MEDSURG.LR_plots()
#BSX_MEDSURG.adjust_proj_qtr(29.1*BSX_MEDSURG_Q1_GROWTH)
BSX_MEDSURG.adjust_proj_qtr(BSX_MEDSURG_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion BSX_MEDSURG

#region BSX_NEUROMODULATION 
"""
Consensus: 4/7/2021 2021Q1 149.5
# Guidedance -3% - 3%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.BSX_NEUROMODULATION_data_20210429
BSX_NEUROMODULATION_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                      from moa_live.stage.BSX_data_20210722
                      where company_name = 'Boston Scientific' and revenue_division ilike '%Neuromodulation%' and year >= 2013
                      group by 1,2,3,4,5,6,7,8
                      order by 4;"""

BSX_NEUROMODULATION_Q1_GROWTH = 1.0 
BSX_NEUROMODULATION_REV = {'DATE' : ['2013Q1','2013Q2','2013Q3','2013Q4', 
                                     '2014Q1','2014Q2','2014Q3','2014Q4', 
                                     '2015Q1','2015Q2','2015Q3','2015Q4', 
                                     '2016Q1','2016Q2','2016Q3','2016Q4', 
                                     '2017Q1','2017Q2','2017Q3','2017Q4', 
                                     '2018Q1','2018Q2','2018Q3','2018Q4', 
                                     '2019Q1','2019Q2','2019Q3','2019Q4',
                                     '2020Q1','2020Q2','2020Q3','2020Q4',
                                     '2021Q1', '2021Q2'], 
                        'SPEND': [82, 102, 107, 127,
                                  97, 102, 103, 119,
                                  102, 110, 111, 126, 
                                  105, 115, 117, 137, 
                                  116, 125, 126, 150, 
                                  131, 160, 155, 177, 
                                  144, 160, 183, 208, 
                                  151, 100, 176, 184,
                                  151, 171.8]} # units are in millions

BSX_NEUROMODULATION = util.GROWTH('BSX_NEUROMODULATION', cutdate, BSX_NEUROMODULATION_QUERY, BSX_NEUROMODULATION_REV)

BSX_NEUROMODULATION_RAW, BSX_NEUROMODULATION_SPEND, BSX_NEUROMODULATION_QTR_SPEND, df_BSX_NEUROMODULATION_REV, BSX_NEUROMODULATION_rev_trend, BSX_NEUROMODULATION_MOA_ACTUAL_PROP, BSX_NEUROMODULATION_PRODUCT_FAMILY, BSX_NEUROMODULATION_PRODUCT_CATEGORY, BSX_NEUROMODULATION_REVENUE_DIVISION = BSX_NEUROMODULATION.spend_growth_rate()

#Spendings
#product family
BSX_NEUROMODULATION.plot_categories(fig_dims=(14,12))

#exploratory
BSX_NEUROMODULATION.plot_rev_trend(date_cut='2013Q1',fig_dims=(16,8))

#growth adjustment
BSX_NEUROMODULATION.plot_growth_adj()
BSX_NEUROMODULATION_REQ_GROWTH = BSX_NEUROMODULATION.required_growth(two_months=False, month1_growth=.304551)

BSX_NEUROMODULATION.LR_plots()
#BSX_NEUROMODULATION.adjust_proj_qtr(29.1*BSX_NEUROMODULATION_Q1_GROWTH)
BSX_NEUROMODULATION.adjust_proj_qtr(BSX_NEUROMODULATION_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion BSX_NEUROMODULATION

#region BSX_RN 
"""
Consensus: 4/7/2021 2021Q1 31.5
# Guidedance -3% - 3%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.BSX_RN_data_20210429
BSX_RN_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                      from moa_live.stage.BSX_data_20210722
                      where company_name = 'Boston Scientific' and revenue_division ilike '%Electrophysiology%' and year >= 2014
                      group by 1,2,3,4,5,6,7,8
                      order by 4;"""

BSX_RN_Q1_GROWTH = 1.0 
BSX_RN_REV = {'DATE' : ['2014Q1','2014Q2','2014Q3','2014Q4', 
                        '2015Q1','2015Q2','2015Q3','2015Q4', 
                        '2016Q1','2016Q2','2016Q3','2016Q4', 
                        '2017Q1','2017Q2','2017Q3','2017Q4', 
                        '2018Q1','2018Q2','2018Q3','2018Q4', 
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1','2020Q2','2020Q3','2020Q4',
                        '2021Q1', '2021Q2'], 
                        'SPEND': [30, 29, 32, 32,
                                  32, 31, 34, 34,
                                  31, 32, 33, 32.3,
                                  32, 34, 34, 36, 
                                  35, 39, 37, 39,
                                  36, 39, 38, 36,
                                  32, 22, 33, 32,
                                  30, 36.8]} # units are in millions

BSX_RN = util.GROWTH('BSX_RN', cutdate, BSX_RN_QUERY, BSX_RN_REV)

BSX_RN_RAW, BSX_RN_SPEND, BSX_RN_QTR_SPEND, df_BSX_RN_REV, BSX_RN_rev_trend, BSX_RN_MOA_ACTUAL_PROP, BSX_RN_PRODUCT_FAMILY, BSX_RN_PRODUCT_CATEGORY, BSX_RN_REVENUE_DIVISION = BSX_RN.spend_growth_rate()

#Spendings
#product family
BSX_RN.plot_categories(fig_dims=(14,12))

#exploratory
BSX_RN.plot_rev_trend(date_cut='2013Q1',fig_dims=(16,8))

#growth adjustment
BSX_RN.plot_growth_adj()
BSX_RN_REQ_GROWTH = BSX_RN.required_growth(two_months=False, month1_growth=.304551)

BSX_RN.LR_plots()
#BSX_RN.adjust_proj_qtr(29.1*BSX_RN_Q1_GROWTH)
BSX_RN.adjust_proj_qtr(BSX_RN_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion BSX_RN

#region CNMD 
"""
Consensus: 4/7/2021 2021Q1 118.6
# Guidedance 210-225, -1.86915887% to 5.14%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.CNMD_data_20210429
CNMD_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                      from moa_live.stage.CNMD_data_20210722
                      where company_name ilike 'CONMED' and year >= 2015
                      group by 1,2,3,4,5,6,7,8
                      order by 4;"""

CNMD_Q1_GROWTH = 1.02
CNMD_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                      '2016Q1','2016Q2','2016Q3','2016Q4', 
                      '2017Q1','2017Q2','2017Q3','2017Q4', 
                      '2018Q1','2018Q2','2018Q3','2018Q4', 
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3','2020Q4',
                      '2021Q1', '2021Q2'], 
            'SPEND': [87, 89.1, 87.8, 97.6,
                      96.1, 98.7, 99.2, 105.1,
                      99.4, 100, 98.3, 113.3,
                      106.3, 109.7, 107.5, 125.2,
                      117, 129, 128.2, 142.5,
                      118.8, 87.4, 134.2, 141.6,
                      118.8, 134.3]} # units are in millions

CNMD = util.GROWTH('CNMD', cutdate, CNMD_QUERY, CNMD_REV)

CNMD_RAW, CNMD_SPEND, CNMD_QTR_SPEND, df_CNMD_REV, CNMD_rev_trend, CNMD_MOA_ACTUAL_PROP, CNMD_PRODUCT_FAMILY, CNMD_PRODUCT_CATEGORY, CNMD_REVENUE_DIVISION = CNMD.spend_growth_rate()

#Spendings
#product family
CNMD.plot_categories(fig_dims=(14,12))

#exploratory
CNMD.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
CNMD.plot_growth_adj()
CNMD_REQ_GROWTH = CNMD.required_growth(two_months=False, month1_growth=.304551)

CNMD.LR_plots()
CNMD.adjust_proj_qtr(CNMD_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion CNMD

#region CSII
"""
Consensus: 4/8/2021 2021Q1 60.1, 62.9 total
Our first quarter revenue guidance of $55 million to $58 million represents sequential revenue growth of 29% or 36% compared to Q4
"""
CSII_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.CSII_data_20210729 
                where company_name = 'Cardiovascular Systems' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

CSII_Q1_GROWTH = 1.013 
# CSII fiscal quarter is two quarters ahead
CSII_REV_15_20 = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1','2021Q2'], 
                  'SPEND': [43.9, 44.8, 43.9, 39.2,
                            44.5, 48.5, 49.8, 50,
                            52.1, 52.9, 49.7, 52.6,
                            54.7, 57.7, 54.92, 58.7,
                            60.9, 65.7, 61.3, 66,
                            58.1, 40.5, 58.8, 61.9,
                            59.6, 65.1]} # units are in millions
CSII = util.GROWTH('CSII', cutdate, CSII_QUERY, CSII_REV_15_20)
# consensus 59.9 right on the money.
#CSII.spend_growth_rate()

CSII_RAW, CSII_SPEND, CSII_QTR_SPEND, df_CSII_REV_15_20, CSII_rev_trend, CSII_MOA_ACTUAL_PROP, CSII_PRODUCT_FAMILY, CSII_PRODUCT_CATEGORY, CSII_REVENUE_DIVISION  = CSII.spend_growth_rate()

#CSII.get_members()
#product family, category, revenue division
CSII.plot_categories(fig_dims=(12,8))

#Exploratory
# 24.5848207
CSII.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
CSII.plot_growth_adj()
CSII_REQ_GROWTH = CSII.required_growth(two_months=False)
CSII.LR_plots()
CSII.adjust_proj_qtr(CSII_QTR_SPEND['SPEND'].iloc[-1])
CSII.adjust_proj_qtr(62.68)
#endregion CSII

#region EW
#likely to miss
"""
Consensus
"""
EW_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.EW_data_20210722 
                where company_name ilike 'Edwards Lifesciences' and revenue_division ilike 'Transcatheter Heart Valve Therapies'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

EW_Q1_GROWTH = 1.08
# EW fiscal quarter is two quarters ahead
EW_REV_15_20 = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [120.8, 138.7, 157.1, 176.4,
                  	        203.7, 231.4, 245.4, 254.9,
                            285.7, 301.9, 297.7, 312.9, 
                            331.4, 350.1, 343.8, 357.2,
                            368.1, 418, 448.2, 495.3,
                            480.7, 364.9, 471.7, 476.4,
                            480.7, 538.5]} # units are in millions
# consensus 165.8, used yoy growth
EW = util.GROWTH('EW', cutdate, EW_QUERY, EW_REV_15_20)

#EW.spend_growth_rate()
EW_RAW, EW_SPEND, EW_QTR_SPEND, df_EW_REV_15_20, EW_rev_trend, EW_MOA_ACTUAL_PROP, EW_PRODUCT_FAMILY, EW_PRODUCT_CATEGORY, EW_REVENUE_DIVISION  = EW.spend_growth_rate()

#product family, category, revenue division
EW.plot_categories(fig_dims=(12,8))

#Exploratory
EW.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
EW.plot_growth_adj()
EW_REQ_GROWTH = EW.required_growth(two_months=False)
EW.LR_plots()
EW.adjust_proj_qtr(EW_QTR_SPEND['SPEND'].iloc[-1])
#endregion EW

#region GMED
"""
Consensus: 
2021Q1 165.8 4_12_21, 161.7 4/27/2021
Though we expect our first quarter sales to be impacted by COVID, we are optimistic that Q1 will finish slightly ahead of our first quarter in 2020
"""
GMED_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.GMED_data_20210729 
                where company_name = 'GLOBUS MEDICAL' and year >= 2014
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

GMED_Q1_GROWTH = 1.08
# GMED fiscal quarter is two quarters ahead
GMED_REV_15_20 = {'DATE' : ['2014Q1','2014Q2','2014Q3','2014Q4',
                            '2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [101.7, 101.6, 106.6, 117.2,
                            120, 121.5, 125.7, 131.1,
                            127.6, 124.7, 120.5, 127.5,
                            129.7, 126.3, 125.9, 148,
                            145.6, 145.4, 139.1, 163.8,
                            147.5, 160, 162.7, 177.5,
                            158.4, 125.2, 182.1, 198.7,
                            193.3, 191.2]} # units are in millions
# consensus 165.8, used yoy growth
GMED = util.GROWTH('GMED', cutdate, GMED_QUERY, GMED_REV_15_20)

#GMED.spend_growth_rate()
GMED_RAW, GMED_SPEND, GMED_QTR_SPEND, df_GMED_REV_15_20, GMED_rev_trend, GMED_MOA_ACTUAL_PROP, GMED_PRODUCT_FAMILY, GMED_PRODUCT_CATEGORY, GMED_REVENUE_DIVISION  = GMED.spend_growth_rate()

#product family, category, revenue division
GMED.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
GMED.plot_rev_trend(date_cut='2014Q1',fig_dims=(12,8))

#growth adjustment
GMED.plot_growth_adj()
GMED_REQ_GROWTH = GMED.required_growth(two_months=False)
GMED.LR_plots()
GMED.adjust_proj_qtr(GMED_QTR_SPEND['SPEND'].iloc[-1])
GMED.adjust_proj_qtr(170.92)
#endregion GMED

#region INSP
"""
Consensus: 4/8/2021 2021Q1 33.4, 34 4/27/2021
. Therefore, we are providing full year 2021 revenue guidance of $183 million to $188 million, which would represent an increase of 59% to 63% over a full year 2020 revenue of $115.4 million.
"""
INSP_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.INSP_data_20210729 
                where company_name ilike 'INSPIRE MEDICAL SYSTEMS' and year >= 2016
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

INSP_Q1_GROWTH = 1.75 #2 # 1.7
INSP_REV_18_20 = {'DATE' : ['2016Q1','2016Q2','2016Q3','2016Q4', 
                            '2017Q1','2017Q2','2017Q3','2017Q4', 
                            '2018Q1','2018Q2','2018Q3','2018Q4', 
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [2.7, 3.2, 3.8, 4.1,
                            4.5, 4.9, 6.5, 8.4,
                            8.7, 9.5, 11.3, 14.8,
                            14.4, 15.8, 18.6, 24.9,
                            19.3, 11, 33.1, 42.7,
                            37.8, 40.5]} # units are in millions

INSP = util.GROWTH('INSP', cutdate, INSP_QUERY, INSP_REV_18_20)

#INSP.spend_growth_rate()

INSP_RAW, INSP_SPEND, INSP_QTR_SPEND, df_INSP_REV_18_20, INSP_rev_trend, INSP_MOA_ACTUAL_PROP, INSP_PRODUCT_FAMILY, INSP_PRODUCT_CATEGORY, INSP_REVENUE_DIVISION  = INSP.spend_growth_rate()

#product family, category, revenue division
INSP.plot_categories(fig_dims=(12,8))

#Exploratory
# 1.3 sequential growth max
# 1.1
INSP.plot_rev_trend(date_cut='2016Q1',fig_dims=(12,8))

#growth adjustment
INSP.plot_growth_adj()
INSP_REQ_GROWTH = INSP.required_growth(two_months=False, month1_growth=-0.125)
INSP.LR_plots()
#INSP.adjust_proj_qtr(19.3*INSP_Q1_GROWTH)
INSP.adjust_proj_qtr(INSP_QTR_SPEND['SPEND'].iloc[-1])
INSP.adjust_proj_qtr(36.22)
#endregion INSP

#region ISRG
"""
Consensus: 437.5
"""
ISRG_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ISRG_data_20210715 
                where company_name ilike 'Intuitive Surgical' and year >= 2013
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ISRG_Q1_GROWTH = 1.1789385
# ISRG fiscal quarter is two quarters ahead
ISRG_REV_15_20 = {'DATE' : ['2013Q1','2013Q2','2013Q3','2013Q4',
                            '2014Q1','2014Q2','2014Q3','2014Q4',
                            '2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [213.5, 218.1, 195.2, 218.1,
                            198.3, 206.1, 214.8, 219.2, 
                            212.8, 231, 237.8, 255.2, 
                            246.8, 262.2, 270.4, 297.9,
                            287.6, 309.4, 312.7, 353.4,
                            337.6, 360.3, 368.1, 419.2,
                            407.4, 428.6, 450.7, 503.7,
                            444.4, 315.6, 467.2, 557.9,
                            500.8, 489.7]} # units are in millions

ISRG = util.GROWTH('ISRG', cutdate, ISRG_QUERY, ISRG_REV_15_20)

#ISRG.spend_growth_rate()
ISRG_RAW, ISRG_SPEND, ISRG_QTR_SPEND, df_ISRG_REV_15_20, ISRG_rev_trend, ISRG_MOA_ACTUAL_PROP, ISRG_PRODUCT_FAMILY, ISRG_PRODUCT_CATEGORY, ISRG_REVENUE_DIVISION  = ISRG.spend_growth_rate()

#product family, category, revenue division
ISRG.plot_categories(fig_dims=(12,8))

#Exploratory
ISRG.plot_rev_trend(date_cut='2013Q1',fig_dims=(12,8))

#growth adjustment
ISRG.plot_growth_adj()
ISRG_REQ_GROWTH = ISRG.required_growth(two_months=False)
ISRG.LR_plots()
ISRG.adjust_proj_qtr(ISRG_QTR_SPEND['SPEND'].iloc[-1])
#endregion ISRG

#region KIDS
"""
Consensus: 437.5
"""
KIDS_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(total_spend)/1000000 as spend
                from moa_live.stage.KIDS_data_20210729
                where company_name ilike '%ORTHOPEDIATRICS%' and year >= 2013
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

KIDS_Q1_GROWTH = 1.1789385
# KIDS fiscal quarter is two quarters ahead
KIDS_REV = {'DATE' : [
                            '2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [4.6, 6.4, 7.2, 6.7,
                            6.1, 7.6, 7.9, 7.3, 
                            7.3, 9.2, 9.6, 8.8, 
                            8.7, 11.5, 12.4, 10.9,
                            10.3, 13.8, 16.8, 14.2,
                            13.4, 12.1, 19.6, 17.9,
                            16.8, 20.3]} # units are in millions

KIDS = util.GROWTH('KIDS', cutdate, KIDS_QUERY, KIDS_REV)

#KIDS.spend_growth_rate()
KIDS_RAW, KIDS_SPEND, KIDS_QTR_SPEND, df_KIDS_REV_15_20, KIDS_rev_trend, KIDS_MOA_ACTUAL_PROP, KIDS_PRODUCT_FAMILY, KIDS_PRODUCT_CATEGORY, KIDS_REVENUE_DIVISION  = KIDS.spend_growth_rate()

#product family, category, revenue division
KIDS.plot_categories(fig_dims=(12,8))

#Exploratory
KIDS.plot_rev_trend(date_cut='2013Q1',fig_dims=(12,8))

#growth adjustment
KIDS.plot_growth_adj()
KIDS_REQ_GROWTH = KIDS.required_growth(two_months=False)
KIDS.LR_plots()
KIDS.adjust_proj_qtr(KIDS_QTR_SPEND['SPEND'].iloc[-1])
#endregion KIDS

#region LIVN_CARDIO 
"""
Consensus: 4/7/2021 2021Q1 35.6
# Guidedance 8% - 13%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.LIVN_CARDIO_data_20210429
LIVN_CARDIO_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.LIVN_data_20210722
                         where company_name = 'LIVANOVA' and revenue_division ilike '%CARDIOVASCULAR%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

LIVN_CARDIO_Q1_GROWTH = 1.09 
LIVN_CARDIO_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                             '2016Q1','2016Q2','2016Q3','2016Q4', 
                             '2017Q1','2017Q2','2017Q3','2017Q4', 
                             '2018Q1','2018Q2','2018Q3','2018Q4', 
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2','2020Q3','2020Q4',
                             '2021Q1', '2021Q2'], 
                        'SPEND': [39.6, 49.7, 45.9, 51.7,
                                  41, 46.3, 46.8, 48.1, 
                                  38.3, 45.9, 45, 48.7, 
                                  44.9, 48.2, 46.5, 46.1, 
                                  43.5, 46.1, 43.7, 47.1, 
                                  40.3, 28.30, 36.6, 39.8,
                                  40.3, 36.7]} # units are in millions

LIVN_CARDIO = util.GROWTH('LIVN_CARDIO', cutdate, LIVN_CARDIO_QUERY, LIVN_CARDIO_REV)

LIVN_CARDIO_RAW, LIVN_CARDIO_SPEND, LIVN_CARDIO_QTR_SPEND, df_LIVN_CARDIO_REV, LIVN_CARDIO_rev_trend, LIVN_CARDIO_MOA_ACTUAL_PROP, LIVN_CARDIO_PRODUCT_FAMILY, LIVN_CARDIO_PRODUCT_CATEGORY, LIVN_CARDIO_REVENUE_DIVISION = LIVN_CARDIO.spend_growth_rate()

#Spendings
#product family
LIVN_CARDIO.plot_categories(fig_dims=(14,12))

#exploratory
LIVN_CARDIO.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
LIVN_CARDIO.plot_growth_adj()
#LIVN_CARDIO_REQ_GROWTH = LIVN_CARDIO.required_growth(two_months=False, month1_growth=.304551)

LIVN_CARDIO.LR_plots()
#LIVN_CARDIO.adjust_proj_qtr(29.1*LIVN_CARDIO_Q1_GROWTH)
LIVN_CARDIO.adjust_proj_qtr(LIVN_CARDIO_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion LIVN_CARDIO

#region LIVN_NEUROMOD 
"""
Consensus: 4/7/2021 2021Q1 71.2
# Guidedance 8% - 13%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.LIVN_NEUROMOD_data_20210429
LIVN_NEUROMOD_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.LIVN_data_20210722
                         where company_name = 'LIVANOVA' and revenue_division ilike '%NEUROMODULATION%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

LIVN_NEUROMOD_Q1_GROWTH = 1.09 
LIVN_NEUROMOD_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                               '2016Q1','2016Q2','2016Q3','2016Q4', 
                               '2017Q1','2017Q2','2017Q3','2017Q4', 
                               '2018Q1','2018Q2','2018Q3','2018Q4', 
                               '2019Q1','2019Q2','2019Q3','2019Q4',
                               '2020Q1','2020Q2','2020Q3','2020Q4',
                               '2021Q1', '2021Q2'], 
                        'SPEND': [57.5, 63.6, 70.9, 76.8,
                        	      70.2, 75.8, 74.9, 77.6, 
                                  73.7, 81.4, 76.3, 85.6, 
                                  78, 89.4, 87.2, 94.3, 
                                  76.4, 80.2, 87.6, 88, 
                                  71.9, 43.1, 77.2, 84.5,
                                  71.9, 81]} # units are in millions

LIVN_NEUROMOD = util.GROWTH('LIVN_NEUROMOD', cutdate, LIVN_NEUROMOD_QUERY, LIVN_NEUROMOD_REV)

LIVN_NEUROMOD_RAW, LIVN_NEUROMOD_SPEND, LIVN_NEUROMOD_QTR_SPEND, df_LIVN_NEUROMOD_REV, LIVN_NEUROMOD_rev_trend, LIVN_NEUROMOD_MOA_ACTUAL_PROP, LIVN_NEUROMOD_PRODUCT_FAMILY, LIVN_NEUROMOD_PRODUCT_CATEGORY, LIVN_NEUROMOD_REVENUE_DIVISION = LIVN_NEUROMOD.spend_growth_rate()

#Spendings
#product family
LIVN_NEUROMOD.plot_categories(fig_dims=(14,12))

#exploratory
LIVN_NEUROMOD.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
LIVN_NEUROMOD.plot_growth_adj()
#LIVN_NEUROMOD_REQ_GROWTH = LIVN_NEUROMOD.required_growth(two_months=False, month1_growth=.304551)

LIVN_NEUROMOD.LR_plots()
#LIVN_NEUROMOD.adjust_proj_qtr(29.1*LIVN_NEUROMOD_Q1_GROWTH)
LIVN_NEUROMOD.adjust_proj_qtr(LIVN_NEUROMOD_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion LIVN_NEUROMOD

#region LIVN_ACS 
"""
Consensus: 4/7/2021 2021Q1 12.1
# Guidedance 8% - 13%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.LIVN_ACS_data_20210429
LIVN_ACS_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.LIVN_data_20210722
                         where company_name = 'LIVANOVA' and revenue_division ilike '%ADVANCED CIRCULATORY SUPPORT%' and year >= 2018
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

LIVN_ACS_Q1_GROWTH = 1.09 
LIVN_ACS_REV = {'DATE' : ['2018Q2','2018Q3','2018Q4', 
                          '2019Q1','2019Q2','2019Q3','2019Q4',
                          '2020Q1','2020Q2','2020Q3','2020Q4',
                          '2021Q1', '2021Q2'], 
                        'SPEND': [5.5, 5.9, 7.2, 
                                  8, 7.9, 6.3, 8.5,
                                  10.1, 5.7, 12.3, 13,
                                  10.1, 12.9]} # units are in millions

LIVN_ACS = util.GROWTH('LIVN_ACS', cutdate, LIVN_ACS_QUERY, LIVN_ACS_REV)

LIVN_ACS_RAW, LIVN_ACS_SPEND, LIVN_ACS_QTR_SPEND, df_LIVN_ACS_REV, LIVN_ACS_rev_trend, LIVN_ACS_MOA_ACTUAL_PROP, LIVN_ACS_PRODUCT_FAMILY, LIVN_ACS_PRODUCT_CATEGORY, LIVN_ACS_REVENUE_DIVISION = LIVN_ACS.spend_growth_rate()

#Spendings
#product family
LIVN_ACS.plot_categories(fig_dims=(14,12))

#exploratory
LIVN_ACS.plot_rev_trend(date_cut='2018Q2',fig_dims=(16,8))

#growth adjustment
LIVN_ACS.plot_growth_adj()
#LIVN_ACS_REQ_GROWTH = LIVN_ACS.required_growth(two_months=False, month1_growth=.304551)

LIVN_ACS.LR_plots()
#LIVN_ACS.adjust_proj_qtr(29.1*LIVN_ACS_Q1_GROWTH)
LIVN_ACS.adjust_proj_qtr(LIVN_ACS_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion LIVN_ACS

#region LUNG
"""
Consensus: 437.5
"""
LUNG_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(total_spend)/1000000 as spend
                from moa_live.stage.LUNG_data_20210729
                where company_name ilike '%PULMONX%' and year >= 2018
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

LUNG_Q1_GROWTH = 1.1789385
# LUNG fiscal quarter is two quarters ahead
LUNG_REV = {'DATE' : ['2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3','2020Q4',
                      '2021Q1', '2021Q2'], 
                  'SPEND': [0.1, 0.5,
                            0.8, 1.8, 3.4, 4.7,
                            4.5, 1.5, 5.3, 4.9,
                            4.3, 5.6]} # units are in millions

LUNG = util.GROWTH('LUNG', cutdate, LUNG_QUERY, LUNG_REV)

#LUNG.spend_growth_rate()
LUNG_RAW, LUNG_SPEND, LUNG_QTR_SPEND, df_LUNG_REV_15_20, LUNG_rev_trend, LUNG_MOA_ACTUAL_PROP, LUNG_PRODUCT_FAMILY, LUNG_PRODUCT_CATEGORY, LUNG_REVENUE_DIVISION  = LUNG.spend_growth_rate()

#product family, category, revenue division
LUNG.plot_categories(fig_dims=(12,8))

#Exploratory
LUNG.plot_rev_trend(date_cut='2018Q3',fig_dims=(12,8))

#growth adjustment
LUNG.plot_growth_adj()
LUNG_REQ_GROWTH = LUNG.required_growth(two_months=False)
LUNG.LR_plots()
LUNG.adjust_proj_qtr(LUNG_QTR_SPEND['SPEND'].iloc[-1])
#endregion LUNG

#region MMSI_CARDIO 
"""
Consensus: 4/7/2021 2021Q1 131.72
# Guidedance -5%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.MMSI_CARDIO_data_20210429
MMSI_CARDIO_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.MMSI_data_20210722
                         where company_name ilike '%Merit%' and revenue_division ilike '%Cardiovascular%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

MMSI_CARDIO_Q1_GROWTH = .95
MMSI_CARDIO_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                             '2016Q1','2016Q2','2016Q3','2016Q4',
                             '2017Q1','2017Q2','2017Q3','2017Q4',
                             '2018Q1','2018Q2','2018Q3','2018Q4',
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2','2020Q3','2020Q4',
                             '2021Q1', '2021Q2'], 
                    'SPEND': [74.86, 79.67, 78.57, 79.44,
                              79.53, 87.32, 90.36, 90.95,
                              96.02, 101.39, 96.70, 100.23,
                              103.14, 116.32, 116.88, 127.88,
                              130.49, 136.11, 135.67, 140.84,
                              133.48, 112.30, 136.02, 140.41,
                              133.50, 134.1]} # units are in millions

MMSI_CARDIO = util.GROWTH('MMSI_CARDIO', cutdate, MMSI_CARDIO_QUERY, MMSI_CARDIO_REV)

MMSI_CARDIO_RAW, MMSI_CARDIO_SPEND, MMSI_CARDIO_QTR_SPEND, df_MMSI_CARDIO_REV, MMSI_CARDIO_rev_trend, MMSI_CARDIO_MOA_ACTUAL_PROP, MMSI_CARDIO_PRODUCT_FAMILY, MMSI_CARDIO_PRODUCT_CATEGORY, MMSI_CARDIO_REVENUE_DIVISION = MMSI_CARDIO.spend_growth_rate()

#Spendings
#product family
MMSI_CARDIO.plot_categories(fig_dims=(14,12))

#exploratory
MMSI_CARDIO.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
MMSI_CARDIO.plot_growth_adj()
#MMSI_CARDIO_REQ_GROWTH = MMSI_CARDIO.required_growth(two_months=False, month1_growth=.304551)

MMSI_CARDIO.LR_plots()
#MMSI_CARDIO.adjust_proj_qtr(133.48*MMSI_CARDIO_Q1_GROWTH)
MMSI_CARDIO.adjust_proj_qtr(MMSI_CARDIO_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion MMSI_CARDIO

#region MMSI_END 
"""
Consensus: 4/7/2021 2021Q1 7.3
# Guidedance -5%
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.MMSI_END_data_20210429
MMSI_END_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.MMSI_data_20210722
                         where company_name ilike '%Merit%' and revenue_division ilike '%Endoscopy%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

MMSI_END_Q1_GROWTH = .95
MMSI_END_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                             '2016Q1','2016Q2','2016Q3','2016Q4',
                             '2017Q1','2017Q2','2017Q3','2017Q4',
                             '2018Q1','2018Q2','2018Q3','2018Q4',
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2','2020Q3','2020Q4',
                             '2021Q1', '2021Q2'], 
                    'SPEND': [4.8, 5.3, 5.1, 5.7,
                              5.5, 5.5, 6.5, 6.1,
                              6.3, 6.9, 6.6, 7.4,
                              7.2, 8.4, 9.5, 8.2,
                              7.9, 8.9, 8.6, 8.5,
                              8, 6.2, 7.6, 7.9,
                              7.9, 7.3]} # units are in millions

MMSI_END = util.GROWTH('MMSI_END', cutdate, MMSI_END_QUERY, MMSI_END_REV)

MMSI_END_RAW, MMSI_END_SPEND, MMSI_END_QTR_SPEND, df_MMSI_END_REV, MMSI_END_rev_trend, MMSI_END_MOA_ACTUAL_PROP, MMSI_END_PRODUCT_FAMILY, MMSI_END_PRODUCT_CATEGORY, MMSI_END_REVENUE_DIVISION = MMSI_END.spend_growth_rate()

#Spendings
#product family
MMSI_END.plot_categories(fig_dims=(14,12))

#exploratory
MMSI_END.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
MMSI_END.plot_growth_adj()
#MMSI_END_REQ_GROWTH = MMSI_END.required_growth(two_months=False, month1_growth=.304551)

MMSI_END.LR_plots()
#MMSI_END.adjust_proj_qtr(8*MMSI_END_Q1_GROWTH)
MMSI_END.adjust_proj_qtr(MMSI_END_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion MMSI_END

#region NARI
"""
Consensus: 4/8/2021 2021Q1 55.3
Sure, David. Thanks for that question. As you mentioned, the Q1 guidance would be about sort of a low double-digit sequential improvement compared to Q4. So that's something that we really feel comfortable and confident in.
"""
NARI_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.NARI_ALPHA_data_20210805 
                where company_name = 'INARI MEDICAL'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

NARI_Q1_GROWTH = 1.25
NARI_REV = {'DATE' : ['2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [6.9, 10.1, 14.2, 19.9,
                            27, 25.4, 38.7, 48.6,
                            57.4, 59.8]} # units are in millions 1.25 upper estimate, 15% lower.

NARI = util.GROWTH('NARI_ALPHA', cutdate, NARI_QUERY, NARI_REV)

NARI_RAW, NARI_SPEND, NARI_QTR_SPEND, df_NARI_REV, NARI_rev_trend, NARI_MOA_ACTUAL_PROP, NARI_PRODUCT_FAMILY, NARI_PRODUCT_CATEGORY, NARI_REVENUE_DIVISION  = NARI.spend_growth_rate()

#product family, category, revenue division
NARI.plot_categories(fig_dims=(12,8))

#exploratory
NARI.plot_rev_trend(date_cut='2019Q1',fig_dims=(12,8))

#growth adjustment
NARI.plot_growth_adj()
NARI_REQ_GROWTH = NARI.required_growth(two_months=False, month1_growth=.471446)
NARI.LR_plots()
#NARI.adjust_proj_qtr(48.6*NARI_Q1_GROWTH)
NARI.adjust_proj_qtr(NARI_QTR_SPEND['SPEND'].iloc[-1])
NARI.adjust_proj_qtr(57.12)
#growth adjustment
#endregion NARI

#region NUVA
"""
Consensus: 137.6 4/27/2021
As far as Q1 and kind of the first half of 2021, I expect to continue to see increasing levels of strength internationally, but I expect to see also see recovery in the U.S. and again, you also got to think about the U.S. business.
So on a full year the numbers look pretty good. What we are concerned about is the first quarter because of the continuing impact from COVID to a lesser extent, some of the weather challenges we've had in the U.S.
So as we're thinking about the first quarter, we think we'll be roughly plus or minus flat with what we did in the first quarter last year, that number was 260 million.
"""
NUVA_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.NUVA_data_20210722 
                where company_name = 'NUVASIVE' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

NUVA_Q1_GROWTH = .976085455595667
# NUVA fiscal quarter is two quarters ahead
NUVA_REV_15_20 = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [110.2, 116.5, 116.2, 126.4,
                            126.8, 137.8, 133.2, 153.8,
                            140.6, 142.8, 136.5, 149.8,
                            141.5, 150.8, 146.1, 156.6,
                            147.8, 160.2, 160, 168.9,
                            138.5, 113.8, 161.2, 155.2,
                            145.2, 154.3]} # units are in millions
# consensus 220
NUVA = util.GROWTH('NUVA', cutdate, NUVA_QUERY, NUVA_REV_15_20)

#NUVA.spend_growth_rate()
NUVA_RAW, NUVA_SPEND, NUVA_QTR_SPEND, df_NUVA_REV_15_20, NUVA_rev_trend, NUVA_MOA_ACTUAL_PROP, NUVA_PRODUCT_FAMILY, NUVA_PRODUCT_CATEGORY, NUVA_REVENUE_DIVISION  = NUVA.spend_growth_rate()

#product family, category, revenue division
NUVA.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
NUVA.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
NUVA.plot_growth_adj()
NUVA_REQ_GROWTH = NUVA.required_growth(two_months=False)
NUVA.LR_plots()
NUVA.adjust_proj_qtr(NUVA_QTR_SPEND['SPEND'].iloc[-1])
NUVA.adjust_proj_qtr(136.61)
#endregion NUVA

#region PEN_NEURO
"""
Consensus: 40.1 4/27/2021
We are introducing revenue guidance for full-year 2021 in the range of $675 million to $685 million, which represents 20% to 22% growth over full-year 2020 revenue of $516.4 million.
On the neuro piece of the guidance, do you have neuro growing over 10% implicit in that guidance? I'm just trying to get a sense for a rough breakdown of how much you think neuro will grow and how much that contributes to that 20% to 22% overall growth you're forecasting.
"""
PEN_NEURO_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.PEN_data_20210805
                where company_name ilike 'Penumbra' and revenue_division ilike '%Neuro%' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

PEN_NEURO_Q1_GROWTH = 1.1
# PEN_NEURO fiscal quarter is two quarters ahead
PEN_NEURO_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                                '2016Q1','2016Q2','2016Q3','2016Q4',
                                '2017Q1','2017Q2','2017Q3','2017Q4',
                                '2018Q1','2018Q2','2018Q3','2018Q4',
                                '2019Q1','2019Q2','2019Q3','2019Q4',
                                '2020Q1','2020Q2','2020Q3','2020Q4',
                                '2021Q1', '2021Q2'], 
                  'SPEND': [18.9, 20, 20, 18.9,
                            23.6, 25.1, 25.9, 28.1,
                            28, 31.9, 33.5, 37.1,
                            39.7, 41.6, 41.1, 43.7,
                            45.4, 44.6, 44.7, 46.2,
                            44.4, 38.6, 44.3, 40,
                            43.4, 44]} # units are in millions
# consensus 220
PEN_NEURO = util.GROWTH('PEN_NEURO', cutdate, PEN_NEURO_QUERY, PEN_NEURO_REV)

#PEN_NEURO.spend_growth_rate()
PEN_NEURO_RAW, PEN_NEURO_SPEND, PEN_NEURO_QTR_SPEND, df_PEN_NEURO_REV, PEN_NEURO_rev_trend, PEN_NEURO_MOA_ACTUAL_PROP, PEN_NEURO_PRODUCT_FAMILY, PEN_NEURO_PRODUCT_CATEGORY, PEN_NEURO_REVENUE_DIVISION  = PEN_NEURO.spend_growth_rate()

#product family, category, revenue division
PEN_NEURO.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
PEN_NEURO.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
PEN_NEURO.plot_growth_adj()
PEN_NEURO_REQ_GROWTH = PEN_NEURO.required_growth(two_months=False)
PEN_NEURO.LR_plots()
PEN_NEURO.adjust_proj_qtr(PEN_NEURO_QTR_SPEND['SPEND'].iloc[-1])
PEN_NEURO.adjust_proj_qtr(42.78)
#endregion PEN_NEURO

#region PEN_PERI
"""
Consensus: 71.7 4/27/2021
We are introducing revenue guidance for full-year 2021 in the range of $675 million to $685 million, which represents 20% to 22% growth over full-year 2020 revenue of $516.4 million.
On the neuro piece of the guidance, do you have neuro growing over 10% implicit in that guidance? I'm just trying to get a sense for a rough breakdown of how much you think neuro will grow and how much that contributes to that 20% to 22% overall growth you're forecasting.
"""
PEN_PERI_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.PEN_data_20210805 
                where company_name ilike 'Penumbra' and revenue_division ilike '%peri%' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

PEN_PERI_Q1_GROWTH = 1
# PEN_PERI fiscal quarter is two quarters ahead
PEN_PERI_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                                '2016Q1','2016Q2','2016Q3','2016Q4',
                                '2017Q1','2017Q2','2017Q3','2017Q4',
                                '2018Q1','2018Q2','2018Q3','2018Q4',
                                '2019Q1','2019Q2','2019Q3','2019Q4',
                                '2020Q1','2020Q2','2020Q3','2020Q4',
                                '2021Q1', '2021Q2'], 
                  'SPEND': [7.1, 7.6, 13.5, 14.4,
                            15.4, 18.3, 18.2, 20.1,
                            20.2, 21.1, 21.8, 24.2,
                            25.7, 29.2, 31.4, 36.1,
                            36.5, 41.8, 45.6, 49.9,
                            50.7, 39.4, 65.4, 76.8,
                            75.9, 76.2]} # units are in millions
# consensus 220
PEN_PERI = util.GROWTH('PEN_PERI', cutdate, PEN_PERI_QUERY, PEN_PERI_REV)

#PEN_PERI.spend_growth_rate()
PEN_PERI_RAW, PEN_PERI_SPEND, PEN_PERI_QTR_SPEND, df_PEN_PERI_REV, PEN_PERI_rev_trend, PEN_PERI_MOA_ACTUAL_PROP, PEN_PERI_PRODUCT_FAMILY, PEN_PERI_PRODUCT_CATEGORY, PEN_PERI_REVENUE_DIVISION  = PEN_PERI.spend_growth_rate()

#product family, category, revenue division
PEN_PERI.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
PEN_PERI.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
PEN_PERI.plot_growth_adj()
PEN_PERI_REQ_GROWTH = PEN_PERI.required_growth(two_months=False)
PEN_PERI.LR_plots()
PEN_PERI.adjust_proj_qtr(PEN_PERI_QTR_SPEND['SPEND'].iloc[-1])
PEN_PERI.adjust_proj_qtr(80)
#endregion PEN_PERI

#region SIBN
"""
Consensus: 4/27/2021 2021Q1 17.4
Certainly a good portion of that difference is related to the first quarter. And so, if you think about what I said about January and February, we actually had a decline in the business in January, and then a return to growth in February. And we see a very strong March, but not to the levels of making up for what happened in January and February. So, lower numbers [than Q1].
Based on these assumptions, we expect total revenue of $92 million to $94 million, representing growth of 25% to 28%, compared to full-year 2020
So, what appears to be happening is that, like I said, you saw this trough in January, a return to growth in February, and then a very strong start to March. And if you take all of that information and you link it to our guidance, you know, what we're saying is, we don't think that March is going to make up for what we saw in January and February, but we're starting to see the rescheduling of those cases that were canceled in Q4 as well as those cases that were cancelled in January and February.
"""
SIBN_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.SIBN_data_20210729 
                where company_name = 'Si-Bone Inc' and year >= 2016
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

SIBN_Q1_GROWTH = 1.2
SIBN_REV_17_20 = {'DATE' : ['2016Q1','2016Q2','2016Q3','2016Q4', 
                            '2017Q1','2017Q2','2017Q3','2017Q4', 
                            '2018Q1','2018Q2','2018Q3','2018Q4', 
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1','2021Q2'], 
                  'SPEND': [8.8, 9.6, 9.5, 10.9,
                            10.3, 10.1, 10.5, 12.4,
                            11.3, 12.2, 12.2, 14.5,
                            13.5, 15, 14.9, 18.5,
                            15.3, 13.2, 18.9, 20.7,
                            18.8, 20.3]} # units are in millions

SIBN = util.GROWTH('SIBN', cutdate, SIBN_QUERY, SIBN_REV_17_20)

#SIBN.spend_growth_rate()

SIBN_RAW, SIBN_SPEND, SIBN_QTR_SPEND, df_SIBN_REV_17_20, SIBN_rev_trend, SIBN_MOA_ACTUAL_PROP, SIBN_PRODUCT_FAMILY, SIBN_PRODUCT_CATEGORY, SIBN_REVENUE_DIVISION  = SIBN.spend_growth_rate()

#SIBN.get_members()
#product family, category, revenue division
SIBN.plot_categories(fig_dims=(12,8))

#Exploratory
# 9.3 million next month spend, 1.35 MoM growth, 7-8 million
SIBN.plot_rev_trend(date_cut='2016Q1',fig_dims=(12,8))

#growth adjustment
SIBN.plot_growth_adj()
#SIBN_REQ_GROWTH = SIBN.required_growth(two_months=True, month1_growth=.05)
SIBN.LR_plots()
SIBN.adjust_proj_qtr(SIBN_QTR_SPEND['SPEND'].iloc[-1])
SIBN.adjust_proj_qtr(19.83)
#endregion SIBN

#region SILK, months play out sequentially
"""
Consensus: 4/8/2021 2021Q1 21.3
Over the course of 2021, we expect to see continued momentum as the healthcare operating environment normalizes. The key factors governing a return to normal growth are, of course, hospital resources and patient behavior. These are in turn impacted by the pace of virus transmission, the impact of variance and vaccination efforts.
We are cautiously optimistic that normalization will begin in the second quarter, although there are clearly several unknowns. With these caveats in mind, our expectation is for 2021 revenues to be in the range of $102 million to $108 million.

"""
SILK_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.SILK_data_20210722
                where company_name = 'SILK ROAD MEDICAL'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

SILK_Q1_GROWTH = 1.1
SILK_REV_17_20 = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                            '2018Q1','2018Q2','2018Q3','2018Q4', 
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [1.7, 2.8, 4.5, 5.5,
                            5.7, 7.8, 9.6, 11.5,
                            12.8, 14.9, 17, 18.6,
                            18.9, 15.1, 20.1, 21.1,
                            22.1, 25.4]} # units are in millions

SILK = util.GROWTH('SILK', cutdate, SILK_QUERY, SILK_REV_17_20)

#SILK.spend_growth_rate()

SILK_RAW, SILK_SPEND, SILK_QTR_SPEND, df_SILK_REV_17_20, SILK_rev_trend, SILK_MOA_ACTUAL_PROP, SILK_PRODUCT_FAMILY, SILK_PRODUCT_CATEGORY, SILK_REVENUE_DIVISION  = SILK.spend_growth_rate()

#SILK.get_members()
#product family, category, revenue division
SILK.plot_categories(fig_dims=(12,8))

#Exploratory
# 9.3 million next month spend, 1.35 MoM growth, 7-8 million
SILK.plot_rev_trend(date_cut='2017Q1',fig_dims=(12,8))

#growth adjustment
SILK.plot_growth_adj()
#SILK_REQ_GROWTH = SILK.required_growth(two_months=True, month1_growth=.05)
SILK.LR_plots()
SILK.adjust_proj_qtr(SILK_QTR_SPEND['SPEND'].iloc[-1])
SILK.adjust_proj_qtr(23.28)
#endregion SILK

#region SNN_AWM 
"""
Consensus: 4/7/2021 2021Q1 156.31
# Guidedance low to mid single digit declines yoy 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SNN_AWM_data_20210429
SNN_AWM_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SNN_data_20210722
                         where company_name ilike '%Smith & Nephew%' and revenue_division ilike '%Advanced Wound Management%' and year >= 2017
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SNN_AWM_Q1_GROWTH = .97
SNN_AWM_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1','2021Q2'], 
                        'SPEND': [136, 155, 152, 164,
                                  132, 156, 155, 169, 
                                  136, 174, 179, 197, 
                                  158, 142, 177, 198,
                                  158*SNN_AWM_Q1_GROWTH, 180.2]} # units are in millions

SNN_AWM = util.GROWTH('SNN_AWM', cutdate, SNN_AWM_QUERY, SNN_AWM_REV)

SNN_AWM_RAW, SNN_AWM_SPEND, SNN_AWM_QTR_SPEND, df_SNN_AWM_REV, SNN_AWM_rev_trend, SNN_AWM_MOA_ACTUAL_PROP, SNN_AWM_PRODUCT_FAMILY, SNN_AWM_PRODUCT_CATEGORY, SNN_AWM_REVENUE_DIVISION = SNN_AWM.spend_growth_rate()

#Spendings
#product family
SNN_AWM.plot_categories(fig_dims=(14,12))

#exploratory
SNN_AWM.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
SNN_AWM.plot_growth_adj()
#SNN_AWM_REQ_GROWTH = SNN_AWM.required_growth(two_months=False, month1_growth=.304551)

SNN_AWM.LR_plots()
#SNN_AWM.adjust_proj_qtr(158*SNN_AWM_Q1_GROWTH)
SNN_AWM.adjust_proj_qtr(SNN_AWM_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SNN_AWM

#region SNN_REC 
"""
Consensus: 4/7/2021 2021Q1 239.22
# Guidedance low to mid single digit declines yoy 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SNN_REC_data_20210429
SNN_REC_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SNN_data_20210722
                         where company_name ilike '%Smith & Nephew%' and revenue_division ilike '%Orthopaedics%' and year >= 2017
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SNN_REC_Q1_GROWTH = .97
SNN_REC_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1', '2021Q2'], 
                        'SPEND': [253.69, 258.83, 233.71, 273.43,
                                  247.89, 259.69, 245.80, 286.38,
                                  258.01, 273.25, 262.42, 308.74,
                                  254.64, 177.76, 268.80, 287.19,
                                  254.64*.97, 282.3]} # units are in millions

SNN_REC = util.GROWTH('SNN_REC', cutdate, SNN_REC_QUERY, SNN_REC_REV)

SNN_REC_RAW, SNN_REC_SPEND, SNN_REC_QTR_SPEND, df_SNN_REC_REV, SNN_REC_rev_trend, SNN_REC_MOA_ACTUAL_PROP, SNN_REC_PRODUCT_FAMILY, SNN_REC_PRODUCT_CATEGORY, SNN_REC_REVENUE_DIVISION = SNN_REC.spend_growth_rate()

#Spendings
#product family
SNN_REC.plot_categories(fig_dims=(14,12))

#exploratory
SNN_REC.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
SNN_REC.plot_growth_adj()
#SNN_REC_REQ_GROWTH = SNN_REC.required_growth(two_months=False, month1_growth=.304551)

SNN_REC.LR_plots()
#SNN_REC.adjust_proj_qtr(254.64*SNN_REC_Q1_GROWTH)
SNN_REC.adjust_proj_qtr(SNN_REC_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SNN_REC

#region SNN_SMT 
"""
Consensus: 4/7/2021 2021Q1 156.31
# Guidedance low to mid single digit declines yoy 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SNN_SMT_data_20210429
SNN_SMT_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SNN_data_20210722
                         where company_name ilike '%Smith & Nephew%' and revenue_division ilike '%Sports Medicine & ENT%' and year >= 2017
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SNN_SMT_Q1_GROWTH = .97
SNN_SMT_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                         '2018Q1','2018Q2','2018Q3','2018Q4', 
                         '2019Q1','2019Q2','2019Q3','2019Q4',
                         '2020Q1','2020Q2','2020Q3','2020Q4',
                         '2021Q1', '2021Q2'], 
                        'SPEND': [165, 168, 159, 187,
                                  165, 174, 168, 194,
                                  174, 188, 183, 218,
                                  168, 121, 184, 216,                            
                                  168, 188.7]} # units are in millions

SNN_SMT = util.GROWTH('SNN_SMT', cutdate, SNN_SMT_QUERY, SNN_SMT_REV)

SNN_SMT_RAW, SNN_SMT_SPEND, SNN_SMT_QTR_SPEND, df_SNN_SMT_REV, SNN_SMT_rev_trend, SNN_SMT_MOA_ACTUAL_PROP, SNN_SMT_PRODUCT_FAMILY, SNN_SMT_PRODUCT_CATEGORY, SNN_SMT_REVENUE_DIVISION = SNN_SMT.spend_growth_rate()

#Spendings
#product family
SNN_SMT.plot_categories(fig_dims=(14,12))

#exploratory
SNN_SMT.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
SNN_SMT.plot_growth_adj()
#SNN_SMT_REQ_GROWTH = SNN_SMT.required_growth(two_months=False, month1_growth=.304551)

SNN_SMT.LR_plots()
#SNN_SMT.adjust_proj_qtr(168*SNN_SMT_Q1_GROWTH)
SNN_SMT.adjust_proj_qtr(SNN_SMT_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SNN_SMT

#region SWAV
"""
Consensus: 4/8/2021 2021Q1 17.3
"""
SWAV_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.SWAV_data_20210805 
                where company_name = 'SHOCKWAVE MEDICAL' and transaction_date >= '2018-07-01'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

SWAV_Q1_GROWTH = 2.5
SWAV_REV = {'DATE' : ['2018Q3', '2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3','2020Q4',
                      '2021Q1', '2021Q2'], 
                  'SPEND': [2.1, 2.5,
                            3.6, 5.2, 6.2, 7.6,
                            7.8, 5.5, 11.1, 12.7,
                            21, 33.2]} # units are in millions

SWAV = util.GROWTH('SWAV', cutdate, SWAV_QUERY, SWAV_REV)

#SWAV.spend_growth_rate()

SWAV_RAW, SWAV_SPEND, SWAV_QTR_SPEND, df_SWAV_REV, SWAV_rev_trend, SWAV_MOA_ACTUAL_PROP, SWAV_PRODUCT_FAMILY, SWAV_PRODUCT_CATEGORY, SWAV_REVENUE_DIVISION  = SWAV.spend_growth_rate()

#SWAV.get_members()
#product family, category, revenue division
SWAV.plot_categories(fig_dims=(12,8))

#Exploratory
SWAV.plot_rev_trend(date_cut='2018Q3',fig_dims=(12,8))

#growth adjustment
SWAV.plot_growth_adj()
SWAV.LR_plots()
SWAV.adjust_proj_qtr(SWAV_QTR_SPEND['SPEND'].iloc[-1])
#endregion SWAV


#region SYK_MEDSG 
"""
Consensus: 4/7/2021 2021Q1 1328.4
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_MEDSG_data_20210429
SYK_MEDSG_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210722
                         where company_name = 'Stryker' and revenue_division ilike '%MedSurg%' and year >= 2017
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_MEDSG_Q1_GROWTH = 1.09 
SYK_MEDSG_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1', '2021Q2'], 
                        'SPEND': [1033.00, 1067.90, 1052.00, 1232.30,
                                  1106.00, 1140.00, 1157.00, 1340.00,
                                  1221.00, 1287.00, 1247.00, 1434.00,
                                  1294.00, 1004.00, 1269.00, 1469.00,
                                  1242.00,1348.2]} # units are in millions

SYK_MEDSG = util.GROWTH('SYK_MEDSG', cutdate, SYK_MEDSG_QUERY, SYK_MEDSG_REV)

SYK_MEDSG_RAW, SYK_MEDSG_SPEND, SYK_MEDSG_QTR_SPEND, df_SYK_MEDSG_REV, SYK_MEDSG_rev_trend, SYK_MEDSG_MOA_ACTUAL_PROP, SYK_MEDSG_PRODUCT_FAMILY, SYK_MEDSG_PRODUCT_CATEGORY, SYK_MEDSG_REVENUE_DIVISION = SYK_MEDSG.spend_growth_rate()

#Spendings
#product family
SYK_MEDSG.plot_categories(fig_dims=(14,12))

#exploratory
SYK_MEDSG.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
SYK_MEDSG.plot_growth_adj()
#SYK_MEDSG_REQ_GROWTH = SYK_MEDSG.required_growth(two_months=False, month1_growth=.304551)

SYK_MEDSG.LR_plots()
#SYK_MEDSG.adjust_proj_qtr(29.1*SYK_MEDSG_Q1_GROWTH)
SYK_MEDSG.adjust_proj_qtr(SYK_MEDSG_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_MEDSG

#region SYK_NNS 
"""
Consensus: 4/7/2021 2021Q1 1328.4
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_NNS_data_20210429
SYK_NNS_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210722
                         where company_name = 'Stryker' and revenue_division ilike '%Neurotechnology and Spine%' and year >= 2017
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_NNS_Q1_GROWTH = 1.09 
SYK_NNS_REV = {'DATE' : ['2017Q1','2017Q2','2017Q3','2017Q4', 
                         '2018Q1','2018Q2','2018Q3','2018Q4', 
                         '2019Q1','2019Q2','2019Q3','2019Q4',
                         '2020Q1','2020Q2','2020Q3','2020Q4',
                         '2021Q1', '2021Q2'], 
                        'SPEND': [356, 364, 361, 387,
                                  394, 424, 426, 478,
                                  508, 534, 525, 568,
                                  497, 339, 542, 568,
                                  528, 554]} # units are in millions

SYK_NNS = util.GROWTH('SYK_NNS', cutdate, SYK_NNS_QUERY, SYK_NNS_REV)

SYK_NNS_RAW, SYK_NNS_SPEND, SYK_NNS_QTR_SPEND, df_SYK_NNS_REV, SYK_NNS_rev_trend, SYK_NNS_MOA_ACTUAL_PROP, SYK_NNS_PRODUCT_FAMILY, SYK_NNS_PRODUCT_CATEGORY, SYK_NNS_REVENUE_DIVISION = SYK_NNS.spend_growth_rate()

#Spendings
#product family
SYK_NNS.plot_categories(fig_dims=(14,12))

#exploratory
SYK_NNS.plot_rev_trend(date_cut='2017Q1',fig_dims=(16,8))

#growth adjustment
SYK_NNS.plot_growth_adj()
#SYK_NNS_REQ_GROWTH = SYK_NNS.required_growth(two_months=False, month1_growth=.304551)

SYK_NNS.LR_plots()
#SYK_NNS.adjust_proj_qtr(29.1*SYK_NNS_Q1_GROWTH)
SYK_NNS.adjust_proj_qtr(SYK_NNS_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_NNS

#region SYK_ORTHO 
"""
Consensus: 4/7/2021 2021Q1 950
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_ORTHO_data_20210429
SYK_ORTHO_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210429
                         where company_name = 'Stryker' and revenue_division ilike '%Orthopaedics%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_ORTHO_Q1_GROWTH = 1.09 
SYK_ORTHO_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                           '2016Q1','2016Q2','2016Q3','2016Q4', 
                           '2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1'], 
                        'SPEND': [620.4, 632.8, 645.9, 707.7,
                                  671.8, 669.3, 669.5, 741.6, 
                                  718, 713, 701, 807,
                                  751, 753, 731, 848,
                                  787, 795, 791, 907,
                                  783, 527, 840, 935.9,
                                  783*SYK_ORTHO_Q1_GROWTH]} # units are in millions

SYK_ORTHO = util.GROWTH('SYK_ORTHO', cutdate, SYK_ORTHO_QUERY, SYK_ORTHO_REV)

SYK_ORTHO_RAW, SYK_ORTHO_SPEND, SYK_ORTHO_QTR_SPEND, df_SYK_ORTHO_REV, SYK_ORTHO_rev_trend, SYK_ORTHO_MOA_ACTUAL_PROP, SYK_ORTHO_PRODUCT_FAMILY, SYK_ORTHO_PRODUCT_CATEGORY, SYK_ORTHO_REVENUE_DIVISION = SYK_ORTHO.spend_growth_rate()

#Spendings
#product family
SYK_ORTHO.plot_categories(fig_dims=(14,12))

#exploratory
SYK_ORTHO.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
SYK_ORTHO.plot_growth_adj()
#SYK_ORTHO_REQ_GROWTH = SYK_ORTHO.required_growth(two_months=False, month1_growth=.304551)

SYK_ORTHO.LR_plots()
#SYK_ORTHO.adjust_proj_qtr(29.1*SYK_ORTHO_Q1_GROWTH)
SYK_ORTHO.adjust_proj_qtr(SYK_ORTHO_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_ORTHO

#region SYK_KNEE 
"""
Consensus: 4/7/2021 2021Q1 950
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_KNEE_data_20210429
SYK_KNEE_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210722
                         where company_name = 'Stryker' and revenue_division ilike '%Orthopaedics%' and product_category ilike '%Knee%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_KNEE_Q1_GROWTH = 1.09 
SYK_KNEE_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                           '2016Q1','2016Q2','2016Q3','2016Q4', 
                           '2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1','2021Q2'], 
                        'SPEND': [239.2, 244.2, 243.8, 280.4,
                                  261.2, 260.9, 257.2, 296.7,
                              	 286, 282, 270, 331,
                                  301, 304, 291, 348,
                                  320,	324, 318, 385,
                                  322, 179, 332, 336.9,
                                  294, 323]} # units are in millions

SYK_KNEE = util.GROWTH('SYK_KNEE', cutdate, SYK_KNEE_QUERY, SYK_KNEE_REV)

SYK_KNEE_RAW, SYK_KNEE_SPEND, SYK_KNEE_QTR_SPEND, df_SYK_KNEE_REV, SYK_KNEE_rev_trend, SYK_KNEE_MOA_ACTUAL_PROP, SYK_KNEE_PRODUCT_FAMILY, SYK_KNEE_PRODUCT_CATEGORY, SYK_KNEE_REVENUE_DIVISION = SYK_KNEE.spend_growth_rate()

#Spendings
#product family
SYK_KNEE.plot_categories(fig_dims=(14,12))

#exploratory
SYK_KNEE.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
SYK_KNEE.plot_growth_adj()
#SYK_KNEE_REQ_GROWTH = SYK_KNEE.required_growth(two_months=False, month1_growth=.304551)

SYK_KNEE.LR_plots()
#SYK_KNEE.adjust_proj_qtr(29.1*SYK_KNEE_Q1_GROWTH)
SYK_KNEE.adjust_proj_qtr(SYK_KNEE_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_KNEE

#region SYK_HIP 
"""
Consensus: 4/7/2021 2021Q1 950
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_HIP_data_20210429
SYK_HIP_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210722
                         where company_name = 'Stryker' and revenue_division ilike '%Orthopaedics%' and product_category ilike '%HIP%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_HIP_Q1_GROWTH = 1.09 
SYK_HIP_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                           '2016Q1','2016Q2','2016Q3','2016Q4', 
                           '2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1','22021Q2'], 
                        'SPEND': [192.8, 197.9, 196.6, 214.8,
                        	       201.4, 199.9, 196.2, 214.9,
                                  204, 203, 194, 219, 
                                  205, 207, 198, 228,
                                  213, 219, 211, 239,
                                  201, 140, 223, 213,
                                  186.3, 222.6]} # units are in millions

SYK_HIP = util.GROWTH('SYK_HIP', cutdate, SYK_HIP_QUERY, SYK_HIP_REV)

SYK_HIP_RAW, SYK_HIP_SPEND, SYK_HIP_QTR_SPEND, df_SYK_HIP_REV, SYK_HIP_rev_trend, SYK_HIP_MOA_ACTUAL_PROP, SYK_HIP_PRODUCT_FAMILY, SYK_HIP_PRODUCT_CATEGORY, SYK_HIP_REVENUE_DIVISION = SYK_HIP.spend_growth_rate()

#Spendings
#product family
SYK_HIP.plot_categories(fig_dims=(14,12))

#exploratory
SYK_HIP.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
SYK_HIP.plot_growth_adj()
#SYK_HIP_REQ_GROWTH = SYK_HIP.required_growth(two_months=False, month1_growth=.304551)

SYK_HIP.LR_plots()
#SYK_HIP.adjust_proj_qtr(29.1*SYK_HIP_Q1_GROWTH)
SYK_HIP.adjust_proj_qtr(SYK_HIP_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_HIP

#region SYK_TE 
"""
Consensus: 4/7/2021 2021Q1 950
# Guidedance 8% - 10% for the year
"""
# non same store moa.build_kd_20210429, same store moa_live.stage.SYK_TE_data_20210429
SYK_TE_QUERY = """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                         from moa_live.stage.SYK_data_20210722
                         where company_name = 'Stryker' and revenue_division ilike '%Orthopaedics%' and product_category ilike '%Trauma and Extremities%' and year >= 2015
                         group by 1,2,3,4,5,6,7,8
                         order by 4;"""

SYK_TE_Q1_GROWTH = 1.09 
SYK_TE_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4', 
                           '2016Q1','2016Q2','2016Q3','2016Q4', 
                           '2017Q1','2017Q2','2017Q3','2017Q4', 
                           '2018Q1','2018Q2','2018Q3','2018Q4', 
                           '2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3','2020Q4',
                           '2021Q1','2021Q2'], 
                        'SPEND': [188.4, 190.7, 205.5, 212.5,
                                  209.2, 208.5, 216.1, 230,
                                  228, 228, 237, 257, 
                                  245, 242, 242, 272, 
                                  254, 252, 262, 283,
                                  260, 208, 285, 386,
                                  440,447.8]} # units are in millions

SYK_TE = util.GROWTH('SYK_TE', cutdate, SYK_TE_QUERY, SYK_TE_REV)

SYK_TE_RAW, SYK_TE_SPEND, SYK_TE_QTR_SPEND, df_SYK_TE_REV, SYK_TE_rev_trend, SYK_TE_MOA_ACTUAL_PROP, SYK_TE_PRODUCT_FAMILY, SYK_TE_PRODUCT_CATEGORY, SYK_TE_REVENUE_DIVISION = SYK_TE.spend_growth_rate()

#Spendings
#product family
SYK_TE.plot_categories(fig_dims=(14,12))

#exploratory
SYK_TE.plot_rev_trend(date_cut='2015Q1',fig_dims=(16,8))

#growth adjustment
SYK_TE.plot_growth_adj()
#SYK_TE_REQ_GROWTH = SYK_TE.required_growth(two_months=False, month1_growth=.304551)

SYK_TE.LR_plots()
#SYK_TE.adjust_proj_qtr(29.1*SYK_TE_Q1_GROWTH)
SYK_TE.adjust_proj_qtr(SYK_TE_QTR_SPEND['SPEND'].iloc[-1])
# TODO CHECK IF GROWTH RATES HAS PREDICTIVE POWER ON PROPORTION
#endregion SYK_TE


#region VAPO_CAP
"""
Consensus: 4/8/2021 2021Q1 8.1
53-73% YoY growth 2021Q1 75/25% for US and International 
"""
VAPO_CAP_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.VAPO_data_20210805 
                where company_name = 'VAPOTHERM' and revenue_division ilike 'CAPITAL EQUIPMENT' and year >= 2018
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

VAPO_CAP_Q1_GROWTH = 1.53
# '2018Q1','2018Q2','2018Q3','2018Q4', 
# 1.8, 2.4, 2.1, 2.3,
VAPO_CAP_REV = {'DATE' : ['2019Q1','2019Q2','2019Q3','2019Q4',
                          '2020Q1','2020Q2','2020Q3','2020Q4',
                          '2021Q1','2021Q2'], 
                  'SPEND': [2.2, 1.9, 1.9, 1.9,
                            4.2, 15.8, 14.4, 17.4,
                            8, 1.8]} # units are in millions

VAPO_CAP = util.GROWTH('VAPO_CAP', cutdate, VAPO_CAP_QUERY, VAPO_CAP_REV)

#VAPO_CAP.spend_growth_rate()

VAPO_CAP_RAW, VAPO_CAP_SPEND, VAPO_CAP_QTR_SPEND, df_VAPO_CAP_REV, VAPO_CAP_rev_trend, VAPO_CAP_MOA_ACTUAL_PROP, VAPO_CAP_PRODUCT_FAMILY, VAPO_CAP_PRODUCT_CATEGORY, VAPO_CAP_REVENUE_DIVISION  = VAPO_CAP.spend_growth_rate()

#VAPO_CAP.get_members()
#product family, category, revenue division
VAPO_CAP.plot_categories(fig_dims=(12,8))

#Exploratory
VAPO_CAP.plot_rev_trend(date_cut='2018Q1',fig_dims=(12,8))

#growth adjustment
VAPO_CAP.plot_growth_adj()
VAPO_CAP_REQ_GROWTH = VAPO_CAP.required_growth(two_months=True, month1_growth=.05)
VAPO_CAP.adjust_proj_qtr(4.2*VAPO_CAP_Q1_GROWTH)
VAPO_CAP.LR_plots()
VAPO_CAP.adjust_proj_qtr(VAPO_CAP_QTR_SPEND['SPEND'].iloc[-1])
VAPO_CAP.adjust_proj_qtr(8.942182)
# accurate wheter we captures these facilities.
# correlate to covid cases. find regions doing well and bad. are ppl buying more, do they need to buy more. In nyc bought a ton of beginning surge. Facilties need more now, already had the huge amount of it, not get that huge capital. Lever from each existing company. Basically will our data will do a reasonable job? the methodology should work fine.
# facility level adjustment on vapotherm revenue increases 3 times.
#endregion VAPO_CAP

#region VAPO_DISP
"""
Consensus: 4/8/2021 2021Q1 14.4
53-73% YoY growth 2021Q1 75/25% for US and International 
"""
VAPO_DISP_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.VAPO_data_20210805 
                where company_name = 'VAPOTHERM' and revenue_division ilike 'DISP%'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

VAPO_DISP_Q1_GROWTH = 1.53
VAPO_DISP_REV = {'DATE' : ['2018Q1','2018Q2','2018Q3','2018Q4', 
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1', '2021Q2'], 
                  'SPEND': [6.3, 5.2, 5.1, 6.4,
                            7.5, 6.5, 6, 7.7,
                            9.7, 9.4, 10.4, 15,
                            12.5, 10.3]} # units are in millions

VAPO_DISP = util.GROWTH('VAPO_DISP', cutdate, VAPO_DISP_QUERY, VAPO_DISP_REV)

#VAPO_DISP.spend_growth_rate()

VAPO_DISP_RAW, VAPO_DISP_SPEND, VAPO_DISP_QTR_SPEND, df_VAPO_DISP_REV, VAPO_DISP_rev_trend, VAPO_DISP_MOA_ACTUAL_PROP, VAPO_DISP_PRODUCT_FAMILY, VAPO_DISP_PRODUCT_CATEGORY, VAPO_DISP_REVENUE_DIVISION  = VAPO_DISP.spend_growth_rate()

#VAPO_DISP.get_members()
#product family, category, revenue division
VAPO_DISP.plot_categories(fig_dims=(12,8))

#Exploratory
VAPO_DISP.plot_rev_trend(date_cut='2018Q1',fig_dims=(12,8))

#growth adjustment
VAPO_DISP.plot_growth_adj()
VAPO_DISP_REQ_GROWTH = VAPO_DISP.required_growth(two_months=True, month1_growth=.05)
VAPO_DISP.LR_plots()
VAPO_DISP.adjust_proj_qtr(VAPO_DISP_QTR_SPEND['SPEND'].iloc[-1])
VAPO_DISP.adjust_proj_qtr(11.84617)
# accurate wheter we captures these facilities.
# correlate to covid cases. find regions doing well and bad. are ppl buying more, do they need to buy more. In nyc bought a ton of beginning surge. Facilties need more now, already had the huge amount of it, not get that huge capital. Lever from each existing company. Basically will our data will do a reasonable job? the methodology should work fine.
# facility level adjustment on vapotherm revenue increases 3 times.
#endregion VAPO_DISP

#region XENT
"""
Consensus: 23.6 2/27/2021 worldwide
Specifically, we believe that current consensus revenue for 2021 is appropriate, even with COVID headwinds and uncertainty. And our revenue outlook at $116 million to $120 million for 2020 is consistent with our prior statements, regarding growth relative to 2019 up between 5%, to 10% versus 2019 and up 42% to 49% versus 2020. The in addition, we expect quarterly growth rates relative to 2019 will strengthen as the year progresses with COVID carrying a lessening impact and our new products building momentum, inclusive of the late-Q2 full national launch beyond our measured and evaluative launch today of VenSure sinus balloon and Cube navigation.
"""
XENT_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.XENT_data_20210729 
                where company_name ilike 'Intersect ENT' and year >= 2014
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

XENT_Q1_GROWTH = 1.42
XENT_REV = {'DATE' : ['2014Q1','2014Q2','2014Q3','2014Q4',
                      '2015Q1','2015Q2','2015Q3','2015Q4',
                      '2016Q1','2016Q2','2016Q3','2016Q4',
                      '2017Q1','2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3','2020Q4',
                      '2021Q1','2021Q2'], 
                  'SPEND': [7.5, 8.6, 9.1, 13.4,
                            13.4, 15.2, 14.2, 18.8,
                            16.7, 19.3, 18.4, 24.1,
                            20.3, 23.8, 22.2, 29.3,
                            24.6, 26, 24.2, 32.2,
                            26.1, 26.1, 24.3, 31.1,
                            19.2, 9.5, 21.8, 25.9,
                            21.9, 25.6]} # units are in millions

XENT = util.GROWTH('XENT', cutdate, XENT_QUERY, XENT_REV)

#XENT.spend_growth_rate()
XENT_RAW, XENT_SPEND, XENT_QTR_SPEND, df_XENT_REV_15_20, XENT_rev_trend, XENT_MOA_ACTUAL_PROP, XENT_PRODUCT_FAMILY, XENT_PRODUCT_CATEGORY, XENT_REVENUE_DIVISION  = XENT.spend_growth_rate()

#product family, category, revenue division
XENT.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
XENT.plot_rev_trend(date_cut='2014Q1',fig_dims=(12,8))

#growth adjustment
XENT.plot_growth_adj()
XENT_REQ_GROWTH = XENT.required_growth(two_months=False)

XENT.LR_plots()
XENT.adjust_proj_qtr(XENT_QTR_SPEND['SPEND'].iloc[-1])
XENT.adjust_proj_qtr(21.11)
#endregion XENT

#region ZBH HIPS
"""
 Based on what we've seen so far in the quarter and in tandem with our latest estimates for procedure cadence, we project that Q1 revenue will be down in the low single-digit to mid-single-digit percentage range versus Q1 2020
"""
ZBH_HIP_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ZBH_data_20210729 
                where company_name ilike 'Zimmer Biomet' and revenue_division ilike 'HIP' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ZBH_HIP_Q1_GROWTH = .97
# ZBH_HIP fiscal quarter is two quarters ahead
ZBH_HIP_REV = {'DATE' :['2015Q1','2015Q2','2015Q3','2015Q4',
                              '2016Q1','2016Q2','2016Q3','2016Q4',
                              '2017Q1','2017Q2','2017Q3','2017Q4',
                              '2018Q1','2018Q2','2018Q3','2018Q4',
                              '2019Q1','2019Q2','2019Q3','2019Q4',
                              '2020Q1','2020Q2','2020Q3','2020Q4',
                              '2021Q1','2021Q2'], 
                  'SPEND': [244.5, 246, 239.6, 249.9,
                            244.5, 247.3, 237.6, 252.7,
                            244.5, 243.4, 226.6, 254.4,
                            247.8, 250, 240, 258.5, 
                            247.1, 253.3, 249, 266.9,
                            232.5, 170.7, 268.6, 269.7,
                            235.2, 253.6]} # units are in millions
ZBH_HIP = util.GROWTH('ZBH_HIP', cutdate, ZBH_HIP_QUERY, ZBH_HIP_REV)

#ZBH_HIP.spend_growth_rate()
ZBH_HIP_RAW, ZBH_HIP_SPEND, ZBH_HIP_QTR_SPEND, df_ZBH_HIP_REV, ZBH_HIP_rev_trend, ZBH_HIP_MOA_ACTUAL_PROP, ZBH_HIP_PRODUCT_FAMILY, ZBH_HIP_PRODUCT_CATEGORY, ZBH_HIP_REVENUE_DIVISION  = ZBH_HIP.spend_growth_rate()

#product family, category, revenue division
ZBH_HIP.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
ZBH_HIP.plot_rev_trend(date_cut='2015Q1',fig_dims=(12,8))

#growth adjustment
ZBH_HIP.plot_growth_adj()
ZBH_HIP_REQ_GROWTH = ZBH_HIP.required_growth(two_months=False)
ZBH_HIP.LR_plots()
ZBH_HIP.adjust_proj_qtr(ZBH_HIP_QTR_SPEND['SPEND'].iloc[-1])
ZBH_HIP.adjust_proj_qtr(226.67)
#endregion ZBH_HIP

#region ZBH KNEES
"""
Consensus: 372.1
 Based on what we've seen so far in the quarter and in tandem with our latest estimates for procedure cadence, we project that Q1 revenue will be down in the low single-digit to mid-single-digit percentage range versus Q1 2020
"""
ZBH_KNEE_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ZBH_data_20210729 
                where company_name ilike 'Zimmer Biomet' and revenue_division ilike 'Knee' and transaction_date >= '2015-04-01'
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ZBH_KNEE_Q1_GROWTH = .97
# ZBH_KNEE fiscal quarter is two quarters ahead
ZBH_KNEE_REV_15_20 = {'DATE' : ['2015Q2','2015Q3','2015Q4',
                                '2016Q1','2016Q2','2016Q3','2016Q4',
                                '2017Q1','2017Q2','2017Q3','2017Q4',
                                '2018Q1','2018Q2','2018Q3','2018Q4',
                                '2019Q1','2019Q2','2019Q3','2019Q4',
                                '2020Q1','2020Q2','2020Q3','2020Q4',
                                '2021Q1', '2021Q2'], 
                  'SPEND': [427, 415, 401, 441,
                            429.1, 416.8, 397, 443.6,
                            428, 405.4, 381.5, 441.6,
                            417.2, 408.1, 384.6, 432.8,
                            403.8, 401.9, 382, 434.5,
                            360.1, 216.7, 395.2, 432.7,
                            353.2]} # units are in millions

ZBH_KNEE = util.GROWTH('ZBH_KNEE', "20210429", ZBH_KNEE_QUERY, ZBH_KNEE_REV_15_20)

#ZBH_KNEE.spend_growth_rate()
ZBH_KNEE_RAW, ZBH_KNEE_SPEND, ZBH_KNEE_QTR_SPEND, df_ZBH_KNEE_REV_15_20, ZBH_KNEE_rev_trend, ZBH_KNEE_MOA_ACTUAL_PROP, ZBH_KNEE_PRODUCT_FAMILY, ZBH_KNEE_PRODUCT_CATEGORY, ZBH_KNEE_REVENUE_DIVISION  = ZBH_KNEE.spend_growth_rate()

#product family, category, revenue division
ZBH_KNEE.plot_categories(fig_dims=(12,8))

#Exploratory
# assume a 10% sequential growth
ZBH_KNEE.plot_rev_trend(date_cut='2015Q2',fig_dims=(12,8))

#growth adjustment
ZBH_KNEE.plot_growth_adj()
ZBH_KNEE_REQ_GROWTH = ZBH_KNEE.required_growth(two_months=False)

ZBH_KNEE.LR_plots()
ZBH_KNEE.adjust_proj_qtr(ZBH_KNEE_QTR_SPEND['SPEND'].iloc[-1])
ZBH_KNEE.adjust_proj_qtr(352.24) # 10% decrease sequencial growth
#endregion ZBH_KNEE

#region ZBH SETS
"""
 Based on what we've seen so far in the quarter and in tandem with our latest estimates for procedure cadence, we project that Q1 revenue will be down in the low single-digit to mid-single-digit percentage range versus Q1 2020
"""
ZBH_SET_QUERY =  """select month, quarter, year, transaction_date, company_name, revenue_division, product_category, product_family, sum(projected_total_spend) as spend
                from moa_live.stage.ZBH_data_20210729 
                where company_name ilike 'Zimmer Biomet' and revenue_division ilike 'S.E.T' and year >= 2015
                group by 1,2,3,4,5,6,7,8
                order by 4;"""

ZBH_SET_Q1_GROWTH = .97
# ZBH_SET fiscal quarter is two quarters ahead
ZBH_SET_REV = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                               '2016Q1','2016Q2','2016Q3','2016Q4',
                               '2017Q1','2017Q2','2017Q3','2017Q4',
                               '2018Q1','2018Q2','2018Q3','2018Q4',
                               '2019Q1','2019Q2','2019Q3','2019Q4',
                               '2020Q1','2020Q2','2020Q3','2020Q4',
                               '2021Q1', '2021Q2'], 
                  'SPEND': [253, 243.2, 244, 259.7,
                            257.5, 262.2, 260.9, 276.9,
                            266.2, 263.7, 255.9, 279.8,
                            240.3, 238.8, 226.8, 248.2,
                            242.1, 243.8, 238.3, 257.6,
                            216.5, 165.1, 240.5, 246.5,
                            254.3, 264.3]} # units are in millions

ZBH_SET = util.GROWTH('ZBH_SET', cutdate, ZBH_SET_QUERY, ZBH_SET_REV)

#ZBH_SET.spend_growth_rate()
ZBH_SET_RAW, ZBH_SET_SPEND, ZBH_SET_QTR_SPEND, df_ZBH_SET_REV, ZBH_SET_rev_trend, ZBH_SET_MOA_ACTUAL_PROP, ZBH_SET_PRODUCT_FAMILY, ZBH_SET_PRODUCT_CATEGORY, ZBH_SET_REVENUE_DIVISION  = ZBH_SET.spend_growth_rate()

#product family, category, revenue division
ZBH_SET.plot_categories(fig_dims=(12,8))

#Exploratory
ZBH_SET.plot_rev_trend(date_cut='2014Q1',fig_dims=(12,8))

#growth adjustment
ZBH_SET.plot_growth_adj()
ZBH_SET_REQ_GROWTH = ZBH_SET.required_growth(two_months=False)
ZBH_SET.LR_plots()
ZBH_SET.adjust_proj_qtr(ZBH_SET_QTR_SPEND['SPEND'].iloc[-1])
ZBH_SET.adjust_proj_qtr(236.19)
#endregion ZBH_SET

