
# Header import libraries and read data to get ----------------------------
setwd("D:/RedX Capital/crypto/Data")
library(quantmod)
tickers <- read.csv("D:/RedX Capital/crypto/dow.csv")
yh_symbols <- tickers$YH_TICKER

# gets data from yahoo finance --------------------------------------------
master_list <- list()
for (i in yh_symbols) { # gets the data and pauses for 5 seconds. adds to list
  master_list[[i]] <- getSymbols(i, auto.assign = FALSE, from="2008-01-01")
  Sys.sleep(2)
}
# gets data from yahoo finance --------------------------------------------


# function that converts xts to data frame --------------------------------
reorganize_df <- function(xts, new_col_name) { # takes xts object returns its dataframe form
  column=paste(strsplit(new_col_name, "-")[[1]][1],"_Adj", sep="")
  df <- data.frame(as.Date(index(xts)), xts[,6]) # the sixth column is the adjuste price
  rownames(df) <- NULL
  colnames(df) <- c("Date", column)
  return(df)
}
# function that converts xts to data frame --------------------------------


# Left joining all the data together --------------------------------------
master_df <- reorganize_df(master_list[[1]], yh_symbols[1])
for (i in 2:length(yh_symbols)){
  df = reorganize_df(master_list[[i]], yh_symbols[i])
  master_df <- merge(x=master_df, y=df, by="Date", all.x=TRUE)
}
# Left joining all the data together --------------------------------------

master_df <- write.csv("dow_crpyto.csv")

library(Quandl)
BTC_MKTCP = Quandl("BCHAIN/MKTCP")