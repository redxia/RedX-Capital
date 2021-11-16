# Author: Redmond Xia
# Date: 07/07/2021
# Description: Scaling up the two month data based on the distribution model

#region libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from utilities import util
import statsmodels.api as sm
%load_ext autoreload
%autoreload 2
cutdate='20210701' 
#endregion libraries
sns.set_palette('dark')


""" consensus 189.1 2Q2021"""
ABMD_QUERY =  """select month, quarter, year, sum(projected_total_spend_report) as reported,  sum(projected_total_spend) as spend
                from moa_live.stage.ABMD_data_{date}
                where company_name ilike 'ABIOMED Inc' and year >= 2015
                group by 1,2,3
                order by 3,2,1;""".format(date=cutdate)

ABMD_Q1_GROWTH = 1.08 # 2017Q2 cut date, in-sample
# ABMD fiscal quarter is two quarters ahead
ABMD_REV_15_20 = {'DATE' : ['2015Q1','2015Q2','2015Q3','2015Q4',
                            '2016Q1','2016Q2','2016Q3','2016Q4',
                            '2017Q1','2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1','2020Q2','2020Q3','2020Q4',
                            '2021Q1'], 
                  'SPEND': [57.7, 63.7, 66.7, 75,
                            81.8, 89.6, 89.3, 100.3,
                            108.2, 114.7, 113.6, 130.7,
                            146.2, 151.7, 152.2, 165.7,
                            169.7, 168.3, 164.2, 177.1,
                            164, 126.2, 163.2, 179.6,
                            186.1]} # units are in millions

ABMD = util.GROWTH('ABMD', cutdate, ABMD_QUERY, ABMD_REV_15_20)
