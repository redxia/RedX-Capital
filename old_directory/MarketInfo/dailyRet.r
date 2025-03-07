library(quantmod)
library(alphavantager)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)
#library(AlpacaforR)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

symbols <- "SPY"
#Stock <- getSymbols(symbols, src = "av", output.size = "full", periodicity = "daily", auto.assign = FALSE)
dateMarch6 <- as.Date("2020-01-01")
#Stock <- Stock[index(Stock) >= dateMarch6,]
#SPY <- getSymbols("SPY", from = dateMarch6, auto.assign = FALSE)

#SPY <- av_get(symbols, "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
SPY <- getSymbols("SPY", from=Sys.Date()-(365), to = Sys.Date()+1, verbose = FALSE, auto.assign = FALSE)
#SPY <- SPY[SPY$timestamp >= dateMarch6,]
#Stock <- av_get(symbols, "TIME_SERIES_INTRADAY", interval = "60min", outputsize = "full")
par(mfrow=c(2,1))
SPY$Returns <- SPY$SPY.Adjusted / shift(SPY$SPY.Adjusted) - 1
SPY <- na.omit(SPY)
SPY$col <- as.factor(ifelse(SPY$Returns > 0,1,0))
SPY <- as.data.frame(SPY)
barplot(SPY$Returns, col = c("red","green")[SPY$col], main = "SPY Daily Moves", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.2,.15,.01))
abline(h = seq(-.2,.15,.01))
#box()

avgRet <- function(x){
  return(prod(x + 1))
}
SPY$RollMean <- c(rep(NA,2),rollapply(SPY$Returns, width = 3, FUN = avgRet))
SPY$colRoll <- as.factor(ifelse(SPY$RollMean - 1 > 0, 1, 0))
barplot(SPY$RollMean - 1, col = c("red","green")[SPY$colRoll], main = "SPY/3 day rolling average", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.2,.15,.01))
abline(h = seq(-.2,.15,.01))

# model1 <- auto.arima(SPY$RollMean-1)
# model2 <- auto.arima(SPY$Returns, max.p = 10, max.d = 5, max.D = 5, max.q = 10)
# prediction <- c((SPY$RollMean - 1),predict(model1, n.ahead = 5)$pred)
# #prediction <- c((SPY$Returns),predict(model2, n.ahead = 5)$pred)
# barplot(prediction)
# 
# #Returns <- data.frame(index(Stock)[-1],(diff(Stock$DIA.Close)) / Stock$DIA.Close[-1])
# colnames(Returns) <- c("timestamp","Close")
# barplot(Returns$Close)
# plot(Returns$Close,type = 'l')
# 
# mean(Returns$Close, na.rm = TRUE)
# sd(Returns$Close)
# confiINT <- c(quantile(Returns$Close, .1), quantile(Returns$Close,.9))
# # confiINT <- mean(Returns$Close) + c(1.5 * sd(Returns$Close), -1.5 * sd(Returns$Close))
# confiINT
# positiveRet <- data.frame(time = Returns$timestamp,Close = ifelse(Returns$Close > 0 , Returns$Close,0))
# negativeRet <- data.frame(time = Returns$timestamp,Close = ifelse(Returns$Close < 0 , Returns$Close , 0))
# #Returns$Adjusted.Close <- ifelse(Returns$Adjusted.Close > 0,Returns$Adjusted.Close,0)
# #positiveRet$Close > 0 
# onlyPositive <- Returns$Close > 0
# PositiveGains <- Returns[onlyPositive,]
# dateDiff <- diff(PositiveGains$timestamp)
# dateDiff
# PositiveGains
# PositiveGains$Close
# PositiveGains$dateDiff <- c(0,dateDiff)
# plusMinus1D <- sort(unique(c(which(PositiveGains$Close > .02) - 1,which(PositiveGains$Close > .02),which(PositiveGains$Close > .02) +1)),decreasing = FALSE)
# 
# #plusMinus1D <- sort(c(which(PositiveGains$dateDiff == 1) -1, which(PositiveGains$dateDiff == 1), which(PositiveGains$dateDiff == 1) + 1), decreasing = FALSE)
# PositiveGains[plusMinus1D,]
# 
# culreturn <- function(x){
#   return(prod(x + 1))
# }
# rollAVG <- c(numeric(5),rollapply(Returns$Adjusted.Close,6,culreturn))
# Returns$rollAvg5 <- rollAVG
# plot(Returns$timestamp[-(1:5)],Returns$rollAvg5[-(1:5)],type = 'l')
# plot(Returns$timestamp,Returns$Adjusted.Close, type = 'l')
# plot(Stock$timestamp[1500:1800],Stock$adjusted_close[1500:1800], type = 'l')
