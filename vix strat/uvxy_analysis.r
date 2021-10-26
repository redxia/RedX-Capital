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
getSymbols('UVXY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
#getSymbols('SPY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
UVXY = UVXY['20111031/']
#SPY = SPY['20111031/']
# getSymbols('SVXY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
# getSymbols('VXX', verbose = FALSE, from = "2009-01-30", src = 'av', output = 'full')
# getSymbols('SPY', verbose = FALSE, from = "2011-01-01", src = 'av', output = 'full')
#UVXY_AV = av_get("UVXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#VIXY = av_get("VIXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#SVXY = av_get("SVXY", "TIME_SERIES_DAILY_ADJUSTED", outputsize = "full")
#getSymbols("^VIX", verbose = FALSE, from = "2000-01-30")
UVXY_Ret = (UVXY$UVXY.Close / shift(UVXY$UVXY.Close) - 1)[-1]
#SPY_Ret = (SPY$SPY.Close / shift(SPY$SPY.Close) - 1)[-1]
# getting the data --------------------------------------------------------


# trend plots -------------------------------------------------------------
# plot(UVXY["20120101/"]$UVXY.Close/as.numeric(UVXY["20120101/"]$UVXY.Close[1]), ylim=c(0,9))
# lines(SVXY["20120101/"]$SVXY.Close/as.numeric(SVXY["20120101/"]$SVXY.Close[1]), col='red')
# lines(VXX["20120101/"]$VXX.Close/as.numeric(VXX["20120101/"]$VXX.Close[1]), col='red')
# lines(SPY["20120101/"]$SPY.Close/as.numeric(SPY["20120101/"]$SPY.Close[1]), col='red')
#plot(as.numeric(SPY_Ret$SPY.Close), as.numeric(UVXY_Ret$UVXY.Close))
#plot(as.numeric(SPY_Ret$SPY.Close[UVXY_Ret$UVXY.Close < 2]), as.numeric(UVXY_Ret$UVXY.Close[UVXY_Ret$UVXY.Close < 2]))
#abline(h=0,v=0)
# trend plots -------------------------------------------------------------

# plotting ----------------------------------------------------------------
plot(UVXY["20120101/"]$UVXY.Close, ylim=c(0,115))

# lines(VXX["20120101/"]$VXX.Close, col='red')
# lines(SPY["20120101/"]$SPY.Close/as.numeric(SPY["20120101/"]$SPY.Close[1]), col='red')

# plot(UVXY$UVXY.Close[index(UVXY) >= "2017-01-01"], main = "UVXY after 2017")
# plot(UVXY['20160101/20170101']$UVXY.Close, main = "UVXY year 2016")
# plot(UVXY$UVXY.Close[index(UVXY) >= "2020-01-01"], main = "UVXY after 2020")
# plot(UVXY_Rets["20120101/"][UVXY_Rets["20120101/"]$UVXY.Close<2])

# Plotting
#years <- c('2009', '2010', '2011', '2012', '2013', '2014', '2015','2016','2017','2018','2019','2020','2021')

# do this for returns, clean up the printing
# plotting ----------------------------------------------------------------

# time spent quantile -----------------------------------------------
quantile_uvxy = quantile(UVXY$UVXY.Close, c(.001,.005,.01,.025,.05,.1)) # the percentage of time and it's value
quantile_top_uvxy = quantile(UVXY$UVXY.Close, c(.999,.9975,.996,.995,.99,.975,.95,.9,.825,.75))
quantile_uvxy_ret = quantile(UVXY_Ret$UVXY.Close, c(.001, .005,.01,.025,.05,.1)) # the percentage of time and it's value
quantile_top_uvxy_ret = quantile(UVXY_Ret$UVXY.Close, c(.999,.9975,.996,.995,.99,.975,.95,.9,.825,.75)) # the percentage of time and it's value

cat("Percentage of days existance etf \n(.1%,  .5%,  1%,  2.5%,  5%,  10%): \n",  # number of days that is percentage
    nrow(UVXY) * c(.001,.005,.01,.025,.05,.1),'\n',
    'Long-term bottom quantile \n(.1%,.5%,1%,2.5%,5%,10%): \n', round(quantile_uvxy,2), '\n',
    'Long-term top quantile \n(99.9% 99.75% 99.6% 99.5% 99% 97.5% 95% 90% 82.5% 75%): \n', round(quantile_top_uvxy,2), '\n',
    'Long-term bottom return quantile \n(.1%, .5%, 1%, 2.5%, 5%, 10%): \n', round(quantile_uvxy_ret,2), '\n',
    'Long-term top return quantile \n(99.9% 99.75% 99.6% 99.5% 99% 97.5% 95% 90% 82.5% 75%): \n', round(quantile_top_uvxy_ret,3), '\n')

cat('Probability of UVXY above 0: ',nrow(UVXY_Ret[UVXY_Ret$UVXY.Close > 0]) / nrow(UVXY_Ret$UVXY.Close),'\n')
cat('Probability of UVXY below 0: ',nrow(UVXY_Ret[UVXY_Ret$UVXY.Close < 0]) / nrow(UVXY_Ret$UVXY.Close),'\n')


# number of days below quantile
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[1],]) 
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[2],])
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[3],])
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[4],])
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[5],])
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[6],])

# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[1],]) / nrow(UVXY) # percentage time under qunatile
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[2],]) / nrow(UVXY)
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[3],]) / nrow(UVXY)
# nrow(UVXY[UVXY$UVXY.Close < quantile_uvxy[4],]) / nrow(UVXY)
# time spent quantile -----------------------------------------------

# break down of quantile by year ------------------------------------------
years = c("20120101","20130101","20140101","20150101","20160101",
          "20170101","20180101","20190101","20200101","20210101")
upperQ999 = numeric(length(years)-1)
upperQ995 = numeric(length(years)-1)
upperQ99 = numeric(length(years)-1)
upperQ985 = numeric(length(years)-1)
upperQ98 = numeric(length(years)-1)
upperQ975 = numeric(length(years)-1)
upperQ95 = numeric(length(years)-1)
upperQ90 = numeric(length(years)-1)
upperQ825 = numeric(length(years)-1)
upperQ75 = numeric(length(years)-1)

lowerQ05 = numeric(length(years)-1)
lowerQ1 = numeric(length(years)-1)
lowerQ25 = numeric(length(years)-1)
lowerQ35 = numeric(length(years)-1)
lowerQ5 = numeric(length(years)-1)
lowerQ10 = numeric(length(years)-1)
lowerQ175 = numeric(length(years)-1)
lowerQ25 = numeric(length(years)-1)

upperQ999_ret = numeric(length(years)-1)
upperQ995_ret = numeric(length(years)-1)
upperQ99_ret = numeric(length(years)-1)
upperQ985_ret = numeric(length(years)-1)
upperQ98_ret = numeric(length(years)-1)
upperQ975_ret = numeric(length(years)-1)
upperQ95_ret = numeric(length(years)-1)
upperQ90_ret = numeric(length(years)-1)
upperQ825_ret = numeric(length(years)-1)
upperQ75_ret = numeric(length(years)-1)

lowerQ05_ret = numeric(length(years)-1)
lowerQ1_ret = numeric(length(years)-1)
lowerQ25_ret = numeric(length(years)-1)
lowerQ35_ret = numeric(length(years)-1)
lowerQ5_ret = numeric(length(years)-1)
lowerQ10_ret = numeric(length(years)-1)
lowerQ175_ret = numeric(length(years)-1)
lowerQ125_ret = numeric(length(years)-1)

week52High = numeric(length(years)-1)
week52Low = numeric(length(years)-1)

