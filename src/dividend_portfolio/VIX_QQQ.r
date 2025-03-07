library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)
library(dplyr)

symbols <- c("^IXIC","^VIX")

getSymbols(symbols, from=Sys.Date()-(365*37), to = Sys.Date()+1, verbose = FALSE)


IXIC$Returns=IXIC$IXIC.Adjusted/shift(IXIC$IXIC.Adjusted) -1

avgRet <- function(x){
  return(prod(x + 1))
}

IXIC$Returns <- rollapply(IXIC$Returns, width = 3, FUN = avgRet)-1
# IXIC$Returns <- c(rep(NA,2),rollapply(IXIC$Returns, width = 3, FUN = avgRet))-1


IXIC=data.frame(IXIC)
IXIC$Date=as.Date(rownames(IXIC))
VIX=data.frame(VIX)
VIX$Date=as.Date(rownames(VIX))
sp500_vix=merge(VIX, IXIC[c("Date","Returns")], by='Date', all.x=TRUE)
sp500_vix=na.omit(sp500_vix)
decile_amt=10
sp500_vix$vix_decile=ntile(sp500_vix$VIX.Adjusted,decile_amt)

print_probability <-function(df, decile) {
  cat("VIX decile cutoff", decile, quantile(df$VIX.Adjusted,decile/decile_amt),'\n')
  df=df[df$vix_decile==decile,]
  cat("SD",sd(df$Returns),' ')
  cat("Median",median(df$Returns),' ')
  cat("Mean",mean(df$Returns),'\n')
  
  top_movers=df[df$Returns>0,]
  bottom_movers=df[df$Returns<0,]
  
  print("top movers and losers")
  
  cat("SD",sd(top_movers$Returns),' ')
  cat(sd(bottom_movers$Returns),'\n')
  cat("median",median(top_movers$Returns),' ')
  cat(median(bottom_movers$Returns),'\n')
  cat("mean",mean(top_movers$Returns),' ')
  cat(mean(bottom_movers$Returns),'\n')
  
  cat("number observation",nrow(top_movers),'\n')
  cat("number observation", nrow(bottom_movers),'\n')  
  
  for (i in seq(.001,.065,.001)) {
    cat("Top movers greater than ",i,sum(top_movers$Returns>i)/nrow(top_movers) ,' ')
    cat(sum(abs(bottom_movers$Returns)>i)/nrow(bottom_movers),'\n')
    # cat("Top movers greater than ",i,sum(df$Returns>i)/nrow(df) ,'\n')
  }
  
  
  # for (i in seq(-.001,-.045,-.001)) {
  # for (i in seq(.001,.045,.001)) {
  # cat("bottom movers greater than",i,sum(abs(bottom_movers$Returns)>i)/nrow(bottom_movers),'\n')
  # cat("bottom movers greater than abs ",i,sum(bottom_movers$Returns<i)/nrow(bottom_movers),'\n')
  # cat("bottom movers greater than abs ",i,sum(df$Returns<i)/nrow(df),'\n')
  # }
}

for (i in seq(10,10)) {
  print_probability(sp500_vix,i)
}


latest_decile=sp500_vix[sp500_vix$vix_decile==10,]
sum(latest_decile[(nrow(latest_decile)-4):nrow(latest_decile),"Returns"]>0)/5
sum(latest_decile[(nrow(latest_decile)-6):nrow(latest_decile),"Returns"]>0)/7 # non extreme volatile as in quartilier edge these two are good 5/7
# for none high vix quartile average day 7-10 #Towards the end don't buy the bull

sum(latest_decile[(nrow(latest_decile)-9):nrow(latest_decile),"Returns"]>0)/10 # need long if so
sum(latest_decile[(nrow(latest_decile)-13):nrow(latest_decile),"Returns"]>0)/14

sum(latest_decile[(nrow(latest_decile)-20):nrow(latest_decile),"Returns"]>0)/21
sum(latest_decile[(nrow(latest_decile)-31):nrow(latest_decile),"Returns"]>0)/32
# 
# 


