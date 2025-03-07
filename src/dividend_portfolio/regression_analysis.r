# This script identify the beta, and provides a regression analysis
library(quantmod)
library(data.table)
market_symbols <- c('SPY', 'QQQ', 'IWB', 'IWR', 'IWM', 'IVE','IVW','IWP','IWS','IWO','IWN','DEM','IDV','MTUM', 'QUAL', 'USMV','DVYE','DIA','JEPI','SVOL','HYG')
#TODO add high div or IDV, DEM, BIZD, SLX, USO,
# parameters
symbol = 'AAPL'

date = Sys.Date() - 365 #
getSymbols(symbol, from=date, to = Sys.Date()+1, verbose = FALSE)
getSymbols(market_symbols, from=date, to = Sys.Date()+1, verbose = FALSE)

AAPL_rets = na.omit(AAPL$AAPL.Adjusted / shift(AAPL$AAPL.Adjusted) - 1)
MTUM_rets = na.omit(MTUM$MTUM.Adjusted / shift(MTUM$MTUM.Adjusted) - 1)
QUAL_rets = na.omit(QUAL$QUAL.Adjusted / shift(QUAL$QUAL.Adjusted) - 1)
USMV_rets = na.omit(USMV$USMV.Adjusted / shift(USMV$USMV.Adjusted) - 1)
DEM_rets =na.omit(DEM$DEM.Adjusted / shift(DEM$DEM.Adjusted) - 1)
IDV_rets =na.omit(IDV$IDV.Adjusted / shift(IDV$IDV.Adjusted) - 1)
SPY_rets = na.omit(SPY$SPY.Adjusted / shift(SPY$SPY.Adjusted) - 1)
QQQ_rets = na.omit(QQQ$QQQ.Adjusted / shift(QQQ$QQQ.Adjusted) - 1)
IWB_rets = na.omit(IWB$IWB.Adjusted / shift(IWB$IWB.Adjusted) - 1)
IWR_rets = na.omit(IWR$IWR.Adjusted / shift(IWR$IWR.Adjusted) - 1)
IWM_rets = na.omit(IWM$IWM.Adjusted / shift(IWM$IWM.Adjusted) - 1)
IVE_rets = na.omit(IVE$IVE.Adjusted / shift(IVE$IVE.Adjusted) - 1)
IVW_rets = na.omit(IVW$IVW.Adjusted / shift(IVW$IVW.Adjusted) - 1)
IWP_rets = na.omit(IWP$IWP.Adjusted / shift(IWP$IWP.Adjusted) - 1)
IWS_rets = na.omit(IWS$IWS.Adjusted / shift(IWS$IWS.Adjusted) - 1)
IWO_rets = na.omit(IWO$IWO.Adjusted / shift(IWO$IWO.Adjusted) - 1)
IWN_rets = na.omit(IWN$IWN.Adjusted / shift(IWN$IWN.Adjusted) - 1)
DVYE_rets = na.omit(DVYE$DVYE.Adjusted / shift(DVYE$DVYE.Adjusted) - 1)
DIA_rets = na.omit(DIA$DIA.Adjusted / shift(DIA$DIA.Adjusted) - 1)
JEPI_rets = na.omit(JEPI$JEPI.Adjusted / shift(JEPI$JEPI.Adjusted) - 1)
#JEPQ_rets = na.omit(JEPQ$JEPQ.Adjusted / shift(JEPQ$JEPQ.Adjusted) - 1)
SVOL_rets = na.omit(SVOL$SVOL.Adjusted / shift(SVOL$SVOL.Adjusted) - 1)
HYG_rets = na.omit(HYG$HYG.Adjusted / shift(HYG$HYG.Adjusted) - 1)



data = data.frame(AAPL_rets$AAPL.Adjusted, MTUM_rets$MTUM.Adjusted,QUAL_rets$QUAL.Adjusted, USMV_rets$USMV.Adjusted, SPY_rets$SPY.Adjusted, QQQ_rets$QQQ.Adjusted ,DEM_rets$DEM.Adjusted, IDV_rets$IDV.Adjusted, IWB_rets$IWB.Adjusted, IWR_rets$IWR.Adjusted, IWM_rets$IWM.Adjusted,IVE_rets$IVE.Adjusted,IVW_rets$IVW.Adjusted,IWP_rets$IWP.Adjusted,IWS_rets$IWS.Adjusted,IWO_rets$IWO.Adjusted,IWN_rets$IWN.Adjusted, DVYE_rets$DVYE.Adjusted,DIA_rets$DIA.Adjusted,JEPI_rets$JEPI.Adjusted,SVOL_rets$SVOL.Adjusted,HYG_rets$HYG.Adjusted)

correlation_matrix=cor(data)
r2_matrix=cor(data)^2
View(r2_matrix)

