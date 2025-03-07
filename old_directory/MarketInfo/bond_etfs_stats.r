library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)
library(dplyr)

symbols <- c("TLT","HYG",'LQD')

getSymbols(symbols, from=Sys.Date()-(365*150), to = Sys.Date()+1, verbose = FALSE)

TLT=to.period(TLT)
HYG=to.period(HYG)
LQD=to.period(LQD)

# TLT=to.period(TLT, period='years')
# VIX=to.period(VIX, period='years')

TLT$Returns=TLT$TLT.Adjusted/shift(TLT$TLT.Adjusted) -1
LQD$Returns=LQD$LQD.Adjusted/shift(LQD$LQD.Adjusted) -1
HYG$Returns=HYG$HYG.Adjusted/shift(HYG$HYG.Adjusted) -1

mean(HYG$Returns,na.rm=TRUE)
median(HYG$Returns,na.rm=TRUE)
sd(HYG$Returns, na.rm=TRUE)
mean(HYG$Returns,na.rm=TRUE)/sd(HYG$Returns, na.rm=TRUE)

mean(LQD$Returns, na.rm=TRUE)
median(LQD$Returns, na.rm=TRUE)
sd(LQD$Returns, na.rm=TRUE)
mean(LQD$Returns, na.rm=TRUE)/sd(LQD$Returns, na.rm=TRUE)
  
mean(TLT$Returns, na.rm=TRUE)
median(TLT$Returns, na.rm=TRUE)
sd(TLT$Returns, na.rm=TRUE)
mean(TLT$Returns, na.rm=TRUE)/sd(TLT$Returns, na.rm=TRUE)