for (i in 2:length(years)) {
  curr_year = paste(years[i-1],'/',years[i],sep='')
  week52High[i-1] = max(UVXY[curr_year]$UVXY.Close)
  week52Low[i-1] = min(UVXY[curr_year]$UVXY.Close)
  cat("The current year: ", years[i-1],'\n',
      "The year minimum: ", week52Low[i-1],'\n',
      "The year maximum: ", week52High[i-1],'\n',
      "The year ret minimum: ", min(UVXY_Ret[curr_year]$UVXY.Close),'\n',
      "The year ret maximum: ", max(UVXY_Ret[curr_year]$UVXY.Close),'\n',
      'Prob UVXY above 0: ',nrow(UVXY_Ret[UVXY_Ret[curr_year]$UVXY.Close > 0]) / nrow(UVXY_Ret[curr_year]$UVXY.Close),'\n',
      'Prob UVXY below 0: ',nrow(UVXY_Ret[UVXY_Ret[curr_year]$UVXY.Close < 0]) / nrow(UVXY_Ret[curr_year]$UVXY.Close),'\n',
      'The lower quantiles: \n .5%   1%    2.5%  3.5%  5%   10% 17.5% 25%\n',
      round(quantile(UVXY[curr_year]$UVXY.Close, c(.005, .01,.025,.035,.05,.1, .175, .25)),2), '\n',
      'Returns: \n .5%    1%    2.5%  3.5%  5%  10% 17.5% 25% \n',
      round(quantile(UVXY_Ret[curr_year]$UVXY.Close, c(.005, .01,.025,.035,.05,.1, .175, .25)),2), '\n',
      'The upper quantile: \n 99.9%  99.5% 99%  98.5%  98%   97.5% 95%  90% 82.5% 75%\n',
      round(quantile(UVXY[curr_year]$UVXY.Close, c(.999,.995, .99,.985,.98,.975,.95,.90, .825, .75)),2), '\n',
      'Returns: \n 99.9% 99.5% 99%  98.5%  98%  97.5%  95%  90% 82.5% 75% \n', 
      round(quantile(UVXY_Ret[curr_year]$UVXY.Close, c(.999,.995,.99,.985,.98,.975,.95,.90, .825, .75)),3),
      '\n \n'
  )
  lowerQ05[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .005),2)
  lowerQ1[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .01),2)
  lowerQ25[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .025),2)
  lowerQ35[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .035),2)
  lowerQ5[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .05),2)
  lowerQ10[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .1),2)
  lowerQ175[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .175),2)
  lowerQ25[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .25),2)
  upperQ999[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .999),2)
  upperQ995[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .995),2)
  upperQ99[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .99),2)
  upperQ985[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .985),2)
  upperQ98[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .98),2)
  upperQ975[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .975),2)
  upperQ95[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .95),2)
  upperQ90[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .9),2)
  upperQ825[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .825),2)
  upperQ75[i-1] = round(quantile(UVXY[curr_year]$UVXY.Close, .75),2)
  
  lowerQ05_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .005),2)
  lowerQ1_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .01),2)
  lowerQ25_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .025),2)
  lowerQ35_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .035),2)
  lowerQ5_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .05),2)
  lowerQ10_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .1),2)
  lowerQ175_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .175),2)
  lowerQ25_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .25),2)
  upperQ999_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .999),2)
  upperQ995_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .995),2)
  upperQ99_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .99),2)
  upperQ985_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .985),2)
  upperQ98_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .98),2)
  upperQ975_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .975),2)
  upperQ95_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .95),2)
  upperQ90_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .9),2)
  upperQ825_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .825),2)
  upperQ75_ret[i-1] = round(quantile(UVXY_Ret[curr_year]$UVXY.Close, .75),2)
}

