import pandas as pd
import numpy as np
from gp.settings import namespace as settings
from utilities import util
import openpyxl as pxl


# Creates a pandas data frame to store in the values
proj_results = pd.DataFrame({"Ticker":settings.ticker_list, 
                             "SameStore_12_12":np.repeat(np.nan,len(settings.ticker_list)),
                             "SameStore_LR":np.repeat(np.nan,len(settings.ticker_list)),
                             "SameStore_No_CVD_LR":np.repeat(np.nan,len(settings.ticker_list)),
                             "SameStore_No_LR":np.repeat(np.nan,len(settings.ticker_list)),
                             "No_SameStore_12_12":np.repeat(np.nan,len(settings.ticker_list)),
                             "No_SameStore_LR":np.repeat(np.nan,len(settings.ticker_list)),
                             "No_SameStore_No_CVD_LR":np.repeat(np.nan,len(settings.ticker_list))
                             })

# The directory to store the excel sheet creation
# Requires that you have an Alphas and FY_QTR ex. 2021Q1
if len(settings.ticker_list)==1:
    filename="..\\Alphas\\"+settings.FY_QTR+"\\"+settings.FY_QTR+"_Estimate_"+settings.cut_date+"_"+settings.ticker_list[0]+".xlsx"
elif len(settings.ticker_list)<=6:
    filename="..\\Alphas\\"+settings.FY_QTR+"\\"+settings.FY_QTR+"_Estimate_"+settings.cut_date+"_"+settings.ticker_list[0].split('_')[0]+".xlsx"
else:
    filename="..\\Alphas\\"+settings.FY_QTR+"\\"+settings.FY_QTR+"_Estimate_"+settings.cut_date+".xlsx"

print(filename)


# for each ticker, store the projection and create the facility check xlsx sheet
for tic in settings.ticker_list:
    TIC_PROJ_SS = util.PROJECTION(FY_QTR=settings.FY_QTR, ticker=tic, cutdate=settings.cut_date, prev_18mo=settings.prev_18mo, exclude_id=settings.exclude_id, same_store=True)
    RAW, PROJ, LR = TIC_PROJ_SS.summary_qtr_projection_facility(remove_covid=False)
    proj_results.loc[tic==proj_results['Ticker'],'SameStore_No_LR'] = RAW.iloc[-1,4]
    proj_results.loc[tic==proj_results['Ticker'],'SameStore_12_12'] = PROJ.iloc[-1,4]
    proj_results.loc[tic==proj_results['Ticker'],'SameStore_LR'] = LR.iloc[-1,9]
    RAW_CVD, PROJ_CVD, LR_CVD = TIC_PROJ_SS.summary_qtr_projection_facility(remove_covid=True)
    proj_results.loc[tic==proj_results['Ticker'],'SameStore_No_CVD_LR'] = LR_CVD.iloc[-1,9]

    TIC_PROJ_No_SS = util.PROJECTION(FY_QTR=settings.FY_QTR, ticker=tic, cutdate=settings.cut_date, prev_18mo=settings.prev_18mo, exclude_id=settings.exclude_id, same_store=False)
    RAW_No_SS, PROJ_No_SS, LR_No_SS = TIC_PROJ_No_SS.summary_qtr_projection_facility(remove_covid=False)
    proj_results.loc[tic==proj_results['Ticker'],'No_SameStore_12_12'] = PROJ_No_SS.iloc[-1,4]
    proj_results.loc[tic==proj_results['Ticker'],'No_SameStore_LR'] = LR_No_SS.iloc[-1,4]
    RAW_CVD_No_SS, PROJ_CVD_No_SS, LR_CVD_No_SS = TIC_PROJ_No_SS.summary_qtr_projection_facility(remove_covid=True)
    proj_results.loc[tic==proj_results['Ticker'],'No_SameStore_No_CVD_LR'] = LR_CVD_No_SS.iloc[-1,4]

    FACILITY = TIC_PROJ_SS.facility_check()
    
    # creating a facility check for each of the sheet
    if settings.wkbk_exist:
        excel_book = pxl.load_workbook(filename)
        with pd.ExcelWriter(filename) as writer:
            writer.book = excel_book
            writer.sheets = {worksheet.title: worksheet for worksheet in excel_book.worksheets}
            FACILITY.to_excel(writer, sheet_name=tic, index=True)
            writer.save()
    else:
        with pd.ExcelWriter(filename) as writer:
            FACILITY.to_excel(writer, sheet_name=tic, index=True)
            writer.save()
        settings.wkbk_exist=True


proj_results['Average'] = proj_results.mean(axis=1)
# outputing the projections results
print(proj_results)
excel_book = pxl.load_workbook(filename)
with pd.ExcelWriter(filename) as writer:
    writer.book = excel_book
    writer.sheets = {worksheet.title: worksheet for worksheet in excel_book.worksheets}
    proj_results.to_excel(writer, sheet_name="SUMMARY", index=False)
    writer.save()


