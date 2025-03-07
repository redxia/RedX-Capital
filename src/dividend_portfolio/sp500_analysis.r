library(quantmod)
library(lubridate)
library(forecast)
library(zoo)
library(data.table)
library(dplyr)

symbols <- c("^GSPC","^VIX")

getSymbols(symbols, from=Sys.Date()-(365*150), to = Sys.Date()+1, verbose = FALSE)

# GSPC=to.period(GSPC)
# VIX=to.period(VIX)

# GSPC=to.period(GSPC, period='years')
# VIX=to.period(VIX, period='years')

GSPC$Returns=GSPC$GSPC.Adjusted/shift(GSPC$GSPC.Adjusted) -1

# avgRet <- function(x){
#   return(prod(x + 1))
# }

# GSPC$Returns <- rollapply(GSPC$Returns, width = 5, FUN = avgRet)-1
# GSPC$Returns <- c(rep(NA,2),rollapply(GSPC$Returns, width = 3, FUN = avgRet))-1


GSPC=data.frame(GSPC)
GSPC$Date=as.Date(rownames(GSPC))



VIX=data.frame(VIX)
VIX$Date=as.Date(rownames(VIX))
sp500_vix=merge(VIX, GSPC[c("Date","Returns")], by='Date', all.x=TRUE)
sp500_vix=na.omit(sp500_vix)
decile_amt=5
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
  
  for (i in seq(.002,.15,.002)) {
    cat("Top movers greater than ",i,sum(top_movers$Returns>i)/nrow(top_movers) ,' ')
    cat(sum(abs(bottom_movers$Returns)>i)/nrow(bottom_movers),'\n')
    # cat("Top movers greater than ",i,sum(df$Returns>i)/nrow(df) ,'\n')
  }
  
}

for (i in seq(1,decile_amt)) {
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
  cat("Positive ",positive_seq,'\n')
  cat("Negative ",negative_seq,'\n')
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

  cat("median ",sum((median(positive_seq)+1)<positive_seq)/length(positive_seq),' ')
  cat(sum((median(negative_seq)+1)<negative_seq)/length(negative_seq),'\n')
}



# latest_decile[(nrow(latest_decile)-10):nrow(latest_decile),]
# GSPC$Ticker="GSPC"
# VIX$Returns=VIX$VIX.Adjusted/shift(VIX$VIX.Adjusted) -1
# VIX$Lag=shift(VIX$VIX.Adjusted)
# VIX$Lag_2=shift(VIX$VIX.Adjusted,2)
# VIX$Ticker="VIX"
# 
# 
# plot(as.numeric(VIX$VIX.Adjusted[-1]), as.numeric(GSPC$Returns[-1]))
# plot(as.numeric(sp500_vix$VIX.Adjusted), as.numeric(sp500_vix$Returns))
# plot(as.numeric(VIX$Lag[-1]), as.numeric(GSPC$Returns[-1]))
# plot(as.numeric(VIX$Returns[-1]), as.numeric(GSPC$Returns[-1]))
# plot(as.numeric(VIX$Lag[-1]), as.numeric(GSPC$Returns[-1]))
# plot(as.numeric(na.omit(VIX$Lag_2)), as.numeric(GSPC$Returns[c(-1,-2)]))
# model=lm(as.numeric(GSPC$Returns[-1])~as.numeric(VIX$Lag[-1]))
# abline(lm(as.numeric(GSPC$Returns[-1])~as.numeric(VIX$Lag[-1])))
# 
# plot(as.numeric(sp500_vix$VIX.Adjusted), as.numeric(sp500_vix$Returns))
# model=lm(as.numeric(sp500_vix$Returns)~as.numeric(sp500_vix$VIX.Adjusted))
# model$coefficients[1]+model$coefficients[1]*22.79
# abline(model)
# summary(model)
# summary(model)

