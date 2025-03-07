library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)

symbols <- "SPY"
rolling_amt=3
SPY <- getSymbols("SPY", from=Sys.Date()-(365*2), to = Sys.Date()+1, verbose = FALSE, auto.assign = FALSE)

par(mfrow=c(2,1))
SPY$Returns <- SPY$SPY.Adjusted / shift(SPY$SPY.Adjusted) - 1
SPY <- na.omit(SPY)
SPY$col <- as.factor(ifelse(SPY$Returns > 0,1,0))
SPY <- as.data.frame(SPY)
barplot(SPY$Returns, col = c("red","green")[SPY$col], main = "SPY Daily Moves", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.2,.15,.01))
abline(h = seq(-.2,.15,.01),v=seq(1,252*2,21))
#box()

avgRet <- function(x){
  return(prod(x + 1))
}
SPY$RollMean <- c(rep(NA,rolling_amt-1),rollapply(SPY$Returns, width = rolling_amt, FUN = avgRet))
SPY$colRoll <- as.factor(ifelse(SPY$RollMean - 1 > 0, 1, 0))
barplot(SPY$RollMean - 1, col = c("red","green")[SPY$colRoll], main = "SPY/3 day rolling average", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.2,.15,.01))
abline(h = seq(-.2,.15,.01),v=seq(1,252*2,21))

cat("Above 0 Ret: ", mean(SPY$Returns>0),'\n')
cat("Below 0 Ret: ", mean(SPY$Returns<0))