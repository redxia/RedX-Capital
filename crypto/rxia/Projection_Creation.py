# Author: Redmond Xia
# Date: 02/09/2021
# Description: Script to autogenerate the outlier check excel sheet for alphatec

import pandas as pd
from utilities import util
import numpy as np
%load_ext autoreload
%autoreload 2

"""
util.projection(FY_QTR, ticker, cutdate, prev_15mo, exclude_id)
Ex:
FY_QTR = '2019Q4' #Year and the quarter, pandas default ex. 2020Q1
ticker = 'ATEC' # The ticker symbol
cutdate = '20200227' # the week before report
prev_15mo = "'2018-10-01'" # 15 months before the cut date 
exclude_id='86494' or "86494,21367" # to remove this facility, needs to be manually remove in sql
""" # TODO possibly do, test the error rate for linear, quadratic and cubic fits
# GMED_2021Q1.get_members() #This is used to manually run 
# FY_QTR = '2021Q1' #Year and the quarter, pandas default ex. 2020Q1
# ticker = 'GMED' # The ticker symbol
# cutdate = '20210415' # the week before report
# prev_15mo = "'2019-10-01'"
# PROJECTION_STR = """SELECT YEAR, QUARTER, QUARTERLY_ESTIMATE/1000000 as RAW_SPEND, OFFICIAL_REVENUE/1000000 AS REPORTED, FACTOR, SCALED_QUARTERLY_ESTIMATE/1000000 AS PROJECTIONS FROM research.kdolgin.estimator_12_12_GMED_scaled_estimate_20210415_rx WHERE year >= '2018' ORDER BY 1,2;"""
# SUMMARY_STR = """SELECT GP_TRANSACTION_DATE, PANEL_FACILITY_CNT, FACILITY_FACTOR, AVG_FACILITY_SPEND, COMPANY_FACILITY_COUNT, TOTAL_SPEND FROM research.kdolgin.estimator_12_03_GMED_factor_20210415_rx ORDER BY 1 ASC;"""
# FACILITY_STR = """SELECT TRANSACTION_DATE, FACILITYID, SUM(TOTAL_SPEND) AS SPEND FROM moa.BUILD_kd_20210415.runner_11_05_GMED_aggregation_20210415 WHERE TRANSACTION_DATE >= '2019-10-01' AND facilityid IN (SELECT FACILITY_ID FROM moa.BUILD_kd_20210415.estimator_12_00_all_moa_same_store_20210415) GROUP BY 1,2 ORDER BY 1 DESC;"""


#region ATEC
ticker='ATEC'

ATEC_2019Q1 = util.PROJECTION('2019Q1', ticker, '20190502',"'2018-01-01'")#, '16588')
ATEC_2019Q1.summary_qtr_projection_facility()

ATEC_2019Q2 = util.PROJECTION('2019Q2', ticker, '20190718',"'2018-04-01'", '86494')
ATEC_2019Q2.summary_qtr_projection_facility()

ATEC_2019Q3 = util.PROJECTION('2019Q3', ticker, '20191024',"'2018-07-01'")#, '787')
ATEC_2019Q3.summary_qtr_projection_facility()

#, '86494, 16588', '16588'
ATEC_2019Q4 = util.PROJECTION('2019Q4', ticker, '20200227',"'2018-10-01'")#,'16588')
ATEC_2019Q4.summary_qtr_projection_facility()

ATEC_2020Q1 = util.PROJECTION('2020Q1', ticker, '20200507',"'2019-01-01'")
ATEC_2020Q1.summary_qtr_projection_facility()

ATEC_2020Q2 = util.PROJECTION('2020Q2', ticker, '20200730',"'2019-04-01'")#, '86494')
ATEC_2020Q2.summary_qtr_projection_facility()

ATEC_2020Q3 = util.PROJECTION('2020Q3', ticker, '20201029',"'2019-07-01'", '86494')
ATEC_2020Q3.summary_qtr_projection_facility()

# ATEC_2020Q4 = util.PROJECTION('2020Q4', ticker, '20210218',"'2020-10-01'")
# ATEC_2020Q4.summary_qtr_projection_facility()
ATEC_2020Q4 = util.PROJECTION('2020Q4', 'ATEC', '20210225',"'2019-10-01'")
ATEC_2020Q4.summary_qtr_projection_facility()

ATEC_2021Q1 = util.PROJECTION('2021Q1', ticker, '20210408',"'2020-01-01'")
ATEC_2021Q1.summary_qtr_projection_facility()

