# TODO change these functions for general df with either xts of df inputs
# getting the data --------------------------------------------------------
print('Getting the Data')
getSymbols('UVXY', verbose = FALSE, from = "2011-10-04" ) # when the etf started
getSymbols('SPY', verbose = FALSE, from = "1990-01-01" )
getSymbols('^VIX', verbose = FALSE, from='1990-01-01')

VIX_Ret = (VIX$VIX.Adjusted / shift(VIX$VIX.Adjusted) - 1)[-1]
VIX_Ret <- as.data.frame(VIX_Ret)
VIX_Ret$Date <- rownames(VIX_Ret)
rownames(VIX_Ret) <- NULL
VIX_Ret$col = as.factor(ifelse(VIX_Ret$VIX.Adjusted > 0, 1, 0))
VIX_Ret = VIX_Ret[,c('Date', 'VIX.Adjusted','col')]

UVXY_Ret = (UVXY$UVXY.Adjusted / shift(UVXY$UVXY.Adjusted) - 1)[-1]
UVXY_Ret <- as.data.frame(UVXY_Ret)
UVXY_Ret$Date = rownames(UVXY_Ret)
rownames(UVXY_Ret) = NULL
UVXY_Ret = UVXY_Ret[,c('Date','UVXY.Adjusted')]
UVXY_VIX_Ret = merge(UVXY_Ret, VIX_Ret, by='Date', all.x=TRUE)
df_VIX = as.data.frame(VIX)
df_VIX$Date <- rownames(df_VIX)
rownames(df_VIX) <- NULL
df_VIX = df_VIX[,c('Date','VIX.Open','VIX.Low','VIX.Adjusted')]

UVXY_av = getSymbols('UVXY', verbose = FALSE, from = "2011-10-04", src='av', to=Sys.Date()+1, output='full', auto.assign=FALSE) 
UVXY_av <- as.data.frame(UVXY_av)
UVXY_av$Date = rownames(UVXY_av)
rownames(UVXY_av) <- NULL
UVXY_av = UVXY_av[,c('Date','UVXY.Close')]
VIX <- as.data.frame(VIX)
VIX$Date = rownames(VIX)
rownames(VIX) <- NULL
VIX = VIX[,c('Date', 'VIX.Adjusted')]
UVXY_VIX = merge(UVXY_av, VIX, by='Date', all.x=TRUE)

SPY_Ret = (SPY$SPY.Adjusted / shift(SPY$SPY.Adjusted) - 1)[-1]
SPY_Ret <- as.data.frame(SPY_Ret)
SPY_Ret$Date = rownames(SPY_Ret)
rownames(SPY_Ret) <- NULL
SPY_Ret = SPY_Ret[,c('Date','SPY.Adjusted')]
SPY_Ret$std = round(c(rep(NA,20),rollapply(SPY_Ret$SPY.Adjusted,21, sd) * sqrt(252))  * 100,2)# annaulized
UVXY_SPY_Ret = merge(UVXY_Ret, SPY_Ret, by='Date', all.x=TRUE)
VIX_SPY = merge(df_VIX, SPY_Ret, by='Date', all.x=TRUE)
print('Finished getting the data')
# getting the data --------------------------------------------------------


# CAPM UVXY -----------------------------------------------------------
plot_capm_uvxy_vix <- function() {
  plot(UVXY_VIX_Ret$VIX.Adjusted, UVXY_VIX_Ret$UVXY.Adjusted, xlab='VIX', ylab='UVXY')
  uvxy_vix_lm = lm(UVXY.Adjusted~VIX.Adjusted, data=UVXY_VIX_Ret)
  abline(uvxy_vix_lm)
  abline(h=0,v=0)
  abline(0,1,col='red')
  print(summary(uvxy_vix_lm))
  return(uvxy_vix_lm)
}

plot_capm_uvxy_SPY <- function() {
  plot(UVXY_SPY_Ret$SPY.Adjusted, UVXY_SPY_Ret$UVXY.Adjusted, xlab='SPY', ylab='UVXY')
  uvxy_SPY_lm = lm(UVXY.Adjusted~SPY.Adjusted, data=UVXY_SPY_Ret)
  abline(uvxy_SPY_lm)
  abline(h=0,v=0)
  abline(0,1,col='red')
  print(summary(uvxy_SPY_lm))
  return(uvxy_SPY_lm)
}
# CAPM UVXY -----------------------------------------------------------


#  VIX vs SP500 volatility ------------------------------------------------
plot_vix_sp500std <- function() {
  plot(VIX_SPY$std,VIX_SPY$VIX.Adjusted)
  lm_model = lm(VIX.Adjusted~std, data=VIX_SPY)
  abline(lm_model)
  abline(h=0,v=0)
  abline(0,1,col='red')
  print(summary(lm_model))
  VIX_SPY$Date = as.Date(VIX_SPY$Date)
  plot(VIX_SPY$Date,VIX_SPY$std, type='l')
  lines(VIX_SPY$Date,VIX_SPY$VIX.Adjusted, col='red')
  legend('topleft',c('SP 500', 'VIX'), col=c('black','red'), lty=1)
}
#  VIX vs SP500 volatility ------------------------------------------------


