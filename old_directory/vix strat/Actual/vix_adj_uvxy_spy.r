# packages ----------------------------------------------------------------
library(quantmod)
library(forecast)
library(timeDate)
library(data.table)
library(quantmod)
library(tseries)
library(alphavantager)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")
setwd("D:/RedX Capital/vix strat/Actual")
source('utilities.r')
# packages ----------------------------------------------------------------

# TODO VIX analytics first, then do a UVXY and VIX analytics
# VIX market timing based on VIX
# UVXY VIX Analytics year by year apply returns. overlap and view them


# basic plotting CAPM and avtual vs realized ------------------------------
uvxy_vix_capm = plot_capm_uvxy_vix()

plot_vix_sp500std()
# basic plotting CAPM and avtual vs realized ------------------------------



# VIX ---------------------------------------------------------------------
# top 50 returns ----------------------------------------------------------
cat('VIX\n','Top 50 returns: \n', sort(as.numeric(VIX_Ret$VIX.Adjusted), decreasing=TRUE)[1:50],'\n',
    'Bottom 50 returns: \n', sort(as.numeric(VIX_Ret$VIX.Adjusted), decreasing=FALSE)[1:50], '\n')
50/nrow(VIX_Ret)

#par(mfrow=c(1,1))
VIX_Ret_Recent = VIX_Ret[VIX_Ret$Date > Sys.Date()-(365*1.5),]
VIX_Ret_Recent$col = as.factor(ifelse(VIX_Ret_Recent$VIX.Adjusted > 0, 1, 0))
barplot(VIX_Ret_Recent$VIX.Adjusted, col = c('red','green')[VIX_Ret_Recent$col], main='VIX Returns', space=0, axes=FALSE, ylab='Returns')
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h = seq(-.5,1,.1))

avgRet <- function(x){
  return(prod(x + 1))
}
VIX_Ret_Recent$RollMean <- c(rep(NA,2),rollapply(VIX_Ret_Recent$VIX.Adjusted, width = 3, FUN = avgRet))
VIX_Ret_Recent$colRoll <- as.factor(ifelse(VIX_Ret_Recent$RollMean - 1 > 0, 1, 0))
barplot(VIX_Ret_Recent$RollMean - 1, col = c("red","green")[VIX_Ret_Recent$colRoll], main = "SP 500/3 day rolling average", space = 0, axes = FALSE, ylab = "Returns")
axis(side = 2, pos = 0, at = seq(-.5,1,.1))
abline(h = seq(-.5,1,.1))
# top 50 returns ----------------------------------------------------------
par(mfrow=c(1,1))
plot(VIX$VIX.Adjusted)


# Yearly VIX plot ---------------------------------------------------------
plot_tic_year('1990-01-01','1990-12-31','19900101','19901231', VIX, VIX_Ret)
plot_tic_year('1991-01-01','1991-12-31','19910101','19911231', VIX, VIX_Ret)
plot_tic_year('1992-01-01','1992-12-31','19920101','19921231', VIX, VIX_Ret)
plot_tic_year('1993-01-01','1993-12-31','19930101','19931231', VIX, VIX_Ret)
plot_tic_year('1994-01-01','1994-12-31','19940101','19941231', VIX, VIX_Ret)
plot_tic_year('1995-01-01','1995-12-31','19950101','19951231', VIX, VIX_Ret)
plot_tic_year('1996-01-01','1996-12-31','19960101','19961231', VIX, VIX_Ret)
plot_tic_year('1997-01-01','1997-12-31','19970101','19971231', VIX, VIX_Ret)
plot_tic_year('1998-01-01','1998-12-31','19980101','19981231', VIX, VIX_Ret)
plot_tic_year('1999-01-01','1999-12-31','19990101','19991231', VIX, VIX_Ret)
plot_tic_year('2000-01-01','2000-12-31','20000101','20001231', VIX, VIX_Ret)
plot_tic_year('2001-01-01','2001-12-31','20010101','20011231', VIX, VIX_Ret)
plot_tic_year('2002-01-01','2002-12-31','20020101','20021231', VIX, VIX_Ret)
plot_tic_year('2003-01-01','2003-12-31','20030101','20031231', VIX, VIX_Ret)
plot_tic_year('2004-01-01','2004-12-31','20040101','20041231', VIX, VIX_Ret)
plot_tic_year('2005-01-01','2005-12-31','20050101','20051231', VIX, VIX_Ret)
plot_tic_year('2006-01-01','2006-12-31','20060101','20061231', VIX, VIX_Ret)
plot_tic_year('2007-01-01','2007-12-31','20070101','20071231', VIX, VIX_Ret)
plot_tic_year('2008-01-01','2008-12-31','20080101','20081231', VIX, VIX_Ret)
plot_tic_year('2009-01-01','2009-12-31','20090101','20091231', VIX, VIX_Ret)
plot_tic_year('2010-01-01','2010-12-31','20100101','20101231', VIX, VIX_Ret)
plot_tic_year('2011-01-01','2011-12-31','20110101','20111231', VIX, VIX_Ret)
plot_tic_year('2012-01-01','2012-12-31','20120101','20121231', VIX, VIX_Ret)
plot_tic_year('2013-01-01','2013-12-31','20130101','20131231', VIX, VIX_Ret)
plot_tic_year('2014-01-01','2014-12-31','20140101','20141231', VIX, VIX_Ret)
plot_tic_year('2015-01-01','2015-12-31','20150101','20151231', VIX, VIX_Ret)
plot_tic_year('2016-01-01','2016-12-31','20160101','20161231', VIX, VIX_Ret)
plot_tic_year('2017-01-01','2017-12-31','20170101','20171231', VIX, VIX_Ret)
plot_tic_year('2018-01-01','2018-12-31','20180101','20181231', VIX, VIX_Ret)
plot_tic_year('2019-01-01','2019-12-31','20190101','20191231', VIX, VIX_Ret)
plot_tic_year('2020-01-01','2020-12-31','20200101','20201231', VIX, VIX_Ret)
plot_tic_year('2021-01-01','2021-12-31','20210101','20211231', VIX, VIX_Ret)
# Yearly VIX plot ---------------------------------------------------------

