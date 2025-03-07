# beta/alpha research model
library(stringr)
library(readxl)
library(forecast)
setwd("D:/RedXCapital/Dividends")
path="D:/RedXCapital/Dividends/Data/Symbol"
market_path="D:/RedXCapital/Dividends/Data/Market Data"
symbols=list.files(path)

merge_hmm <- function(df1,df2, variable) {
  colnames(df2)[4] <- 'Mkt Returns'
  df1=merge(df1, df2[,c('Date', 'Mkt Returns', 'HMM_State')], by = "Date", all.x=TRUE)
  df1$Date <- as.Date(df1$Date)
  df1$HMM_State <- as.factor(df1$HMM_State)
  df1=na.omit(df1[,c('Date', variable, 'HMM_State')])
  return(df1)
}

for (i in symbols) {
  stock=read.csv(paste(path,"/",i,sep=''))
  market_symbol=dividends[dividends[,'Symbol']==str_split(i,'.csv')[[1]][1],'Sector ETF']
  market=read.csv(paste(market_path, '/',market_symbol,'.csv',sep=''))
  print(i)
  model=ar(na.omit(stock$R2_Mkt_3mo), order.max = 10)
  plot(forecast(model,h=25), main=paste("AR",model$order,i))
  print(forecast(model,h=22)$mean)
}


# look at beta model