# year plot ---------------------------------------------------------------
plot_tic_year = function(start_date, end_date, xts_start_date, xts_end_date, df_symbol, df_symbol_ret) {
  isYear = df_symbol_ret$Date <= end_date & df_symbol_ret$Date >= start_date
  df_year = df_symbol_ret[isYear,]
  cat(start_date,'\n','Top 10 returns: \n', sort(df_year[,2], decreasing=TRUE)[1:10],'\n',
      'Bottom 10 returns: \n', sort(df_year[,2], decreasing=FALSE)[1:10], '\n',
      'Number of days: ',nrow(df_year),'\n',
      'Numbers of days ret above 0: ',sum(df_year[,2] > 0),'\n',
      'Numbers of days ret <= 0: ',sum(df_year[,2] <= 0),'\n',
      'probs > 0: ', sum(df_year[,2] > 0) / nrow(df_year),'\n',
      'probs <= 0: ', sum(df_year[,2] <= 0) / nrow(df_year),'\n')
  par(mfrow=c(2,1))
  xtsYear = paste(xts_start_date,xts_end_date, sep='/')
  plot(index(df_symbol[xtsYear]), df_symbol[xtsYear][,6], type='l', xlab='Date', ylab='VIX', main=start_date)
  barplot(df_year[,2], col = c('red','green')[df_year$col], space=0, axes=FALSE, ylab='Returns', ylim=c(-.5,1)) 
  axis(side = 2, pos = 0, at = seq(-.5,1,.1))
  abline(h=seq(-.5,1,.1))
  par(mfrow=c(1,1))
}
# year plot ---------------------------------------------------------------


# VIX every 4 year --------------------------------------------------------
plot_tic_90_93 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['19910101/19911231']), "%m-%d"), 
          data.frame(df_symbol['19900101/19901231'][,6], # adjust this date
                     df_symbol['19910101/19911231'][,6],
                     df_symbol['19920101/19921231'][-1,6],  
                     df_symbol['19930101/19931231'][,6] 
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='1990-1993' 
  )
  abline(v = as.Date(index(df_symbol['19910101/19911231']), "%m-%d")
         [c(seq(1,nrow(df_symbol['19910101/19911231']), 21),253)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("1990","1991",'1992', '1993'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,40,5), lty=3, col='blue') # add references
}

plot_tic_94_97 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['19960101/19961231'][-1]), "%m-%d"), 
          data.frame(c(df_symbol['19940101/19941231'][1,6],df_symbol['19940101/19941231'][,6]), # adjust this date
                     c(df_symbol['19950101/19951231'][1,6],df_symbol['19950101/19951231'][,6]),
                     df_symbol['19960101/19961231'][-1,6],  
                     df_symbol['19970101/19971231'][,6] 
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='1994-1997' 
  )
  abline(v = as.Date(index(df_symbol['19960101/19961231'][-1]), "%m-%d")
         [c(seq(1,nrow(df_symbol['19960101/19961231'][-1]), 21),253)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("1994","1995",'1996', '1997'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,40,5), lty=3, col='blue') # add references
}