# Overlapping plot
plot_tic_90_93(VIX)
plot_tic_94_97(VIX)
plot_tic_98_01(VIX)
plot_tic_02_05(VIX)
plot_tic_06_09(VIX)
plot_tic_10_13(VIX)
plot_tic_14_17(VIX)
plot_tic_18_21(VIX)
# VIX ---------------------------------------------------------------------
# TODO build a hypothetical price series include both high and lows.
# TODO time series prediction 5 days for 
# TODO overlap alpha vantage and uvxy and vix data series
# TODO look at SPY when it drops heavily, make an easier plot analysis, basically market timing strategy
# TODO index analysis first, that is russell 1k,2k, value, growth, check their overtime alpha, beta levels, find predictability.
# TODO basically an index timing strategy.


# UVXY_ALPHA --------------------------------------------------------------
UVXY_SPY_Ret$alpha = NA
UVXY_SPY_Ret$beta = NA
for (i in 253:nrow(UVXY_SPY_Ret)) {
  model = lm(UVXY.Adjusted~SPY.Adjusted, data=UVXY_SPY_Ret[(i-252):i,])
  UVXY_SPY_Ret$alpha[i] = round(as.numeric(model$coefficients[1]) * 252,4)
  UVXY_SPY_Ret$beta[i] = round(as.numeric(model$coefficients[2]),4)
}
plot(as.Date(UVXY_SPY_Ret$Date),UVXY_SPY_Ret$alpha, type='l')
abline(h=0, col='red') # TODO HPF or prediction models or look at the RSI

plot(as.Date(UVXY_SPY_Ret$Date),UVXY_SPY_Ret$beta, type='l')
abline(h=0, col='red') # TODO HPF or prediction models or look at the RSI. OR HPF and look at average time below
library(plot3D)
scatter3D(index(UVXY_SPY_Ret), UVXY_SPY_Ret$beta, UVXY_SPY_Ret$alpha, clab=c('Index', 'Beta', 'Alpha'))
# UVXY_ALPHA --------------------------------------------------------------


# UVXY_VIX Line Plots -----------------------------------------------------
plot_uvxy_vix('2012-01-01','2012-12-31',UVXY_VIX)
#plot_uvxy_vix('2012-01-01','2012-12-31',UVXY_VIX, compare=TRUE)
plot_uvxy_vix('2013-01-01','2013-12-31',UVXY_VIX)
plot_uvxy_vix('2014-01-01','2014-12-31',UVXY_VIX)
plot_uvxy_vix('2015-01-01','2015-12-31',UVXY_VIX)
plot_uvxy_vix('2016-01-01','2016-12-31',UVXY_VIX)
plot_uvxy_vix('2017-01-01','2017-12-31',UVXY_VIX)
plot_uvxy_vix('2018-01-01','2018-12-31',UVXY_VIX)
plot_uvxy_vix('2019-01-01','2019-12-31',UVXY_VIX)
plot_uvxy_vix('2020-01-01','2020-12-31',UVXY_VIX)
plot_uvxy_vix('2021-01-01','2021-12-31',UVXY_VIX)
# UVXY_VIX Line Plots -----------------------------------------------------
