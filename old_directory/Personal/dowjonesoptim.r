# Mean variance Optimal
source("efficient_frontier.r")

library(quantmod)
# t10yr <- getSymbols(Symbols = "DGS10", src = "FRED", auto.assign = FALSE)
# rf <- mean(t10yr, na.rm = TRUE) / 100
rf <- .0025

# replace the symbols with the ones you want.
symbols <- c("UNH","GS","HD","MSFT","MCD","V","AMGN","CRM","BA","CAT")
getSymbols(symbols, auto.assign = TRUE, from = Sys.Date()-365, to = Sys.Date()) # from pick a date

df <- data.frame(UNH$UNH.Adjusted,GS$GS.Adjusted,HD$HD.Adjusted,MSFT$MSFT.Adjusted,MCD$MCD.Adjusted,
                 V$V.Adjusted,AMGN$AMGN.Adjusted,CRM$CRM.Adjusted,BA$BA.Adjusted,CAT$CAT.Adjusted)

# Expected Returns
mu <- c(.039,.0711,.0473,.045,.037, .0625, .037,.055,.089,.08)
mu

# Mean Variance 
#Return Series
UNH <- (diff(UNH$UNH.Adjusted)) / UNH$UNH.Adjusted[-1]
GS <- (diff(GS$GS.Adjusted)) / GS$GS.Adjusted[-1]
HD <- (diff(HD$HD.Adjusted)) / HD$HD.Adjusted[-1]
MSFT <- (diff(MSFT$MSFT.Adjusted)) / MSFT$MSFT.Adjusted[-1]
MCD <- (diff(MCD$MCD.Adjusted)) / MCD$MCD.Adjusted[-1]
V <- (diff(V$V.Adjusted)) / V$V.Adjusted[-1]
AMGN <- (diff(AMGN$AMGN.Adjusted)) / AMGN$AMGN.Adjusted[-1]
CRM <- (diff(CRM$CRM.Adjusted)) / CRM$CRM.Adjusted[-1]
BA <- (diff(BA$BA.Adjusted)) / BA$BA.Adjusted[-1]
CAT <- (diff(CAT$CAT.Adjusted)) / CAT$CAT.Adjusted[-1]

# Covariance matrix
covPRC <- data.frame(UNH,GS,HD,MSFT,MCD,V,AMGN,CRM,BA,CAT)
covariance <- cov(covPRC)

# Optimization
library(quadprog)
tg.pt <- tangency.portfolio(mu, covariance, 0, shorts = FALSE)
tg.pt$weights # Mean variance optimal

# Plotting the efficient frontier
ef.pt <- efficient.frontier(mu,covariance, nport = 100, alpha.min = 0, alpha.max = 1,shorts = FALSE)
er <- ef.pt$weights %*% mu
sigma2 <- sqrt(diag(ef.pt$weights %*% covariance %*% t(ef.pt$weights)))
efficientFrontier <- cbind(er,sigma2)
colnames(efficientFrontier)[1] <- "Expected Return"
plot(efficientFrontier[,2],efficientFrontier[,1], type = 'l')
maxSharpe <- which.max(efficientFrontier[,1] / efficientFrontier[,2])
maxSharpe
points(efficientFrontier[maxSharpe,2],efficientFrontier[maxSharpe,1], col = 'blue')
ef.pt$weights
