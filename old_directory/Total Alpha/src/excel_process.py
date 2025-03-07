import win32com.client
import time
import pandas as pd
import numpy as np
from datetime import datetime
import utilities

today=datetime.today()
date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if today.hour>=16 else utilities.last_business().strftime("%Y%m%d")

def auto_size_wrksht(directory, sheet):    
    excel_app=win32com.client.DispatchEx('Excel.Application')
    workbook=excel_app.Workbooks.Open(directory)
    if type(sheet) == list:
        for i in sheet:
            worksheet=workbook.Worksheets(i)
            worksheet.Columns.AutoFit()
            time.sleep(.5)
    elif type(sheet)== str:
        worksheet=workbook.Worksheets(sheet)
        worksheet.Columns.AutoFit()
    workbook.Save()
    workbook.Close(SaveChanges=1)
    excel_app.Application.Quit()
    return

def sheet_adj(writer, sheet, num_row=0, num_col=0): # summary 1,1,1,25,45
    workbook=writer.book
    worksheet=writer.sheets[sheet]
    worksheet.set_zoom(85)
    number_format=workbook.add_format({'num_format':'#,###.#0_);[Red](#,###.#0)'})
    int_format=workbook.add_format({'num_format':'#,##0_);[Red](#,##0)'})
    percent_format=workbook.add_format({'num_format':'##.0%_);[Red](##.0%)'})
    int_pct_format=workbook.add_format({'num_format':'#0%_);[Red](#0%)'})
    percent_float_format=workbook.add_format({'num_format':'##.#0%_);[Red](##.#0%)'})
    
    ping_bg=workbook.add_format({'bg_color':'#FCE4D6'})
    yellow_bg=workbook.add_format({'bg_color':'#FFFF00'})
    
    red_bg=workbook.add_format({'bg_color':'#F8696B'})
    orange_bg=workbook.add_format({'bg_color':'#FFC000'})
    lightog_bg=workbook.add_format({'bg_color':'#FFEB84'})
    green_bg=workbook.add_format({'bg_color':'#63BE7B'})
    
    if sheet=='portfolio':
        
        worksheet.set_column('D:X',11, int_format)
        worksheet.set_column('Y:Z',11, percent_format)
        worksheet.set_column('AA:AH',11, number_format)

    elif sheet=="Summary":
        worksheet.hide_gridlines(2)
        #             border=workbook.add_format()
