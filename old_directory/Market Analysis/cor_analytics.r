library(data.table)
library(DescTools)
library(mFilter)
library(forecast)

sp500_t10y_t2yr=read.csv("sp500_t10y_t2y.csv")
sp500_t10y_t2yr
sp500_t10y_t2yr$Date
model=ar(sp500_t10y_t2yr$t10yr_t2yr, order.max=1)
prediction=forecast(model,h=252)
(prediction$mean+prediction$lower[,1])/2

model_lm=lm(sp500_t10y_t2yr$returns_12mo[(nrow(sp500_t10y_t2yr)-378):nrow(sp500_t10y_t2yr)]~sp500_t10y_t2yr$t10yr_t2yr[(nrow(sp500_t10y_t2yr)-378):nrow(sp500_t10y_t2yr)])
summary(model_lm)
plot(sp500_t10y_t2yr$returns_12mo[(nrow(sp500_t10y_t2yr)-378):nrow(sp500_t10y_t2yr)]~sp500_t10y_t2yr$t10yr_t2yr[(nrow(sp500_t10y_t2yr)-378):nrow(sp500_t10y_t2yr)])
for (i in 1:24){
  print(i)
  sp500_ffund=read.csv('spy.csv')
  #sp500_m1$Returns=sp500_m1$Adjusted/shift(sp500_m1$Adjusted,i)-1
  #sp500_m1$M1_Returns=sp500_m1$M1/shift(sp500_m1$M1,9)-1
  sp500_ffund[,paste("ffund_lag",i,sep="")]=shift(sp500_ffund$fedfunds,i)
  sp500_ffund=na.omit(sp500_ffund) # TODO winsorize instead
  #sp500_m1[,paste("M1Returns_lag",i,sep="")]=Winsorize(sp500_m1[,paste("M1Returns_lag",i,sep="")], 
                                                       # minval = tail(Small(sp500_m1[,paste("M1Returns_lag",i,sep="")],k=1),1), 
                                                       # maxval = head(Large(sp500_m1[,paste("M1Returns_lag",i,sep="")],k=nrow(sp500_m1[sp500_m1[,paste("M1Returns_lag",i,sep="")]>2,])+1),1)
  # )
   print(cor(sp500_ffund[,paste("ffund_lag",i,sep="")],sp500_ffund$spy_returns_12mo))
  #plot(sp500_m1[,paste("M1Returns_lag",i,sep="")],sp500_m1$Returns)
  #abline(h=0,v=0)
  #abline(lm(sp500_m1$Returns~sp500_m1[,paste("M1Returns_lag",i,sep="")]), col='red')
}# large 6 smmall one
model=lm(sp500_ffund$spy_returns_12mo~poly(sp500_ffund[,paste("ffund_lag",i,sep="")],2))
model=lm(sp500_ffund$spy_returns_12mo~sp500_ffund[,paste("ffund_lag",i,sep="")]+I(sp500_ffund[,paste("ffund_lag",i,sep="")]^2))
plot(sp500_ffund[,paste("ffund_lag",i,sep="")],sp500_ffund$spy_returns_12mo)
lines(sp500_ffund$ffund_lag19,model$fitted.values)


for (i in 1:24){
  print(i)
  sp500_m1=read.csv('sp500_m1.csv')
  sp500_m1$Returns=sp500_m1$Adjusted/shift(sp500_m1$Adjusted,i)-1
  sp500_m1$M1_Returns=sp500_m1$M1/shift(sp500_m1$M1,9)-1
  sp500_m1[,paste("M1Returns_lag",i,sep="")]=shift(sp500_m1$M1_Returns,i)
  sp500_m1=na.omit(sp500_m1) # TODO winsorize instead
  sp500_m1[,paste("M1Returns_lag",i,sep="")]=Winsorize(sp500_m1[,paste("M1Returns_lag",i,sep="")], 
                                                       minval = tail(Small(sp500_m1[,paste("M1Returns_lag",i,sep="")],k=1),1), 
                                                       maxval = head(Large(sp500_m1[,paste("M1Returns_lag",i,sep="")],k=nrow(sp500_m1[sp500_m1[,paste("M1Returns_lag",i,sep="")]>2,])+1),1)
                                                       )
  print(cor(sp500_m1[,paste("M1Returns_lag",i,sep="")],sp500_m1$Returns))
  plot(sp500_m1[,paste("M1Returns_lag",i,sep="")],sp500_m1$Returns)
  abline(h=0,v=0)
  abline(lm(sp500_m1$Returns~sp500_m1[,paste("M1Returns_lag",i,sep="")]), col='red')
}# large 6 smmall one

sp500_m1=read.csv('sp500_m1.csv')
sp500_m1$M1_Returns=sp500_m1$M1/shift(sp500_m1$M1,6)-1
sp500_m1$Returns=sp500_m1$Adjusted/shift(sp500_m1$Adjusted,3)-1
sp500_m1[,"M1_Returns"]=Winsorize(sp500_m1[,"M1_Returns"], 
                                                     minval = tail(Small(sp500_m1[,"M1_Returns"],k=1),1), 
                                                     maxval = head(Large(sp500_m1[,"M1_Returns"],k=nrow(sp500_m1[sp500_m1[,"M1_Returns"]>2,])+1),1)
                                                      )
sp500_m1=na.omit(sp500_m1) # TODO winsorize instead
hpf=hpfilter(sp500_m1$M1_Returns, freq = 6)
sp500_m1$M1_Returns_hpf=hpf$trend[,1]
plot(x=sp500_m1$M1_Returns_hpf,y=sp500_m1$Returns)
cor(sp500_m1$M1_Returns_hpf,sp500_m1$Returns)
abline(h=0,v=0)
abline(lm(sp500_m1$Returns~sp500_m1$M1_Returns_hpf), col='red')

sp500_m1=read.csv('sp500_m1.csv')
sp500_m1$Returns=sp500_m1$Adjusted/shift(sp500_m1$Adjusted,6)-1
sp500_m1$M1_Returns=sp500_m1$M1/shift(sp500_m1$M1,12)-1
sp500_m1$Returns_lag6=shift(sp500_m1$Returns,6)



sp500_m1=na.omit(sp500_m1)
sp500_m1=sp500_m1[sp500_m1$M1_Returns<2,]
cor(sp500_m1$Returns,sp500_m1$M1_Returns)
plot(y=sp500_m1$Returns,x=sp500_m1$M1_Returns)
abline(h=0,v=0)


sp500_m1=read.csv('sp500_m1_yearly.csv')
sp500_m1
sp500_m1$Returns=sp500_m1$Adjusted/shift(sp500_m1$Adjusted)-1
sp500_m1$Returns_lag6=shift(sp500_m1$Returns,6)
sp500_m1$M1_Returns=sp500_m1$M1/shift(sp500_m1$M1,12)-1

sp500_m1=na.omit(sp500_m1)
sp500_m1=sp500_m1[sp500_m1$M1_Returns<4,]
cor(sp500_m1$Returns,sp500_m1$M1_Returns)
plot(y=sp500_m1$Returns,x=sp500_m1$M1_Returns)
abline(h=0,v=0)
