# Author: Redmond Xia
# Basic Optimization for option profits
#
getOptions <- function(symbols, Expiration, daysAhead, type, TargetPrc) {
  Stock = getSymbols(Symbols = symbols, from=Sys.Date() - 100, to=Sys.Date() + 1, auto.assign = FALSE)
  Stock_today <- as.numeric(Stock[(nrow(Stock)),6])
  Option <- getOptionChain(symbols, Exp = Expiration) 
  ATMExpectedSell <- getOptionChain(symbols, Exp = daysAhead)
  
  rownames(Option$calls) <- 1:nrow(Option$calls)
  Option$calls <- Option$calls[,-c(2,3)]
  rownames(Option$puts) <- 1:nrow(Option$puts)
  Option$puts <- Option$puts[,-c(2,3)]
  ATMExpectedSell$calls$Intrinsic <- round(Stock_today,0) - ATMExpectedSell$calls$Strike 
  Option$calls$Intrinsic <- round(TargetPrc,0) - Option$calls$Strike 
  ATMExpectedSell$puts$Intrinsic <- ATMExpectedSell$puts$Strike - round(Stock_today,0)
  Option$puts$Intrinsic <- Option$puts$Strike - round(TargetPrc  ,0)
  if (type=='Calls' | type=='Puts') {
    if (type=="Calls") {
      Option=Option$calls
      ATMExpectedSell=ATMExpectedSell$calls
    } else if (type=="Puts") {
      Option=Option$puts
      ATMExpectedSell=ATMExpectedSell$puts    
    } 
    Option$MktPrc <- (ifelse(is.na(Option$Bid),0,Option$Bid) + Option$Ask) / 2
    ATMExpectedSell$ExpSellPrc <- (ifelse(is.na(ATMExpectedSell$Bid),0,ATMExpectedSell$Bid) + ATMExpectedSell$Ask) / 2    
  } else {
    Option$calls$MktPrc <- (ifelse(is.na(Option$calls$Bid),0,Option$calls$Bid) + Option$calls$Ask) / 2
    Option$puts$MktPrc <- (ifelse(is.na(Option$puts$Bid),0,Option$puts$Bid) + Option$puts$Ask) / 2
    ATMExpectedSell$calls$ExpSellPrc <- (ifelse(is.na(ATMExpectedSell$calls$Bid),0,ATMExpectedSell$calls$Bid) + ATMExpectedSell$calls$Ask) / 2    
    ATMExpectedSell$puts$ExpSellPrc <- (ifelse(is.na(ATMExpectedSell$puts$Bid),0,ATMExpectedSell$puts$Bid) + ATMExpectedSell$puts$Ask) / 2    
  }
  return(list(Option=Option,ATMExpectedSell=ATMExpectedSell))
}

profits <- function(Option,ATMExpectedSell, type) {
  # This is the amount of options you're able to buy.
  Option=merge(Option, ATMExpectedSell[,c('Intrinsic','ExpSellPrc')], all.x=TRUE, by="Intrinsic", sort=FALSE)
  Option$NumOption <- floor(budget / (Option$MktPrc * 100)) # each contract is worth 100 shares
  Option$Revenue <- (Option$ExpSellPrc * 100) * Option$NumOption
  
  # Greater than 0.1 due to machine error
  if (type=="Calls") {
    Option$IncrProfit <- c(Option$Revenue[1],diff(Option$Revenue))
    Option$BuySell <- c(NA,ifelse(diff(Option$IncrProfit / 
                                         c(1,diff(Option$Strike))) > 0.1, 1,0))
  } else if (type=="Puts") {
    Option$IncrProfit <- c(-1*diff(Option$Revenue),0)
    Option$BuySell <- c(NA,ifelse(-1*diff(Option$IncrProfit / c(-1*diff(Option$Strike),1)) > 0.1, 1,0))
  }
  Option <- Option[,-c(12,14)]
  Option=Option[Option$Intrinsic >= -2,]
  Option=Option[Option$Intrinsic<=45, ]
  Option=Option[order(Option$Strike),]
  return(Option)
}

nakedOption <- function(symbols, Expiration, daysAhead, type, TargetPrc) {
  option_chains <- getOptions(symbols, Expiration, daysAhead, type, TargetPrc)
  Option=option_chains$Option
  ATMExpectedSell=option_chains$ATMExpectedSell
  
  Option$MktPrc <- (ifelse(is.na(Option$Bid),0,Option$Bid) + Option$Ask) / 2
  ATMExpectedSell$ExpSellPrc <- (ifelse(is.na(ATMExpectedSell$Bid),0,ATMExpectedSell$Bid) + ATMExpectedSell$Ask) / 2
  Option=profits(Option,ATMExpectedSell, type)
  return(Option[,-c(1,5,6,7,8,9,10,11)])
}

