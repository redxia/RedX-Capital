# Updates the hmm states
setwd("C:/RedXCapital/Dividends")
path="C:/RedXCapital/Dividends/Data/Market Data"
symbols=list.files(path)
library(depmixS4)

for (i in symbols){
  market=read.csv(paste(path,'/',i, sep=''))
  returns= as.numeric(na.omit(market$Returns))
  hmm <- depmix(returns~1, family=gaussian(), nstates=2, data=data.frame(returns=returns))
  hmmfit <- fit(hmm, verbose=FALSE)
  post_probs <- posterior(hmmfit)
  market$HMM_State <- c(NA,post_probs$state)
  write.csv(market,paste(path,'/',i, sep=''), row.names = FALSE)
}

# post_probs$date <- as.Date(market$Date[-1])
# post_probs$market <- market$Close[-1]
# x = post_probs[,-c(1,4,5)] * max(market$Close)
# matplot(cbind(x[post_probs$date > '2020-01-01',], market[market$Date>'2020-01-01','Close']), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='left', c('Regime #1', "Regime #2", i), fill=1:3, bty='n') #TODO bug that the state might swtich see if it is positive, assign by random
