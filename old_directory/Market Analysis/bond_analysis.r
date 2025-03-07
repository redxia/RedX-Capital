tlt=read.csv('tlt_analysis.csv')

#t2yr_model=lm(t2yr~fedfunds, data=tlt[4600:nrow(tlt),])
t2yr_model=lm(t2yr~fedfunds, data=tlt)
#t2yr_model=lm(t2yr~log(fedfunds), data=tlt[4600:nrow(tlt),])
plot(tlt$fedfunds,tlt$t2yr, main='fedfunds vs 2yr')
#lines(tlt[4600:nrow(tlt),"fedfunds"],log(tlt[4600:nrow(tlt),"fedfunds"])*t2yr_model$coefficients[1]+t2yr_model$coefficients[1], col='red')
abline(t2yr_model, col='red')
abline(h=0,v=0)

t2yr_detrender=lm(tlt$t2yr~as.numeric(rownames(tlt)), tlt)
fedfund_detrender=lm(fedfunds~as.numeric(rownames(tlt)), tlt)

t10yr_model=lm(tlt$t10yr~tlt$t2yr)
t10yr_model=lm(tlt$t10yr_detrend~tlt$t2yr_detrend)
plot(tlt$t2yr[4600:nrow(tlt)], tlt$t10yr[4600:nrow(tlt)], main='2yr detrend vs 10yr detrend')
plot(tlt$t2yr_detrend[4600:nrow(tlt)], tlt$t10yr_detrend[4600:nrow(tlt)], main='2yr detrend vs 10yr detrend')
abline(t10yr_model, col='red')
abline(h=0,v=0)
abline(0,.6, col='green')

t20yr_model=lm(tlt$t20yr~tlt$t10yr)
plot(tlt$t10yr[4600:nrow(tlt)], tlt$t20yr[4600:nrow(tlt)], main='10yr vs. 20yr')
abline(t20yr_model, col='red')
abline(h=0,v=0)

tlt_model=lm(tlt$Close~tlt$t20yr)
plot(tlt$t20yr[4600:nrow(tlt)],tlt$Close[4600:nrow(tlt)], main='t20yr vs tlt')
abline(tlt_model, col='red')
abline(h=0,v=0)

