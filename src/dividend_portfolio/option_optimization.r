# Author: Redmond Xia
# Basic Optimization for option profits
# includes spreads, need to develop the shorts
library(quantmod)
library(lubridate)
setwd("C:/RedXCapital/Dividends")
source("option_strategy.r")

# Parameters to change
type <- "Calls"
budget <- 1000 #How much you want to invest
TargetPrc <- 386.21 # The price you expect the stock to hit
symbols <- "SPY" # The symbol you want
Expiration <- "2022-11-04" # Date you want the option to expire at in format "YYYY-MM-DD"
daysAhead <- "2022-11-07" # How many months you expect to sell the option before expiration from the current date
# . Add that value to today's day to find Option

naked <- nakedOption(symbols, Expiration, daysAhead, type, TargetPrc)
Bull_spread <- spreadOption(symbols, Expiration, daysAhead, type, TargetPrc)
IronCondor <- ironCondorOption(symbols, Expiration, daysAhead, type, TargetPrc)

SPY <- ironCondorOption("SPY", Expiration, daysAhead, type, 370.53)
QQQ <- ironCondorOption("QQQ", Expiration, daysAhead, type, 279.94)
#condor when vix gives a confirmed signal