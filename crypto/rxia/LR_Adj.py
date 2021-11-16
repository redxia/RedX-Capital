# Author: Redmond Xia
# Date: 09/12/2021
# Description: Rolling forward linear models for alpha improvement

#region importing libaries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from utilities import util
# import statsmodels.api as sm
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.linear_model import Lasso
# from sklearn.linear_model import Ridge
# from sklearn.linear_model import RidgeCV
# from sklearn.linear_model import LassoCV
%load_ext autoreload
%autoreload 2
#cutdate='20210805' # 20210429 20210304 20210318
#endregion libraries
sns.set_palette('dark')

# TODO Build a function for regression of moa spend adjustment
# TODO format query.
#region ABMD
# ABMD fiscal quarter is three quarters ahead
ABMD_REV = {'DATE' : ['2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1', '2020Q3', '2020Q4',
                      '2021Q1','2021Q2', '2021Q3'],
            'REVENUE' : [130.7, 
                         146.2, 151.7, 152.2, 165.7,
                         169.7, 168.3, 164, 177,
                         164, 163.2, 179.6, 
                         186.1, 197.5, 194.9],
            'CONSENSUS' : [127.8, 
                           137.5, 145.7, 144.7, 162.6,
                           179.6, 174.4, 166.2, 180.4,
                           164.6, 161.6, 176.9,
                           177.5, 189.1, 194.9],
            'PROJ': [140.715326, 
                     153.508187, 141.374782, 166.345471, 161.647089,
                     151.804223, 182.083457, 172.384239, 185.006286,
                     180.428435, 164.753695,163.759217, 
                     178.976098, 195.035276, 211.008103048] # SS 12_12 
            # 'PROJ': [127.795591, 
            #          148.123241, 126.418223, 138.736689, 145.459179,
            #          124.646545, 172.093504, 158.500548, 174.327943,
            #          176.469619, 165.083438, 163.217333,
            #          183.744983, 193.143676] # SS NO LR 189.5821051                     
}

