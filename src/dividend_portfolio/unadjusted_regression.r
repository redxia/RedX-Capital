# This script identify the beta, and provides a regression analysis
library(quantmod)
library(data.table)
# parameters
tickers = c('BITO','BITI')
# date = Sys.Date() - 365 #
date = Sys.Date() - (365*.25) #
# date = Sys.Date() - 183 #
# date = Sys.Date() - 88 #

getSymbols(tickers, from=date, to = Sys.Date()+1, verbose = FALSE)
# getSymbols('DBITO3MO', src='FRED', from=date, to = Sys.Date()+1)
#rf = as.numeric(DBITO3MO[nrow(DBITO3MO),]) / 100
rf=0
BITO_rets = na.omit(BITO$BITO.Close / shift(BITO$BITO.Close) - 1)
BITI_rets = na.omit(BITI$BITI.Adjusted / shift(BITI$BITI.Adjusted) - 1)

data = data.frame(BITO_rets$BITO.Close, BITI_rets$BITI.Adjusted)
data = data[order(data$BITI.Adjusted),]

#data$yhat = predict(polyReg, data)
plot(data$BITI.Adjusted-rf, data$BITO.Close-rf, 
     xlab=paste(tickers[2],' Returns'),
     ylab=paste(tickers[1],' Returns'),
     main='CAPM Model')


abline(h=0,v=0, col='grey',lty='dashed')
#lines(data$BITI.Adjusted,data$yhat, col='red')

linTrReg <- lm(I(BITO.Close-rf)~I(BITI.Adjusted-rf), data = data)
#polyReg <- lm(T.Adjusted~BITI.Adjusted + I(BITI.Adjusted^2) + I(BITI.Adjusted^3), data = data)
#polyReg <- lm(T.Adjusted~exp(-BITI.Adjusted * 16), data = data)
abline(linTrReg, col='red')
points(x=mean(BITI_rets$BITI.Adjusted), y=mean(BITO_rets$BITO.Close), col='darkred', pch=22,lwd=4)
stock_cor = cor(BITO_rets$BITO.Close,BITI_rets$BITI.Adjusted)
summary(linTrReg)
#summary(polyReg)
cat(paste(tickers[1],"Correlation:", round(stock_cor,2)), '            ')
cat(paste(tickers[1],"R^2:", round(stock_cor^2,2), '                '))
cat(paste(tickers[1],'Beta Coefficient:'), round(coef(linTrReg)[2],2))
cat(paste(tickers[1],'Alpha:'), round(coef(linTrReg)[1] * length(BITO_rets$BITO.Close) * 100,2)) #annualized

cat(paste(tickers[1],'Mean: '), round(mean(BITO_rets$BITO.Close) * length(BITO_rets$BITO.Close) * 100,2))
cat(paste(tickers[1],'Volatiltiy:'), round(sd(BITO_rets$BITO.Close) * sqrt(length(BITO_rets$BITO.Close)) * 100,2))
cat(paste(tickers[2],'Mean: '), round(mean(BITI_rets$BITI.Adjusted) * length(BITI_rets$BITI.Adjusted) * 100,2))
cat(paste(tickers[2],'Volatiltiy:'), round(sd(BITI_rets$BITI.Adjusted) * sqrt(length(BITI_rets$BITI.Adjusted)) * 100),2)


prob_error = (nrow(data[data$BITO.Close < 0 & data$BITI.Adjusted > 0,]) + 
                nrow(data[data$BITO.Close > 0 & data$BITI.Adjusted < 0,])
) / nrow(data)
cat('Probability of being off BITIgonal (Historical): ', round(prob_error,4))


prob_topleft = (nrow(data[data$BITO.Close > 0 & data$BITI.Adjusted < 0,])) / nrow(data)
cat('Probability of being top left (Historical): ', round(prob_topleft,4))

prob_botright = (nrow(data[data$BITO.Close < 0 & data$BITI.Adjusted > 0,])) / nrow(data)
cat('Probability of being bottom right (Historical): ', round(prob_botright,4))

prob_topright = (nrow(data[data$BITO.Close > 0 & data$BITI.Adjusted > 0,])) / nrow(data)
cat('Probability of being top right (Historical): ', round(prob_topright,4))

prob_botleft = (nrow(data[data$BITO.Close < 0 & data$BITI.Adjusted < 0,])) / nrow(data)
cat('Probability of being bottom left (Historical): ', round(prob_botleft,4))
