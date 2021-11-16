library(quantmod)
# Setting directory and declaring btc as base -----------------------------
setwd("D:/RedXCapital/crypto/Data/master_data")
file_names <-list.files()
file_names <- file_names[file_names != "temp"]
tickers <- read.csv("D:/RedXCapital/crypto/crypto_master.csv")
tickers$TICKER <- tolower(tickers$TICKER)
btc_file <- 'btc-usd-max.csv'


# functions ---------------------------------------------------------------
tic_close_mkt_str <- function(file_name) { # gets the ticker and return {ticker}_close and {ticker}_mktcap
  tic <- strsplit(file_name, "-")[[1]][1]
  tic_close = paste(tic,"_close", sep="")
  tic_mktcap = paste(tic,"_mktcp", sep="")
  return(c(tic_close, tic_mktcap))
}

reorganize_df <- function(file_name) { # Reads csv files and organizes the columns
  df <- read.csv(file_name)
  df$Close <- as.numeric(c(df$price[-1],NA))
  df <- df[,c(1,5,3)]
  tic_info <- tic_close_mkt_str(file_name)
  colnames(df) <- c("Date", tic_info[1], tic_info[2])
  df$Date <- as.Date(df$Date)
  return(na.omit(df))
}
# functions ---------------------------------------------------------------

master_df <- reorganize_df(btc_file)
ticker_close <- vector()
ticker_mktcap <- vector()
for (i in file_names) {
  tic_info <- tic_close_mkt_str(i)
  ticker_close <- c(ticker_close, tic_info[1])
  ticker_mktcap <- c(ticker_mktcap, tic_info[2])
}

file_names <- file_names[file_names != btc_file]
for (i in file_names) {
  df <- reorganize_df(i)
  master_df <- merge(x=master_df, y=df, by="Date", all.x=TRUE)
}
master_df$total_mktcp <- rowSums(master_df[,ticker_mktcap], na.rm=TRUE)
ticker_weight <- vector()
for (i in ticker_mktcap) {
  tic <- strsplit(i, "_")[[1]][1]
  tic_weight <- paste(tic, "_wgt", sep="")
  ticker_weight <- c(ticker_weight, tic_weight)
  master_df[tic_weight] <- master_df[,i] / master_df$total_mktcp
}
idx_df <- data.frame(Date=master_df[,"Date"])
idx_df$index <- rowSums(master_df[ticker_weight] * master_df[ticker_close], na.rm=TRUE)
idx_df$returns <- as.numeric(quantmod::Lag(idx_df$index)) / idx_df$index - 1
#plot(idx_df$Date, idx_df$index, type='l', xlab="Date", ylab="Price", main="Crpyto Index")
write.csv(idx_df,"D:/RedXCapital/crypto/Data/Crypto_DJ.csv", row.names = FALSE)
plot(idx_df$Date, idx_df$index, type='l', xlab="Date", ylab="Price", main="Crpyto Index")
plot(idx_df[idx_df$Date >= "2017-01-01",]$Date, idx_df[idx_df$Date >= "2017-01-01",]$index, type='l', xlab="Date", ylab="Price", main="Crpyto Index")
#plot(idx_df$Date, idx_df$returns, type='l', xlab="Date", ylab="Price", main="Crpyto Index")

