# Mean variance Optimal
library(quantmod)
t10yr <- getSymbols(Symbols = "DGS10", src = "FRED", auto.assign = FALSE)
t10yr <- t10yr[index(t10yr) >= "2013-05-02" & index(t10yr) <= "2020-05-07",]
rf <- mean(t10yr, na.rm = TRUE ) / 100

symbols <- c("EFC","NRZ","MFA","RWT")
getSymbols(symbols, auto.assign = TRUE, from = "2017-05-02", to = "2020-04-10")
rates <- rep(mean(t10yr, na.rm = TRUE),length(symbols)) / 100

data <- data.frame(EFC$EFC.Adjusted,NRZ$NRZ.Adjusted,MFA$MFA.Adjusted,)

minStock <- apply(data,2,min)
maxStock <- apply(data,2,max)
minStock[4] <- 1 + minStock[4]
minStock[3] <- minStock[3] + 1
#returns <- apply(data,2,function(x){diff(log(x))})

# Mean Variance Optimal
#mu <- apply(returns,2,mean)
mu <- maxStock / minStock - 1
covariance <- cov(data)
numerator <- solve(covariance,mu - rates)
denominator <- sum(solve(covariance,mu - rates))
weights <- numerator / denominator

portVal <- 14000
dividends <- c(.45,.5,.45,.2)
rankings <- (portVal/minStock) * dividends
weightsDvd <- rankings / sum(rankings)
weightsDvd * portVal


weights * portVal