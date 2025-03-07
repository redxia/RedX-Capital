# This script identify the beta, and provides a regression analysis
library(quantmod)
library(data.table)
# parameters
# tickers = c('TSPY','XDTE','TSPY')
tickers = c('TSPY','XDTE','TSPY')
# date = Sys.Date() - 365 #
date = Sys.Date() - (365*.5) #
# date = Sys.Date() - 183 #
# date = Sys.Date() - 88 #

getSymbols(tickers, from=date, to = Sys.Date()+1, verbose = FALSE)
# getSymbols('DMO3MO', src='FRED', from=date, to = Sys.Date()+1)
#rf = as.numeric(DMO3MO[nrow(DMO3MO),]) / 100
rf=0
TSPY_rets = na.omit(periodReturn(TSPY$TSPY.Adjusted, period = 'daily'))
XDTE_rets = na.omit(periodReturn(XDTE$XDTE.Adjusted, period = 'daily'))
TSPY_rets = na.omit(periodReturn(TSPY$TSPY.Adjusted, period = 'daily'))

# data = data.frame(TSPY=TSPY_rets,XDTE=XDTE_rets)
data = data.frame(TSPY=TSPY_rets,XDTE=XDTE_rets,TSPY=TSPY_rets)
colnames(data) = c("TSPY",'XDTE')
colnames(data) = c("TSPY",'XDTE','TSPY')
data = data[order(data$XDTE),]
# data$pos_neg = data$XDTE < -.005

#data$yhat = predict(polyReg, data)
plot(data$XDTE-rf, data$TSPY-rf, 
     xlab=paste(tickers[2],' Returns'),
     ylab=paste(tickers[1],' Returns'),
     main='CAPM Model')
abline(h=0,v=0, col='grey',lty='dashed')
#lines(data$XDTE,data$yhat, col='red')

linTrReg <- lm(I(TSPY-rf)~I(XDTE-rf), data = data)
# data$piecewise <- ifelse (data$pos_neg, abs(data$XDTE)^1.5, data$XDTE)
# polyReg <- lm(TSPY ~XDTE * pos_neg, data = data)
polyReg <- lm(TSPY ~XDTE + TSPY, data = data) 
# polyReg <- lm(TSPY ~ I(abs(XDTE)^3/2), data = data) 
# polyReg <- lm(TSPY~I(XDTE^2), data = data)
#polyReg <- lm(T.Adjusted~exp(-XDTE * 16), data = data)
abline(linTrReg, col='red')

# lines(x=data$XDTE, y=predict(polyReg), col='darkred', pch=22,lwd=2)
points(x=mean(data$XDTE), y=mean(data$TSPY), col='darkred', pch=22,lwd=4)
summary(linTrReg)
#summary(polyReg)
stock_cor = cor(data$TSPY,data$XDTE)

cat(paste(tickers[1],"Correlation:", round(stock_cor,2)), '            ')
cat(paste(tickers[1],"R^2:", round(stock_cor^2,2), '                '))
cat(paste(tickers[1],'Beta Coefficient:'), round(coef(linTrReg)[2],2))
cat(paste(tickers[1],'Alpha:'), round(coef(linTrReg)[1] * 252 * 100,2)) #annualized

# cat(paste(tickers[1],'Mean: '), round(mean(TSPY_rets$TSPY) * length(TSPY_rets$TSPY) * 100,2))
# cat(paste(tickers[1],'Volatiltiy:'), round(sd(TSPY_rets$TSPY) * round(sqrt(length(TSPY_rets$TSPY))) * 100,2))
# cat(paste(tickers[2],'Mean: '), round(mean(XDTE_rets$XDTE) * length(XDTE_rets$XDTE) * 100,2))
# cat(paste(tickers[2],'Volatiltiy:'), round(sd(XDTE_rets$XDTE) * round(sqrt(length(XDTE_rets$XDTE))) * 100),2)

cat(paste(tickers[1],'Mean: '), round(mean(data$TSPY) * 252 * 100,2))
cat(paste(tickers[1],'Volatiltiy:'), round(sd(data$TSPY) * sqrt(252) * 100,2))
cat(paste(tickers[2],'Mean: '), round(mean(data$XDTE) * 252 * 100,2))
cat(paste(tickers[2],'Volatiltiy:'), round(sd(data$XDTE) * sqrt(252) * 100),2)


prob_error = (nrow(data[data$TSPY < 0 & data$XDTE > 0,]) + 
              nrow(data[data$TSPY > 0 & data$XDTE < 0,])
              ) / nrow(data)
cat('Probability of being offXDTEgonal (Historical): ', round(prob_error,4))


prob_topleft = (nrow(data[data$TSPY > 0 & data$XDTE < 0,])) / nrow(data)
cat('Probability of being top left (Historical): ', round(prob_topleft,4))

prob_botright = (nrow(data[data$TSPY < 0 & data$XDTE > 0,])) / nrow(data)
cat('Probability of being bottom right (Historical): ', round(prob_botright,4))

prob_topright = (nrow(data[data$TSPY > 0 & data$XDTE > 0,])) / nrow(data)
cat('Probability of being top right (Historical): ', round(prob_topright,4))

prob_botleft = (nrow(data[data$TSPY < 0 & data$XDTE < 0,])) / nrow(data)
cat('Probability of being bottom left (Historical): ', round(prob_botleft,4))

