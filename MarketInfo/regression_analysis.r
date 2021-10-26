# This script identify the beta, and provides a regression analysis
library(quantmod)
library(data.table)
# parameters
tickers = c('ARKK','QQQ')
date = Sys.Date() - 365 #"2020-06-09"#

getSymbols(tickers, from=date, to = Sys.Date()+1, verbose = FALSE)
getSymbols('DGS3MO', src='FRED', from=date, to = Sys.Date()+1)
rf = as.numeric(DGS3MO[nrow(DGS3MO),]) / 100

ARKK_rets = na.omit(ARKK$ARKK.Adjusted / shift(ARKK$ARKK.Adjusted) - 1)
QQQ_rets = na.omit(QQQ$QQQ.Adjusted / shift(QQQ$QQQ.Adjusted) - 1)

data = data.frame(ARKK_rets$ARKK.Adjusted, QQQ_rets$QQQ.Adjusted)
data = data[order(data$QQQ.Adjusted),]

#data$yhat = predict(polyReg, data)
plot(data$QQQ.Adjusted-rf, data$ARKK.Adjusted-rf, 
     xlab=paste(tickers[2],' Returns'),
     ylab=paste(tickers[1],' Returns'),
     main='CAPM Model')


abline(h=0,v=0, col='grey',lty='dashed')
#lines(data$QQQ.Adjusted,data$yhat, col='red')

linTrReg <- lm(I(ARKK.Adjusted-rf)~I(QQQ.Adjusted-rf), data = data)
#polyReg <- lm(T.Adjusted~QQQ.Adjusted + I(QQQ.Adjusted^2) + I(QQQ.Adjusted^3), data = data)
#polyReg <- lm(T.Adjusted~exp(-QQQ.Adjusted * 16), data = data)
abline(linTrReg, col='red')
points(x=mean(QQQ_rets$QQQ.Adjusted), y=mean(ARKK_rets$ARKK.Adjusted), col='darkred', pch=22,lwd=4)
stock_cor = cor(ARKK_rets$ARKK.Adjusted,QQQ_rets$QQQ.Adjusted)
summary(linTrReg)
#summary(polyReg)
cat(paste(tickers[1],"Correlation:", round(stock_cor,2)), '            ')
cat(paste(tickers[1],"R^2:", round(stock_cor^2,2), '                '))
cat(paste(tickers[1],'Beta Coefficient:'), round(coef(linTrReg)[2],2))
cat(paste(tickers[1],'Alpha:'), round(coef(linTrReg)[1] * length(ARKK_rets$ARKK.Adjusted) * 100,2)) #annualized

cat(paste(tickers[1],'Mean: '), round(mean(ARKK_rets$ARKK.Adjusted) * length(ARKK_rets$ARKK.Adjusted) * 100,2))
cat(paste(tickers[1],'Volatiltiy:'), round(sd(ARKK_rets$ARKK.Adjusted) * sqrt(length(ARKK_rets$ARKK.Adjusted)) * 100,2))
cat(paste(tickers[2],'Mean: '), round(mean(QQQ_rets$QQQ.Adjusted) * length(QQQ_rets$QQQ.Adjusted) * 100,2))
cat(paste(tickers[2],'Volatiltiy:'), round(sd(QQQ_rets$QQQ.Adjusted) * sqrt(length(QQQ_rets$QQQ.Adjusted)) * 100),2)


prob_error = (nrow(data[data$ARKK.Adjusted < 0 & data$QQQ.Adjusted > 0,]) + 
              nrow(data[data$ARKK.Adjusted > 0 & data$QQQ.Adjusted < 0,])
              ) / nrow(data)
cat('Probability of being off Diagonal (Historical): ', round(prob_error,4))


prob_topleft = (nrow(data[data$ARKK.Adjusted > 0 & data$QQQ.Adjusted < 0,])) / nrow(data)
cat('Probability of being top left (Historical): ', round(prob_topleft,4))

prob_botright = (nrow(data[data$ARKK.Adjusted < 0 & data$QQQ.Adjusted > 0,])) / nrow(data)
cat('Probability of being bottom right (Historical): ', round(prob_botright,4))

prob_topright = (nrow(data[data$ARKK.Adjusted > 0 & data$QQQ.Adjusted > 0,])) / nrow(data)
cat('Probability of being top right (Historical): ', round(prob_topright,4))

prob_botleft = (nrow(data[data$ARKK.Adjusted < 0 & data$QQQ.Adjusted < 0,])) / nrow(data)
cat('Probability of being bottom left (Historical): ', round(prob_botleft,4))