ATEC_2021Q1 = util.PROJECTION('2021Q1', ticker, '20210415',"'2020-01-01'")
ATEC_2021Q1.summary_qtr_projection_facility()
#endregion ATEC

#region ABMD
ticker='ABMD'
ABMD_2021Q1 = util.PROJECTION('2021Q1', 'ABMD', '20210408',"'2020-01-01'")
ABMD_2021Q1.summary_qtr_projection_facility()
ABMD_2021Q1 = util.PROJECTION('2021Q1', 'ABMD', '20210415',"'2019-10-01'")
ABMD_2021Q1.summary_qtr_projection_facility()
ABMD_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ABMD

#region ABMD_IMP
ABMD_IMP_2021Q1 = util.PROJECTION('2021Q1', 'ABMD_IMP', '20210422',"'2019-10-01'", exclude_id="21367") 
ABMD_IMP_2021Q1.summary_qtr_projection_facility(remove_covid=False)
ABMD_IMP_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ABMD_IMP

#region ATRC
ATRC_2021Q1 = util.PROJECTION('2021Q1', 'ATRC', '20210422',"'2019-10-01'") # ,exclude_id="42958"
ATRC_2021Q1.summary_qtr_projection_facility(remove_covid=False)
ATRC_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ATRC

#region BSX_CARDIO
BSX_CARDIO_2021Q1 = util.PROJECTION('2021Q1', 'BSX_CARDIO', '20210422',"'2019-10-01'", exclude_id="7765, 2638, 14455, 25009") #7765 2638 14455 25009
BSX_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=False)
BSX_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion BSX_CARDIO

#region BSX_MEDSURG
BSX_MEDSURG_2021Q1 = util.PROJECTION('2021Q1', 'BSX_MEDSURG', '20210422',"'2019-10-01'")#, exclude_id="2638") #28228,2638
BSX_MEDSURG_2021Q1.summary_qtr_projection_facility(remove_covid=False)
BSX_MEDSURG_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion BSX_MEDSURG

#region BSX_NEUROMODULATION
BSX_NEUROMODULATION_2021Q1 = util.PROJECTION('2021Q1', 'BSX_NEUROMODULATION', '20210422',"'2019-10-01'", exclude_id="787") #787, 80959
BSX_NEUROMODULATION_2021Q1.summary_qtr_projection_facility(remove_covid=False)
BSX_NEUROMODULATION_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion BSX_NEUROMODULATION

#region BSX_RN
BSX_RN_2021Q1 = util.PROJECTION('2021Q1', 'BSX_RN', '20210422',"'2019-10-01'")#, exclude_id="86494") #86494
BSX_RN_2021Q1.summary_qtr_projection_facility(remove_covid=False)
BSX_RN_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion BSX_RN

#region CNMD
CNMD_2021Q1 = util.PROJECTION('2021Q1', 'CNMD', '20210422',"'2019-10-01'")#, exclude_id="20698") #9259, 20698
CNMD_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
CNMD_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion CNMD

#region CSII
CSII_2021Q1 = util.PROJECTION('2021Q1', 'CSII', '20210429',"'2019-10-01'")#, exclude_id="20698") #9259, 20698
CSII_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
CSII_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion CSII

#region EW_THV
ticker='EW_THV'
EW_THV_2021Q1 = util.PROJECTION('2021Q1', 'EW_THV', '20210415',"'2019-10-01'")
EW_THV_2021Q1.summary_qtr_projection_facility()
EW_THV_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion EW_THV

#region GMED
ticker='GMED'
GMED_2021Q1 = util.PROJECTION('2021Q1', 'GMED', '20210429',"'2019-10-01'")
GMED_2021Q1.summary_qtr_projection_facility(remove_covid=False)
GMED_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion GMED

#region INSP
ticker='INSP'
INSP_2021Q1 = util.PROJECTION('2021Q1', 'INSP', '20210429',"'2019-10-01'")
INSP_2021Q1.summary_qtr_projection_facility(remove_covid=False)
INSP_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion INSP

#region ISRG
ticker='ISRG'
ISRG_2021Q1 = util.PROJECTION('2021Q1', 'ISRG', '20210415',"'2019-10-01'")
ISRG_2021Q1.summary_qtr_projection_facility()
ISRG_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ISRG

