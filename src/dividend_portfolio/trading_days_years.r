library(RQuantLib)
library(lubridate)
library(quantmod)
library(data.table)
tradingDayOfyear <- function(myDate, calendar = "UnitedStates/NYSE") {
  FirstOfyear <- as.Date(paste(year(myDate), "01", "01", sep="/")) 
  businessDaysBetween(calendar, from = FirstOfyear, to = myDate,
                      includeFirst = 1, includeLast = 1)
}


SPX <- getSymbols("^GSPC", from=Sys.Date()-(365*75), to = Sys.Date()+1, verbose = FALSE, auto.assign = FALSE)
SPX = as.data.frame(SPX)
SPX$Date <- as.Date(rownames(SPX))
SPX$tradingDayYear<-tradingDayOfyear(SPX$Date)
SPX$Returns <- SPX$GSPC.Close/shift(SPX$GSPC.Close,3) -1
SPX <- na.omit(SPX)
setDT(SPX)
avgRetByDay=SPX[,list(mean=mean(Returns)), by=tradingDayYear]
avgRetByDay=avgRetByDay[order(avgRetByDay$tradingDayYear),]
avgRetByDay=avgRetByDay[-254,]
avgRetByDay$mean=round(avgRetByDay$mean*100,4)
plot(avgRetByDay$tradingDayYear,avgRetByDay$mean, type='l')
abline(h=0, v=seq(0,254,21), col='gray')

tradingDayOfyear(Sys.Date())