ABMD = pd.DataFrame(ABMD_REV)
ABMD_SUMMARY, ABMD_RESULT=util.linear_roll_fwd(df=ABMD, start_idx=4)
current_qtr='2021Q3_SS_12_12_RMQ2'
ABMD_RESULT.to_excel("Alphas\ABMD\ABMD_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABMD_SUMMARY.to_excel('Alphas\ABMD\ABMD_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABMD)
#endregion ABMD



#region ABT_EP
# ABT_EP fiscal quarter is three quarters ahead
ABT_EP_REV = {'DATE' : ['2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q3', '2020Q4', #   '2021Q2',
                        '2021Q1','2021Q2', '2021Q3'], # 
            'REVENUE' : [163.0, 
                         159.0, 170.0, 168.0, 178.0,
                         175.0, 190.0, 185.0, 193.0,
                         164.0,  192.0, 184.0, # 120.0,
                         179.0, 209.0, 210],
            'CONSENSUS' : [153.6, 
                           165, 184.3, 180.4, 193.4,
                           209.7, 213.6, 189.9, 203.1,
                           186.5, 166.3, 205, #  # 76.8,
                           184, 194.1, 210],
        #     'PROJ': [155.6, 
        #              130.3, 165.9, 172.9, 182.5, 
        #              190.0, 197.7, 188.6, 207.0,
        #              175.9,  188.8, 180.4, # 121.2,
        #              183.3, 217.0] # SS NO_LR
             'PROJ': [171.4, 
                      179.7, 181.4, 176.9, 187.0,
                      190.3, 214.4, 193.4, 218.2,
                      183.1, 193.1, 183.3, # , 136.5
                      194.5, 229.0, 196.9] # AVG  , 179.1
        #      'PROJ': [170.0, 163.2, 166.1, 177.6,
        #               181.1, 197.3, 171.6, 208.7,
        #               162.0, 122.2, 170.1, 182.3,
        #               195.5, 210.8] # AVG _AVG_GR , 179.1        , 163.8
}

ABT_EP = pd.DataFrame(ABT_EP_REV)
current_qtr='2021Q3_AVG'
ABT_EP_SUMMARY, ABT_EP_RESULT=util.linear_roll_fwd(df=ABT_EP, start_idx=3)
ABT_EP_RESULT.to_excel("Alphas\ABT\ABT_EP_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_EP_SUMMARY.to_excel('Alphas\ABT\ABT_EP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_EP)
#endregion ABT_EP


#region ABT_HF
# ABT_HF fiscal quarter is three quarters ahead
ABT_HF_REV = {'DATE' : ['2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2021Q2' ,'2020Q3', '2020Q4',
                      '2021Q1','2021Q2', '2021Q3'], # 
            'REVENUE' : [128.0,
                         114.0, 117.0, 111.0, 125.0,
                         143.0, 149.0, 136.0, 146.0,
                         152.0, 115.0, 144.0, 136.0,
                         145.0, 168.0, 165.6], # 
            'CONSENSUS' : [128.5, 
                           122.4, 125.9, 128.1, 127.3,
                           119.1, 141.3, 139.4, 146.1,
                           150.7, 138.7, 131.3, 155.8,
                           150.6, 152.6, 165.6], # 
            'PROJ': [130.3,
                     105.9, 119.2, 106.6, 124.0,
                     150.9, 127.4, 141.6, 139.0,
                     171.3, 108.7, 163.6, 127.1,
                     159.4, 149.1, 160.07669] # SS NO LR 
}

ABT_HF = pd.DataFrame(ABT_HF_REV)
current_qtr='2021Q3_SS_NO_LR'
ABT_HF_SUMMARY, ABT_HF_RESULT=util.linear_roll_fwd(df=ABT_HF, start_idx=4)
ABT_HF_RESULT.to_excel("Alphas\ABT\ABT_HF_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_HF_SUMMARY.to_excel('Alphas\ABT\ABT_HF_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_HF)
#endregion ABT_HF


#region ABT_NM
# ABT_NM fiscal quarter is three quarters ahead
ABT_NM_REV = {'DATE' : ['2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2', #'2020Q3', '2020Q4', # 
                      '2021Q1','2021Q2','2021Q3'], # 
            'REVENUE' : [175.0, 
                         168.0, 173.0, 172.0, 177.0,
                         152.0, 168.0, 165.0, 175.0,
                         137.0,85.0, #170.0, 172.0, # 
                         145.0, 166.0, 172.6
], # 
            'CONSENSUS' : [176.2, 
                           169, 193.2, 181.4, 186.4,
                           176.9, 172.4, 174, 177.7,
                           146.2,57.9, #135.2,  177.6, # 
                           154.1, 157.8, 172.6],# 
            'PROJ': [151.3061, 
                     154.7415, 169.0284, 169.4538, 181.2369, 
                     172.4514, 157.3909, 145.2054, 153.8088,
                     166.1838,94.4802, #131.9993,  141.9255, # 
                     139.7142, 158.2512, 160.7441] # AVG  
}

ABT_NM = pd.DataFrame(ABT_NM_REV)
ABT_NM_SUMMARY, ABT_NM_RESULT=util.linear_roll_fwd(df=ABT_NM, start_idx=4)
current_qtr='2021Q3_AVG_RMQ34'
ABT_NM_RESULT.to_excel("Alphas\ABT\ABT_NM_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_NM_SUMMARY.to_excel('Alphas\ABT\ABT_NM_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_NM)
#endregion ABT_NM


#region ABT_RM
# ABT_RM fiscal quarter is three quarters ahead
ABT_RM_REV = {'DATE' : ['2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q3','2020Q4', # '2020Q1','2020Q2',
                        '2021Q1','2021Q2', '2021Q3'], # , '2021Q3'
            'REVENUE' : [247.0, 
                         287.0, 285.0, 273.0, 263.0,
                         252.0, 273.0, 265.0, 267.0,
                         242.0,  248.0, #  185.0, 228.0,
                         241.0, 269.0, 262],
            'CONSENSUS' : [237.5, 
                           271.2, 276, 247.7, 244,
                           262.6, 245.4, 256.5, 253.2,
                           241.6, 256.3, #  142.5,242.2,
                           235.9, 250.3, 262],
            'PROJ': [258.7723271, 
                     255.430875, 283.717076, 281.123923, 288.346885,
                     273.949126, 273.554339, 257.909524, 266.001176,
                     237.284952, 245.894286, # 259.792676, 209.230755,
                     228.367843, 269.771696, 254.3589194] # Avg 
            # 'PROJ': [127.795591, 
            #          148.123241, 126.418223, 138.736689, 145.459179,
            #          124.646545, 172.093504, 158.500548, 174.327943,
            #          176.469619, 165.083438, 163.217333,
            #          183.744983, 193.143676] # SS NO LR 189.5821051                     
}
current_qtr='2021Q3_AVG_RMQ12'
ABT_RM = pd.DataFrame(ABT_RM_REV)
ABT_RM_SUMMARY, ABT_RM_RESULT=util.linear_roll_fwd(df=ABT_RM, start_idx=4)
ABT_RM_RESULT.to_excel("Alphas\ABT\ABT_RM_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_RM_SUMMARY.to_excel('Alphas\ABT\ABT_RM_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_RM)
#endregion ABT_RM

#region ABT_SH
# ABT_SH fiscal quarter is three quarters ahead
ABT_SH_REV = {'DATE' : ['2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q3', '2020Q4', # '2020Q1', '2021Q2',
                      '2021Q1','2021Q2', '2021Q3'], # 
            'REVENUE' : [112.0, 
                         109.0, 118.0, 126.0, 135.0,
                         136.0, 152.0, 158.0, 170.0,
                          159.0, 154.0, # 136.0, 91.0,
                         169.0, 191.0, 203.1],
            'CONSENSUS' : [108.8, 
                           117.5, 113.1, 118.3, 129.1,
                           132.5, 141.7, 158.4, 169.1,
                            144.8, 180.7, # 160.3, 89.8,
                           158.3, 177, 203.1],  #
            'PROJ': [124.9,
                     111.4, 130.9, 125.5, 148.8,
                     148.4, 156.2, 173.2, 170.5,
                      159.8, 155.2, # 162.6, 128.1,
                     155.6, 175.1, 172.3] # AVG 
            # 'PROJ': [127.795591, 
            #          148.123241, 126.418223, 138.736689, 145.459179,
            #          124.646545, 172.093504, 158.500548, 174.327943,
            #          176.469619, 165.083438, 163.217333,
            #          183.744983, 193.143676] # SS NO LR 189.5821051                     
}

ABT_SH = pd.DataFrame(ABT_SH_REV)
current_qtr='2021Q3_AVG_RMQ12'
ABT_SH_SUMMARY, ABT_SH_RESULT=util.linear_roll_fwd(df=ABT_SH, start_idx=4)
ABT_SH_RESULT.to_excel("Alphas\ABT\ABT_SH_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_SH_SUMMARY.to_excel('Alphas\ABT\ABT_SH_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_SH)
#endregion ABT_SH

#region ABT_VAS
# ABT_VAS fiscal quarter is three quarters ahead
ABT_VAS_REV = {'DATE' : ['2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1', '2020Q2','2020Q3', '2020Q4',
                      '2021Q1','2021Q2', '2021Q3'], # 
            'REVENUE' : [289.0, 
                         286.0, 284.0, 284.0, 272.0,
                         266.0, 270.0, 251.0, 260.0,
                         230.0, 168.0, 230.0, 225.0,
                         219.0, 246.0, 260.8],
            'CONSENSUS' : [290.9, 
                           303.1, 292.8, 287.9, 285.4,
                           286.9, 276.2, 275.7, 261.8,
                           247.4, 160.6, 237.3, 249.9,
                           244.1, 235.8, 260.8],
            'PROJ': [295.8674663, 
                     255.465066, 298.73914, 286.268123, 311.177496,
                     264.046261, 268.887018, 257.072588, 282.765858,
                     224.817066, 171.322432, 227.90891, 227.456301,
                     216.387578, 236.57573,230.6501] # AVG 
}

ABT_VAS = pd.DataFrame(ABT_VAS_REV)
current_qtr='2021Q3_AVG'
ABT_VAS_SUMMARY, ABT_VAS_RESULT=util.linear_roll_fwd(df=ABT_VAS, start_idx=4)
ABT_VAS_RESULT.to_excel("Alphas\ABT\ABT_VAS_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ABT_VAS_SUMMARY.to_excel('Alphas\ABT\ABT_VAS_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ABT_VAS)
#endregion ABT_VAS



#region ATEC 
# ATEC fiscal quarter is three quarters ahead
ATEC_REV = {'DATE' : ['2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2021Q2', '2020Q3', '2020Q4', # 
                      '2021Q1','2021Q2', '2021Q3'
                      ], # 
            'REVENUE' : [19.2, 20.4, 21, 23.1,
                         23, 26.1, 28.1, 31.1,
                         29.1, 28.8, 40.1, 43.1, # 
                         43.7, 61.9 , 52.2
                         ],
            'CONSENSUS' : [22.4, 20.5, 21.8, 20.7,
                           22.4, 24.3, 25.8, 29.4,
                           28.9, 15.7, 37.5,  43.1, # 
                           38.9, 45.2, 52.2
                           ], #
            'PROJ': [20.6, 22.1, 22.3, 21.3,
                     24.0, 25.2, 26.9, 29.1,
                     29.0, 26.9, 34.2, 44.6,
                     51.2, 50.5, 44.3
] # avg 
        #     'PROJ': [22.235206, 23.657686, 22.54716, 21.976701,
        #              23.560617, 26.95912, 28.415664, 28.824083,
        #              33.68101, 28.738979, 35.841671, 47.620229,
        #              52.08621, 53.49633] # SS 12_12                     
}

ATEC = pd.DataFrame(ATEC_REV)
current_qtr='2021Q3_AVG'
ATEC_SUMMARY, ATEC_RESULT=util.linear_roll_fwd(df=ATEC, start_idx=3)
ATEC_RESULT.to_excel("Alphas\ATEC\ATEC_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ATEC_SUMMARY.to_excel('Alphas\ATEC\ATEC_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ATEC)
#endregion ATEC

#region ATRC 
ATRC_REV = {'DATE' : ['2017Q3','2017Q4', # '2017Q2'
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1', '2020Q2','2020Q4', #'2020Q1', '2020Q2', '2020Q4', # 
                      '2021Q1','2021Q2', '2021Q3'
                      ], # 
            'REVENUE' : [33.4, 36.2, # 35.5, 
                         38.4, 40.8, 39.8, 43.1,
                         43.0, 47.2, 46.1, 49.5,
                         43.5, 33.7, 47.4, # 43.5, 33.7, 47.4, # 44.7
                         50.3, 60.1, 57.5
                         ], # 
            'CONSENSUS' : [34.6, 35.5, # 34.7,
                           36, 38.9, 38.2, 41.2,
                           43.1, 45.8, 43.9, 48.5,
                           45.2, 27.7, 47.3, # 45.2	, 27.7, 47.3, #39.9,
                           46, 50.4, 57.5
                           ], #
        #     'PROJ': [39.193279, 33.65633, 37.525089, 
        #              37.772671, 38.298101, 40.751306, 40.053213,
        #              39.394215, 47.355187, 53.392155, 57.500068,
        #              42.658584, 44.086436, 
        #              48.599638, 57.648047, 56.566451059]  # , 56.566451059 NSS 12_12
            'PROJ': [30.51400803, 34.790465, 
                     36.42977998, 38.97065712, 43.44964334, 39.11820341,
                     42.39087302, 51.68964634, 53.21718434, 49.64686544,
                     44.21609216, 34.85010384, 46.1961815,
                     52.25241707, 59.66498689, 63.5608
]  # , 58.97240038
                #      NSS 12_12 GR
}

current_qtr='2021Q3_NSS_12_12_GR_RMQ3'
ATRC = pd.DataFrame(ATRC_REV)
ATRC_SUMMARY, ATRC_RESULT=util.linear_roll_fwd(df=ATRC, start_idx=5)
ATRC_RESULT.to_excel("Alphas\ATRC\ATRC_RESULTS_{date}.xlsx".format(date=current_qtr), index=True)
ATRC_SUMMARY.to_excel('Alphas\ATRC\ATRC_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ATRC)
#endregion ATRC

#region BSX_CARDIO 
BSX_CARDIO_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                            '2018Q1','2018Q2','2018Q3','2018Q4',
                            '2019Q1','2019Q2','2019Q3','2019Q4',
                            '2020Q1', '2020Q2', #'2020Q3', '2020Q4',
                            '2021Q1','2021Q2', '2021Q3'
                            ],
            'REVENUE' : [424.00, 412.00, 438.00,
                         426.00, 448.00, 435.00, 453.00,
                         452.00, 473.00, 482.00, 587.00,
                         521.00, 378.00, #491, 479,
                         581.00,  656.00, 619.5
                         ],
            'CONSENSUS' : [381.1, 382, 382,
                           381.7, 407, 384.5, 368.5,
                           390.7, 388.7, 388.9, 436.5,
                           534.1, 365, #495.9, 521.5,
                           518.6, 604.9,619.5
                           ],
            'PROJ': [460.307603, 402.878083, 425.735366, 
                     387.264252, 451.72029, 440.135975, 506.019635,
                     475.497761, 482.832209, 473.415302, 550.85038,
                     497.615933, 389.006766, # 540.325571, 544.502032,
                     576.942131, 652.961361, 540.4827558
                     ] 
}

BSX_CARDIO = pd.DataFrame(BSX_CARDIO_REV)
current_qtr='2021Q3_NSS_LR_RMQ34'
BSX_CARDIO_SUMMARY, BSX_CARDIO_RESULT=util.linear_roll_fwd(df=BSX_CARDIO, start_idx=6)
BSX_CARDIO_RESULT.to_excel("Alphas\BSX\BSX_CARDIO_RESULTS_{date}.xlsx".format(date=current_qtr))
BSX_CARDIO_SUMMARY.to_excel('Alphas\BSX\BSX_CARDIO_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=BSX_CARDIO)
#endregion BSX_CARDIO

#region BSX_RN 
BSX_RN_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1','2020Q3','2020Q4', # , '2020Q2'
                        '2021Q1','2021Q2'#, '2021Q3'
                        ],
            'REVENUE' : [34.00, 34.00, 36.00,
                         35.00, 39.00, 37.00, 39.00,
                         36.00, 39.00, 38.00, 36.00,
                         32.00, 33.00, 32.00, # , 22.00
                         30.40, 34.00#, 35.9
],
            'CONSENSUS' : [32, 35, 34.6, 
                           34.4, 36.9, 38.5, 38.4,
                           38.5, 41.5, 39.7, 40.1, 
                           34.5, 32.5, 35.7, # , 18.4
                           31.5, 36.8#, 35.9
                           ],
            'PROJ': [31.533428, 34.437381, 36.830663, 
                     33.452687, 38.320472, 39.809615, 41.179221,
                     40.737647, 37.105825, 37.928157, 39.157766,
                     37.041061, 37.015242, 31.025501, # , 22.654258
                     31.231883, 33.876159# , 28.165655
                     ]  # SS NO LR
}

BSX_RN = pd.DataFrame(BSX_RN_REV)
BSX_RN_SUMMARY, BSX_RN_RESULT=util.linear_roll_fwd(df=BSX_RN, start_idx=6)
current_qtr='2021Q2_SS_NO_LR_RMQ2'
BSX_RN_RESULT.to_excel("Alphas\BSX\BSX_RN_RESULTS_{date}.xlsx".format(date=current_qtr))
BSX_RN_SUMMARY.to_excel('Alphas\BSX\BSX_RN_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=BSX_RN)
#endregion BSX_RN

#region BSX_MEDSG
BSX_MEDSG_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1','2020Q3','2020Q4', # , '2020Q2'
                        '2021Q1','2021Q2', '2021Q3'
                        ], # 
            'REVENUE' : [421.00, 410.00, 450.00, 
                         428.00, 458.00, 461.00, 498.00,
                         484.00, 518.00, 534.00, 548.00,
                         493.00 ,521.00 , 553.00, # ,  352.00
                         537.00, 601.00, 593.7
                         ], # 
            'CONSENSUS' : [426.1, 448.7, 474.8,
                           461.1, 438.7, 449.2, 494.8,
                           479.2, 509.1, 518.7, 561, 
                           495.2,473.3, 561.9, # ,  280.5
                           517.7, 577, 593.7
                           ], # 
            'PROJ': [435.5411104, 407.1159874, 445.3955762,
                     410.891953, 456.126791, 463.71849, 506.9072442,
                     486.052969, 521.524434, 504.9655762, 534.3168306,
                     491.3099192,526.9696666, 546.2211684, # ,  393.8860842
                     530.2461386, 581.6740886 , 578.3970907
]  # 
}

BSX_MEDSG = pd.DataFrame(BSX_MEDSG_REV)
BSX_MEDSG_SUMMARY, BSX_MEDSG_RESULT=util.linear_roll_fwd(df=BSX_MEDSG, start_idx=6)
current_qtr='2021Q3_AVG_RMQ2'
BSX_MEDSG_RESULT.to_excel("Alphas\BSX\BSX_MEDSG_RESULTS_{date}.xlsx".format(date=current_qtr))
BSX_MEDSG_SUMMARY.to_excel('Alphas\BSX\BSX_MEDSG_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=BSX_MEDSG)
#endregion BSX_MEDSG

#region BSX_NEUROMODULATION 
BSX_NEUROMODULATION_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q3','2020Q4', #'2020Q2'
                        '2021Q1','2021Q2', '2021Q3'
                        ],
            'REVENUE' : [125.00, 126.00, 150.00,
                         131.00, 160.00, 155.00, 177.00,
                         144.00, 160.00, 183.00, 208.00,
                         151.00, 176.00, 184.00,
                         151.00, 194.00, 190
                         ],
            'CONSENSUS' : [121.8, 125.8, 147.1, 
                           127.7, 141.8, 154, 180.7, 
                           156.2, 173.8, 171.4, 206.4,
                           155.6, 164.8, 201.5,
                           149.5, 171.80, 190
                           ],
            # 'PROJ': [129.6219703, 134.6751605, 153.0570223,
            #          136.658386, 158.6428363, 147.6890813, 162.3509653,
            #          153.3294795, 153.6809218, 169.0906973, 174.0930488,
            #          165.9739108, 147.9587698, 163.114514,
            #          147.9019578, 201.0428635, 186.6760642]  # average
            'PROJ': [130.243891, 118.904392, 141.572787,
                     129.902863, 153.094815, 133.238041, 156.388277,
                     144.152411, 153.330274, 165.592436, 183.788561,
                     160.139934, 159.60379, 182.3953,
                     148.422466, 201.810415, 178.701568
                     ]  # SS NO LR
}

BSX_NEUROMODULATION = pd.DataFrame(BSX_NEUROMODULATION_REV)
BSX_NEUROMODULATION_SUMMARY, BSX_NEUROMODULATION_RESULT=util.linear_roll_fwd(df=BSX_NEUROMODULATION, start_idx=6)
current_qtr='2021Q3_SS_NO_LR_RMQ2'
BSX_NEUROMODULATION_RESULT.to_excel("Alphas\BSX\BSX_NEUROMODULATION_RESULTS_{date}.xlsx".format(date=current_qtr))
BSX_NEUROMODULATION_SUMMARY.to_excel('Alphas\BSX\BSX_NEUROMODULATION_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=BSX_NEUROMODULATION)
#endregion BSX_NEUROMODULATION

#region CSII 
CSII_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q2', '2020Q4',
                        '2021Q1','2021Q2', '2021Q3'
                        ],
            'REVENUE' : [52.9, 49.7, 52.6, 
                         54.7, 57.7, 54.9, 58.6,
                         60.9, 65.7, 61.5, 66.0,
                         58.1, 40.5, 61.9, #, 58.8
                         59.6, 67.3,56
],
            'CONSENSUS' : [51.9, 53.3, 54, 
                           55.2, 35.5, 33.8, 54.5,
                           57.2, 60.9, 58.3, 65.9,
                           66.3, 37.1,  63.7, # 54.4,
                           60.1, 65.1,56
],
            'PROJ': [53.305367, 49.877791, 51.862489,
                     55.498578, 54.298037, 57.529834, 56.788315,
                     62.29604084, 63.66569955, 60.79759984, 65.21682646,
                     61.17, 44.09, 56.96, # 51.95,
                     60.09919071, 65.44697036, 61.308893
] 
}

CSII = pd.DataFrame(CSII_REV)
CSII_SUMMARY, CSII_RESULT=util.linear_roll_fwd(df=CSII, start_idx=6)
current_qtr='2021Q3_NSS_12_12'
CSII_RESULT.to_excel("Alphas\CSII\CSII_RESULTS_{date}.xlsx".format(date=current_qtr))
CSII_SUMMARY.to_excel('Alphas\CSII\CSII_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=CSII)
#endregion CSII

#region CNMD
CNMD_REV = {'DATE' : ['2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q3','2020Q4', # '2020Q1', '2020Q2',
                        '2021Q1', '2021Q2'#, '2021Q3'
                        ],
            'REVENUE' : [98.3, 113.3, 
                         106.3, 109.7, 107.5, 125.2, 
                         117.026, 129, 128.2, 142.5, 
                          134.2, 141.6, # 118.8, 87.4,
                         123.9, 143#, 141.3
],
            'CONSENSUS' : [97.7, 108.7, 
                           100.5, 105.1, 102.2, 117.1,
                           109.1, 121.8, 121.6, 142,
                            110.7, 144.9, # 122.5, 63.4,
                           118.6, 134.3#, 141.3
],
            'PROJ': [99.035426, 106.709141, 
                     104.321627, 112.469801, 103.745562, 115.619078,
                     109.586347, 113.782446, 121.236638, 141.666262,
                      137.441371, 151.96466, # 135.207113, 108.52392,
                     108.729853, 121.491911] # SS_NO_LR
        #     'PROJ': [103.3880455, 108.7976925,
        #              106.7046563, 119.293127, 109.723417, 122.5722803,
        #              114.4282233, 115.782361, 123.8167108, 145.5857698,
        #               144.800285, 152.546004, # 141.4748133, 118.1354945,
        #              113.3630558, 127.6920448#, 130.545107
        #              ] # Average
}

CNMD = pd.DataFrame(CNMD_REV)
CNMD_SUMMARY, CNMD_RESULT=util.linear_roll_fwd(df=CNMD, start_idx=4)
current_qtr='2021Q2_AVG_RMQ12'
CNMD_RESULT.to_excel("Alphas\CNMD\CNMD_RESULTS_{date}.xlsx".format(date=current_qtr))
CNMD_SUMMARY.to_excel('Alphas\CNMD\CNMD_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=CNMD)
#endregion CNMD

#region EW
EW_THV_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1','2020Q2','2020Q3','2020Q4',
                        '2021Q1','2021Q2','2021Q3'], # 
            'REVENUE' : [301.9, 297.7, 312.9,
                           331.4, 350.1, 343.8, 357.2,
                           368.1, 418, 448.2, 495.3,
                           480.7, 363.6, 471.7, 477.1,
                           480.6, 563.5, 565.8],
            'CONSENSUS' :[295.2, 297.4, 305,
                          339.1, 348.4, 348.4, 358.9,
                          370.5, 389.6, 400, 447.1,
                          463.2, 275.2, 451.3, 501.1,
                          479.4, 538.5, 565.8],
            'PROJ': [292.056518, 305.333684, 324.073661,
                     298.136291, 334.666464, 332.528713, 362.57546,
                     369.658673, 433.459823, 459.751296, 485.009335,
                     473.437584, 365.541644, 455.177833, 486.67915,
                     453.185308, 570.1759, 529.9632974
] # SS NO LR
        #     'PROJ': [312.229213, 309.4278648, 328.3105555,
        #              322.2280548, 352.980663, 365.0101058, 378.8583453,
        #              387.052133, 430.4380178, 450.25159, 487.9517008,
        #              479.729367, 397.9680253, 460.952262, 495.7411898,
        #              465.9994935, 577.6200635] # AVG  
}

EW_THV = pd.DataFrame(EW_THV_REV)
EW_THV_SUMMARY, EW_THV_RESULT=util.linear_roll_fwd(df=EW_THV, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
EW_THV_RESULT.to_excel("Alphas\EW\EW_THV_RESULTS_{date}.xlsx".format(date=current_qtr))
EW_THV_SUMMARY.to_excel('Alphas\EW\EW_THV_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=EW_THV)
#endregion EW

#region GMED
GMED_REV = {'DATE' : [#'2017Q2',
                        '2017Q3','2017Q4',
                        '2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q2','2020Q3','2020Q4',
                        '2021Q1','2021Q2', '2021Q3'
                        ],
            'REVENUE' : [#126.3, 
                         125.90, 137.10, 
                         132.90, 131.60, 135.50, 150.30,
                         141.30, 149.60, 150.40, 164.30,
                         151.90, 118.30, 173.50, 182.10,
                         181.90, 196.10, 177.9
                         ],
            'CONSENSUS' : [#127.8, 
                           126.3, 134.2,
                           130.3, 141.2, 140.1, 159,
                           154.2, 153.3, 153.9, 176.6,
                           155.8, 83, 164.1, 194.2,
                           165.8, 177.1, 177.9
                           ],
            # 'PROJ': [114.69, 144.33, 
            #          119.77, 133.67, 134.05, 142.64,
            #          148.80, 150.45, 152.22, 164.32,
            #          145.00, 121.49, 173.52, 192.18,
            #          167.08, 208.72,182.390096116471] # SS NO LR gr
            'PROJ': [#139.982171, 
                     127.113397, 145.716085, 
                     127.293206, 128.027443, 130.414018, 137.284226, 
                     135.913396, 144.710746, 147.241999, 160.871753, 
                     141.97221, 113.547165, 166.547296,184.481783, 
                     169.265911, 194.221795, 169.64659
                     ] # SS NO LR 
}

GMED = pd.DataFrame(GMED_REV)
GMED_SUMMARY, GMED_RESULT=util.linear_roll_fwd(df=GMED, start_idx=6)
current_qtr='2021Q3_SS_NO_LR_RM2017Q2'
GMED_RESULT.to_excel("Alphas\GMED\GMED_RESULTS_{date}.xlsx".format(date=current_qtr))
GMED_SUMMARY.to_excel('Alphas\GMED\GMED_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=GMED)
#endregion GMED

#region INSP
INSP_REV = {'DATE' : ['2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q2', '2020Q3','2020Q4',
                        '2021Q1','2021Q2', '2021Q3'
                        ],
            'REVENUE' : [8.70,  9.50 , 11.30 , 14.80 ,
                         14.40 , 15.80 , 18.60 , 24.90 ,
                         19.30 ,11, 33.1, 42.70 ,
                          37.80 , 49.40 , 51.7
                          ],
            'CONSENSUS' : [8.7, 8.2, 9.4, 12.2,
                           13.1, 14.7, 16.8, 21.3,
                           19.2, 7, 21, 39.4, 
                           34.1, 40.5, 51.7
                           ],
            'PROJ': [10.829697, 6.541515, 9.560399, 14.369297,
                     10.575539, 15.401618, 20.813879, 24.993203,
                     22.631636,10.60297, 29.868554, 44.44854,
                     35.76077, 43.818149, 58.94924
                     ]  # SS_NO_LR
}

INSP = pd.DataFrame(INSP_REV)
INSP_SUMMARY, INSP_RESULT=util.linear_roll_fwd(df=INSP, start_idx=5)
current_qtr='2021Q3_SS_NO_LR'
INSP_RESULT.to_excel("Alphas\INSP\INSP_RESULTS_{date}.xlsx".format(date=current_qtr))
INSP_SUMMARY.to_excel('Alphas\INSP\INSP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=INSP)
#endregion INSP

#region ISRG
ISRG_REV = {'DATE' : ['2018Q1','2018Q2','2018Q3','2018Q4',
                        '2019Q1','2019Q2','2019Q3','2019Q4',
                        '2020Q1', '2020Q2','2020Q3','2020Q4',
                        '2021Q1','2021Q2', '2021Q3'], #
            'REVENUE' : [337.6, 360.3, 368.1, 419.2,
                         407.4, 428.6, 450, 503.7,
                         444.4, 315.6, 467, 557.9,
                         500.8, 577.5, 544.6], #
            'CONSENSUS' : [322.1, 347.5, 363.6, 409.3,
                           390.9, 427.1, 432, 497.7, 
                           451.8, 243.7, 420, 520.8,
                           437.5, 489.7, 544.6], #
            'PROJ': [337.617763, 340.533852, 367.111166, 393.711618, # SS NO LR
                     389.418306, 393.123795, 460.920072, 510.993393,
                     458.799858, 330.689202, 449.267549, 559.730793,
                     500.606266, 561.012467, 524.784891]  #
        #     'PROJ': [365.6530364, 361.2155232, 380.7388296, 423.1988622,
        #              390.4818742, 416.675642, 467.9454752, 509.3249616,
        #              463.1652786, 356.0964954, 468.173142, 559.243104,
        #              517.4270528, 585.887929]  # avg , 515.4464064
}

current_qtr='2021Q3_SS_NO_LR'
ISRG = pd.DataFrame(ISRG_REV)
ISRG_SUMMARY, ISRG_RESULT=util.linear_roll_fwd(df=ISRG, start_idx=5)
ISRG_RESULT.to_excel("Alphas\ISRG\ISRG_RESULTS_{date}.xlsx".format(date=current_qtr))
ISRG_SUMMARY.to_excel('Alphas\ISRG\ISRG_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ISRG)
#endregion ISRG

#region KIDS
KIDS_REV = {'DATE' : ['2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1', '2020Q2','2020Q3','2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                        ],
            'REVENUE' : [9.6, 8.8, 
                         8.7, 11.5, 12.4, 10.9,
                         10.3, 13.8, 16.8, 14.2,
                         13.4, 12.1, 19.6, 17.9,
                         16.8, 21.7, 21.7
            ],
            'CONSENSUS' : [9.2, 8.8,
                           8.6, 10.9, 11.6, 10.9,
                           10.7, 14, 15.3, 14.1,
                           9.6, 8.9, 17.1, 17.4,
                           17, 20.3, 21.7
],
            'PROJ': [10.512836, 8.128757,
                     9.790157, 10.772716, 11.839888, 10.440819,
                     11.510742, 11.540955, 14.334566, 11.830688,
                     13.832916, 12.992255, 20.043105, 17.814846,
                     15.459056, 19.420445, 20.158825
                     ] # SS NO LR 
}

KIDS = pd.DataFrame(KIDS_REV)
KIDS_SUMMARY, KIDS_RESULT=util.linear_roll_fwd(df=KIDS, start_idx=5)
current_qtr='2021Q3_SS_NO_LR'
KIDS_RESULT.to_excel("Alphas\KIDS\KIDS_RESULTS_{date}.xlsx".format(date=current_qtr))
KIDS_SUMMARY.to_excel('Alphas\KIDS\KIDS_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=KIDS)
#endregion KIDS

#region LIVN_CARDIO 
LIVN_CARDIO_REV = {'DATE' : ['2018Q4',
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2' ,'2020Q3','2020Q4',
                             '2021Q1','2021Q2', '2021Q3'
                             ],
            'REVENUE' : [46,
                         43.5, 46.1, 43.7, 47.1,
                         40.2,28.3, 36.7, 39.8,
                         38.4, 39.6, 36.1
                         ],
            'CONSENSUS' : [50.9, 
                           44.8, 49.8, 47.6, 45.2, 
                           41, 26.3, 34.5, 41.7, 
                           35.5, 34.5, 36.1
                           ],
            'PROJ': [46.989101, 
                     44.96403, 43.702688, 44.353759, 45.829256,
                     38.575678, 28.399746, 35.873239, 40.217526,
                     39.141881, 42.851411, 35.478422
                     ] 
}

LIVN_CARDIO = pd.DataFrame(LIVN_CARDIO_REV)
current_qtr="2021Q3_SS_NO_LR"
LIVN_CARDIO_SUMMARY, LIVN_CARDIO_RESULT=util.linear_roll_fwd(df=LIVN_CARDIO, start_idx=4)
LIVN_CARDIO_RESULT.to_excel("Alphas\LIVN\LIVN_CARDIO_RESULTS_{date}.xlsx".format(date=current_qtr))
LIVN_CARDIO_SUMMARY.to_excel('Alphas\LIVN\LIVN_CARDIO_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=LIVN_CARDIO)
#endregion LIVN_CARDIO

#region LIVN_NEUROMOD 
LIVN_NEUROMOD_REV = {'DATE' : ["2017Q4",
                               '2018Q1','2018Q2','2018Q3','2018Q4',
                               '2019Q1','2019Q2','2019Q3','2019Q4',
                               '2020Q1', '2020Q4',
                               '2021Q1','2021Q2', '2021Q3'
                               ],
            'REVENUE' : [85.6, 
                         78, 89.4, 87.2, 94.4,
                         76.9, 80.6, 88.4, 89.5,
                         73.3, 85.2,
                         82.3, 91.8, 89.9
                         ],
            'CONSENSUS' : [84.6, 
                           79.6, 88.6, 84.1, 91.7,
                           78.8, 75.3, 79.4, 91.1,
                           76.4, 84.5,
                           72.8, 81, 89.9
                           ],
            # 'PROJ': [77.079218, 
            #          62.094912, 82.380222, 93.684644, 91.718652, 
            #          64.796487, 82.592423, 93.530482, 94.752853,
            #          69.17027, 41.479636, 88.036068, 
            #          80.035042, 86.134301] ## ss no lr
            'PROJ': [89.3349638, 
                     76.4732516, 84.0546364, 93.3485324, 102.022689,
                     85.1835834, 84.3522852, 88.6003144, 94.6237974,
                     81.9310082, 77.1637746,
                     82.5331784, 82.9669444, 87.522142
                     ] ## avg          
}

LIVN_NEUROMOD = pd.DataFrame(LIVN_NEUROMOD_REV)
LIVN_NEUROMOD_SUMMARY, LIVN_NEUROMOD_RESULT=util.linear_roll_fwd(df=LIVN_NEUROMOD, start_idx=4)
current_qtr='2021Q3_AVG_RMQ23'
LIVN_NEUROMOD_RESULT.to_excel("Alphas\LIVN\LIVN_NEUROMOD_RESULTS_{date}.xlsx".format(date=current_qtr))
LIVN_NEUROMOD_SUMMARY.to_excel('Alphas\LIVN\LIVN_NEUROMOD_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=LIVN_NEUROMOD)
#endregion LIVN_NEUROMOD

#region LIVN_ACS 
LIVN_ACS_REV = {'DATE' : ['2018Q4',
                             '2019Q1','2019Q2','2019Q3','2019Q4',
                             '2020Q1','2020Q2' ,'2020Q3','2020Q4',
                             '2021Q1','2021Q2', '2021Q3'
                             ],
            'REVENUE' : [7.2,
                         8, 7.9, 6.3, 8.5,
                         10.1, 5.7, 12.3, 13,
                         12.6, 13,13.4
                         ],
            'CONSENSUS' : [6.4, 
                     7.6,7.9, 8.2, 8.6,
                     9.3, 9.4, 9.4, 13.4,
                     12.1, 12.9, 13.4
            ],
            'PROJ': [8.6083525, 
                     11.855845, 7.580439, 7.235162333, 6.74784075,
                     9.72954825, 14.30122625, 7.463214, 8.75512975,
                     12.58972125, 14.7586415, 13.696527
] 
}

LIVN_ACS = pd.DataFrame(LIVN_ACS_REV)
LIVN_ACS_SUMMARY, LIVN_ACS_RESULT=util.linear_roll_fwd(df=LIVN_ACS, start_idx=4)
current_qtr='2021Q3_AVG'
LIVN_ACS_RESULT.to_excel("Alphas\LIVN\LIVN_ACS_RESULTS_{date}.xlsx".format(date=current_qtr))
LIVN_ACS_SUMMARY.to_excel('Alphas\LIVN\LIVN_ACS_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=LIVN_ACS)
#endregion LIVN_ACS

#region LUNG
#endregion LUNG

#region MMSI_CARDIO 
MMSI_CARDIO_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                             '2018Q1','2018Q2','2018Q3','2018Q4',
                             '2019Q1','2019Q2', #'2019Q4', #'2019Q3',
                             '2020Q1', '2021Q2','2020Q3', '2020Q4',
                             '2021Q1','2021Q2'#, '2021Q3'
                             ], #
            'REVENUE' : [101.394, 96.702, 100.228, 
                         103.137, 116.324, 116.879, 127.884,
                         130.492, 136.113, #140.84, #  135.671,
                         133.487, 112.302, 136.016, 140.407,
                         133.889, 151.264#, 141.568
                         ], # 
            'CONSENSUS' : [105.5, 100, 101.6, 
                           104.1, 114.9, 113.4, 122.3,
                           128.9, 135.8, # 142.9, # 135,
                           133.1, 96.2, 119.9, 136.4,
                           126.9, 134.1#, 141.568
                           ], # 
            # 'PROJ': [87.178279, 91.342507, 100.733727,
            #          105.84968, 109.7528, 119.020125, 133.414613,
            #          132.795618, 152.609214, 97.471471, 141.68403,
            #          135.417887, 122.063973, 141.096298, 149.815104,
            #          148.061681, 145.165018]  # SS NO LR
        #     'PROJ': [72.96982, 65.24264, 67.038315, 
        #              69.716635, 74.275135, 78.517891, 98.009578, 
        #              88.99094, 112.555032, 95.024424, 100.287091, 
        #              91.620923, 87.516848, 100.283298, 101.454444,
        #              106.724689, 102.553728]  # , 93.108445  
        #              #NSS_LR            # 
            'PROJ': [86.38212125, 89.1167085, 98.21522525,
                     102.7441553, 108.6671125, 115.2687958, 125.2535798,
                     130.7947898, 133.6694518, # 112.0790535, # 96.866507,
                     129.7156473, 118.5965428, 138.9394075,137.9500002,
                     137.0661206, 135.1688316#, 142.9319698
                     ]  # AVG         
}

MMSI_CARDIO = pd.DataFrame(MMSI_CARDIO_REV)
MMSI_CARDIO_SUMMARY, MMSI_CARDIO_RESULT=util.linear_roll_fwd(df=MMSI_CARDIO, start_idx=6)
current_qtr='2021Q2_AVG_RM19Q34'
MMSI_CARDIO_RESULT.to_excel("Alphas\MMSI\MMSI_CARDIO_RESULTS_{date}.xlsx".format(date=current_qtr))
MMSI_CARDIO_SUMMARY.to_excel('Alphas\MMSI\MMSI_CARDIO_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=MMSI_CARDIO)
#endregion MMSI_CARDIO

#region MMSI_END 
MMSI_END_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                             '2018Q1','2018Q2','2018Q3','2018Q4',
                             '2019Q1','2019Q2', '2019Q3','2019Q4',
                             '2020Q1','2020Q3', '2020Q4',
                             '2021Q1','2021Q2', '2021Q3'
                             ], #
            'REVENUE' : [6.712, 6.389, 7.161, 
                         6.918, 8.121, 9.229, 7.921,
                         7.568, 8.549, 8.34, 8.138,
                         7.578, 7.093, 7.349,
                         7.473, 7.507, 7.614
                         ], #
            'CONSENSUS' : [6.4, 7, 7.3, 
                           7.1, 7.6, 8.2, 9.1, 
                           8.2, 9.3, 9.9, 8.6,
                           7.8, 6.7, 7.1,
                           7.3, 7.83, 7.614
                           ], # 
            'PROJ': [7.002645, 6.552864, 7.119023,
                     8.008946, 7.21452, 8.172533, 8.01083,
                     8.346753, 9.445482, 8.216777, 9.512061,
                     8.614649, 7.807427, 7.108591,
                     6.64211, 7.549224, 7.97077383513712
                     ]  # 
                     # SS_LR
        #     'PROJ': [7.002645, 6.552864, 7.119023,
        #              8.008946, 7.21452, 8.172533, 8.01083,
        #              8.346753, 9.445482, 8.216777, 9.043447,
        #              7.807427, 7.108591,
        #              6.64211, 7.549224, 7.99091809546936] # AVG 
}

MMSI_END = pd.DataFrame(MMSI_END_REV)
MMSI_END_SUMMARY, MMSI_END_RESULT=util.linear_roll_fwd(df=MMSI_END, start_idx=6)
current_qtr='2021Q3_SS_LR_RMQ2'
MMSI_END_RESULT.to_excel("Alphas\MMSI\MMSI_END_RESULTS_{date}.xlsx".format(date=current_qtr))
MMSI_END_SUMMARY.to_excel('Alphas\MMSI\MMSI_END_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=MMSI_END)
#endregion MMSI_END

#region NARI
#endregion NARI

#region NUVA
NUVA_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2', '2020Q3', '2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [142.8, 136.5, 149.8, 
                         141.5, 150.8, 146.1, 156.6,
                         147.8, 160.2, 160, 168.9,
                         138.5, 113.8, 161.2, 155.2,
                         145.3, 160.1, 157.1
],
            'CONSENSUS' : [146.9, 140.6, 150.7, 
                           138.3, 144.1, 139.4, 157.2,
                           145.1, 153.9, 150.4, 165.9,
                           151.8, 87.3, 143, 162.8,
                           137.6, 154.5, 157.1
                           ],
            'PROJ': [146.0151657, 138.5088693, 153.1020813,
                     148.5055823, 151.95275, 152.6891793, 150.6170733,
                     150.4880627, 158.5622553, 162.334849, 181.374094,
                     144.4272777, 107.4497607, 150.0413537, 153.8458027,
                     138.415219, 165.9479957, 155.1177237
                     ]# AVG
}

NUVA = pd.DataFrame(NUVA_REV)
NUVA_SUMMARY, NUVA_RESULT=util.linear_roll_fwd(df=NUVA, start_idx=6)
current_qtr='2021Q3_AVG'
NUVA_RESULT.to_excel("Alphas\\NUVA\\NUVA_RESULTS_{date}.xlsx".format(date=current_qtr))
NUVA_SUMMARY.to_excel('Alphas\\NUVA\\NUVA_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=NUVA)
#endregion NUVA

#region PEN_PERI
PEN_PERI_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2','2020Q4', # '2020Q3',
                      '2021Q1','2021Q2' , '2021Q3'
                      ],
            'REVENUE' : [21.1, 21.8, 24.2, 
                         25.7, 29.2, 31.4, 36.1,
                         36.5, 41.8, 45.6, 49.9,
                         50.7, 39.4, 65.4, #76.8,
                         75.9, 84.2, 82.3
                         ],
            'CONSENSUS' : [23.7, 24.3, 26.8, 
                           25.8, 28.5, 28.9, 33.8,
                           36.3, 39.6, 39.2, 45.6,
                           40.6, 27.6, 71.1, #   45.8,
                           71.7, 76.2 , 82.3
                           ],
            'PROJ': [21.569503, 18.476145, 22.252935,
                     23.473988, 29.3961, 32.984333, 36.283174,
                     40.486242, 41.786252, 45.458795, 50.771913,
                     52.133781, 37.497847,  74.06526, #57.524785,
                     78.438134, 95.395509 , 87.065164
                     ] ## SS NO LR
}

PEN_PERI = pd.DataFrame(PEN_PERI_REV)
PEN_PERI_SUMMARY, PEN_PERI_RESULT=util.linear_roll_fwd(df=PEN_PERI, start_idx=6)
current_qtr='2021Q3_SS_NO_LR_RMQ3'
PEN_PERI_RESULT.to_excel("Alphas\PEN\PEN_PERI_RESULTS_{date}.xlsx".format(date=current_qtr))
PEN_PERI_SUMMARY.to_excel('Alphas\PEN\PEN_PERI_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=PEN_PERI)
#endregion PEN_PERI

#region PEN_NEURO
PEN_NEURO_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2', '2020Q3', '2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [31.9, 33.5, 37.1, 
                         39.7, 41.6, 41.1, 43.7,
                         45.4, 44.6, 44.7, 46.2,
                         44.4, 38.1, 44.3, 40,
                         43.4, 43.4, 46
                         ],
            'CONSENSUS' : [27.2, 27.6, 31.3,
                           34.3, 37.9, 37.3, 40.3,
                           43.9, 44.7, 47.2, 46.6,
                           44.8, 34.1, 36.3, 25.8,
                           40.1, 44, 46
                           ],
            'PROJ': [32.874216, 32.709141, 37.935437,
                     42.251004, 37.443665, 41.04614, 44.765534,
                     43.990313, 47.752837, 45.818938, 46.722229,
                     45.996594, 38.449043, 42.535157, 43.599046,
                     43.887762, 45.86029 , 43.580936
                     ] ##SS_NO_LR

}

PEN_NEURO = pd.DataFrame(PEN_NEURO_REV)
PEN_NEURO_SUMMARY, PEN_NEURO_RESULT=util.linear_roll_fwd(df=PEN_NEURO, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
PEN_NEURO_RESULT.to_excel("Alphas\\PEN\\PEN_NEURO_RESULTS_{date}.xlsx".format(date=current_qtr))
PEN_NEURO_SUMMARY.to_excel('Alphas\\PEN\\PEN_NEURO_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=PEN_NEURO)
#endregion PEN_NEURO

#region SIBN
SIBN_REV = {'DATE' : ['2018Q4',
                      '2019Q1','2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2' ,'2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [14.3, 
                         13.5, 15, 14.9, 18.3, 
                         15.3, 13, 20.6,
                         18.8, 20.2, 20.80
],
            'CONSENSUS' : [13.9, 
                           13.6, 14.6, 14.9, 18.1,
                           16.1, 13.2, 20.8,
                           17.4, 20.3, 20.80
],
            'PROJ': [14.20977633, 
                     12.241336, 13.400415, 11.29006533, 15.69551933,
                     15.79871767, 15.4969078, 18.20015733,
                     18.76652533, 22.16137667, 22.85103575]# average
}

SIBN = pd.DataFrame(SIBN_REV)
SIBN_SUMMARY, SIBN_RESULT=util.linear_roll_fwd(df=SIBN, start_idx=4)
current_qtr='2021Q3_AVG'
SIBN_RESULT.to_excel("Alphas\SIBN\SIBN_RESULTS_{date}.xlsx".format(date=current_qtr))
SIBN_SUMMARY.to_excel('Alphas\SIBN\SIBN_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SIBN)
#endregion SIBN

#region SILK
SILK_REV = {'DATE' : ['2019Q3','2019Q4',
                      '2020Q1','2020Q2' ,'2020Q3','2020Q4',
                      '2021Q1','2021Q2','2021Q3'
                      ],
            'REVENUE' : [17, 18.6, 
                         18.9, 15.1, 20.1, 21.1, 
                         22.1, 26.5, 26.2
                         ],
            'CONSENSUS' : [15.9, 17.9, 
                           17.5, 9.3, 20.6, 21.4,
                           21.3, 25.4, 26.2
                           ],
            'PROJ': [16.555177, 20.95882, 
                     20.977809, 13.935155, 20.327735, 21.447908,
                     23.166477, 24.808459, 24.6641841
                     ]  ## SS NO LR
}

SILK = pd.DataFrame(SILK_REV)
SILK_SUMMARY, SILK_RESULT=util.linear_roll_fwd(df=SILK, start_idx=4)
current_qtr='2021Q3_SS_NO_LR'
SILK_RESULT.to_excel("Alphas\SILK\SILK_RESULTS_{date}.xlsx".format(date=current_qtr))
SILK_SUMMARY.to_excel('Alphas\SILK\SILK_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SILK)
#endregion SILK

#region SNN_AWM 
SNN_AWM_REV = {'DATE' : ['2017Q3','2017Q4', #'2017Q2'
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q3', '2020Q4', # '2020Q2',
                      '2021Q1','2021Q2'#,  '2021Q3'
                      ],
            'REVENUE' : [136.5, 149.8,  # 142.8,
                         141.5, 150.8, 146.1, 156.6, 
                         147.8, 160.2, 160, 168.9, 
                         138.5, 161.2, 155.2,  # 113.8,
                         145.3 , 160.1#,190.2392418
                         ],
            'CONSENSUS' : [140.6, 150.7,  # 146.9,
                           138.3, 144.1, 139.4, 157.2, 
                           145.1, 153.9, 150.4, 165.9, 
                           151.8,  143, 162.8, # 87.3,
                           137.6, 154.5 #, 190.2392418
                           ],
            'PROJ': [148.9053262, 149.5822524, 
                     133.6606911, 153.3217884, 164.0473869, 150.8736619,
                     156.1681274, 147.3901274, 176.9974073, 177.4923464,
                     163.4870217,  130.7400176, 163.4199032, # 122.1794506,
                     162.2346414, 150.1345273#, 170.3387067
                     ] ## NSS_12_03_LR_GR

}

SNN_AWM = pd.DataFrame(SNN_AWM_REV)
SNN_AWM_SUMMARY, SNN_AWM_RESULT=util.linear_roll_fwd(df=SNN_AWM, start_idx=5)
current_qtr='2021Q2_NSS_LR_GR_RMQ2'
SNN_AWM_RESULT.to_excel("Alphas\\SNN\\SNN_AWM_RESULTS_{date}.xlsx".format(date=current_qtr))
SNN_AWM_SUMMARY.to_excel('Alphas\\SNN\\SNN_AWM_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SNN_AWM)
#endregion SNN_AWM

#region SNN_REC 
SNN_REC_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4', #
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q3', '2020Q4', # '2020Q2',
                      '2021Q1','2021Q2',  '2021Q3'
                      ],
            'REVENUE' : [258.9, 233.8, 273.5, 
                         248.0, 259.9, 246.0, 286.6,
                         258.1, 273.2, 262.4, 308.7,
                         254.6,  268.6, 282.9, # 177.7,
                         273.4, 282.4, 286.2627961
                         ],
            'CONSENSUS' : [259.0, 242.2, 287.9,
                           268.2, 269.7, 237.4, 273.9,
                           263.5, 260.1, 254.8, 292.8,
                           273.9,  246.8, 305.4, # 160.0,
                           235.5, 259.2, 286.2627961
                           ],
            'PROJ': [247.907928, 238.883569, 247.724826,
                     261.91146, 253.94561, 242.615351, 254.579728,
                     268.399838, 275.084432, 271.085658, 284.415838,
                     271.373095,  224.775093, 259.077875, # 213.921474,
                     205.444937, 222.849967, 258.789032
                     ] ## NSS_12_12

}
SNN_REC = pd.DataFrame(SNN_REC_REV)
SNN_REC_SUMMARY, SNN_REC_RESULT=util.linear_roll_fwd(df=SNN_REC, start_idx=5)
current_qtr='2021Q3_NSS_12_12_RMQ2'
SNN_REC_RESULT.to_excel("Alphas\\SNN\\SNN_REC_RESULTS_{date}.xlsx".format(date=current_qtr))
SNN_REC_SUMMARY.to_excel('Alphas\\SNN\\SNN_REC_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SNN_REC)
#endregion SNN_REC

#region SNN_SMT 
SNN_SMT_REV = {'DATE' : ['2017Q3','2017Q4', #'2017Q2'
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1','2020Q2', '2020Q3', '2020Q4', # 
                      '2021Q1','2021Q2',  '2021Q3'
                      ],
            'REVENUE' : [158.9, 186.3, 
                         164.9, 174.1, 167.6, 193.5,
                         174.0, 187.5, 182.8, 218.1, 
                         168.0, 120.6, 183.7, 211.9,
                         188.8, 198.3, 196.5926023
                         ],
            'CONSENSUS' : [164.6259896, 196.1257633, 
                           178.3282489, 180.7175293, 161.6990244, 184.92287,
                           177.6150454, 178.523032, 177.5050165, 206.938033,
                           180.7368375, 108.6262626, 168.7723977, 228.8247454,
                           162.7024761, 181.9531051, 196.5926023
                           ],
            'PROJ': [144.2814299, 203.4795957,
                     144.3695814, 159.8290724, 159.3868799, 194.232628,
                     196.2714866, 182.8582244, 171.2985904, 219.0976416,
                     184.3869175, 111.4786436, 180.1921478, 210.4042342,
                     188.6905858, 205.1911147, 184.4047896
                     ] ## SS_NO_LR_GR

}

SNN_SMT = pd.DataFrame(SNN_SMT_REV)
SNN_SMT_SUMMARY, SNN_SMT_RESULT=util.linear_roll_fwd(df=SNN_SMT, start_idx=5)
current_qtr='2021Q3_SS_NO_LR'
SNN_SMT_RESULT.to_excel("Alphas\\SNN\\SNN_SMT_RESULTS_{date}.xlsx".format(date=current_qtr))
SNN_SMT_SUMMARY.to_excel('Alphas\\SNN\\SNN_SMT_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SNN_SMT)
#endregion SNN_SMT

#region SWAV
SWAV_REV = {'DATE' : ['2019Q2','2019Q3','2019Q4',
                      '2020Q1','2020Q2', '2020Q3' ,'2020Q4',
                      '2021Q1','2021Q2'#, '2021Q3'
                      ],
            'REVENUE' : [5.2, 6.2, 7.6, 
                         7.8, 5.5, 11.1, 12.7,
                         21, 42.9#, 48.2
],
            'CONSENSUS' : [4.4, 5.6, 7.2,
                           7.8, 4.6, 8.5, 11.8,
                           19.7, 33.3#, 48.2
],
            'PROJ': [5.297114, 5.0896794, 6.1586502,
                     7.2767034, 7.181866, 9.3418472, 11.8956772,
                     18.181186, 35.7340326#, 47.620132
]# average
}

SWAV = pd.DataFrame(SWAV_REV)
SWAV_SUMMARY, SWAV_RESULT=util.linear_roll_fwd(df=SWAV, start_idx=4)
current_qtr='2021Q3_AVG'
SWAV_RESULT.to_excel("Alphas\SWAV\SWAV_RESULTS_{date}.xlsx".format(date=current_qtr))
SWAV_SUMMARY.to_excel('Alphas\SWAV\SWAV_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SWAV)
#endregion SWAV


#region SYK_MEDSG 
SYK_MEDSG_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2', '2020Q3','2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [1058, 1052, 1220,
                         1106, 1140, 1157, 1340,
                         1237, 1302, 1263, 1448,
                         1294, 1015.56, 1269, 1469,
                         1242, 1368, 1360.20],
            'CONSENSUS' : [1039.70, 1014.90, 1210.80,
                           1103.50, 1134.30, 1134.60, 1337.50,
                           1200.00, 1242.70, 1282.10, 1458.80,
                           1269.80, 1083.00, 1206.50, 1476.10,
                           1328.40, 1345.5, 1360.20
                           ],
        #     'PROJ': [1179.436436, 1155.309068, 1117.513254,
        #              1089.432275, 1172.602964, 1108.647159, 1347.119808,
        #              1244.285296, 1425.712411, 1328.943557, 1483.322387,
        #              1272.855431, 1087.787873, 1335.332793, 1434.528164,
        #              1354.52483, 1427.982728, 1369.50571
        #              ] # maybe remove Q2 # avg
            'PROJ': [1105.525903, 1102.62401, 1050.678694, 
                     1041.193202, 1106.194794, 1053.980117, 1289.261978,
                     1205.185854, 1390.544797, 1285.774208, 1448.737428,
                     1254.265445, 1038.069636, 1288.539141, 1384.65113,
                     1292.080341, 1391.527629, 1300.114781
                     ] # maybe remove Q2 # SS_NO_LR
                     #1375.4

}

SYK_MEDSG = pd.DataFrame(SYK_MEDSG_REV)
SYK_MEDSG_SUMMARY, SYK_MEDSG_RESULT=util.linear_roll_fwd(df=SYK_MEDSG, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
SYK_MEDSG_RESULT.to_excel('Alphas\SYK\SYK_MEDSG_RESULTS_{date}.xlsx'.format(date=current_qtr))
SYK_MEDSG_SUMMARY.to_excel('Alphas\SYK\SYK_MEDSG_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SYK_MEDSG)
#endregion SYK_MEDSG

#region SYK_NNS 
SYK_NNS_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q3','2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [364, 361, 419, 
                         394, 424, 426, 478,
                         492, 519, 509, 568, 
                         497, 542, 568,
                         528, 588, 579.70
                         ],
            'CONSENSUS' : [347.9, 342, 364.1,
                           328.3, 383.5, 395.8, 444.2,
                           469.9, 524.1, 526.1, 559.5,
                           521.4, 471.8, 578.8,
                           525.9, 556.6, 579.70
                           ],
            'PROJ': [398.7209163, 404.1195873, 388.04246,
                     390.5824625, 421.3357003, 425.9753278, 478.4365813,
                     495.1471903, 545.1014655, 489.7801188, 526.3376355,
                     502.0270505, 509.7415969, 549.9647328,
                     518.156396, 563.1385443, 567.7652603
                     ] # avg

}

SYK_NNS = pd.DataFrame(SYK_NNS_REV)
SYK_NNS_SUMMARY, SYK_NNS_RESULT=util.linear_roll_fwd(df=SYK_NNS, start_idx=6)
current_qtr='2021Q3_AVG'
SYK_NNS_RESULT.to_excel("Alphas\SYK\SYK_NNS_RESULTS_{date}.xlsx".format(date=current_qtr))
SYK_NNS_SUMMARY.to_excel('Alphas\SYK\SYK_NNS_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SYK_NNS)
#endregion SYK_NNS

#region SYK_KNEE 
SYK_KNEE_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2',  '2020Q4', # '2020Q3',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [282, 270, 331, 
                         301, 304, 291, 348,
                         320, 324, 318, 385,
                         322, 179,  336.9, # 332,
                         294, 349, 339.20
],
            'CONSENSUS' : [279.8, 273.1, 324.4,
                           302.9, 304.7, 286.3, 352.7,
                           320, 321.6, 308, 371.1, 
                           317.1,166.7, 390.1, #  286,
                           314.8, 325.1, 339.20
],
            'PROJ': [295.485783, 282.11059, 318.131987,
                     272.223014, 293.433847, 285.276206, 301.629611,
                     272.780806, 313.671511, 317.742294, 401.426058,
                     324.935253, 188.035358,  318.475221, # 285.7385326,
                     290.969217, 353.668058,  322.120197276
                     ]
}

SYK_KNEE = pd.DataFrame(SYK_KNEE_REV)
SYK_KNEE_SUMMARY, SYK_KNEE_RESULT=util.linear_roll_fwd(df=SYK_KNEE, start_idx=6)
current_qtr='2021Q3_NSS_12_12_RMQ3'
SYK_KNEE_RESULT.to_excel("Alphas\SYK\SYK_KNEE_RESULTS_{date}.xlsx".format(date=current_qtr))
SYK_KNEE_SUMMARY.to_excel('Alphas\SYK\SYK_KNEE_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SYK_KNEE)
#endregion SYK_KNEE

#region SYK_HIP 
SYK_HIP_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q4', #  
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [203, 194, 219,
                         205, 207, 198, 228,
                         213, 219, 211, 239,
                         201, 140, 213, # 
                         186.3, 221, 221.80
],
            'CONSENSUS' : [203.8, 201.3, 226.9, 
                           211, 210.8, 204.5, 228.9,
                           215.1, 214.7, 208.2, 241.3,
                           210.8, 114.7, 248.5, # 
                           201.2, 221.4, 221.80
                        ],
            'PROJ': [209.084022, 197.573532, 203.544789, 
                     194.277516, 208.819904, 195.172466, 214.719985,
                     221.854961, 225.289266, 213.766413, 244.405024, 
                     208.547909, 147.348876, 228.218092, # 
                     193.643748, 182.436614, 170.9280682
] # SS_NO_LR

}

SYK_HIP = pd.DataFrame(SYK_HIP_REV)
SYK_HIP_SUMMARY, SYK_HIP_RESULT=util.linear_roll_fwd(df=SYK_HIP, start_idx=6)
current_qtr='2021Q3_SS_NO_LR_RMQ3'
SYK_HIP_RESULT.to_excel("Alphas\SYK\SYK_HIP_RESULTS_{date}.xlsx".format(date=current_qtr))
SYK_HIP_SUMMARY.to_excel('Alphas\SYK\SYK_HIP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SYK_HIP)
#endregion SYK_HIP

#region SYK_TE 
SYK_TE_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2', '2020Q3','2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [228, 237, 257,
                         245, 242, 242, 272,
                         254, 252, 262, 283,
                         260, 208, 285, 386,
                         440, 475, 476.30
],
            'CONSENSUS' : [228, 242.3, 254.4, 
                           251, 258.2, 259.6, 270.6,
                           267.3, 261.6, 265.5, 290.5,
                           260, 170.2, 252.1, 366,
                           434, 451.7 , 476.30
],
            'PROJ': [203.428745, 228.285539, 247.008679,
                     228.581112, 239.598366, 223.715611, 268.66537,
                     266.382822, 256.094073, 258.874794, 297.440058,
                     272.825051, 210.55343, 269.1678885, 393.64087,
                     403.956901, 443.110523, 416.945642232871
                     ] # SS_NO_LR

}

SYK_TE = pd.DataFrame(SYK_TE_REV)
SYK_TE_SUMMARY, SYK_TE_RESULT=util.linear_roll_fwd(df=SYK_TE, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
SYK_TE_RESULT.to_excel("Alphas\SYK\SYK_TE_RESULTS_{date}.xlsx".format(date=current_qtr))
SYK_TE_SUMMARY.to_excel('Alphas\SYK\SYK_TE_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=SYK_TE)
#endregion SYK_TE


#region VAPO_CAP
VAPO_CAP_REV = {'DATE' : ['2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3' ,'2020Q4',
                           '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [2.2, 1.9, 1.9, 1.9,
                         4.2, 15.8, 14.4, 17.4,
                         8, 2.5,3.23245
],
            'CONSENSUS' : [0.393745, 0.253187, 0.711872, 0.475597,
                           1.397344, 3.061977, 1.561457, 4.277644,
                           2.777235, 0.632496, 3.23245
                           ],
            'PROJ': [0.393745, 0.253187, 0.711872, 0.475597,
                     1.397344, 3.061977, 1.561457, 4.277644,
                     2.777235, 0.632496,  3.23245
] 
}

VAPO_CAP = pd.DataFrame(VAPO_CAP_REV)
VAPO_CAP_SUMMARY, VAPO_CAP_RESULT=util.linear_roll_fwd(df=VAPO_CAP, start_idx=3)
current_qtr='2021Q3_SS_NO_LR'
VAPO_CAP_RESULT.to_excel("Alphas\VAPO\VAPO_CAP_RESULTS_{date}.xlsx".format(date=current_qtr))
VAPO_CAP_SUMMARY.to_excel('Alphas\VAPO\VAPO_CAP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=VAPO_CAP)
#endregion VAPO_CAP

#region VAPO_DISP
VAPO_DISP_REV = {'DATE' : ['2019Q1','2019Q2','2019Q3','2019Q4',
                           '2020Q1','2020Q2','2020Q3' ,'2020Q4',
                           '2021Q1','2021Q2'#, '2021Q3'
                      ],
            'REVENUE' : [7.5, 6.5, 6, 7.7,
                         9.7, 9.4, 10.4, 15,
                         12.5, 7.3
],
            'CONSENSUS' : [6.455656, 6.537524, 6.944115, 8.763934,
                           9.988595, 9.540203, 9.739466, 11.507653,
                           11.280688, 9.605593 #, 15.807045
                           ],
            'PROJ': [6.41349, 6.167831, 5.950069, 8.454262,
                     10.110397, 8.833284, 9.527201, 11.406402,
                     10.763881, 8.171288#, 17.100716

] 
}

VAPO_DISP = pd.DataFrame(VAPO_DISP_REV)
VAPO_DISP_SUMMARY, VAPO_DISP_RESULT=util.linear_roll_fwd(df=VAPO_DISP, start_idx=3)
current_qtr='2021Q2_SS_NO_LR'
VAPO_DISP_RESULT.to_excel("Alphas\VAPO\VAPO_DISP_RESULTS_{date}.xlsx".format(date=current_qtr))
VAPO_DISP_SUMMARY.to_excel('Alphas\VAPO\VAPO_DISP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=VAPO_DISP)
#endregion VAPO_DISP

#region XENT
XENT_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1', '2020Q2', '2020Q3','2020Q4',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [23.8, 22.2, 29.3, 
                         24.4, 25.5, 23.4, 30.9, 
                         24.9, 24.8, 22.9, 29.5,
                         18.5, 9.2, 20.1, 23.3,
                         19.5, 21.6,27.3
                         ],
            'CONSENSUS' : [25.7, 21.3, 27.9, 
                           23.7, 27.9, 24.1, 32,
                           26, 26.8, 23.9, 30.4, 
                           22.7, 4.4, 20.8, 26.5,
                           21.8, 25.6, 27.3
                           ],
            'PROJ': [22.644805, 25.367766, 33.117342, 
                     21.735882, 23.137768, 24.444399, 24.795833,
                     22.573627, 25.856438, 22.568064, 31.39359,
                     19.948632, 7.728248, 17.415381, 21.519392,
                     17.992315, 21.312121, 20.014593
                     ]

}

XENT = pd.DataFrame(XENT_REV)
XENT_SUMMARY, XENT_RESULT=util.linear_roll_fwd(df=XENT, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
XENT_RESULT.to_excel("Alphas\\XENT\\XENT_RESULTS_{date}.xlsx".format(date=current_qtr))
XENT_SUMMARY.to_excel('Alphas\\XENT\\XENT_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=XENT)
#endregion XENT

#region ZBH HIPS
ZBH_HIP_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3', '2020Q4', #  
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [245, 228, 256, 
                         248, 250, 240, 259,
                         247, 253, 249,267, 
                         233, 170.7, 268.6, 269.7,
                         235.2,258.1 ,258.20
                        ],
            'CONSENSUS' : [245.9, 236.3, 246.6,
                           240.9, 243, 230.1, 258.8,
                           247.3, 250.7, 243.4, 266,
                           237.7, 99.7, 229.4, 269.7,
                           228.1, 254.6 , 258.20
                        ],
            'PROJ': [252.6208812, 215.081035, 248.052442,
                     239.31676, 244.079853, 244.702903, 256.008329,
                     243.313591, 260.009275, 247.110125, 273.300244,
                     244.79898, 160.725374, 256.268486, 241.508412,
                     219.662881, 246.415596, 226.631651
                     ] # SS_NO_LR

}

ZBH_HIP = pd.DataFrame(ZBH_HIP_REV)
ZBH_HIP_SUMMARY, ZBH_HIP_RESULT=util.linear_roll_fwd(df=ZBH_HIP, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
ZBH_HIP_RESULT.to_excel("Alphas\ZBH\ZBH_HIP_RESULTS_{date}.xlsx".format(date=current_qtr))
ZBH_HIP_SUMMARY.to_excel('Alphas\ZBH\ZBH_HIP_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ZBH_HIP)
#endregion ZBH_HIP

#region ZBH KNEES
ZBH_KNEE_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1','2020Q2','2020Q3', '2020Q4', #  
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [405.4, 381.5, 441.6,
                         417.2, 408.1, 384.6, 432.8,
                         403.8, 401.9, 382, 434.5,
                         360.1, 216.7, 395.2, 432.7,
                         358.8, 400.3, 392.60

                        ],
            'CONSENSUS' : [410.6, 389.0, 432.6, 
                           416.5, 402.5, 384.4, 443.2,
                           411.3, 397.8, 383.5, 430.7,
                           387.0, 155.3, 343.0, 437.0,
                           363.4, 392.2, 392.60
                        ],
            'PROJ': [402.5431579, 371.081552, 439.572683,
                     398.572019, 412.359794, 394.582408, 452.816271,
                     416.873618, 393.883359, 393.488994, 456.467533,
                     398.868927, 210.807349, 380.84588, 387.164572,
                     337.167854, 395.280704, 387.128724
                     ] # SS_NO_LR

}

ZBH_KNEE = pd.DataFrame(ZBH_KNEE_REV)
ZBH_KNEE_SUMMARY, ZBH_KNEE_RESULT=util.linear_roll_fwd(df=ZBH_KNEE, start_idx=6)
current_qtr='2021Q3_SS_NO_LR'
ZBH_KNEE_RESULT.to_excel("Alphas\ZBH\ZBH_KNEE_RESULTS_{date}.xlsx".format(date=current_qtr))
ZBH_KNEE_SUMMARY.to_excel('Alphas\ZBH\ZBH_KNEE_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ZBH_KNEE)
#endregion ZBH_KNEE

#region ZBH SETS
ZBH_SET_REV = {'DATE' : ['2017Q2','2017Q3','2017Q4',
                      '2018Q1','2018Q2','2018Q3','2018Q4',
                      '2019Q1','2019Q2', '2019Q3','2019Q4',
                      '2020Q1','2020Q3', '2020Q4', #   '2020Q2',
                      '2021Q1','2021Q2', '2021Q3'
                      ],
            'REVENUE' : [292.1, 282.3, 311.1,
                         290, 294.1, 283, 302.3,
                         287.7, 289.8, 284.8, 310,
                         250,  240.5, 244.5,  #165.2,
                         260.7, 293.4, 267.80
                        ],
            'CONSENSUS' : [282.3, 277.4, 291.4,
                           286.1, 285.9, 277.3, 303.6,
                           286.4, 288.5, 284.2, 312.6,
                           280,  206.8, 257, # 103.7,
                           214.9, 264.3, 267.80
                        ],
            'PROJ': [295.0703891, 277.784125, 298.283163,
                     283.113603, 302.239594, 280.880937, 307.713943,
                     295.701026, 292.264769, 270.62893, 286.81162,
                     247.245908, 261.938526, 245.437123, #  217.101788,
                     230.84656, 256.177872 , 259.378291
                     ] # NSS_12_12

}

ZBH_SET = pd.DataFrame(ZBH_SET_REV)
ZBH_SET_SUMMARY, ZBH_SET_RESULT=util.linear_roll_fwd(df=ZBH_SET, start_idx=6)
current_qtr='2021Q3_NSS_12_12_RMQ2'
ZBH_SET_RESULT.to_excel("Alphas\ZBH\ZBH_SET_RESULTS_{date}.xlsx".format(date=current_qtr))
ZBH_SET_SUMMARY.to_excel('Alphas\ZBH\ZBH_SET_SUMMARY_{date}.xlsx'.format(date=current_qtr), index=False)
util.plot_lr_splines(df=ZBH_SET)
#endregion ZBH_SET

