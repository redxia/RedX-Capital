library(quantmod)

sp500=getSymbols("^GSPC", verbose = FALSE, from =as.Date("1900-01-1"),to=Sys.Date()+1, auto.assign = FALSE)
sp500=as.data.frame(sp500)
sp500$Date=rownames(sp500)
write.csv(sp500,"sp500.csv", row.names=FALSE)


sp500_monthly=getSymbols("^GSPC", verbose = FALSE, from =as.Date("1900-01-1"),to=Sys.Date()+1, auto.assign = FALSE)
sp500_monthly=to.period(sp500_monthly,period="months")
sp500_monthly=as.data.frame(sp500_monthly)
sp500_monthly$Date=rownames(sp500_monthly)
colnames(sp500_monthly)=c("Open","High","Low","Close","Volume","Adjusted","Date")

write.csv(sp500_monthly,"sp500_monthly.csv", row.names=FALSE)


sp500_yearly=getSymbols("^GSPC", verbose = FALSE, from =as.Date("1900-01-1"),to=Sys.Date()+1, auto.assign = FALSE)
sp500_yearly=to.period(sp500_yearly,period="years")
sp500_yearly=as.data.frame(sp500_yearly)
sp500_yearly$Date=rownames(sp500_yearly)
colnames(sp500_yearly)=c("Open","High","Low","Close","Volume","Adjusted","Date")
write.csv(sp500_yearly,"sp500_yearly.csv", row.names=FALSE)


