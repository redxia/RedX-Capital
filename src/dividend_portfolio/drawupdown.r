library(quantmod)
library(tseries)
getSymbols("^GSPC", verbose = FALSE, from =as.Date("1900-01-1"),to=Sys.Date()+1, return.clasee='ts')
GSPC$Returns= GSPC$GSPC.Close / stats::lag(GSPC$GSPC.Close) - 1
n_row=nrow(GSPC)
library(caTools)

# do this for two years the culmulative return.
# GSPC$Maxdrawdown <- runmin(GSPC$Returns, 252*12)
# GSPC$Maxdrawup <- runmax(GSPC$Returns, 252*12)

# plot(GSPC$Date,GSPC$Maxdrawdown, type='l' , main='Maximum Drawdown')
# polygon(c(as.numeric(GSPC$Date),max(GSPC$Date),0),c(GSPC$Maxdrawdown,0,0), col='slateblue1')
# plot(GSPC$Maxdrawup, type='l')
# polygon(c(index(GSPC),max(index(GSPC)),0),c(abs(GSPC$Maxdrawdown),0,0), col='slateblue1')
GSPC$Returns_2yr= GSPC$GSPC.Close / stats::lag(GSPC$GSPC.Close,21*12*2) - 1
GSPC$Cummax_2yr=runmax(GSPC$GSPC.Close,252*2)
GSPC$Maxdrawdown_2yr = GSPC$GSPC.Close / GSPC$Cummax_2yr - 1
GSPC=na.omit(GSPC)
GSPC=as.data.frame(GSPC)
GSPC$Date= as.Date(rownames(GSPC), origin=rownames(GSPC)[1])
plot(GSPC$Date,GSPC$Maxdrawdown_2yr, type='l' , main='Maximum Drawdown', col='blue')
polygon(c(as.numeric(GSPC$Date),max(GSPC$Date),0),c(GSPC$Maxdrawdown_2yr,0,-as.numeric(GSPC$Date[1])), col='skyblue')
abline(h=seq(-.8,0,.05), lty=2)
 #TODO create maximum draw up and and loop this for all etfs. # TODO highlight the hmm lines
