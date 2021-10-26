library(quantmod)
library(alphavantager)
library(lubridate)
library(timeDate)
library(bizdays)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

dropDateGush <- "2020-03-18"
symbols <- "GUSH"

StockDaily <- av_get(symbols, "TIME_SERIES_DAILY_ADJUSTED", outputsize = "compact")
StockDaily <- StockDaily[StockDaily$timestamp >= as.Date(dropDateGush) + 6,]
avgStockDaily <- data.frame(timestamp = StockDaily$timestamp, AvgPrc = (StockDaily$open + StockDaily$high + StockDaily$low + StockDaily$close) / 4 )
avgRet = diff(avgStockDaily$AvgPrc) / avgStockDaily$AvgPrc[-1]
#plot(avgRet, type = 'l')


##### Hourly Data Frequency #####
Stock <- av_get(symbols, "TIME_SERIES_INTRADAY", interval = '60min' , outputsize = "full")
Stock <- Stock[Stock$timestamp > dropDateGush,]
avgStock <- data.frame(timestamp = Stock$timestamp, AvgPrc = (Stock$open + Stock$high + Stock$low + Stock$close) / 4)
avgStock <- rbind(avgStock,data.frame(timestamp = rep(NA,1001), AvgPrc = rep(NA,1001)))

### Adjust the time stamps of the predictions
create.calendar("Rmetrics/NYSE", as.Date(holidayNYSE()), weekdays = c("saturday","sunday"))
constantRatio <- round(365 / 252,2) # The ratio of non business days to business days
aheadTime <- as.Date(dropDateGush) + constantRatio * (floor(nrow(avgStock) / 7))
businessDays <- rep(as.Date(bizseq(dropDateGush,aheadTime,"Rmetrics/NYSE")), each = 7)
eachDay <- seq(1,nrow(avgStock)+1,7)
businessHours <- c(hours(9),hours(10),hours(11),hours(12),hours(13),hours(14),hours(15)) + minutes(30)
businessDateHM <- structure(rep(NA_real_, nrow(avgStock)), class=c("POSIXct") )

for(i in eachDay[2:length(eachDay)]){
  businessDateHM[eachDay[which(i == eachDay)-1]:(i-1)] <- as.POSIXct(businessDays[eachDay[which(i == eachDay)-1]:(i-1)] + businessHours, tz = "America/New_York")
}
businessDateHM <- force_tz(businessDateHM + 60 * 60 * 3, tzone = "EST")
avgStock$timestamp <- businessDateHM
avgStock$Day <- weekdays(avgStock$timestamp)

##### Plotting average stock price #####
#plot(avgStock$AvgPrc , type = 'l', lwd = 2, ylim = c(11,210))
#plot(avgStock$AvgPrc[1:(nrow(Stock)+140)] , type = 'l', lwd = 2, ylim = c(11,65))
plot(avgStock$AvgPrc[1:(nrow(Stock)+140)] , type = 'l', lwd = 2, ylim = c(95,160))
abline(v = seq(1, nrow(avgStock), 7) , col = 'lightblue') # Every day
abline(v = c(22,which(avgStock$Day == "Monday")[which(diff(which(avgStock$Day == "Monday"))  > 1) + 1]), col = 'red' ,lwd = 2) 
abline(v = which(avgStock$Day =="Tuesday")[c(FALSE,diff(which(avgStock$Day == "Tuesday")) < 29 & diff(which(avgStock$Day == "Tuesday")) > 1)][-c(1,3,5)], col = 'red', lwd = 2)
lines(Stock$high, col = 'green')
lines(Stock$low, col = 'red')
avgStock$index <- index(avgStock) / 7
cubicReg <- lm(AvgPrc~ log(index) + I(index^(1+mean(avgRet))), data = avgStock[1:nrow(Stock),])
cubicPred <- predict(cubicReg,avgStock)
avgStock$Pred <- cubicPred
avgStock$CI_Up <- cubicPred + qnorm(.9625) * sd(cubicReg$residuals)
avgStock$CI_Low <- cubicPred - qnorm(.9625) * sd(cubicReg$residuals)
avgStock$CI_UpT <- avgStock$CI_Up + (avgStock$index)^(.05)

lines(avgStock$Pred, col = 'orange')
lines(avgStock$CI_Up, col = 'grey')
lines(avgStock$CI_UpT, col = 'darkgreen')
lines(avgStock$CI_Low, col = 'grey')
########################################################


##### Higher Frequency Stock Plots #####
Stock15min <- av_get(symbols, "TIME_SERIES_INTRADAY", interval = '15min' , outputsize = "full")
avgStock15 <- data.frame(timestamp = Stock15min$timestamp, AvgPrc = (Stock15min$open + Stock15min$high + Stock15min$low + Stock15min$close) / 4 )
avgStock15 <- rbind(avgStock15,data.frame(timestamp = rep(NA,3120), AvgPrc = rep(NA,3120)))