# mode <- function(x) {
#   ux <- unique(x)
#   ux[which.max(tabulate(match(x,ux)))]
# }

for (i in 1:decile_amt){
  latest_decile=sp500_vix[sp500_vix$vix_decile==i,]
  print(i)
  latest_decile$cum_days=ifelse(latest_decile$Returns>0,TRUE, FALSE)
  positive_seq=rle(latest_decile$cum_days)$lengths[rle(latest_decile$cum_days)$values]
  latest_decile$cum_days=ifelse(latest_decile$Returns<0,TRUE, FALSE)
  negative_seq=rle(latest_decile$cum_days)$lengths[rle(latest_decile$cum_days)$values]
  
  cat("SD ",round(sd(positive_seq),1),' ')
  cat(round(sd(negative_seq),1),'\n')
  cat('Median ',median(positive_seq),' ')
  cat(median(negative_seq),'\n')
  cat('Mean ',round(mean(positive_seq),1),' ')
  cat(round(mean(negative_seq),1),'\n')
  cat("1sdabove ",sum((mean(positive_seq)+round(sd(positive_seq),1))<positive_seq)/length(positive_seq),' ')
  cat(sum((mean(negative_seq)+round(sd(negative_seq),1))<negative_seq)/length(negative_seq),'\n')
  
  cat("2sdabove ",sum((mean(positive_seq)+round(2*sd(positive_seq),1))<positive_seq)/length(positive_seq),' ')
  cat(sum((mean(negative_seq)+round(2*sd(negative_seq),1))<negative_seq)/length(negative_seq),'\n')

  cat("1plusmedian",sum((median(positive_seq)+1)<positive_seq)/length(positive_seq),' ')
  cat(sum((median(negative_seq)+1)<negative_seq)/length(negative_seq),'\n')
  cat("2plusmedian",sum((median(positive_seq)+2)<positive_seq)/length(positive_seq),' ')
  cat(sum((median(negative_seq)+2)<negative_seq)/length(negative_seq),'\n')  
  
  cat("Maxpos", max(positive_seq),' ')
  cat(max(negative_seq),'\n')
  # cat("Top 5 longest seq ",sort(unique(positive_seq), decreasing = TRUE)[1:5]," ")
  # cat(" ", sort(unique(negative_seq), decreasing = TRUE)[1:5],'\n')
  
}



# latest_decile[(nrow(latest_decile)-10):nrow(latest_decile),]
# IXIC$Ticker="IXIC"
# VIX$Returns=VIX$VIX.Adjusted/shift(VIX$VIX.Adjusted) -1
# VIX$Lag=shift(VIX$VIX.Adjusted)
# VIX$Lag_2=shift(VIX$VIX.Adjusted,2)
# VIX$Ticker="VIX"
# 
# 
# plot(as.numeric(VIX$VIX.Adjusted[-1]), as.numeric(IXIC$Returns[-1]))
# plot(as.numeric(sp500_vix$VIX.Adjusted), as.numeric(sp500_vix$Returns))
# plot(as.numeric(VIX$Lag[-1]), as.numeric(IXIC$Returns[-1]))
# plot(as.numeric(VIX$Returns[-1]), as.numeric(IXIC$Returns[-1]))
# plot(as.numeric(VIX$Lag[-1]), as.numeric(IXIC$Returns[-1]))
# plot(as.numeric(na.omit(VIX$Lag_2)), as.numeric(IXIC$Returns[c(-1,-2)]))
# model=lm(as.numeric(IXIC$Returns[-1])~as.numeric(VIX$Lag[-1]))
# abline(lm(as.numeric(IXIC$Returns[-1])~as.numeric(VIX$Lag[-1])))
# 
# plot(as.numeric(sp500_vix$VIX.Adjusted), as.numeric(sp500_vix$Returns))
# model=lm(as.numeric(sp500_vix$Returns)~as.numeric(sp500_vix$VIX.Adjusted))
# model$coefficients[1]+model$coefficients[1]*22.79
# abline(model)
# summary(model)
# summary(model)