cat("UVXY: \n",
    'Quantile .5%: \n',"12   13   14    15   16   17    18   19   20\n",lowerQ05,'\n',
    'Quantile 1%: \n',"12   13   14    15   16   17   18   19   20\n",lowerQ1,'\n',
    'Quantile 2.5%: \n',"12   13   14   15   16   17   18   19   20\n",lowerQ25,'\n',
    'Quantile 3.5%: \n',"12   13   14    15   16   17 18 19    20\n",lowerQ35,'\n',
    'Quantile 5%: \n',"12   13   14    15   16   17   18   19    20\n",lowerQ5,'\n',
    'Quantile 10%: \n',"12   13   14    15    16   17    18   19   20\n",lowerQ10,'\n',
    'Quantile 17.5%: \n',"12   13   14    15    16   17    18   19   20\n",lowerQ175,'\n',
    'Quantile 25%: \n',"12   13   14    15    16   17    18   19   20\n",lowerQ25,'\n \n',
    'Lower quantiles: \n .5%   1%   2.5%  3.5%  5%   10%   17.5%   25%\n',
    round(mean(lowerQ05),2),'',round(mean(lowerQ1),2),'',round(mean(lowerQ25),2),'',
    round(mean(lowerQ35),2),'',round(mean(lowerQ5),2),'',round(mean(lowerQ10),2),'',
    round(mean(lowerQ175),2),'', round(mean(lowerQ25),2),'\n \n',
    'Quantile 99.9%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ999,'\n',
    'Quantile 99.5%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ995,'\n',
    'Quantile 99%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ99,'\n',
    'Quantile 98.5%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ985,'\n',
    'Quantile 97.5%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ975,'\n',
    'Quantile 95%: \n',"12    13    14    15    16    17    18    19    20 \n",upperQ95,'\n',
    'Quantile 90%: \n',"12    13    14    15    16    17    18   19    20 \n",upperQ90,'\n',
    'Quantile 82.5%: \n',"12    13    14    15    16    17    18   19    20 \n",upperQ825,'\n',
    'Quantile 75%: \n',"12    13    14    15    16    17    18   19    20 \n",upperQ75,'\n \n',
    'Upper quantile: \n 99.9%  99.5%  99%   98.5%   98%    97.5%   95%  90%   82.5%   75%\n',
    round(mean(upperQ999),2),'',round(mean(upperQ995),2),'',round(mean(upperQ99),2),'',round(mean(upperQ985),2),'',
    round(mean(upperQ98),2),'',round(mean(upperQ975),2),'',round(mean(upperQ95),2),'',
    round(mean(upperQ90),2),'',round(mean(upperQ825),2),'',round(mean(upperQ75),2), '\n \n'
    )

cat('Returns: \n',
    'Quantile .5%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ05_ret,'\n',
    'Quantile 1%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ1_ret,'\n',
    'Quantile 2.5%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ25_ret,'\n',
    'Quantile 3.5%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ35_ret,'\n',
    'Quantile 5%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ5_ret,'\n',
    'Quantile 10%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ10_ret,'\n',
    'Quantile 17.5%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ175_ret,'\n',
    'Quantile 25%: \n',"12    13    14    15    16    17    18    19    20\n",lowerQ25_ret,'\n \n',
    'Lower quantiles: \n .5%,    1%    2.5%    3.5%    5%    10%   17.5%   25%\n',
    round(mean(lowerQ05_ret),2),'',round(mean(lowerQ1_ret),2),'',round(mean(lowerQ25_ret),2),'',
    round(mean(lowerQ35_ret),2),'',round(mean(lowerQ5_ret),2),'',round(mean(lowerQ10_ret),2),'',
    round(mean(lowerQ175_ret),2),'',round(mean(lowerQ25_ret),2),'\n \n',
    'Quantile 99.9%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ999_ret,'\n',
    'Quantile 99.5%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ995_ret,'\n',
    'Quantile 99%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ99_ret,'\n',
    'Quantile 98.5%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ985_ret,'\n',
    'Quantile 97.5%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ975_ret,'\n',
    'Quantile 95%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ95_ret,'\n',
    'Quantile 90%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ90_ret,'\n',
    'Quantile 82.5%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ825_ret,'\n',
    'Quantile 75%: \n',"12   13   14   15   16   17   18   19   20\n",upperQ75_ret,'\n',
    'Upper quantile: \n 99.9% 99.5% 99%   98.5% 98% 97.5%  95%   90%   82.5%   75%\n',
    round(mean(upperQ999_ret),2),'',round(mean(upperQ995_ret),2),'',round(mean(upperQ99_ret),2),'',
    round(mean(upperQ985_ret),2),'',round(mean(upperQ98_ret),2),'',round(mean(upperQ975_ret),2),'',
    round(mean(upperQ95_ret),2),'',round(mean(upperQ90_ret),2),'',round(mean(upperQ825_ret),2),'',
    round(mean(upperQ75_ret),2), '\n \n'
)
# break down of quantile by year ------------------------------------------

