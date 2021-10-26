library(depmixS4)
library(quantmod)
library(alphavantager)
#library(AlpacaforR)

av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")
 
#getSymbols("SPY", periodicity = 'intraday', verbose = FALSE, output='full', src='av', interval='60min')
getSymbols("SPY", from="2000-01-01", to = Sys.Date()+1, verbose = FALSE)
SPYRets = SPY$SPY.Adjusted / stats::lag(SPY$SPY.Adjusted) - 1
returns = as.numeric(SPYRets)
hmm <- depmix(returns ~ 1, family=gaussian(), nstates=2, data=data.frame(returns=returns))
hmmfit <- fit(hmm, verbose=FALSE)
post_probs = posterior(hmmfit)
post_probs$date <- index(SPY)
post_probs$sp500 <- SPY$SPY.Adjusted


# 2020 year
x = post_probs[,-c(1,4,5)] * max(SPY['20200101/']$SPY.Adjusted)
matplot(cbind(x[post_probs$date > '2020-01-01',], SPY['20200101/']$SPY.Adjusted), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
legend(x='left', c('Regime #1', "Regime #2", 'SPY'), fill=1:3, bty='n')

View(tail(post_probs,22*5))

# x = post_probs[,-c(1,4,5)] * max(SPY$SPY.Adjusted)
# matplot(cbind(x, SPY$SPY.Adjusted), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #1', "Regime #2", 'SP500'), fill=1:3, bty='n')

# Intraday data very noisy
#Sys.setenv('APCA-PAPER-API-KEY-ID' = "PK70MOT1TD6DWCD6AV2C")
#Sys.setenv('APCA-PAPER-API-SECRET-KEY' = "nHrAa3XfLN2mBfxXZ7BwROOck4fSu81FZOVUcSSr")
#SPY = get_bars('SPY', timeframe = '15Min', limit = 1000)[[1]]
# SPY = getSymbols("SPY", periodicity = 'intraday', verbose = FALSE, output='full', src='av', interval='60min', auto.assign = FALSE)
# spy_returns <- na.omit(SPY$SPY.Close/ lag(SPY$SPY.Close) - 1)
# hmm_intra = depmix(spy_returns ~ 1, family=gaussian(), nstates=2, data=spy_returns)
# hmm_fit_intra = fit(hmm_intra, verbose=FALSE)
# post_probs_intra = posterior(hmm_fit_intra)
# post_probs_intra$date <- index(spy_returns)
# post_probs_intra$sp500 = SPY$SPY.Close[-1]
# x = post_probs_intra[,-c(1,4,5)] * max(SPY['20200101/']$SPY.Close)
# matplot(cbind(x[post_probs_intra$date > '2020-01-01',], SPY['20200101/']$SPY.Close[-1]), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #1', "Regime #2", 'SP500'), fill=1:3, bty='n')

# 
# ## Financial crisis
# x = post_probs[,-c(1,4,5)] * max(SPY['20080101/20110101']$SPY.Adjusted)
# matplot(cbind(x[post_probs$date < "2011-01-01" & post_probs$date > '2008-01-01',], SPY['20080101/20110101']$SPY.Adjusted), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #2', "Regime #1",'SP500'), fill=1:3, bty='n')
# 
# # post 2016
# x = post_probs[,-c(1,4,5)] * max(SPY['20160101/']$SPY.Adjusted)
# matplot(cbind(x[post_probs$date > '2016-01-01',], SPY['20160101/']$SPY.Adjusted), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #1', "Regime #2", 'SP500'), fill=1:3, bty='n')