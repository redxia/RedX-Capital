# Author: Redmond Xia
# Basic Optimization for option profits
# 
#
#

library(quantmod)
library(alphavantager)
library(lubridate)
av_api_key("TCQT2QFAN6SOOT8I")
setDefaults(getSymbols.av, api.key = "TCQT2QFAN6SOOT8I")

# Parameters to change
budget <- 6000 #How much you want to invest
TargetPrc <- 345 # The price you expect the stock to hit
symbols <- "DIA" # The symbol you want
Expiration <- "2021-07-16" # Date you want the option to expire at in format "YYYY-MM-DD"
daysAhead <- "2021-07-09" # How many months you expect to sell the option before expiration from the current date
# . Add that value to today's day to find Option

Stock = getSymbols(Symbols = symbols, from=Sys.Date() - 100, to=Sys.Date() + 1, auto.assign = FALSE)
#Stock <- av_get(symbols, "TIME_SERIES_INTRADAY", interval = "1min", outputsize = "full")
Stock_today <- as.numeric(Stock[(nrow(Stock)),6])
#Stock_today <- Stock[(nrow(Stock)-15),]
#(hour(Stock$timestamp[nrow(Stock)]) == 16)

#plot(Stock$timestamp, Stock$close, type = 'l')

# yahoo finance have option chains info delayed by 15 minutes
Option <- getOptionChain(symbols, Exp = Expiration) 
rownames(Option$calls) <- 1:nrow(Option$calls)
Option$calls <- Option$calls[,-c(2,3)]

# How many months you expect to sell the option before expiration. Add that value to today's day to find Option
ATMExpectedSell <- getOptionChain(symbols, Exp = daysAhead)
ATMExpectedSell$calls$MktPrc <- (ifelse(is.na(ATMExpectedSell$calls$Bid),0,ATMExpectedSell$calls$Bid) + ATMExpectedSell$calls$Ask) / 2

# The at the money premium measurement
ATMPremium <- ATMExpectedSell$calls[which.min(abs(ATMExpectedSell$calls$Strike - 
                                           Stock_today)),'MktPrc']


Option$calls$MktPrc <- (ifelse(is.na(Option$calls$Bid),0,Option$calls$Bid) + Option$calls$Ask) / 2
Option$calls$ExpSellPrc <- pmax(TargetPrc - Option$calls$Strike,0) + ATMPremium

# This is the amount of options you're able to buy.
Option$calls$NumOption <- floor(budget / (Option$calls$MktPrc * 100)) # each contract is worth 100 shares
Option$calls$Revenue <- (Option$calls$ExpSellPrc * 100) * Option$calls$NumOption
Option$calls$IncrProfit <- c(Option$calls$Revenue[1],diff(Option$calls$Revenue))

# Greater than 0.1 due to machine error
Option$calls$BuySell <- c(NA,ifelse(diff(Option$calls$IncrProfit / 
                                           c(Option$calls$IncrProfit[1],diff(Option$calls$Strike))) > 0.1, 1,0))
#Option$calls
View(Option$calls)
Stock_today
