# packages ----------------------------------------------------------------
library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(alphavantager)
library(quantmod)
library(tseries)
library(zoo)
library(lubridate)
library(DescTools) # winsorized tools
# years that are similar
#2021 2020 2018 2012 2013, 2012, 2013 (2015)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")
# packages ----------------------------------------------------------------
setwd("D:/RedX Capital/vix strat")

# getting the data --------------------------------------------------------
# getSymbols('UVXY', verbose = FALSE, from = "2011-01-01", to=Sys.Date()+1)
# getSymbols('VIXY', verbose = FALSE, from = "2008-01-01" )
getSymbols('UVXY', verbose = FALSE, from = "2011-01-01" , to = Sys.Date()+1, src = 'av', output = 'full')
# getSymbols('^VIX', verbose = FALSE, from='1985-01-01')

# VIX_Ret = VIX$VIX.Adjusted / shift(VIX$VIX.Adjusted) - 1
# VIX_Ret <- as.data.frame(VIX_Ret)
# VIX_Ret$Date <- rownames(VIX_Ret)
# rownames(VIX_Ret) <- NULL
# VIX_Ret = VIX_Ret[,c('Date', 'VIX.Adjusted')]
# #UVXY = UVXY['20111031/']

UVXY_Ret = (UVXY$UVXY.Close / shift(UVXY$UVXY.Close) - 1)[-1]
UVXY_Ret <- as.data.frame(UVXY_Ret)
UVXY_Ret$Date = rownames(UVXY_Ret)
rownames(UVXY_Ret) = NULL
UVXY_Ret$col = as.factor(ifelse(UVXY_Ret$UVXY.Close > 0, 1, 0))
UVXY_Ret = UVXY_Ret[,c('Date','UVXY.Close', 'col')]

# UVXY_VIX_Ret = merge(UVXY_Ret, VIX_Ret, by='Date', all.x=TRUE)
# 
# VIXY_Ret = (VIXY$VIXY.Adjusted / shift(VIXY$VIXY.Adjusted) - 1)[-1]
# VIXY_Ret <- as.data.frame(VIXY_Ret)
# VIXY_Ret$Date = rownames(VIXY_Ret)
# rownames(VIXY_Ret) = NULL
# VIXY_Ret$col = as.factor(ifelse(VIXY_Ret$VIXY.Adjusted > 0, 1, 0))
# VIXY_Ret = VIXY_Ret[,c('Date','VIXY.Adjusted', 'col')]
# VIXY_VIX_Ret = merge(VIXY_Ret, VIX_Ret, by='Date', all.x=TRUE) 
# getting the data --------------------------------------------------------

# plot(UVXY_VIX_Ret$VIX.Adjusted, UVXY_VIX_Ret$UVXY.Close, xlab='VIX', ylab='UVXY')
# uvxy_vix_lm = lm(UVXY.Close~VIX.Adjusted, data=UVXY_VIX_Ret)
# abline(uvxy_vix_lm)
# abline(h=0,v=0)
# abline(0,1,col='red')
# summary(uvxy_vix_lm)

# plot(VIXY_VIX_Ret$VIX.Adjusted, VIXY_VIX_Ret$VIXY.Adjusted, xlab='VIX', ylab='VIXY')
# VIXY_vix_lm = lm(VIXY.Adjusted~VIX.Adjusted, data=VIXY_VIX_Ret)
# abline(VIXY_vix_lm)
# abline(h=0,v=0)
# summary(VIXY_vix_lm)
# TODO build a hypothetical price series include both high and lows.
#isNon_Split = UVXY_VIX_Ret$UVXY.Close <= 2 # taking out the splits
# plot(UVXY_VIX_Ret[isNon_Split,]$VIX.Adjusted, UVXY_VIX_Ret[isNon_Split,]$UVXY.Close, xlab='VIX', ylab='UVXY')
# uvxy_vix_lm = lm(UVXY.Close~VIX.Adjusted, data=UVXY_VIX_Ret[isNon_Split,])
# abline(uvxy_vix_lm)
# abline(h=0,v=0)
# summary(uvxy_vix_lm)
# UVXY_Unadj = as.numeric(VIX[UVXY_VIX_Ret$Date[1] == index(VIX),]$VIX.Adjusted) * cumprod(UVXY_VIX_Ret[isNon_Split,]$UVXY.Close+1)
# manually adjust the 9 splits returns