#region LIVN_NEUROMOD
LIVN_NEUROMOD_2021Q1 = util.PROJECTION('2021Q1', 'LIVN_NEUROMOD', '20210422',"'2019-10-01'")#, exclude_id="20698") #14455, 68668, 10612, 21367, 9229, 
LIVN_NEUROMOD_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
LIVN_NEUROMOD_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion LIVN_NEUROMOD

#region LIVN_CARDIO
LIVN_CARDIO_2021Q1 = util.PROJECTION('2021Q1', 'LIVN_CARDIO', '20210422',"'2019-10-01'", exclude_id="14752") #14752
LIVN_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
LIVN_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion LIVN_CARDIO

#region LIVN_ACS
LIVN_ACS_2021Q1 = util.PROJECTION('2021Q1', 'LIVN_ACS', '20210422',"'2019-10-01'")#, exclude_id="20698") #14455, 68668, 10612, 21367, 9229, 
LIVN_ACS_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
LIVN_ACS_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion LIVN_ACS

#region LUNG
#"cut_dates": ["20200430", "20200730", "20201029"],
LUNG = util.PROJECTION('2020Q4', 'LUNG', '20210225',"'2019-07-01'")
LUNG.summary_qtr_projection_facility(remove_covid=False) 
LUNG.summary_qtr_projection_facility(remove_covid=True)
#endregion LUNG

#region KIDS
#"cut_dates": [  "20190502","20190801","20191031","20200227","20200430","20200730","20201029","20210304","20210422"],
KIDS = util.PROJECTION('2020Q4', 'KIDS', '20210304',"'2019-07-01'")#,"9313") #9313, 21298
KIDS.summary_qtr_projection_facility(remove_covid=False) 
KIDS.summary_qtr_projection_facility(remove_covid=True)
#endregion KIDS

#region MMSI_CARDIO
MMSI_CARDIO_2021Q1 = util.PROJECTION('2021Q1', 'MMSI_CARDIO', '20210422',"'2019-10-01'", exclude_id="1558") #1558
MMSI_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
MMSI_CARDIO_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion MMSI_CARDIO

#region MMSI_END
MMSI_END_2021Q1 = util.PROJECTION('2019Q1', 'MMSI_END', '20190418',"'2017-10-01'", exclude_id="1744")
MMSI_END_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
MMSI_END_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion MMSI_END

#region NARI
ticker='NARI_ALPHA'
NARI_2021Q1 = util.PROJECTION('2021Q1', 'NARI_ALPHA', '20210429',"'2019-10-01'")
NARI_2021Q1.summary_qtr_projection_facility(remove_covid=False)
NARI_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion NARI

#region NUVA
ticker='NUVA'
NUVA_2021Q1 = util.PROJECTION('2021Q1', 'NUVA', '20210429',"'2019-10-01'")
NUVA_2021Q1.summary_qtr_projection_facility(remove_covid=False)
NUVA_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion NUVA

#region PEN_NEURO
ticker='PEN_NEURO'
PEN_NEURO_2021Q1 = util.PROJECTION('2021Q1', 'PEN_NEURO', '20210429',"'2019-10-01'")
PEN_NEURO_2021Q1.summary_qtr_projection_facility(remove_covid=False)
PEN_NEURO_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion PEN_NEURO

#region PEN_PERI
ticker='PEN_PERI'
PEN_PERI_2021Q1 = util.PROJECTION('2021Q1', 'PEN_PERI', '20210429',"'2019-10-01'")
PEN_PERI_2021Q1.summary_qtr_projection_facility(remove_covid=False)
PEN_PERI_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion PEN_PERI

#region SILK
ticker='SILK'
SILK_2021Q1 = util.PROJECTION('2021Q1', 'SILK', '20210429',"'2019-10-01'")
SILK_2021Q1.summary_qtr_projection_facility(remove_covid=False)
SILK_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SILK

#region SIBN
ticker='SIBN'
SIBN_2021Q1 = util.PROJECTION('2021Q1', 'SIBN', '20210429',"'2019-10-01'")
SIBN_2021Q1.summary_qtr_projection_facility(remove_covid=False)
SIBN_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SIBN

#region SNN_REC
SNN_REC_2021Q1 = util.PROJECTION('2021Q1', 'SNN_REC', '20210422',"'2019-10-01'", exclude_id="4999, 52039") # 4999, 52039
SNN_REC_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SNN_REC_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SNN_REC

#region SNN_SMT
SNN_SMT_2021Q1 = util.PROJECTION('2021Q1', 'SNN_SMT', '20210422',"'2019-10-01'", exclude_id="28651") # 28651
SNN_SMT_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SNN_SMT_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SNN_SMT

