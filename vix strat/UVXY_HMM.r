setwd("D:/RedX Capital/vix strat")
library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(alphavantager)
library(quantmod)
library(tseries)
library(depmixS4)
#library(AlpacaforR)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")
# packages ----------------------------------------------------------------


# getting the data --------------------------------------------------------
getSymbols('UVXY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')


# vix beta ----------------------------------------------------------------
getSymbols('SPY', verbose = FALSE, src = 'av', output = 'full')
UVXY_Ret = data.frame((UVXY$UVXY.Close / shift(UVXY$UVXY.Close) - 1))
UVXY_Ret$date = as.Date(rownames(UVXY_Ret))
SPY_Ret = data.frame((SPY$SPY.Close / shift(SPY$SPY.Close) - 1))
SPY_Ret$date = as.Date(rownames(SPY_Ret))

UVXY_SPY = merge(UVXY_Ret, SPY_Ret, by='date', all.x=TRUE)
UVXY_SPY = UVXY_SPY[-1,]

getSymbols('DGS3MO', src='FRED', from=date, to = Sys.Date()+1)
rf = as.numeric(DGS3MO[nrow(DGS3MO),]) / 100

UVXY_SPY$beta = NA

for (i in (22):nrow(UVXY_SPY)) {
  beta = lm(UVXY.Close~I(SPY.Close - rf), data=UVXY_SPY[(i-21):(i-1),])$coefficients[2]
  UVXY_SPY$beta[i] = beta
}

#UVXY = UVXY['20111031/'] # last day of october, return is first of january
#SPY = SPY['20111031/'] # last day of october, return is first of january.

# HMM model ---------------------------------------------------------------
SPYRets = SPY$SPY.Close / stats::lag(SPY$SPY.Close) - 1
returns = as.numeric(SPYRets)
hmm <- depmix(returns ~ 1, family=gaussian(), nstates=2, data=data.frame(returns=returns))
hmmfit <- fit(hmm, verbose=FALSE)
post_probs = posterior(hmmfit)
post_probs$date <- index(SPY)
post_probs$sp500 <- as.numeric(SPY$SPY.Close)
UVXY_SPY = merge(UVXY_SPY, post_probs, by='date', all.x=TRUE)


# 2020 year
# x = post_probs[,-c(1,4,5)] * max(SPY['20200101/']$SPY.Adjusted)
# matplot(cbind(x[post_probs$date > '2020-01-01',], SPY['20200101/']$SPY.Adjusted), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #1', "Regime #2", 'SPY'), fill=1:3, bty='n')
plot(UVXY_SPY[UVXY_SPY$date > "2020-01-01",]$beta, UVXY_SPY[UVXY_SPY$date > "2020-01-01",]$S2)
# HMM model ---------------------------------------------------------------