# TODO build the cboe to UVXY
# TODO MEASURE THE DISTANCE FROM HIGH TO LOW DAILY VOLATILITY
# TODO rolling 3 days min and max tdistribution could be 5 days also
# TODO the probability distribution before the jump
# TODO write everything into functions

# Top 50 returns and bar plot ---------------------------------------------
cat('UVXY\n','Top 50 returns: \n', sort(as.numeric(UVXY_Ret$UVXY.Close), decreasing=TRUE)[1:50],'\n',
    'Bottom 50 returns: \n', sort(as.numeric(UVXY_Ret$UVXY.Close), decreasing=FALSE)[1:50], '\n')
50/nrow(UVXY_Ret)

#par(mfrow=c(1,1))
UVXY_Ret_Recent = UVXY_Ret[UVXY_Ret$Date > Sys.Date()-(365*1.5),]
UVXY_Ret_Recent$col = as.factor(ifelse(UVXY_Ret_Recent$UVXY.Close > 0, 1, 0))
barplot(UVXY_Ret_Recent$UVXY.Close, col = c('red','green')[UVXY_Ret_Recent$col], main='UVXY Returns', space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h = seq(-.5,1,.1))

avgRet <- function(x){
  return(prod(x + 1))
}
UVXY_Ret_Recent$RollMean <- c(rep(NA,2),rollapply(UVXY_Ret_Recent$UVXY.Close, width = 3, FUN = avgRet))
UVXY_Ret_Recent$colRoll <- as.factor(ifelse(UVXY_Ret_Recent$RollMean - 1 > 0, 1, 0))
barplot(UVXY_Ret_Recent$RollMean - 1, col = c("red","green")[UVXY_Ret_Recent$colRoll], main = "SP 500/3 day rolling average", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h = seq(-.5,1,.1))
# Top 50 returns and bar plot ---------------------------------------------

# 2012 --------------------------------------------------------------------
year_2012 = UVXY_Ret$Date <= '2012-12-31' & UVXY_Ret$Date >= "2012-01-01"
UVXY_Ret_2012 = UVXY_Ret[year_2012,]
UVXY_Ret_2012$winsorized = Winsorize(UVXY_Ret_2012$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))


cat('2012\n','Top 10 returns: \n', sort(UVXY_Ret_2012$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2012$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2012),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2012$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2012$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2012$UVXY.Close > 0) / nrow(UVXY_Ret_2012),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2012$UVXY.Close <= 0) / nrow(UVXY_Ret_2012),'\n')
# par(mfrow=c(1,1))
# hist(UVXY_Ret_2012$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20120101/20121231']), UVXY['20120101/20121231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2012')
barplot(UVXY_Ret_2012$winsorized, col = c('red','green')[UVXY_Ret_2012$col], space=0, axes=FALSE, ylab='Returns', ylim=c(-.5,1))
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2012 --------------------------------------------------------------------


