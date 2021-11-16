# This script identify the beta, and provides a regression analysis
library(quantmod)
library(data.table)
# parameters
tickers = c('REML','SPY')
date = Sys.Date() - 365 #"2020-06-09"#

getSymbols(tickers, from=date, to = Sys.Date()+1, verbose = FALSE)
getSymbols('DGS3MO', src='FRED', from=date, to = Sys.Date()+1)
rf = as.numeric(DGS3MO[nrow(DGS3MO),]) / 100

REML_rets = na.omit(REML$REML.Adjusted / shift(REML$REML.Adjusted) - 1)
SPY_rets = na.omit(SPY$SPY.Adjusted / shift(SPY$SPY.Adjusted) - 1)

data = data.frame(REML_rets$REML.Adjusted, SPY_rets$SPY.Adjusted)
data = data[order(data$SPY.Adjusted),]

#data$yhat = predict(polyReg, data)
plot(data$SPY.Adjusted-rf, data$REML.Adjusted-rf, 
     xlab=paste(tickers[2],' Returns'),
     ylab=paste(tickers[1],' Returns'),
     main='CAPM Model')


abline(h=0,v=0, col='grey',lty='dashed')
#lines(data$SPY.Adjusted,data$yhat, col='red')

linTrReg <- lm(I(REML.Adjusted-rf)~I(SPY.Adjusted-rf), data = data)
#polyReg <- lm(T.Adjusted~SPY.Adjusted + I(SPY.Adjusted^2) + I(SPY.Adjusted^3), data = data)
#polyReg <- lm(T.Adjusted~exp(-SPY.Adjusted * 16), data = data)
abline(linTrReg, col='red')
points(x=mean(SPY_rets$SPY.Adjusted), y=mean(REML_rets$REML.Adjusted), col='darkred', pch=22,lwd=4)
stock_cor = cor(REML_rets$REML.Adjusted,SPY_rets$SPY.Adjusted)
summary(linTrReg)
#summary(polyReg)
cat(paste(tickers[1],"Correlation:", round(stock_cor,2)), '            ')
cat(paste(tickers[1],"R^2:", round(stock_cor^2,2), '                '))
cat(paste(tickers[1],'Beta Coefficient:'), round(coef(linTrReg)[2],2))
cat(paste(tickers[1],'Alpha:'), round(coef(linTrReg)[1] * length(REML_rets$REML.Adjusted) * 100,2)) #annualized

cat(paste(tickers[1],'Mean: '), round(mean(REML_rets$REML.Adjusted) * length(REML_rets$REML.Adjusted) * 100,2))
cat(paste(tickers[1],'Volatiltiy:'), round(sd(REML_rets$REML.Adjusted) * sqrt(length(REML_rets$REML.Adjusted)) * 100,2))
cat(paste(tickers[2],'Mean: '), round(mean(SPY_rets$SPY.Adjusted) * length(SPY_rets$SPY.Adjusted) * 100,2))
cat(paste(tickers[2],'Volatiltiy:'), round(sd(SPY_rets$SPY.Adjusted) * sqrt(length(SPY_rets$SPY.Adjusted)) * 100),2)


prob_error = (nrow(data[data$REML.Adjusted < 0 & data$SPY.Adjusted > 0,]) + 
              nrow(data[data$REML.Adjusted > 0 & data$SPY.Adjusted < 0,])
              ) / nrow(data)
cat('Probability of being off Diagonal (Historical): ', round(prob_error,4))


prob_topleft = (nrow(data[data$REML.Adjusted > 0 & data$SPY.Adjusted < 0,])) / nrow(data)
cat('Probability of being top left (Historical): ', round(prob_topleft,4))

prob_botright = (nrow(data[data$REML.Adjusted < 0 & data$SPY.Adjusted > 0,])) / nrow(data)
cat('Probability of being bottom right (Historical): ', round(prob_botright,4))

prob_topright = (nrow(data[data$REML.Adjusted > 0 & data$SPY.Adjusted > 0,])) / nrow(data)
cat('Probability of being top right (Historical): ', round(prob_topright,4))

prob_botleft = (nrow(data[data$REML.Adjusted < 0 & data$SPY.Adjusted < 0,])) / nrow(data)
cat('Probability of being bottom left (Historical): ', round(prob_botleft,4))