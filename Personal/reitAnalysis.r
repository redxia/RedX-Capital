library(data.table)
df <- fread("REIT_Data.csv")

# Cap is in thousands
df$prc <- abs(df$prc)
df$divYield <- df$odiv / df$prc
df <- df[,-c(9,10)]
#ticker <- unique(df$ticker)
#output <- write.table(ticker, "REIT_TIC.txt", sep = "\t", row.names = FALSE)

df <- df[!df$divYield == 0,]
df <- df[,-c(8)]
df$year <- floor(df$caldt / 10000)
df$month <- floor(df$caldt %% 10000 / 100)
df$day <- df$caldt %% 100
df$date <- paste(df$year,"/",df$month,"/",df$day, sep = "")
df$date <- as.Date(df$date)
df <- df[,-c(1,4,9,10,11)]
# Dates after 2015
df_2015 <- df[df$date >= "2015-01-01"]

x <- table(df_Size$ticker)
y <- as.data.frame(x)