#region SNN_AWM
SNN_AWM_2021Q1 = util.PROJECTION('2021Q1', 'SNN_AWM', '20210422',"'2019-10-01'")#, exclude_id="20698") #370, 
SNN_AWM_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SNN_AWM_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SNN_AWM

#region SYK_ORTHO
SYK_ORTHO_2021Q1 = util.PROJECTION('2021Q1', 'SYK_ORTHO', '20210422',"'2019-10-01'", exclude_id="2740, 280") #2740, 6760, 280
SYK_ORTHO_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SYK_ORTHO_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SYK_ORTHO

#region SYK_NNS
SYK_NNS_2021Q1 = util.PROJECTION('2021Q1', 'SYK_NNS', '20210422',"'2019-10-01'")#, exclude_id="20698") #
SYK_NNS_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SYK_NNS_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SYK_NNS

#region SYK_MEDSG
SYK_MEDSG_2021Q1 = util.PROJECTION('2021Q1', 'SYK_MEDSG', '20210422',"'2019-10-01'")#, exclude_id="3535") #7441, 3535
SYK_MEDSG_2021Q1.summary_qtr_projection_facility(remove_covid=False) 
SYK_MEDSG_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion SYK_MEDSG

#region VAPO_CAP
ticker='VAPO_CAP'
VAPO_CAP_2021Q1 = util.PROJECTION('2021Q1', 'VAPO_CAP', '20210429',"'2019-10-01'",exclude_id="114277")
#exclude_id="114277,280,10057,"
VAPO_CAP_2021Q1.summary_qtr_projection_facility(remove_covid=False)
VAPO_CAP_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion VAPO_CAP

#region VAPO_DISP
ticker='VAPO_DISP'
VAPO_DISP_2021Q1 = util.PROJECTION('2021Q1', 'VAPO_DISP', '20210429',"'2019-10-01'", exclude_id="114277")
#exclude_id="114277,10057,280"
VAPO_DISP_2021Q1.summary_qtr_projection_facility(remove_covid=False)
VAPO_DISP_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion VAPO_DISP

#region XENT
ticker='XENT'
XENT_US = util.PROJECTION('2021Q1', 'XENT', '20210506',"'2019-10-01'")#, exclude_id="90043")
XENT_US.summary_qtr_projection_facility(remove_covid=False)
XENT_US.summary_qtr_projection_facility(remove_covid=True)
#endregion XENT

#region XENT_US
ticker='XENT_US'
XENT_US = util.PROJECTION('2020Q4', 'XENT_US', '20210506',"'2019-10-01'", exclude_id="86494, 90043")#, exclude_id="89923")#, 86494
#66244
# 2020Q4 #89923
# 2021Q1 86494, 90043
XENT_US.summary_qtr_projection_facility(remove_covid=False)
XENT_US.summary_qtr_projection_facility(remove_covid=True)
#endregion XENT_US

#region ZBH
ticker='ZBH'
ZBH_2021Q1 = util.PROJECTION('2021Q1', 'ZBH', '20210415',"'2019-10-01'")
ZBH_2021Q1.summary_qtr_projection_facility()
ZBH_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ZBH

#region ZBH_HIPS
ticker='ZBH_HIPS'
ZBH_HIPS_2021Q1 = util.PROJECTION('2021Q1', 'ZBH_HIPS', '20210429',"'2019-10-01'")
ZBH_HIPS_2021Q1.summary_qtr_projection_facility(remove_covid=False)
ZBH_HIPS_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ZBH_HIPS

#region ZBH_KNEE
ticker='ZBH_KNEE'
ZBH_KNEE_2021Q1 = util.PROJECTION(FY_QTR='2021Q1',ticker='ZBH_KNEE', cutdate='20210429',prev_15mo="'2019-10-01'")
ZBH_KNEE_2021Q1.summary_qtr_projection_facility(remove_covid=False)
ZBH_KNEE_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ZBH_KNEE

#region ZBH_SET
ticker='ZBH_SET'
ZBH_SET_2021Q1 = util.PROJECTION(FY_QTR='2021Q1',ticker='ZBH_SET',cutdate='20210429',prev_15mo="'2019-10-01'")
# exclude_id=""
ZBH_SET_2021Q1.summary_qtr_projection_facility(remove_covid=False)
ZBH_SET_2021Q1.summary_qtr_projection_facility(remove_covid=True)
#endregion ZBH_SET