#             border.set_bottom(1)
#             worksheet.conditional_format('C5:E5', {'type':'no_errors','format':border})
#             worksheet.conditional_format('C9:E9', {'type':'no_errors','format':border})
        worksheet.set_column('A:A',1)
        worksheet.set_column('B:B',1)
        # worksheet.set_column('C:C',12)
        int_sum_fmt=workbook.add_format({'align':'right','num_format': '#,##0_);[Red](#,##0)'})
        pct_sum_fmt=workbook.add_format({'align':'right','num_format': '##.0%_);[Red](##.0%)'})
        number_sum_fmt=workbook.add_format({'align':'right','num_format': '#,###.#0_);[Red](#,###.#0)'})
        right_alighn=workbook.add_format({'align':'right'})
        worksheet.set_column('E:E',11, right_alighn)
        worksheet.conditional_format('E6:E6', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E8:E9', {'type':'no_blanks', 'format':number_sum_fmt})
        worksheet.conditional_format('E11:E20', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E21:E21', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E23:E27', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E28:E28', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E29:E29', {'type':'no_blanks', 'format':number_sum_fmt})
        worksheet.conditional_format('E30:E30', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E31:E31', {'type':'no_blanks', 'format':number_sum_fmt})
        worksheet.conditional_format('E32:E39', {'type':'no_blanks', 'format':int_sum_fmt})
        # worksheet.conditional_format('E35:E40', {'type':'no_blanks', 'format':int_fmt})
        worksheet.conditional_format('E40:E40', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E41:E41', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E42:E42', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E43:E46', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E47:E47', {'type':'no_blanks', 'format':pct_sum_fmt})
        worksheet.conditional_format('E49:E50', {'type':'no_blanks', 'format':int_sum_fmt})
        worksheet.conditional_format('E51:E51', {'type':'no_blanks', 'format':number_sum_fmt})

    elif sheet=='Alpha': #TODO yellow color more than 5 %. more than 10% another. More than 15%, more than 20% different hue, more than 25% Red.
        worksheet.set_column('B:S',11, percent_format)
        worksheet.set_column('T:T',11, number_format)
        worksheet.set_column('U:AD',11, percent_format)
        # worksheet.set_column('AA:AB',11, percent_format)
        worksheet.conditional_format('$A2:$A{end_row}'.format(end_row=num_row),{'type':'formula',
                                                                                "criteria":'=OR($A2="SPY",$A2="QQQ")',
                                                                                'format':ping_bg})
        worksheet.conditional_format('$P2:$T{end_row}'.format(end_row=num_row),{'type':'formula',
                                                                                "criteria":'=OR($A2="SPY",$A2="QQQ")',
                                                                                'format':ping_bg})        
        # worksheet.conditional_format('$P2:$T{end_row}'.format(end_row=num_row),{'type':'formula',
        #                                                                         "criteria":'=OR($A2="SPY",$A2="QQQ")"',
        #                                                                         'format':ping_bg})        
        worksheet.conditional_format("$B1:$E{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$F1:$H{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$I1:$L{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$M1:$O{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$U1:$Z{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$AA1:$AA{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$AB1:$AB{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$AA1:$AA{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$AC1:$AD{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        
    return writer




def output_excel(optimal_weights, returns, total_index, correlation):

    pos_directory=r"C:\RedXCapital\Total Alpha\Data\mvo_pos_"+date+".xlsx"
    writer=pd.ExcelWriter(pos_directory, engine='xlsxwriter')
    
    time.sleep(1)
    optimal_weights.to_excel(writer, sheet_name='Mvo', index=False)
    # returns
    total_index.to_excel(writer, sheet_name='Total Index', index=False)
    correlation.loc[optimal_weights['Tickers'],optimal_weights['Tickers']].to_excel(writer, sheet_name='Total Index Correlation')
    writer.save()
    writer.close()
    time.sleep(1)




# start_time=datetime.now()
# date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if start_time.hour>16 else utilities.last_business().strftime("%Y%m%d")
# positions=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx")
# start_date=start_time-timedelta(days=365*2)


# historical=yf.download(positions.loc[positions['Symbol'].notna(),'Symbol'].to_list(),start=(start_time-timedelta(days=365*2+6)).strftime("%Y-%m-%d"), end=utilities.next_business().strftime('%Y-%m-%d'))
# #TODO use vix buckets
# # historical.reset_index(inplace=True)
# returns=historical['Close'].pct_change(5)
# del returns['TOTAL']

# class_groups=utilities.read_config_file("ClassGroups.jsonc")

# for idx, row in positions.iterrows():
#     if row['Class Group'] !='Total':
#         try:
#             positions.loc[idx,'Adjustment Factor']=list(class_groups[row['Class Group']].values())[0]
#         except:
#             positions.loc[idx,'Adjustment Factor']=list(class_groups[row['Class Group']].values())[0]

# positions['Symbol']=positions['Symbol'].ffill()
# positions['Effective Delta']=positions['Dollar Delta'] * positions['Adjustment Factor'] #TODO run the regression eventually instead of this
# returns.quantile([0.05,0.95])
# portfolio_returns=pd.DataFrame(index=returns.index)
# del returns['TOTAL']
# for idx, row in positions.loc[positions['Right'].notna(),['Class Group','Symbol','Effective Delta']].iterrows():
#     if row['Symbol']!='Total':
#         portfolio_returns[row['Class Group']]=row['Effective Delta']*returns[row['Symbol']]

# portfolio_returns=pd.concat([portfolio_returns,portfolio_returns.sum(axis=1)], axis=1)
# portforlio_var=portfolio_returns.sum(axis=1).quantile([0.05,0.1,0.9,.95])
# print(portforlio_var)
# print(portfolio_returns.sort_values(0)) #TODO need to get the return series returns.

