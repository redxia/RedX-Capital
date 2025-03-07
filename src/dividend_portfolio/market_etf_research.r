# beta/alpha research model
library(stringr)
library(readxl)
library(forecast)
setwd("D:/RedXCapital/Dividends")
path="D:/RedXCapital/Dividends/Data/Symbol"
market_path="D:/RedXCapital/Dividends/Data/Market Data"
symbols=list.files(market_path)

merge_hmm <- function(df1,df2, variable) {
  colnames(df2)[4] <- 'Mkt Returns'
  df1=merge(df1, df2[,c('Date', 'Mkt Returns', 'HMM_State')], by = "Date", all.x=TRUE)
  df1$Date <- as.Date(df1$Date)
  df1$HMM_State <- as.factor(df1$HMM_State)
  df1=na.omit(df1[,c('Date', variable, 'HMM_State')])
  return(df1)
}

for (i in symbols) {
  market=read.csv(paste(market_path, '/',i,sep=''))
  print(i)
  market=na.omit(market)
  market$Date=as.Date(market$Date)
  market$HMM_State=as.factor(market$HMM_State)
  if (mean(market[market['HMM_State']==2,"Returns"]) > mean(market[market['HMM_State']==1,"Returns"])) {
    bull=TRUE # indicating a bull state for two 
  } else {
    bull=FALSE 
  }
  if (bull==TRUE) { # we want bear, if state two is bullish
    returns=market[market['HMM_State']==2,"Close"]
    mkt_ret=market[market['HMM_State']==2,"Returns"]
  } else {
    returns=market[market['HMM_State']==1,"Close"]
    mkt_ret=market[market['HMM_State']==1,"Returns"]
  }
  print(mean(mkt_ret))
  # model=auto.arima(returns, max.d=1, max.p=10, max.q=10)
  model=ar(mkt_ret)
  print(model)
  plot(forecast(model,h=25), main=paste("ARIMA",model$arma[1],i))
  print(forecast(model,h=21)$mean)
  cat('\n')
}


# look at beta model