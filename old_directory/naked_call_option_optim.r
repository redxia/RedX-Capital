# Author: Redmond Xia
# Basic Optimization for option profits
#
library(quantmod)
library(lubridate)

# Parameters to change
budget <- 1000 #How much you want to invest
TargetPrc <- 405 # The price you expect the stock to hit
symbols <- "SPY" # The symbol you want
Expiration <- "2022-10-12" # Date you want the option to expire at in format "YYYY-MM-DD"
daysAhead <- "2022-09-30" # How many months you expect to sell the option before expiration from the current date
# . Add that value to today's day to find Option

Stock = getSymbols(Symbols = symbols, from=Sys.Date() - 100, to=Sys.Date() + 1, auto.assign = FALSE)
Stock_today <- as.numeric(Stock[(nrow(Stock)),6])

# yahoo finance have option chains info delayed by 15 minutes
Option <- getOptionChain(symbols, Exp = Expiration) 
rownames(Option$calls) <- 1:nrow(Option$calls)
Option$calls <- Option$calls[,-c(2,3)]

# How many months you expect to sell the option before expiration. Add that value to today's day to find Option
ATMExpectedSell <- getOptionChain(symbols, Exp = daysAhead)
ATMExpectedSell$calls$ExpSellPrc <- (ifelse(is.na(ATMExpectedSell$calls$Bid),0,ATMExpectedSell$calls$Bid) + ATMExpectedSell$calls$Ask) / 2

ATMExpectedSell$calls$Intrinsic <- round(Stock_today,0) - ATMExpectedSell$calls$Strike 

# The at the money premium measurement

Option$calls$MktPrc <- (ifelse(is.na(Option$calls$Bid),0,Option$calls$Bid) + Option$calls$Ask) / 2
# this is bull spread
Option$calls$Intrinsic <- TargetPrc - Option$calls$Strike #- Option$calls$MktPrc
Option$calls=merge(Option$calls, ATMExpectedSell$calls[,c('Intrinsic','ExpSellPrc')], all.x=TRUE, by="Intrinsic", sort=FALSE)


# This is the amount of options you're able to buy.
Option$calls$NumOption <- floor(budget / (Option$calls$MktPrc * 100)) # each contract is worth 100 shares
Option$calls$Revenue <- (Option$calls$ExpSellPrc * 100) * Option$calls$NumOption
Option$calls$IncrProfit <- c(Option$calls$Revenue[1],diff(Option$calls$Revenue))

# Greater than 0.1 due to machine error
Option$calls$BuySell <- c(NA,ifelse(diff(Option$calls$IncrProfit / 
                                           c(1,diff(Option$calls$Strike))) > 0, 1,0))
#Option$calls
Option$calls <- Option$calls[,-c(1,12,14)]
Option$calls <- Option$calls[Option$calls[,'Strike']>=(Stock_today-2),]
Option$calls <- Option$calls[Option$calls[,'Strike']<=(TargetPrc),]
View(Option$calls)
Stock_today
