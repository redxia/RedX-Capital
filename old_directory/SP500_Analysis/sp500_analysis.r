library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)
library(dplyr)

symbols <- c("^GSPC","^VIX")

getSymbols(symbols, from=Sys.Date()-(365*150), to = Sys.Date()+1, verbose = FALSE)

GSPC=to.period(GSPC)
VIX=to.period(VIX)

# GSPC=to.period(GSPC, period='years')
# VIX=to.period(VIX, period='years')

GSPC$Returns=GSPC$GSPC.Adjusted/shift(GSPC$GSPC.Adjusted) -1

avgRet <- function(x){
  return(prod(x + 1))
}





GSPC=data.frame(GSPC)
GSPC$Date=as.Date(rownames(GSPC))
# GSPC$Roll3_Returns <- rollapply(GSPC$Returns, width = 3, FUN = avgRet)-1
# GSPC$Roll5_Returns <- rollapply(GSPC$Returns, width = 5, FUN = avgRet)-1

GSPC$Roll3_Returns <- c(rep(NA,2),rollapply(GSPC$Returns, width = 3, FUN = avgRet))-1
GSPC$Roll5_Returns <- c(rep(NA,4),rollapply(GSPC$Returns, width = 5, FUN = avgRet))-1


VIX=data.frame(VIX)
VIX$Date=as.Date(rownames(VIX))
GSPC$Returns=round(GSPC$Returns,4)
GSPC$Roll3_Returns=round(GSPC$Roll3_Returns,4)
GSPC$Roll5_Returns=round(GSPC$Roll5_Returns,4)
GSPC$GSPC.Open=round(GSPC$GSPC.Open,2)
GSPC$GSPC.High=round(GSPC$GSPC.High,2)
GSPC$GSPC.Low=round(GSPC$GSPC.Low,2)
GSPC$GSPC.Close=round(GSPC$GSPC.Close,2)  
GSPC$GSPC.Adjusted=round(GSPC$GSPC.Adjusted,2)  
VIX$VIX.Open=round(VIX$VIX.Open,2)
VIX$VIX.High=round(VIX$VIX.High,2)
VIX$VIX.Low=round(VIX$VIX.Low,2)
VIX$VIX.Close=round(VIX$VIX.Close,2)  
VIX$VIX.Adjusted=round(VIX$VIX.Adjusted,2)  


sp500_vix=merge(GSPC,VIX[,c("VIX.Open","VIX.High","VIX.Low","VIX.Close",'Date')], by='Date', all.x=TRUE)
# sp500_vix=na.omit(sp500_vix)
decile_amt=5
sp500_vix$vix_decile=ntile(sp500_vix$VIX.Close,decile_amt)

