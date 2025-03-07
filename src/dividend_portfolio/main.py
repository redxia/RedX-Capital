from datetime import datetime
from dividend import dividend_analysis
from market_risk import market_analysis
import time
import create_report
# from utilities import port_model
# import sys
from utilities import utilities
from ibkr import ibkr
# from risk_shock import pnlDeltas
from risk_model import risk_exposures
from liquidity import liquidity
from excel import excel
import pandas as pd
from var import var_calculator
from alpha_model import alpha_model
import pandas.io.formats.excel
from optimizer import optimizer
import sys
pandas.io.formats.excel.ExcelFormatter.header_style=None
#TODO Volatility analysis page.include long term and short time volatility. Daily dollar move based on this.
#TODO max drawdown list.

if __name__=="__main__":
    today=datetime.today() 
    date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if today.hour>=16 else utilities.last_business().strftime("%Y%m%d")
    position_path=r"C:\RedXCapital\Dividends\Data\Position" #TODO add vix in the account level
    pos_directory=position_path+'\\'+'ibkr_pos_'+date+'.xlsx'
    try:
        current_positions, account_summary=ibkr.download_positions()
        print(account_summary)
        portfolio_value=account_summary['GrossPositionValue'].sum() + account_summary['SMA'].sum() * 2
        risk_exposure, returns=risk_exposures.risk_exposures(positions=current_positions.copy(), lookback=1)
        beta_exposures=risk_exposures.portfolio_beta(risk_exposure.copy(), returns.copy())
        portfolio_var, vix_adj_returns=var_calculator.var_calculator(positions=current_positions.copy(), risk_exposure=risk_exposure.copy())
        alpha=alpha_model.alpha(historical=vix_adj_returns.copy(), risk_exposure=risk_exposure.copy())
        #TODO volatility and convariance matrix.
        #TODO MVO sheet
        dividend=dividend_analysis.dividend_summary(positions=current_positions.copy(), portfolio_value=portfolio_value, alpha=alpha.copy())
        # mvo=optimizer.optimize_semivariance(portfolio_value, dividend)
        spx_daily=market_analysis.daily_returns()
        qqq_daily=market_analysis.daily_returns('QQQ')
        ZVOL_daily=market_analysis.daily_ZVOL_returns()
        spx_monthly=market_analysis.monthly_returns()
        spx_yearly=market_analysis.yearly_returns()
        svix_daily=market_analysis.daily_svix_returns()
        liquidity_df=liquidity.liquidity_model(positions=current_positions.copy()) #TODO add concentration addon here
        summary=create_report.create_summary(risk_exposure.copy(), dividend.copy(), alpha.copy(), current_positions.copy(), portfolio_var.copy(), liquidity_df.copy(), account_summary.copy(), spx_daily.copy(), spx_monthly.copy(), spx_yearly.copy(), svix_daily.copy())
                
        #current_positions.to_csv(position_path+'\\'+'ibkr_pos_'+date+'.csv', index=False) # TODO make this into excel
        print("Downloaded Positions and Summary!")
        
        writer=pd.ExcelWriter(pos_directory, engine='xlsxwriter')
        
        time.sleep(1)
        summary.to_excel(writer, sheet_name='Summary', index=False, header=False)
        risk_exposure.to_excel(writer, sheet_name='Risk Exposures', index=False)
        beta_exposures.to_excel(writer, sheet_name='Beta Exposures', index=False)
        # mvo.to_excel(writer, sheet_name='MVO', index=False)
        dividend.to_excel(writer, sheet_name='Dividend', index=False)
        current_positions.to_excel(writer, sheet_name='Current Portfolio', index=False)
        alpha.to_excel(writer, sheet_name='Alpha', index=False)
        portfolio_var.to_excel(writer, sheet_name='5VaR', index=False)
        liquidity_df.to_excel(writer, sheet_name='Liquidity', index=False)
        # account_summary.to_excel(writer, sheet_name='Account Summary', index=False)
        spx_daily.to_excel(writer, sheet_name='SPY Daily', index=False)
        qqq_daily.to_excel(writer, sheet_name='QQQ Daily', index=False)
        spx_monthly.to_excel(writer, sheet_name='SPY Monthly', index=False)
        spx_yearly.to_excel(writer, sheet_name='SPY Yearly', index=False)
        svix_daily.to_excel(writer, sheet_name='SVIX Daily', index=False)
        ZVOL_daily.to_excel(writer, sheet_name='ZVOL Daily', index=False)
        
        writer=excel.sheet_adj(writer,'Summary', summary.shape[0]+1)
        writer=excel.sheet_adj(writer,'Current Portfolio', current_positions.shape[0]+1)
        # writer=excel.sheet_adj(writer,'Account Summary')    
        writer=excel.sheet_adj(writer,'Risk Exposures',num_row=risk_exposure.shape[0]+1)
        writer=excel.sheet_adj(writer,'Beta Exposures',num_row=beta_exposures.shape[0]+1)
        writer=excel.sheet_adj(writer,'Liquidity')
        # writer=excel.sheet_adj(writer,'MVO',num_row=mvo.shape[0]+1)
        writer=excel.sheet_adj(writer,'Dividend',num_row=dividend.shape[0]+1)    
        writer=excel.sheet_adj(writer,'5VaR',num_row=portfolio_var.shape[0]+1)    
        writer=excel.sheet_adj(writer,'Alpha',num_row=alpha.shape[0]+1)   
        writer=excel.sheet_adj(writer,'SPY Daily',num_row=spx_daily.shape[0]+1)   
        writer=excel.sheet_adj(writer,'SPY Monthly',num_row=spx_monthly.shape[0]+1)   
        writer=excel.sheet_adj(writer,'SPY Yearly',num_row=spx_yearly.shape[0]+1)   
        writer=excel.sheet_adj(writer,'SVIX Daily',num_row=svix_daily.shape[0]+1)   
        writer=excel.sheet_adj(writer,'QQQ Daily',num_row=qqq_daily.shape[0]+1)   
        writer=excel.sheet_adj(writer,'ZVOL Daily',num_row=ZVOL_daily.shape[0]+1)   
        
        directory=r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx"
        
        writer.save()
        writer.close()
        time.sleep(1)
        excel.auto_size_wrksht(directory, list(writer.sheets.keys()))
        time.sleep(7)

    except:
        pass
    
    
    if datetime.today().isoweekday() == 7:
        utilities.send_outlook_email(to='redmond.xia@gmail.com', subject='COB Report RedX Capital '+today.strftime('%m/%d/%Y'), cc='linsimon95@gmail.com', html_msg='Here is your position for today: '+today.strftime('%m/%d/%Y'), attachment_dir=pos_directory)
    else:
        utilities.send_outlook_email(to='redmond.xia@gmail.com', subject='COB Report RedX Capital '+today.strftime('%m/%d/%Y'), cc='', html_msg='Here is your position for today: '+today.strftime('%m/%d/%Y'), attachment_dir=pos_directory)
        

sys.exit()
    # utilities.send_outlook_email(to='redmond.xia@gmail.com', subject='COB Report RedX Capital '+today.strftime('%m/%d/%Y'), cc='', html_msg='Here is your position for today: '+today.strftime('%m/%d/%Y'), attachment_dir=pos_directory)

             #T TODO beta is 4 month
# arg 1 portfolvio value # arg 2 run prev day # arg 3 have a target beta
    # if len(sys.argv)>=3:
    #     if sys.argv[2]=='prev':
    #         port_model.run_optimizations(portfolio_value, utilities.last_business().strftime("%Y%m%d"))
    #     if len(sys.argv)==4:
    #         target_beta=sys.argv[3]
    #         port_model.run_optimizations(portfolio_value)
    # else:
    #     port_model.run_optimizations(portfolio_value)
    
    #TODO once my portfolio gets large enough invest in sofi weekly income.
    #TODO expected dividend payout
    