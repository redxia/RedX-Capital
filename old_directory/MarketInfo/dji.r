# Dow Jones

library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(alphavantager)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

DJI <- fread("DJIRec.csv")

DJI$Returns <- DJI$`Adj Close`  / shift(DJI$`Adj Close`) - 1
tsDJI <- ts(DJI$`Adj Close`, start = 1, frequency = 365)
plot(tsDJI[150:length(tsDJI)],type = "l")
plot(DJI$`Adj Close`, type = "l")
View(DJI[200:nrow(DJI),])
barplot(DJI$Returns[150:length(DJI$Returns)])
# DJIA_fit <- arima(DJI,  order = c(5,0,3))
# pred <- predict(DJIA_fit, n.ahead = 90)
# 
# x <- c(DJI, pred$pred[1:90])
# 
# num_price <- nrow(DJI)
#num_ts <- length(x)
#plot(1:num_ts, x, type = 'l')
#abline(v = num_price + 1 , col = 'red')
# library(bizdays)
# create.calendar("USA/ANBIMA", as.Date(holidayNYSE()), weekdays = c("saturday","sunday"))
# df <- data.frame(as.Date(bizseq("2020-03-06","2020-08-27","USA/ANBIMA"))) # Update this because it dpends on time and add both one day
# colnames(df) <- "date"
# df$DJIA <- x
# plot(df$date,df$DJIA, type = 'l')
# abline(v = df$date[num_price + 1], h = mean(x) , col = 'red')
#csv <- write.csv(df,"ARMA105_DJI.csv")
