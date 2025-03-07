library(stringr)
library(readxl)
library(ggplot2)
setwd("D:/RedXCapital/Dividends")
path="D:/RedXCapital/Dividends/Data/Symbol"
market_path="D:/RedXCapital/Dividends/Data/Market Data"
symbols=list.files(path)

plot_xy <- function(df) {
  columns=colnames(df)
  for (i in 2:length(columns)){
    data=na.omit(df[,c(columns[1],columns[i])])
    plot(x=as.Date(data[,columns[1]]), y=data[,columns[i]], xlab=columns[1], ylab=columns[i], type='l', main=columns[i])
  }
}


dividends=read_excel("Dividends.xlsx")
dividends[dividends[,'Symbol']==str_split(i,'.csv')[[1]][1],'Sector ETF']

merge_hmm <- function(df1,df2) {
  colnames(df2)[4] <- 'Mkt Returns'
  df1=merge(df1, df2[,c('Date', 'Mkt Returns', 'HMM_State')], by = "Date", all.x=TRUE)
  df1$Date <- as.Date(df1$Date)
  df1$HMM_State <- as.factor(df1$HMM_State)
  df1=na.omit(df1[,c('Date', 'Close', 'HMM_State')])
  return(df1)
}

for (i in symbols) {
  stock=read.csv(paste(path,"/",i,sep=''))
  market_symbol=dividends[dividends[,'Symbol']==str_split(i,'.csv')[[1]][1],'Sector ETF']
  market=read.csv(paste(market_path, '/',market_symbol,'.csv',sep=''))
  plot_mkt=merge_hmm(stock,market)
  print(ggplot(plot_mkt, aes(x=Date, y=Close, color=HMM_State)) + geom_path(aes(group=1)) + scale_color_manual(values=c('blue', 'green')) + ggtitle(str_split(i,'.csv')[[1]][1]) + geom_point(size=.9)) 
}

library(forecast)
acf(na.omit(stock$B_Mkt_3mo))

# look at beta model