aheadTime15 <- as.Date(dropDateGush) + constantRatio * (floor(nrow(avgStock15) / 26))
businessDays15 <- rep(as.Date(bizseq(as.Date(Stock15min$timestamp[1]),aheadTime15,"Rmetrics/NYSE")), each = 26)
eachDay15 <- seq(1,nrow(avgStock15)+1,26)
businessQuarters <- c(hours(9)+minutes(45),rep(c(hours(10),hours(11),hours(12),hours(13),hours(14),hours(15)), each = 4) + c(minutes(0),minutes(15),minutes(30),minutes(45)), hours(16))
businessDateHM15 <- structure(rep(NA_real_, nrow(avgStock15)), class=c("POSIXct") )

for(i in eachDay15[2:length(eachDay15)]){
  businessDateHM15[eachDay15[which(i == eachDay15) - 1]:(i-1)] <- as.POSIXct(businessDays15[eachDay15[which(i == eachDay15)-1]:(i-1)] + businessQuarters, tz = "America/New_York")
}
businessDateHM15 <- force_tz(businessDateHM15 + 60 * 60 * 3, tzone = "EST")
avgStock15$timestamp <- businessDateHM15
avgStock15$Day <- weekdays(avgStock15$timestamp)

##### Plotting average stock price #####
#plot(avgStock15$AvgPrc , type = 'l', lwd = 2, ylim = c(11,210))
#plot(avgStock15$AvgPrc[1:(nrow(Stock15min)+520)] , type = 'l', lwd = 2, ylim = c(11,65))
plot(avgStock15$AvgPrc[1:(nrow(Stock15min)+520)] , type = 'l', lwd = 2, ylim = c(95,160))
abline(v = seq(1, nrow(avgStock15), 26) , col = 'lightblue') # Every day
abline(v = c(27,which(avgStock15$Day == "Monday")[which(diff(which(avgStock15$Day == "Monday"))  > 1) + 1]), col = 'red' ,lwd = 2) 
abline(v = which(avgStock15$Day =="Tuesday")[c(FALSE,diff(which(avgStock15$Day == "Tuesday")) < 105 & diff(which(avgStock15$Day == "Tuesday")) > 1)][-c(1,3)], col = 'red', lwd = 2)
lines(Stock15min$high, col = 'green')
lines(Stock15min$low, col = 'red')
avgStock15$index <- index(avgStock15) / 26
cubicReg15 <- lm(AvgPrc~ log(index) + I(index^(1+mean(avgRet))), data = avgStock15[1:nrow(Stock15min),])
cubicPred15 <- predict(cubicReg15,avgStock15)
avgStock15$Pred <- cubicPred15
avgStock15$CI_Up <- cubicPred15 + qnorm(.9625) * sd(cubicReg15$residuals)
avgStock15$CI_Low <- cubicPred15 - qnorm(.9625) * sd(cubicReg15$residuals)
avgStock15$CI_UpT <- avgStock15$Pred + qnorm(.9625) * sd(cubicReg15$residuals) * avgStock15$index^.05
lines(avgStock15$Pred, col = 'orange')
lines(avgStock15$CI_Up, col = 'grey')
lines(avgStock15$CI_UpT, col = 'darkgreen')
lines(avgStock15$CI_Low, col = 'grey')
######


# build returns to forecase ahead
#####

#returnsQuarterly <- data.frame(date = avgStock15$timestamp[-1], RET = diff(avgStock15$AvgPrc) / avgStock15$AvgPrc[-1])
# abline(h = c(0,.05), lwd = 2)
# abline(v = seq(14, nrow(returnsQuarterly), 13) , col = 'red') # Every day
# returns <- data.frame(date =  dailyRet$timestamp[-1] , RET = diff(dailyRet$adjusted_close) / dailyRet$adjusted_close[-1])
# 
# avgRet <- mean(returns$RET)
# volatility <- sd(returns$RET)
# 
# confiInterval <- c(avgRet - volatility, avgRet + volatility)
# 
# plot(returns$RET, type = 'l')
# abline(h = confiInterval, col = 'red')
# abline(h = 0)
# abline(v = seq(4,nrow(returns),4), col = 'blue')
# # What happens when you're below confi, the next 5 time ticks
# belowConfi <- c(which(returns$RET < confiInterval[1]),which(returns$RET < confiInterval[1])+1,which(returns$RET < confiInterval[1])+2,which(returns$RET < confiInterval[1])+3,
#                 which(returns$RET < confiInterval[1])+4, which(returns$RET < confiInterval[1])+5)
# belowConfi <- unique(belowConfi)
# belowConfi <- sort(belowConfi)
# belowConfi
# returns <- returns[belowConfi,]
# returns <- na.omit(returns)
# #dateAfter2019 <- as.Date("2019-01-01")
# #returns <- returns[returns$date >= dateAfter2019,]
# 
# 
