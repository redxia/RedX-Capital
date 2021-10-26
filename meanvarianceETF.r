# Mean variance Optimal
source("efficient_frontier.r")

library(quantmod)
t10yr <- getSymbols(Symbols = "DGS10", src = "FRED", auto.assign = FALSE)
t10yr <- t10yr[index(t10yr) >= "2013-05-02" & index(t10yr) <= "2020-04-17",]
rf <- mean(t10yr, na.rm = TRUE) / 100
#rates <- rep(mean(t10yr, na.rm = TRUE),length(symbols)) / 100

symbols <- c("FAS","TECL","GUSH","SOXL","JNUG")

getSymbols(symbols, auto.assign = TRUE, from = "2015-06-01", to = "2020-04-18")


df <- data.frame(FAS$FAS.Adjusted,TECL$TECL.Adjusted,GUSH$GUSH.Adjusted,SOXL$SOXL.Adjusted,JNUG$JNUG.Adjusted)
date2020 <- "2020-01-01"
df_2020 <- df[row.names(df) >= date2020,]

# maxStock <- apply(df_2020,2,max)
# MktCap <- c(997.64,1060,199.56,1070,587.78)
# valueWeight <- MktCap / sum(MktCap)
# maxStock[3] <- 250 # adjust the maximum of GUSH because it is too high
# maxStock[2] <- 250 # adjust TECL because of low volume
# maxStock[5] <- maxStock[5] - 35 # adjust the JNUG price because is is relatively small
# maxStock[1] <- maxStock[1] - 10
# valueMax <- maxStock / sum(maxStock)

# maxStock[2] <- 750 # Adjust TECL max value higher because its price is large
# maxStock[3] <- 1000 # Adjust Gush max value
# maxStock[4] <- 750  # Adjust SOXL because it has a higher price value
# maxStock[5] <- 30 # penalize JNUG because its highest price is small
# maxStock[6] <- 5 # Peanlizes UCO because its max price is the lowest
# minStock <- apply(df_2020,2,min)
currentDate <- "2020-04-17"
df_NOW <- df[row.names(df) >= currentDate,]


# Mean Variance 
#mu <- as.numeric(maxStock / df_NOW - 1)
#mu <- as.numeric(maxStock / df_NOW - 1) * valueWeight * valueMax
#mu <- as.numeric(maxStock / df_NOW - 1) * valueMax
mu
#mu <- as.numeric(maxStock / minStock - 1)
FAS <- (diff(FAS$FAS.Adjusted)) / FAS$FAS.Adjusted[-1]
TECL <- (diff(TECL$TECL.Adjusted)) / TECL$TECL.Adjusted[-1]
GUSH <- (diff(GUSH$GUSH.Adjusted)) / GUSH$GUSH.Adjusted[-1]
SOXL <- (diff(SOXL$SOXL.Adjusted)) / SOXL$SOXL.Adjusted[-1]
JNUG <- (diff(JNUG$JNUG.Adjusted)) / JNUG$JNUG.Adjusted[-1]
FASmu <- mean(FAS$FAS.Adjusted)
TECLmu <- mean(TECL$TECL.Adjusted)
GUSHmu <- mean(GUSH$GUSH.Adjusted)
SOXLmu <- mean(SOXL$SOXL.Adjusted)
JNUGmu <- mean(JNUG$JNUG.Adjusted)
mu <- c(FASmu,TECLmu,GUSHmu,SOXLmu, JNUGmu)

covPRC <- data.frame(FAS,TECL,GUSH,SOXL,JNUG)
covariance <- cov(covPRC)

library(quadprog)
tg.pt <- tangency.portfolio(mu, covariance, 0, shorts = FALSE)
tg.pt$weights

ef.pt <- efficient.frontier(mu,covariance, nport = 100, alpha.min = 0, alpha.max = 1,shorts = FALSE)
er <- ef.pt$weights %*% mu
sigma2 <- sqrt(diag(ef.pt$weights %*% covariance %*% t(ef.pt$weights)))
efficientFrontier <- cbind(er,sigma2)
colnames(efficientFrontier)[1] <- "Expected Return"
plot(efficientFrontier[,2],efficientFrontier[,1], type = 'l')
#maxSharpe <- which.max(diff(efficientFrontier[,1] / efficientFrontier[,2]))
#maxSharpe
#points(efficientFrontier[maxSharpe,2],efficientFrontier[maxSharpe,1], col = 'blue')
dropSharpe <- which.min(diff(efficientFrontier[,1] / efficientFrontier[,2]))
#dropSharpe
points(efficientFrontier[dropSharpe,2],efficientFrontier[dropSharpe,1], col = 'red')
#efficientFrontier[30:90,]
ef.pt$weights
