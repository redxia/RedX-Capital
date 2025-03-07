# Author: Redmond Xia
# Basic Optimization for option profits
# 15 minutes delays

library(quantmod)
library(lubridate)

# Parameters to change
budget <- 3000 #How much you want to invest
TargetPrc <- 375 # The price you expect the stock to hit
symbols <- "SPY" # The symbol you want
Expiration <- "2022-10-12" # Date you want the option to expire at in format "YYYY-MM-DD"
daysAhead <- "2022-09-30" # How many months you expect to sell the option before expiration from today's date
# . Add that value to today's day to find Option

Stock = getSymbols(Symbols = symbols, from=Sys.Date() - 100, to=Sys.Date() + 1, auto.assign = FALSE)
Stock_today <- as.numeric(Stock[(nrow(Stock)),6])

# yahoo finance have option chains info delayed by 15 minutes
Option <- getOptionChain(symbols, Exp = Expiration) 
rownames(Option$puts) <- 1:nrow(Option$puts)
Option$puts <- Option$puts[,-c(2,3)]

# How many months you expect to sell the option before expiration. Add that value to today's day to find Option
ATMExpectedSell <- getOptionChain(symbols, Exp = daysAhead)
ATMExpectedSell$puts$MktPrc <- (ifelse(is.na(ATMExpectedSell$puts$Bid),0,ATMExpectedSell$puts$Bid) + ATMExpectedSell$puts$Ask) / 2

# The at the money premium measurement
ATMPremium <- ATMExpectedSell$puts[which.min(abs(ATMExpectedSell$puts$Strike - 
                                           Stock_today)),'MktPrc']- ATMExpectedSell$puts[ATMExpectedSell$puts$Strike==TargetPrc,"MktPrc"]
#ATMPremium <- ATMExpectedSell$puts[which.min(abs(ATMExpectedSell$puts$Strike - 
#Stock_today)),'MktPrc']


Option$puts$MktPrc <- (ifelse(is.na(Option$puts$Bid),0,Option$puts$Bid) + Option$puts$Ask) / 2
Option$puts$MktPrc <- Option$puts$MktPrc- Option$puts[Option$puts[,"Strike"]==TargetPrc,"MktPrc"]
Option$puts$ExpSellPrc <- Option$puts$MktPrc + ATMPremium 
#Option$puts$ExpSellPrc <- pmax(Option$puts$Strike-TargetPrc,0)
#Option$puts$ExpSellPrc <- Option$puts$ExpSellPrc - Option$puts[Option$puts[,"Strike"]==TargetPrc,"ExpSellPrc"] + ATMPremium

# This is the amount of options you're able to buy.
Option$puts$NumOption <- floor(budget / (Option$puts$MktPrc * 100)) # each contract is worth 100 shares
Option$puts$Revenue <- (Option$puts$ExpSellPrc * 100) * Option$puts$NumOption
Option$puts$IncrProfit <- c(-1*diff(Option$puts$Revenue),0)

# Greater than 0.1 due to machine error #TODO fix this
Option$puts$BuySell <- c(NA,ifelse(-1*diff(Option$puts$IncrProfit / c(-1*diff(Option$puts$Strike),1)) > 0.1, 1,0))
Option$puts <-Option$puts[,-c(11,13)]
Option$puts <- Option$puts[Option$puts[,'Strike']>=(TargetPrc-2),]
Option$puts <- Option$puts[Option$puts[,'Strike']<=(Stock_today+2),]
View(Option$puts)
Stock_today
