library(alphavantager)
library(quantmod)
library(data.table)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

DJI <- av_get("DIA", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
# DJI <- av_get("DIA", "TIME_SERIES_INTRADAY", interval = "1min" , outputsize = "full")
#SP <- av_get("SPY",  "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")

dateMarch6 <- as.Date("2020-01-01")
DJI_M <- DJI[DJI$timestamp >= dateMarch6,]
SP_M <- SP[SP$timestamp >= dateMarch6,]
DJI_M$Returns <- DJI_M$adjusted_close / shift(DJI_M$adjusted_close) - 1
SP_M$Returns <- SP_M$adjusted_close / shift(SP_M$adjusted_close) - 1

barplot(DJI_M$Returns)

DJI_M$lagRet <- shift(DJI_M$Returns)
#DJI_M$UpDay <- ifelse(DJI_M$lagRet < 0 & DJI_M$Returns > 0, 1,0)
DJI_M$UpDay <- ifelse(DJI_M$Returns > 0, 1,0)
plot(DJI_M$lagRet,DJI_M$UpDay)
model1 <- glm(UpDay~lagRet, data = DJI_M, family = "binomial")
points(DJI_M$lagRet,c(NA,NA,model1$fitted.values), col = "red")
DJI_M$logReg <- c(NA,NA,model1$fitted.values)
DJI_M$logRegClass <- ifelse(DJI_M$logReg > .5, 1, 0)
points(DJI_M$lagRet,DJI_M$logRegClass, col = "blue")
View(DJI_M[DJI_M$logReg > .5,])
table(DJI_M$logRegClass,DJI_M$UpDay)
sum(diag(table(DJI_M$logRegClass,DJI_M$UpDay))) / sum(table(DJI_M$logRegClass,DJI_M$UpDay))


DJI_M$DownDay <- ifelse(DJI_M$lagRet > 0 & DJI_M$Returns < 0,1,0)
plot(DJI_M$lagRet,DJI_M$DownDay)
model2 <- glm(DownDay~lagRet, data = DJI_M, family = "binomial")
points(DJI_M$lagRet,c(NA,NA,model2$fitted.values), col = 'red')
DJI_M$logRegDown <- c(NA,NA,model2$fitted.values)
DJI_M$logRegClassDown <- ifelse(DJI_M$logRegDown > .5,1,0)
points(DJI_M$lagRet,DJI_M$logRegClassDown, col = "blue")
table(DJI_M$logRegClassDown, DJI_M$DownDay)
sum(diag(table(DJI_M$logRegClassDown, DJI_M$DownDay))) / sum(table(DJI_M$logRegClassDown, DJI_M$DownDay))
View(DJI_M[DJI_M$logRegDown > .5,])

logPred <- function(x) {.5 * (1 + exp(-x)) - 1}
uniroot(logPred,lower = 0, upper = 1)$root
#barplot(SP_M$Returns)