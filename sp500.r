sp500 <- read.csv("sp500_3_26.csv")
library(forecast)
library(bizdays)

foo <- ts(sp500$Adj.Close, start = 1,frequency = 365)
fooH <- ts(sp500$High, start = 1,frequency = 365)
fooL <- ts(sp500$Low, start = 1,frequency = 365)
#ar_fit <- arima(foo, order = c(8,0,4))

ar_fit <- arima(foo, order = c(50,0,20))
ar_fitH <- arima(fooH, order = c(50,0,20))
ar_fitL <- arima(fooL, order = c(50,0,20))

predH <- predict(ar_fitH, n.ahead = 60)
predL <- predict(ar_fitL, n.ahead = 60)
xH <- c(sp500$High,predH$pred[1:60])
xL <- c(sp500$Low,predL$pred[1:60])
pred <- predict(ar_fit, n.ahead = 60)
x <- c(sp500$Adj.Close,pred$pred[1:60])
num_price <- nrow(sp500)
num_ts <- length(x)
plot(1:num_ts, x, type = 'l', xlab = "Time", ylab = "sp500")
abline(v = num_price + 1, col = 'red')
lines((num_price+1):num_ts,x[(num_price+1):num_ts], col = 'blue')
lines((num_price+1):num_ts,xH[(num_price+1):num_ts], col = 'darkorange') # high line
lines((num_price+1):num_ts,xL[(num_price+1):num_ts], col = 'darkgreen') # low line
avgPred = (predH$pred[1:60]+predL$pred[1:60]+pred$pred[1:60]) / 3
lines((num_price+1):num_ts,avgPred, col = 'red', lwd = 2)
legend("bottomleft", legend = c("Adj.Close","High","Low","Avg"),col = c("blue","darkorange","darkgreen",'red'), lty = 1)
seUpper = pred$pred + 2*pred$se
seLower = pred$pred - 2*pred$se
lines((num_price+1):num_ts,seUpper,col = "green")
lines((num_price+1):num_ts, seLower, col = "green")

create.calendar("USA/ANBIMA", holidaysANBIMA, weekdays = c("saturday","sunday"))
df <- data.frame(as.Date(bizseq("2020-03-27","2020-06-24","USA/ANBIMA"))) # Update this because it dpends on time and add both one day
#length(bizseq("2020-03-23","2020-05-27","USA/ANBIMA"))
colnames(df) <- "Date"
df$Adj.Close <- pred$pred
df$High <- predH$pred
df$Low <- predL$pred
df$Avg <- avgPred
df$seUpper <- seUpper
df$seLower <- seLower


csv <- write.csv(df,"sp500_ARMA4525_Prediction_3_23_2020.csv")
