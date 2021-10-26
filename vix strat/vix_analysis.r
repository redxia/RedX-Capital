library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(depmixS4)
library(alphavantager)
library(quantmod)
library(tseries)
#library(AlpacaforR)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

getSymbols('VXX', verbose = FALSE, from = "2009-01-30", src = 'av', output = 'full')
#VXX_AV = av_get("VXX", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#VIXY = av_get("VIXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#SVXY = av_get("SVXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#getSymbols("^VIX", verbose = FALSE, from = "2000-01-30")

plot(VXX['20120101/']$VXX.Close, ylim=c(5,75))
lines(VXX['20100101/']$VXX.High)
lines(VXX['20100101/']$VXX.Low)
plot(VXX$VXX.Close[index(VXX) >= "2017-01-01"], main = "VXX after 2017")
plot(VXX['20160101/20170101']$VXX.Close, main = "VXX year 2016")
plot(VXX$VXX.Close[index(VXX) >= "2020-01-01"], main = "VXX after 2020")
VXX_Rets = (VXX$VXX.Close / shift(VXX$VXX.Close) - 1)[-1]
plot(VXX_Rets)

# Plotting
years <- c('2009', '2010', '2011', '2012', '2013', '2014', '2015','2016','2017','2018','2019','2020')
after2020 = as.numeric(VXX['20200101/']$VXX.Close)
before2010 = as.numeric(VXX['/20100101']$VXX.Close)


# yearly plots ------------------------------------------------------------
#2010-2014
par(mar = c(4,4,4,6))
##c(rep(before2010[1],252 - length(before2010)),before2010),
matplot(as.Date(index(VXX['20100101/20110101']), "%m-%d"), 
        data.frame(VXX['20100101/20110101']$VXX.Close,
                   VXX['20110101/20120101']$VXX.Close,
                   c(VXX['20120101/20130101']$VXX.Close[1],VXX['20120101/20130101']$VXX.Close, VXX['20120101/20130101']$VXX.Close[250]), 
                   VXX['20130101/20140101']$VXX.Close 
        ), 
        type='l', xlab = "Dates", ylab = "VXX", col = c(1:4), lty = 1, lwd = 2
)
abline(v = as.Date(index(VXX['20100101/20110101']), "%m-%d")
       [c(seq(1,nrow(VXX['20100101/20110101']), 21),252)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.2,0), legend = c("2010","2011",'2012', '2013'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(10,75,5), lty=3, col='blue')

#2014-2017
par(mar = c(4,4,4,6))
matplot(as.Date(index(VXX['20160101/20170101']), "%m-%d"), 
        data.frame(VXX['20140101/20150101']$VXX.Close,
                   VXX['20150101/20160101']$VXX.Close,
                   VXX['20160101/20170101']$VXX.Close, 
                   c(VXX['20170101/20180101']$VXX.Close,VXX['20170101/20180101']$VXX.Close[251])
        ), 
        type='l', xlab = "Dates", ylab = "VXX", col = c(1:4), lty = 1, lwd = 2
)
abline(v = as.Date(index(VXX['20160101/20170101']), "%m-%d")
       [c(seq(1,nrow(VXX['20160101/20170101']), 21),251)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.2,0), legend = c("2014","2015","2016",'2017'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(10,75,5), lty=3, col='blue')

# 2018+
par(mar = c(4,4,4,6))
matplot(as.Date(index(VXX['20180101/20190101']), "%m-%d"), 
        data.frame(VXX['20170101/20180101']$VXX.Close,
                   VXX['20180101/20190101']$VXX.Close, 
                   VXX['20190101/20200101']$VXX.Close[-1], 
                   c(after2020, rep(after2020[length(after2020)],251- length(after2020)))
                   ), 
        type='l', xlab = "Dates", ylab = "VXX", col = c(1:4), lty = 1, lwd = 2
        )
abline(v = as.Date(index(VXX['20180101/20190101']), "%m-%d")
       [c(seq(1,nrow(VXX['20180101/20190101']), 21),251)], col = 'blue', lty = 3)
abline(h=seq(10,75,5), lty=3, col='blue')
legend('topright', inset = c(-0.2,0), legend = c("2017","2018","2019",'2020'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
#plot(VXX$VXX.Close)
# yearly plots ------------------------------------------------------------

# quantile(VXX$VXX.Close,.05)
# num_days = diff(index(VXX[VXX$VXX.Close<15,]))
# mean(rle(num_days < 10)$lengths[rle(num_days < 10)$values == T])
# This is the average amount of days it spends below 10
num_days = diff(index(VXX[VXX$VXX.Close<15,]))
days_repeat = rle(num_days >= 10)$lengths #date cutoff
days_repeat = days_repeat[days_repeat != 1]
days_repeat = days_repeat[-length(days_repeat)]# do not count the last sample
mean(days_repeat) # average trading days spent under numdays cutoff
length(days_repeat)

# days above
num_days_above = diff(index(VXX[VXX$VXX.Close>15,]))
days_repeat_above = rle(num_days_above >= 10)$lengths #date cutoff
days_repeat_above = days_repeat_above[days_repeat_above != 1]
days_repeat_above = days_repeat_above[!(days_repeat_above %in% c(14,5,2,8))]
mean(days_repeat_above)
length(days_repeat_above)

# # forecast ----------------------------------------------------------------
# #ets every 6,12 months
# #
# fit <- ets(VXX['20100101/']$VXX.Close, model = 'ZZM', damped = TRUE, lambda = TRUE)
# fcast1 <- forecast(fit, h = 22*6)
# plot(fcast1)
# autoplot(fcast1)
# 
# fit2 <- auto.arima(VXX['20100101/']$VXX.Close, max.order = 10, max.d=0)
# vxx_ma <- Arima(VXX$VXX.Close, order = c(0,0,1))
# vxx_ma_forecast <- forecast(vxx_ma, h = 30 * 6)
# VXX_forecast <- forecast(fit2, h = 30 * 6)
# plot(vxx_ma_forecast)
# plot(VXX_forecast)
# adf.test(VXX$VXX.Close)
# # forecast ----------------------------------------------------------------



# HMM

# # HMM ---------------------------------------------------------------------
# plot(VXX_Rets)
# hmm <- depmix(VXX.Close ~ 1, family=gaussian(), nstates = 2, data=data.frame(VXX_Rets))
# hmmfit <- fit(hmm, verbose=FALSE)
# post_probs = posterior(hmmfit)
# layout(1:2)
# plot(VXX$VXX.Close)
# rownames(post_probs) <- index(VXX_Rets)
# matplot(index(VXX_Rets), post_probs[-1], type='l', main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# 
# #layout(1:2)
# #plot(VXX['20170101/']$VXX.Close)
# rownames(post_probs) <- index(VXX_Rets) 
# #index(VXX_Rets['20170101/']),post_probs[rownames(post_probs) >= '2017-01-01',]
# x = data.frame(post_probs[rownames(post_probs) >= '2017-01-01',-1])
# matplot(cbind(x * 100,VXX['20170101/']$VXX.Close), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# # HMM ---------------------------------------------------------------------

# fit <- auto.arima(post_probs$S2, max.order = 20, seasonal = FALSE)
# fcast1 = forecast(fit, h = 60)
# plot(fcast1)
# fit2 <- ets(post_probs$S2)
# fcast2 = forecast(fit2, h=60)
# plot(fcast2)