# yearly low/high linear regression --------------------------------------------
week52Low = c(week52Low, min(UVXY["20210101/"]$UVXY.Close))
lr_52wklow = lm(week52Low~I(1:length(week52Low)))
nxt_4yr_low = lr_52wklow$coefficients[1] + lr_52wklow$coefficients[2]*(length(week52Low)+1):(length(week52Low)+4)
week52Low = c(week52Low, nxt_4yr_low)
cat("next four years low linear regression: ", nxt_4yr_low,'\n')
plot(week52Low)
abline(lr_52wklow, col='red')

#week52High = c(week52High, max(UVXY["20210101/"]$UVXY.Close))
lr_52wkhigh = lm(week52High~I(1:length(week52High)))
nxt_4yr_high = lr_52wkhigh$coefficients[1] + lr_52wkhigh$coefficients[2]*(length(week52High)+1):(length(week52High)+4)
week52High = c(week52High, nxt_4yr_high)
cat("next four years high linear regression: ", nxt_4yr_high,'\n')
plot(week52High)
abline(lr_52wkhigh, col='red')


# yearly low/high linear regression --------------------------------------------

# TODO build the similar view together
# yearly plots ------------------------------------------------------------
#2012-2015
par(mar = c(4,4,4,6))

matplot(as.Date(index(UVXY['20130101/20140101']), "%m-%d"), 
        data.frame(c(UVXY['20120101/20130101']$UVXY.Close[1],UVXY['20120101/20130101']$UVXY.Close,UVXY['20120101/20130101']$UVXY.Close[250]), # adjust this date
                   UVXY['20130101/20140101']$UVXY.Close,
                   UVXY['20140101/20150101']$UVXY.Close,  
                   UVXY['20150101/20160101']$UVXY.Close 
        ), 
        type='l', xlab = "Dates", ylab = "UVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(0,105)
)
abline(v = as.Date(index(UVXY['20130101/20140101']), "%m-%d")
       [c(seq(1,nrow(UVXY['20130101/20140101']), 21),252)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.35,0), legend = c("2012","2013",'2014', '2015'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(10,105,10), lty=3, col='blue') # add references

#2016-2019
par(mar = c(4,4,4,6))
matplot(as.Date(index(UVXY['20170101/20180101']), "%m-%d"), 
        data.frame(UVXY['20160101/20170101']$UVXY.Close[-252],
                   UVXY['20170101/20180101']$UVXY.Close,
                   UVXY['20180101/20190101']$UVXY.Close, 
                   c(UVXY['20190101/20200101']$UVXY.Close[-252])
        ), 
        type='l', xlab = "Dates", ylab = "UVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(0,90)
)
abline(v = as.Date(index(UVXY['20170101/20180101']), "%m-%d")
       [c(seq(1,nrow(UVXY['20170101/20180101']), 21),251)], col = 'blue', lty = 3)
legend('topright', inset = c(-0.35,0), legend = c("2016","2017","2018",'2019'), 
       col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
abline(h=seq(10,85,10), lty=3, col='blue')

# 2019+
par(mar = c(4,4,4,6))
after2021 = as.numeric(UVXY['20210101/']$UVXY.Close) # use for the latest forward fill. Update
matplot(as.Date(index(UVXY['20190101/20200101']), "%m-%d"), 
        data.frame(UVXY['20190101/20200101']$UVXY.Close,
                   UVXY['20200101/20210101']$UVXY.Close[-253], 
                   c(after2021, rep(after2021[length(after2021)],252 - length(after2021)))
        ), 
        type='l', xlab = "Dates", ylab = "UVXY", col = c(1:4), lty = 1, lwd = 2, ylim=c(0,115)
)
abline(v = as.Date(index(UVXY['20200101/20210101']), "%m-%d")
       [c(seq(1,nrow(UVXY['20200101/20210101']), 21),252)], col = 'blue', lty = 3)
abline(h=seq(10,105,10), lty=3, col='blue')
legend('topright', inset = c(-0.35,0), legend = c("2019","2020","2021"), 
       col=c(1:3), lty=1, lwd = 2, xpd = TRUE)
#plot(UVXY$UVXY.Close)
# yearly plots ------------------------------------------------------------

# time spent under --------------------------------------------------------
# quantile(UVXY$UVXY.Close,.05)
# num_days = diff(index(UVXY[UVXY$UVXY.Close<15,]))
# mean(rle(num_days < 10)$lengths[rle(num_days < 10)$values == T])
# This is the average amount of days it spends below 10
num_days = diff(index(UVXY[UVXY$UVXY.Close<12,]))
days_repeat = rle(num_days >= 10)$lengths #take those that are greater than 10 days apart.
days_repeat = days_repeat[days_repeat != 1]
#days_repeat = days_repeat[-length(days_repeat)]# do not count the last sample
days_repeat = c(days_repeat[-c(5,6,12,13)],29,20) # delete certain values, the 12
mean(days_repeat) # average trading days spent under numdays cutoff
length(days_repeat)

# days above
num_days_above = diff(index(UVXY[UVXY$UVXY.Close>12,]))
days_repeat_above = rle(num_days_above >= 10)$lengths #date cutoff
days_repeat_above = days_repeat_above[days_repeat_above != 1]
days_repeat_above = days_repeat_above[!(days_repeat_above %in% c(6,3,2,9))]
mean(days_repeat_above)
length(days_repeat_above)
# time spent under --------------------------------------------------------

# # forecast ----------------------------------------------------------------
# #ets every 6,12 months
# #
# fit <- ets(UVXY['20100101/']$UVXY.Close, model = 'ZZM', damped = TRUE, lambda = TRUE)
# fcast1 <- forecast(fit, h = 22*6)
# plot(fcast1)
# autoplot(fcast1)
# 
# fit2 <- auto.arima(UVXY['20100101/']$UVXY.Close, max.order = 10, max.d=0)
# UVXY_ma <- Arima(UVXY$UVXY.Close, order = c(0,0,1))
# UVXY_ma_forecast <- forecast(UVXY_ma, h = 30 * 6)
# UVXY_forecast <- forecast(fit2, h = 30 * 6)
# plot(UVXY_ma_forecast)
# plot(UVXY_forecast)
# adf.test(UVXY$UVXY.Close)
# # forecast ----------------------------------------------------------------



# HMM

# # HMM ---------------------------------------------------------------------
# plot(UVXY_Rets)
# hmm <- depmix(UVXY.Close ~ 1, family=gaussian(), nstates = 2, data=data.frame(UVXY_Rets))
# hmmfit <- fit(hmm, verbose=FALSE)
# post_probs = posterior(hmmfit)
# layout(1:2)
# plot(UVXY$UVXY.Close)
# rownames(post_probs) <- index(UVXY_Rets)
# matplot(index(UVXY_Rets), post_probs[-1], type='l', main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# 
# #layout(1:2)
# #plot(UVXY['20170101/']$UVXY.Close)
# rownames(post_probs) <- index(UVXY_Rets) 
# #index(UVXY_Rets['20170101/']),post_probs[rownames(post_probs) >= '2017-01-01',]
# x = data.frame(post_probs[rownames(post_probs) >= '2017-01-01',-1])
# matplot(cbind(x * 100,UVXY['20170101/']$UVXY.Close), type='l', lty=c(3,3,1), main='regime posterior probabilities', ylab = 'probability')
# legend(x='bottomleft', c('Regime #1', "Regime #2"), fill=1:2, bty='n')
# # HMM ---------------------------------------------------------------------

# fit <- auto.arima(post_probs$S2, max.order = 20, seasonal = FALSE)
# fcast1 = forecast(fit, h = 60)
# plot(fcast1)
# fit2 <- ets(post_probs$S2)
# fcast2 = forecast(fit2, h=60)
# plot(fcast2)