# 2013 --------------------------------------------------------------------
year_2013 = UVXY_Ret$Date <= '2013-12-31' & UVXY_Ret$Date >= "2013-01-01"
UVXY_Ret_2013 = UVXY_Ret[year_2013,]
UVXY_Ret_2013$winsorized = Winsorize(UVXY_Ret_2013$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2013\n','Top 10 returns: \n', sort(UVXY_Ret_2013$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2013$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2013),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2013$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2013$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2013$UVXY.Close > 0) / nrow(UVXY_Ret_2013),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2013$UVXY.Close <= 0) / nrow(UVXY_Ret_2013),'\n')
# par(mfrow=c(1,1))
# hist(UVXY_Ret_2013$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20130101/20131231']), UVXY['20130101/20131231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2013')
barplot(UVXY_Ret_2013$winsorized, col = c('red','green')[UVXY_Ret_2013$col], space=0, axes=FALSE, ylab='Returns', ylim=c(-.5,1))
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2013 --------------------------------------------------------------------


# 2014 --------------------------------------------------------------------
year_2014 = UVXY_Ret$Date <= '2014-12-31' & UVXY_Ret$Date >= "2014-01-01"
UVXY_Ret_2014 = UVXY_Ret[year_2014,]
UVXY_Ret_2014$winsorized = Winsorize(UVXY_Ret_2014$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2014\n','Top 10 returns: \n', sort(UVXY_Ret_2014$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2014$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2014),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2014$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2014$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2014$UVXY.Close > 0) / nrow(UVXY_Ret_2014),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2014$UVXY.Close <= 0) / nrow(UVXY_Ret_2014),'\n')
# par(mfrow=c(1,1))
# hist(UVXY_Ret_2014$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20140101/20141231']), UVXY['20140101/20141231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2014')
barplot(UVXY_Ret_2014$winsorized, col = c('red','green')[UVXY_Ret_2014$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2014 --------------------------------------------------------------------


# 2015 --------------------------------------------------------------------
year_2015 = UVXY_Ret$Date <= '2015-12-31' & UVXY_Ret$Date >= "2015-01-01"
UVXY_Ret_2015 = UVXY_Ret[year_2015,]
UVXY_Ret_2015$winsorized = Winsorize(UVXY_Ret_2015$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2015\n','Top 10 returns: \n', sort(UVXY_Ret_2015$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2015$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2015),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2015$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2015$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2015$UVXY.Close > 0) / nrow(UVXY_Ret_2015),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2015$UVXY.Close <= 0) / nrow(UVXY_Ret_2015),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2015$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20150101/20151231']), UVXY['20150101/20151231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2015')
barplot(UVXY_Ret_2015$winsorized, col = c('red','green')[UVXY_Ret_2015$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2015 --------------------------------------------------------------------


# 2016 --------------------------------------------------------------------
year_2016 = UVXY_Ret$Date <= '2016-12-31' & UVXY_Ret$Date >= "2016-01-01"
UVXY_Ret_2016 = UVXY_Ret[year_2016,]
UVXY_Ret_2016$winsorized = Winsorize(UVXY_Ret_2016$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2016\n','Top 10 returns: \n', sort(UVXY_Ret_2016$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2016$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2016),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2016$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2016$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2016$UVXY.Close > 0) / nrow(UVXY_Ret_2016),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2016$UVXY.Close <= 0) / nrow(UVXY_Ret_2016),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2016$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20160101/20161231']), UVXY['20160101/20161231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2016')
barplot(UVXY_Ret_2016$winsorized, col = c('red','green')[UVXY_Ret_2016$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2016 --------------------------------------------------------------------

# 2017 --------------------------------------------------------------------
year_2017 = UVXY_Ret$Date <= '2017-12-31' & UVXY_Ret$Date >= "2017-01-01"
UVXY_Ret_2017 = UVXY_Ret[year_2017,]
UVXY_Ret_2017$winsorized = Winsorize(UVXY_Ret_2017$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2017\n','Top 10 returns: \n', sort(UVXY_Ret_2017$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2017$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2017),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2017$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2017$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2017$UVXY.Close > 0) / nrow(UVXY_Ret_2017),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2017$UVXY.Close <= 0) / nrow(UVXY_Ret_2017),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2017$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20170101/20171231']), UVXY['20170101/20171231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2017')
barplot(UVXY_Ret_2017$winsorized, col = c('red','green')[UVXY_Ret_2017$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2017 --------------------------------------------------------------------

# 2018 --------------------------------------------------------------------
year_2018 = UVXY_Ret$Date <= '2018-12-31' & UVXY_Ret$Date >= "2018-01-01"
UVXY_Ret_2018 = UVXY_Ret[year_2018,]
UVXY_Ret_2018$winsorized = Winsorize(UVXY_Ret_2018$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2018\n','Top 10 returns: \n', sort(UVXY_Ret_2018$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2018$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2018),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2018$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2018$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2018$UVXY.Close > 0) / nrow(UVXY_Ret_2018),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2018$UVXY.Close <= 0) / nrow(UVXY_Ret_2018),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2018$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20180101/20181231']), UVXY['20180101/20181231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2018')
barplot(UVXY_Ret_2018$winsorized, col = c('red','green')[UVXY_Ret_2018$col], space=0, axes=FALSE, ylab='Returns', ylim=c(-.5,1))
axis(side = 2, pos = 0, at = seq(-1,1.2,.1))
abline(h=seq(-1,2,.1))
par(mfrow=c(1,1))
# 2018 --------------------------------------------------------------------

# 2019 --------------------------------------------------------------------
year_2019 = UVXY_Ret$Date <= '2019-12-31' & UVXY_Ret$Date >= "2019-01-01"
UVXY_2019 = UVXY[year_2019,]
UVXY_Ret_2019 = UVXY_Ret[year_2019,]
UVXY_Ret_2019$winsorized = Winsorize(UVXY_Ret_2019$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2019\n','Top 10 returns: \n', sort(UVXY_Ret_2019$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2019$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2019),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2019$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2019$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2019$UVXY.Close > 0) / nrow(UVXY_Ret_2019),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2019$UVXY.Close <= 0) / nrow(UVXY_Ret_2019),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2019$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20190101/20191231']), UVXY['20190101/20191231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2019')
barplot(UVXY_Ret_2019$winsorized, col = c('red','green')[UVXY_Ret_2019$col], space=0, axes=FALSE, ylab='Returns', ylim=c(-.5,1))
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2019 --------------------------------------------------------------------

# 2020 --------------------------------------------------------------------
year_2020 = UVXY_Ret$Date <= '2020-12-31' & UVXY_Ret$Date >= "2020-01-01"
UVXY_Ret_2020 = UVXY_Ret[year_2020,]
UVXY_Ret_2020$winsorized = Winsorize(UVXY_Ret_2020$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))


cat('2020\n','Top 10 returns: \n', sort(UVXY_Ret_2020$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2020$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2020),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2020$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2020$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2020$UVXY.Close > 0) / nrow(UVXY_Ret_2020),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2020$UVXY.Close <= 0) / nrow(UVXY_Ret_2020),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2020$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20200101/20201231']), UVXY['20200101/20201231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2020')
barplot(UVXY_Ret_2020$winsorized, col = c('red','green')[UVXY_Ret_2020$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2020 --------------------------------------------------------------------

# 2021 --------------------------------------------------------------------
year_2021 = UVXY_Ret$Date <= '2021-12-31' & UVXY_Ret$Date >= "2021-01-01"
UVXY_Ret_2021 = UVXY_Ret[year_2021,]
UVXY_Ret_2021$winsorized = Winsorize(UVXY_Ret_2021$UVXY.Close, minval=-.3, maxval=1,probs=c(.02,.98))

cat('2021\n','Top 10 returns: \n', sort(UVXY_Ret_2021$UVXY.Close, decreasing=TRUE)[1:10],'\n',
    'Bottom 10 returns: \n', sort(UVXY_Ret_2021$UVXY.Close, decreasing=FALSE)[1:10], '\n',
    'Number of days: ',nrow(UVXY_Ret_2021),'\n',
    'Numbers of days ret above 0: ',sum(UVXY_Ret_2021$UVXY.Close > 0),'\n',
    'Numbers of days ret <= 0: ',sum(UVXY_Ret_2021$UVXY.Close <= 0),'\n',
    'probs > 0: ', sum(UVXY_Ret_2021$UVXY.Close > 0) / nrow(UVXY_Ret_2021),'\n',
    'probs <= 0: ', sum(UVXY_Ret_2021$UVXY.Close <= 0) / nrow(UVXY_Ret_2021),'\n')

# par(mfrow=c(1,1))
# hist(UVXY_Ret_2021$UVXY.Close, breaks=50)

par(mfrow=c(2,1))
plot(index(UVXY['20210101/20211231']), UVXY['20210101/20211231']$UVXY.Close, type='l', xlab='Date', ylab='UVXY', main='UVXY 2021')
barplot(UVXY_Ret_2021$winsorized, col = c('red','green')[UVXY_Ret_2021$col], space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h=seq(-.5,1,.1))
par(mfrow=c(1,1))
# 2021 --------------------------------------------------------------------
