library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)

symbols <- "^GSPC"
SPY <- getSymbols("^GSPC", from="1969-12-31", to = Sys.Date()+1, verbose = FALSE, auto.assign = FALSE)
SPY=monthlyReturn(SPY)[-1,]

SPY$months=month(index(SPY))
SPY_MONTHLY=aggregate(SPY$monthly.returns, by=list(SPY$months), FUN=mean)
SPY_MONTHLY=data.frame(SPY_MONTHLY)
SPY_MONTHLY=SPY_MONTHLY[order(as.numeric(rownames(SPY_MONTHLY))),]
SPY_MONTHLY=data.frame(SPY_MONTHLY)


SPY_MONTHLY$col <- as.factor(ifelse(SPY_MONTHLY$SPY_MONTHLY > 0,1,0))
barplot(SPY_MONTHLY$SPY_MONTHLY, col = c("red","green")[SPY_MONTHLY$col], main = "SPY Daily Moves", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.2,.15,.005))
# abline(h = seq(-.2,.15,.01),v=seq(1,252*2,21))
abline(v=seq(1,12,1))
#box()

cat("Above 0 Ret: ", mean(SPY$monthly.returns>0, na.rm=TRUE),'\n')
cat("Below 0 Ret: ", mean(SPY$monthly.returns<0, na.rm=TRUE))
print(SPY_MONTHLY)
