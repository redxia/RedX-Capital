import win32com.client
import time

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
        
        # worksheet.set_column('B:B',11, percent_format)
        worksheet.set_column('D:X',11, int_format)
        # worksheet.set_column('E:E',11, number_format)
        # worksheet.set_column('F:I',11, percent_format)
        # worksheet.set_column('J:K',11, int_format)
        # worksheet.set_column('L:L',11, number_format)
        # worksheet.set_column('M:O',11, percent_format)
        # worksheet.set_column('P:P',11, number_format)
        # worksheet.set_column('Q:R',11, int_format)
        # worksheet.set_column('S:U',11, number_format)
        # worksheet.set_column('V:W',11, percent_format)
        # worksheet.set_column('X:X',11, number_format)
        worksheet.set_column('Y:Z',11, percent_format)
        worksheet.set_column('AA:AH',11, number_format)
        # worksheet.set_column('AA:AA',11, int_format)
        # worksheet.set_column('AC:AC',11, percent_format)
        # worksheet.set_column('AD:AI',11, number_format)
        # worksheet.set_column('AJ:AK',11, percent_format)
        # worksheet.set_column('AI:AI',11, int_format)
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
        
    elif sheet=='Current Portfolio':
        worksheet.set_column('D:Z',11, int_format)
        worksheet.set_column('AA:AB',11, percent_format)
        worksheet.set_column('AC:AD',11, number_format)
        worksheet.conditional_format('$A2:$AD{end_row}'.format(end_row=num_row),{'type':'formula',
                                                                                "criteria":'=$B2<>""',
                                                                                'format':ping_bg})
        
        # worksheet.set_column('D:E',11, percent_format)
        # worksheet.set_column('F:G',11, number_format)
        # worksheet.set_column('H:K',11, int_format)
        # worksheet.set_column('L:M',11, number_format)
        # worksheet.set_column('N:AH',11, int_format)
        # worksheet.set_column('N:AG',11, int_format)
        
        #TODO conditional format highlight the rows
        
        # worksheet.set_column('J:L',11, int_format)
        # worksheet.set_column('M:N',11, number_format)
        # worksheet.set_column('O:P',11, percent_format)
    elif sheet=='Account Summary':
        worksheet.set_column('B:I',11, int_format)
    elif sheet=='Risk Shock':
        worksheet.set_column('F:F',11, number_format)
        worksheet.set_column('G:G',11, int_format)
        worksheet.set_column('H:H',11, percent_format)
        worksheet.set_column('I:I',11, int_format)
        worksheet.set_column('J:K',11, number_format)
        worksheet.set_column('L:M',11, int_format)
        worksheet.set_column('N:N',11, percent_format)
        worksheet.set_column('O:O',11, int_format)
        worksheet.set_column('P:P',11, number_format)
        # worksheet.set_column('O:O',11, percent_format)
        worksheet.set_column('Q:Q',11, int_format)
        # worksheet.set_column('Q:Q',11, number_format)
        worksheet.set_column('R:R',11, number_format)
        worksheet.set_column('S:S',11, int_format)
        worksheet.set_column('T:T',11, percent_format)
        worksheet.set_column('U:U',11, int_format)
        worksheet.set_column('V:V',11, number_format)
        worksheet.set_column('W:AW',11, int_format)
        worksheet.set_column('AX:AX',11, number_format)
        worksheet.set_column('AY:BD',11, percent_format)
        worksheet.set_column('BE:AZ',11, number_format)
        worksheet.set_column('BA:BB',11, percent_format)
        worksheet.set_column('BC:BC',11, number_format)
        worksheet.set_column('BD:BE',11, percent_format)
        worksheet.set_column('BF:BF',11, number_format)
        worksheet.set_column('BG:BH',11, percent_format)
        # (max_row, max_col)=(10,10) #TODO do the chargin based on class group. this needs to be anew df could do the toatl plot firs
        # class_group_chart=workbook.add_chart({'type':'line'})
        # class_group_chart.add_series({'name':['Risk Shock',8,0],
        #                               'categories':['Risk Shock',0,18,0,43],
        #                               'values':['Risk Shock',8,18,8,43]
        # })
        # worksheet.insert_chart("J10", class_group_chart, {'x_scale':1.5,'y_scale':1.5})
    elif sheet=='Risk Exposures':
        worksheet.conditional_format('$A2:$J{end_row}'.format(end_row=num_row),{'type':'formula',
                                                                                "criteria":'=$B2=""',
                                                                                'format':ping_bg})
        worksheet.set_column('C:C',11, int_format)
        worksheet.set_column('D:D',11, number_format)
        worksheet.set_column('E:E',11, percent_format)
        worksheet.set_column('F:F',11, number_format)
        worksheet.set_column('G:I',11, int_format)
        worksheet.set_column('J:J',11, percent_format)
    elif sheet=='Beta Exposures':
        worksheet.set_column('B:B',11, int_format)
        worksheet.set_column('C:C',11, percent_format)
        worksheet.set_column('D:F',11, number_format)
        worksheet.set_column('G:G',11, percent_format)
        worksheet.set_column('H:H',11, int_format)
        worksheet.set_column('I:I',11, percent_format)
        worksheet.set_column('J:M',11, number_format)
        worksheet.set_column('N:P',11, percent_format)
        worksheet.set_column('Q:R',11, int_format)
    elif sheet=='MVO':
        worksheet.set_column('B:D',11, percent_format)
        worksheet.set_column('E:E',11, number_format)
        worksheet.set_column('F:F',11, percent_format)
        worksheet.set_column('G:H',11, number_format)
        worksheet.set_column('I:J',11, percent_format)
        worksheet.set_column('K:L',11, number_format)
        worksheet.set_column('M:M',11, percent_float_format)
        worksheet.set_column('N:S',11, int_format)
        # worksheet.set_column('P:Q',11, number_format)
        # worksheet.set_column('R:R',11, percent_format)
        # worksheet.set_column('S:X',11, int_format)
        worksheet.set_column('T:T',11, percent_format)
        worksheet.set_column('U:W',11, percent_float_format)
        # worksheet.set_column('V:V',11, number_format)
        # worksheet.set_column('W:W',11, percent_format)
        # worksheet.set_column('X:X',11, number_format)
        # worksheet.set_column('Y:AD',11, int_format)

    elif sheet=='Liquidity':
        worksheet.set_column('B:C',11, int_format)
        worksheet.set_column('D:D',11, number_format)
        worksheet.set_column('E:E',11, percent_format)
        worksheet.set_column('F:G',11, int_format)
        worksheet.set_column('H:H',11, percent_format)
        worksheet.set_column('I:J',11, int_format)
    elif sheet=="Dividend":
        worksheet.set_column('B:C',11, int_format)
        worksheet.set_column('D:E',11, number_format)
        worksheet.set_column('F:F',11, percent_format)
        worksheet.set_column('G:H',11, number_format)
        worksheet.set_column('I:J',11, int_format)
        worksheet.set_column('K:M',11, percent_format)
        worksheet.set_column('N:R',11, int_format)
        worksheet.set_column('S:T',11, percent_format)
        worksheet.set_column('U:W',11, int_format)
    elif sheet=='5VaR':
        worksheet.set_column('B:D',11, percent_format)
        worksheet.set_column('E:E',11, int_format)
        worksheet.set_column('F:G',11, percent_format)
        worksheet.set_column('I:Q',11, percent_format)
        worksheet.set_column('R:R',11, int_format)
        worksheet.set_column('S:S',11, percent_format)
        worksheet.set_column('T:X',11, int_format)
        worksheet.set_column('Y:Z',11, percent_format)
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
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'between',
        #                                                                         'minimum':-0.15,
        #                                                                         'maximum':-0.05,
        #                                                                         'format':yellow_bg})
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'between',
        #                                                                         'minimum':0.05,
        #                                                                         'maximum':0.15,
        #                                                                         'format':yellow_bg})
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'between',
        #                                                                         'minimum':-0.25,
        #                                                                         'maximum':-0.15,
        #                                                                         'format':orange_bg})
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'between',
        #                                                                         'minimum':0.15,
        #                                                                         'maximum':0.25,
        #                                                                         'format':lightog_bg})                
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'<=',
        #                                                                         'value':-0.25,
        #                                                                         'format':red_bg})
        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'cell',
        #                                                                         "criteria":'>=',
        #                                                                         'value':0.25,
        #                                                                         'format':green_bg})    

        # worksheet.conditional_format('$B2:$O{end_row}'.format(end_row=num_row),{'type':'no_blanks',
                                                                                # 'format':{"type": "3_color_scale"}})
    elif 'SPY Yearly' in sheet:
        worksheet.set_column('B:C',11, number_format)
        worksheet.set_column('D:E',11, percent_format)
        worksheet.set_column('F:F',11, int_format)
        worksheet.set_column('G:H',11, percent_format)
        worksheet.conditional_format("$D1:$D{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$E1:$E{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$G1:$G{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$H1:$H{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
    elif 'SPY ' in sheet or sheet=='SVIX Daily' or sheet=='QQQ Daily' or sheet=='ZVOL Daily':
        worksheet.set_column('B:C',11, number_format)
        worksheet.set_column('D:E',11, percent_format)
        worksheet.set_column('F:F',11, int_format)
        worksheet.set_column('G:I',11, percent_format)
        worksheet.conditional_format("$D1:$D{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$E1:$E{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$G1:$G{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$H1:$H{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        worksheet.conditional_format("$I1:$I{end_row}".format(end_row=num_row), {"type": "3_color_scale"})
        
#         (max_row, max_col)=chart_series_df.shape

#         if account_series:
#             account_chart=workbook.add_chart({'type':'line'}) # add two chart, overall and all positions
#             account_chart.add_series({'name':['Tail Risk Chart', 1, 0],
#                                       'categories': ['Tail Risk Chart', 0, 1, 0, 15],
#                                       'values':['Tail Risk Chart', 1, 1, 1, max_col-1],})              
#             worksheet.insert_chart('N{row}'.format(row=max_row+3), account_chart, {'x_scale': 1.5, 'y_scale': 1.5}) # needs to add data series        
#         else:
#             account_chart=workbook.add_chart({'type':'line'}) # add two chart, overall and all positions
#             account_chart.add_series({'name':['Tail Risk Chart', 1, 0],
#                                       'categories': ['Tail Risk Chart', 0, 1, 0, 15],
#                                       'values':['Tail Risk Chart', 1, 1, 1, max_col-1],})                                                            
#             worksheet.insert_chart('N{row}'.format(row=max_row+3), account_chart, {'x_scale': 1.5, 'y_scale': 1.5}) # needs to add data series                    
#             chart=workbook.add_chart({'type':'line'}) # positions
#             for row_idx in range(2,max_row+1):
#                 chart.add_series({'name':['Tail Risk Chart', row_idx, 0],
#                                   'categories': ['Tail Risk Chart', 0, 1, 0, 15],
#                                   'values':['Tail Risk Chart', row_idx, 1, row_idx, max_col-1],})

#             worksheet.insert_chart('A{row}'.format(row=max_row+3), chart, {'x_scale': 2, 'y_scale': 1.5}) # needs to add data series        

# worksheet.hide_gridlines(2)
#             worksheet.set_column('A:A',1)
#             worksheet.set_column('B:B',1)
#             worksheet.set_column('C:C',1)
#             worksheet.set_column('D:D',25)
#             worksheet.set_column('E:E',45,right_align_fmt)
#             portfolio_margin_fmt=workbook.add_format({'align':'right','num_format': 0, 'bold':True})
#             worksheet.conditional_format('E2:E2', {'type':'no_blanks', 'format':portfolio_margin_fmt})
#             worksheet.conditional_format('E11:E30', {'type':'no_blanks', 'format':number_format})
#             bold=workbook.add_format({'bold':True, 'num_format': '#,###0_);[Red](#,###0)'})
#             border=workbook.add_format()
#             border.set_bottom(1)
#             worksheet.conditional_format('C5:E5', {'type':'no_errors','format':border})
#             worksheet.conditional_format('C9:E9', {'type':'no_errors','format':border})
#             worksheet.set_row(10,15,bold)
#             worksheet.set_row(14,15,bold)
#             worksheet.set_row(26,15,bold)
#             worksheet.conditional_format('C13:E13', {'type':'no_errors','format':border})
#             worksheet.conditional_format('C25:E25', {'type':'no_errors','format':border})
#             worksheet.conditional_format('C29:E29', {'type':'no_errors','format':border})
    return writer