spreadOption <- function(symbols, Expiration, daysAhead, type, TargetPrc) {
  option_chains <- getOptions(symbols, Expiration, daysAhead, type, TargetPrc)
  Option=option_chains$Option
  ATMExpectedSell=option_chains$ATMExpectedSell  
  
  Option$MktPrc <- Option$MktPrc- Option[Option[,"Strike"]==TargetPrc,"MktPrc"]
  ATMExpectedSell$ExpSellPrc <- ATMExpectedSell$ExpSellPrc - ATMExpectedSell[which.min(abs(ATMExpectedSell$Intrinsic)),"ExpSellPrc"]
  # ATMExpectedSell$ExpSellPrc <- ATMExpectedSell$ExpSellPrc - ATMExpectedSell[ATMExpectedSell$Intrinsic==0,"ExpSellPrc"]
  
  Option=profits(Option,ATMExpectedSell, type)
  
  return(Option[,-c(1,5,6,7,8,9,10,11)])
}

Condors <- function(Option, type) {
  option_1=Option
  option_1$Intrinsic <- option_1$Intrinsic + 1
  if (type=="Option") {
    option_1$Option1Prc <- option_1$MktPrc  
  } else {
    option_1$Option1Prc <- option_1$ExpSellPrc
  }
  
  # option_2=option_1 #TODO width about 10
  # option_2$Intrinsic <- option_2$Intrinsic - width
  # if (type=="Option") {
  #   option_2$Option2Prc <- option_2$MktPrc  
  # } else {
  #   option_2$Option2Prc <- option_2$ExpSellPrc
  # }
  # 
  # option_3=option_2
  # option_3$Intrinsic <- option_3$Intrinsic - 1
  # if (type=="Option") {
  #   option_3$Option3Prc <- option_3$MktPrc  
  # } else {
  #   option_3$Option3Prc <- option_3$ExpSellPrc
  # }
  
  Option=merge(Option,option_1[,c('Intrinsic','Option1Prc'),], by="Intrinsic", all.x=TRUE)
  # Option=merge(Option,option_2[,c('Intrinsic','Option2Prc'),], by="Intrinsic", all.x=TRUE)
  # Option=merge(Option,option_3[,c('Intrinsic','Option3Prc'),], by="Intrinsic", all.x=TRUE, sort=TRUE)
  if (type=="Option") {
    Option$MktPrc <- Option$MktPrc - Option$Option1Prc #- Option$Option2Prc+ Option$Option3Prc
  } else {
    Option$ExpSellPrc <- Option$ExpSellPrc - Option$Option1Prc #- Option$Option2Prc+ Option$Option3Prc
  }
  # return(Option[,-match(c("Option1Prc","Option2Prc","Option3Prc"),colnames(Option))])
  return(Option[,-match(c("Option1Prc"),colnames(Option))])
}

condorOption <- function(symbols, Expiration, daysAhead, type, TargetPrc, width) { #TODO this isn't working deprecate
  option_chains <- getOptions(symbols, Expiration, daysAhead, type, TargetPrc)
  Option=option_chains$Option
  ATMExpectedSell=option_chains$ATMExpectedSell
  

  Option=Condors(Option, "Option")
  ATMExpectedSell=Condors(ATMExpectedSell, "ATM")
  Option=profits(Option, type)
  return(Option[,-c(1,5,6,7,8,9,10,11)])
}

ironCondorOption <- function(symbols, Expiration, daysAhead, type, TargetPrc) {
  option_chains <- getOptions(symbols, Expiration, daysAhead, "", TargetPrc)  
  calls=option_chains$Option$calls
  calls=Condors(calls,"Option")
  puts=option_chains$Option$puts
  puts=Condors(puts,"Option")
  iron_condor=merge(calls,puts[,c("Intrinsic",'MktPrc')], by="Intrinsic", all.x=TRUE)
  iron_condor$MktPrc <- iron_condor$MktPrc.x+iron_condor$MktPrc.y
  iron_condor$PutStrike <- 2*iron_condor$Intrinsic+iron_condor$Strike
  iron_condor$BearRet <- iron_condor$Strike/TargetPrc -1
  iron_condor$BullRet <- iron_condor$PutStrike/TargetPrc -1
  iron_condor <- iron_condor[,-c(12,14)]
  iron_condor=iron_condor[iron_condor$Intrinsic >= 0,]
  iron_condor=iron_condor[iron_condor$Intrinsic<=20, ]
  iron_condor=iron_condor[order(iron_condor$Strike),]
  return(iron_condor[,-c(5,6,7,8,9,10,11)])
}