plot_tic_98_01 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['19990101/19991231']), "%m-%d"), 
          data.frame(df_symbol['19980101/19981231'][,6],
                     df_symbol['19990101/19991231'][,6],
                     df_symbol['20000101/20001231'][,6],  
                     c(df_symbol['20010101/20011231'][1,6],df_symbol['20010101/20011231'][1,6],df_symbol['20010101/20011231'][,6],
                       df_symbol['20010101/20011231'][248,6],df_symbol['20010101/20011231'][248,6])
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='1998-2001' 
  )
  abline(v = as.Date(index(df_symbol['19990101/19991231']), "%m-%d")
         [c(seq(1,nrow(df_symbol['19990101/19991231']), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("1998","1999",'2000', '2001'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,45,5), lty=3, col='blue') # add references
}

plot_tic_02_05 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['20030101/20031231']), "%m-%d"), 
          data.frame(df_symbol['20020101/20021231'][,6],
                     df_symbol['20030101/20031231'][,6],
                     df_symbol['20040101/20041231'][,6],  
                     df_symbol['20050101/20051231'][,6]
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='2002-2005' 
  )
  abline(v = as.Date(index(df_symbol['20030101/20031231']), "%m-%d")
         [c(seq(1,nrow(df_symbol['20030101/20031231']), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("2002","2003",'2004', '2005'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,45,5), lty=3, col='blue') # add references
}

plot_tic_06_09 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['20080101/20081231'][-1,6]), "%m-%d"), 
          data.frame(c(df_symbol['20060101/20061231'][1,6],df_symbol['20060101/20061231'][,6]),
                     c(df_symbol['20070101/20071231'][1,6],df_symbol['20070101/20071231'][,6]),
                     df_symbol['20080101/20081231'][-1,6],  
                     df_symbol['20090101/20091231'][,6]
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='2006-2009' 
  )
  abline(v = as.Date(index(df_symbol['20080101/20081231'][-1]), "%m-%d")
         [c(seq(1,nrow(df_symbol['20080101/20081231'][-1]), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("2006","2007",'2008', '2009'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(0,90,10), lty=3, col='blue') # add references
}

plot_tic_10_13 <- function(df_symbol) {
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['20110101/20111231'][,6]), "%m-%d"), 
          data.frame(df_symbol['20100101/20101231'][,6],
                     df_symbol['20110101/20111231'][,6],
                     c(df_symbol['20120101/20121231'][1,6],df_symbol['20120101/20121231'][,6],df_symbol['20120101/20121231'][250,6]),  
                     df_symbol['20130101/20131231'][,6]
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='2010-2013' 
  )
  abline(v = as.Date(index(df_symbol['20110101/20111231'][,6]), "%m-%d")
         [c(seq(1,nrow(df_symbol['20110101/20111231'][,6]), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("2010","2011",'2012', '2013'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,45,5), lty=3, col='blue') # add references
}

plot_tic_14_17 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  matplot(as.Date(index(df_symbol['20150101/20151231'][,6]), "%m-%d"), 
          data.frame(df_symbol['20140101/20141231'][,6],
                     df_symbol['20150101/20151231'][,6],
                     df_symbol['20160101/20161231'][,6],
                     c(df_symbol['20170101/20171231'][1,6],df_symbol['20170101/20171231'][,6])
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='2014-2017' 
  )
  abline(v = as.Date(index(df_symbol['20150101/20151231'][,6]), "%m-%d")
         [c(seq(1,nrow(df_symbol['20150101/20151231'][,6]), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("2014","2015",'2016', '2017'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(5,45,5), lty=3, col='blue') # add references
}

plot_tic_18_21 <- function(df_symbol){
  par(mar = c(4,4,4,6))
  after2021 = as.numeric(df_symbol['20210101/'][,6]) # use for the latest forward fill. Update
  matplot(as.Date(index(df_symbol['20190101/20191231'][,6]), "%m-%d"), 
          data.frame(c(df_symbol['20180101/20181231'][1,6],df_symbol['20180101/20181231'][,6]),
                     df_symbol['20190101/20191231'][,6],
                     df_symbol['20200101/20201231'][-1,6],
                     c(after2021, rep(after2021[length(after2021)],252 - length(after2021)))
          ), 
          type='l', xlab = "Dates", ylab = colnames(df_symbol)[6], col = c(1:4), lty = 1, lwd = 2, main='2018-2021' 
  )
  abline(v = as.Date(index(df_symbol['20190101/20191231'][,6]), "%m-%d")
         [c(seq(1,nrow(df_symbol['20190101/20191231'][,6]), 21),252)], col = 'blue', lty = 3)
  legend('topright', inset = c(-0.35,0), legend = c("2018","2019",'2020', '2021'), 
         col=c(1:4), lty=1, lwd = 2, xpd = TRUE)
  abline(h=seq(0,90,10), lty=3, col='blue') # add references
}

# VIX every 4 year --------------------------------------------------------

#TODO add VIX RSI as subplot in this
#TODO can add spy line
# VIX_UVXY_plot -----------------------------------------------------------
plot_uvxy_vix = function(start_date, end_date, df, compare=FALSE) {
  isYear = df$Date <= end_date & df$Date >= start_date
  df_year = df[isYear,]
  par(mfrow=c(1,1))
  if (compare==TRUE) {
    df_year[,2] = df_year[,2] / df_year[1,2]
    df_year[,3] = df_year[,3] / df_year[1,3]
    plot(as.Date(df_year$Date), df_year[,2], type='l', col='blue', main=start_date, xlab='Date', ylab='Price', ylim=c(min(df_year[,2:3])-.1,max(df_year[,2:3])+.1))
    lines(as.Date(df_year$Date), df_year[,3], col='Red')
    abline(h=seq(0,max(df_year[,2:3])+.1))
  } else {
    plot(as.Date(df_year$Date), df_year[,2], type='l', col='blue', main=start_date, xlab='Date', ylab='Price', ylim=c(min(df_year[,2:3])-5,max(df_year[,2:3])+5))
    lines(as.Date(df_year$Date), df_year[,3], col='Red')
    abline(h=seq(0,max(df_year[,2:3])+5,5), lty=3, col='gray')
    print(as.Date(df_year$Date)[c(seq(1,nrow(df_year), 21))])
    abline(v = as.Date(df_year$Date)[c(seq(1,nrow(df_year), 22),252)], col = 'gray', lty = 3)
  }
  legend('topleft',col=c('blue','red'), legend=c(colnames(df)[2], colnames(df)[3]), lty=1)
}
# VIX_UVXY_plot -----------------------------------------------------------
