# packages ----------------------------------------------------------------
library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(alphavantager)
library(quantmod)
library(tseries)
#library(AlpacaforR)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")
# packages ----------------------------------------------------------------
setwd("D:/RedX Capital/vix strat")

# getting the data --------------------------------------------------------
getSymbols('SVXY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
getSymbols('SPY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
SVXY = SVXY['20111031/']
SPY = SPY['20111031/']
# getSymbols('SVXY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
# getSymbols('VXX', verbose = FALSE, from = "2009-01-30", src = 'av', output = 'full')
# getSymbols('SPY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
#SVXY_AV = av_get("SVXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#VIXY = av_get("VIXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#SVXY = av_get("SVXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#getSymbols("^VIX", verbose = FALSE, from = "2000-01-30")
SVXY_Ret = (SVXY$SVXY.Close / shift(SVXY$SVXY.Close) - 1)[-1]
SPY_Ret = (SPY$SPY.Close / shift(SPY$SPY.Close) - 1)[-1]
# getting the data --------------------------------------------------------


# trend plots -------------------------------------------------------------
# plot(SVXY["20120101/"]$SVXY.Close/as.numeric(SVXY["20120101/"]$SVXY.Close[1]), ylim=c(0,9))
# lines(SVXY["20120101/"]$SVXY.Close/as.numeric(SVXY["20120101/"]$SVXY.Close[1]), col='red')
# lines(VXX["20120101/"]$VXX.Close/as.numeric(VXX["20120101/"]$VXX.Close[1]), col='red')
# lines(SPY["20120101/"]$SPY.Close/as.numeric(SPY["20120101/"]$SPY.Close[1]), col='red')
#plot(as.numeric(SPY_Ret$SPY.Close), as.numeric(SVXY_Ret$SVXY.Close))
#plot(as.numeric(SPY_Ret$SPY.Close[SVXY_Ret$SVXY.Close < 2]), as.numeric(SVXY_Ret$SVXY.Close[SVXY_Ret$SVXY.Close < 2]))
#abline(h=0,v=0)
# trend plots -------------------------------------------------------------

# plotting ----------------------------------------------------------------
plot(SVXY$SVXY.Close)
#plot(SVXY["20120101/"]$SVXY.Close, ylim=c(0,115))

# lines(VXX["20120101/"]$VXX.Close, col='red')
# lines(SPY["20120101/"]$SPY.Close/as.numeric(SPY["20120101/"]$SPY.Close[1]), col='red')

# plot(SVXY$SVXY.Close[index(SVXY) >= "2017-01-01"], main = "SVXY after 2017")
# plot(SVXY['20160101/20170101']$SVXY.Close, main = "SVXY year 2016")
# plot(SVXY$SVXY.Close[index(SVXY) >= "2020-01-01"], main = "SVXY after 2020")
SVXY_Rets = (SVXY$SVXY.Close / shift(SVXY$SVXY.Close) - 1)[-1]
# plot(SVXY_Rets["20120101/"][SVXY_Rets["20120101/"]$SVXY.Close<2])

# Plotting
years <- c('2009', '2010', '2011', '2012', '2013', '2014', '2015','2016','2017','2018','2019','2020','2021')
# plotting ----------------------------------------------------------------



# yearly plots ------------------------------------------------------------
#2012-2015
par(mar = c(4,4,4,6))

matplot(as.Date(index(SVXY['20130101/20140101']), "%m-%d"), 
        data.frame(c(SVXY['20120101/20130101']$SVXY.Close[1],SVXY['20120101/20130101']$SVXY.Close,SVXY['20120101/20130101']$SVXY.Close[250]), # adjust this date
                   SVXY['20130101/20140101']$SVXY.Close,
                   SVXY['20140101/20150101']$SVXY.Close,  
                   SVXY['20150101/20160101']$SVXY.Close 
        ), 
        type='l', xlab = "Dates", ylab = "SVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(40,150)
)
abline(v = as.Date(index(SVXY['20130101/20140101']), "%m-%d")
       [c(seq(1,nrow(SVXY['20130101/20140101']), 21),252)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.35,0), legend = c("2012","2013",'2014', '2015'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(40,150,10), lty=3, col='blue') # add references

#2016-2019
par(mar = c(4,4,4,6))
matplot(as.Date(index(SVXY['20170101/20180101']), "%m-%d"), 
        data.frame(SVXY['20160101/20170101']$SVXY.Close[-252],
                   SVXY['20170101/20180101']$SVXY.Close,
                   SVXY['20180101/20190101']$SVXY.Close, 
                   c(SVXY['20190101/20200101']$SVXY.Close[-252])
        ), 
        type='l', xlab = "Dates", ylab = "SVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(10,170)
)
abline(v = as.Date(index(SVXY['20170101/20180101']), "%m-%d")
       [c(seq(1,nrow(SVXY['20170101/20180101']), 21),251)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.35,0), legend = c("2016","2017","2018",'2019'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(10,170,10), lty=3, col='blue')

# 2019+
par(mar = c(4,4,4,6))
after2021 = as.numeric(SVXY['20210101/']$SVXY.Close) # use for the latest forward fill. Update
matplot(as.Date(index(SVXY['20190101/20200101']), "%m-%d"), 
        data.frame(SVXY['20190101/20200101']$SVXY.Close,
                   SVXY['20200101/20210101']$SVXY.Close[-253], 
                   c(after2021, rep(after2021[length(after2021)],252 - length(after2021)))
        ), 
        type='l', xlab = "Dates", ylab = "SVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(10,150)
)
abline(v = as.Date(index(SVXY['20200101/20210101']), "%m-%d")
       [c(seq(1,nrow(SVXY['20200101/20210101']), 21),252)], col = 'blue', lty = 3)
abline(h=seq(10,70,10), lty=3, col='blue')
legend('topright', inset = c(-0.35,0), legend = c("2019","2020","2021"), 
       col=c(1:3), lty=1, lwd = 2, xpd = TRUE)
#plot(SVXY$SVXY.Close)
# yearly plots ------------------------------------------------------------

# quantile(SVXY$SVXY.Close,.05)
# num_days = diff(index(SVXY[SVXY$SVXY.Close<15,]))
# mean(rle(num_days < 10)$lengths[rle(num_days < 10)$values == T])
# This is the average amount of days it spends below 10
num_days = diff(index(SVXY[SVXY$SVXY.Close<12,]))
days_repeat = rle(num_days >= 10)$lengths #take those that are greater than 10 days apart.
days_repeat = days_repeat[days_repeat != 1]
days_repeat = days_repeat[-length(days_repeat)]# do not count the last sample
days_repeat = c(days_repeat[-c(5,6,12,13)],29,20) # delete certain values, the 12
mean(days_repeat) # average trading days spent under numdays cutoff
length(days_repeat)

# days above
num_days_above = diff(index(SVXY[SVXY$SVXY.Close>12,]))
days_repeat_above = rle(num_days_above >= 10)$lengths #date cutoff
days_repeat_above = days_repeat_above[days_repeat_above != 1]
days_repeat_above = days_repeat_above[!(days_repeat_above %in% c(6,3,2,9))]
mean(days_repeat_above)
length(days_repeat_above)
# # forecast ----------------------------------------------------------------
# #ets every 6,12 months
# #
# fit <- ets(SVXY['20100101/']$SVXY.Close, model = 'ZZM', damped = TRUE, lambda = TRUE)
# fcast1 <- forecast(fit, h = 22*6)
# plot(fcast1)
# autoplot(fcast1)
# 
# fit2 <- auto.arima(SVXY['20100101/']$SVXY.Close, max.order = 10, max.d=0)
# SVXY_ma <- Arima(SVXY$SVXY.Close, order = c(0,0,1))
# SVXY_ma_forecast <- forecast(SVXY_ma, h = 30 * 6)
# SVXY_forecast <- forecast(fit2, h = 30 * 6)
# plot(SVXY_ma_forecast)
# plot(SVXY_forecast)
# adf.test(SVXY$SVXY.Close)
# # forecast ----------------------------------------------------------------



# HMM

# # HMM ---------------------------------------------------------------------
# plot(SVXY_Rets)
# hmm <- depmix(SVXY.Close ~ 1, family=gaussian(), nstates = 2, data=data.frame(SVXY_Rets))
# hmmfit <- fit(hmm, verbose=FALSE)
# post_probs = posterior(hmmfit)
# layout(1:2)
# plot(SVXY$SVXY.Close)
# rownames(post_probs) <- index(SVXY_Rets)
# matplot(index(SVXY_Rets), post_probs[-1], type='l', main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# 
# #layout(1:2)
# #plot(SVXY['20170101/']$SVXY.Close)
# rownames(post_probs) <- index(SVXY_Rets) 
# #index(SVXY_Rets['20170101/']),post_probs[rownames(post_probs) >= '2017-01-01',]
# x = data.frame(post_probs[rownames(post_probs) >= '2017-01-01',-1])
# matplot(cbind(x * 100,SVXY['20170101/']$SVXY.Close), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# # HMM ---------------------------------------------------------------------

# fit <- auto.arima(post_probs$S2, max.order = 20, seasonal = FALSE)
# fcast1 = forecast(fit, h = 60)
# plot(fcast1)
# fit2 <- ets(post_probs$S2)
# fcast2 = forecast(fit2, h=60)
# plot(fcast2)