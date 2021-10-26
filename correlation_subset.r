getSymbols(c('XLE','XOP','IYE','OIH','VDE'), from='2018-01-01', to =Sys.Date() + 1)

df = data.frame(XLE$XLE.Adjusted,XOP$XOP.Adjusted,IYE$IYE.Adjusted,OIH$OIH.Adjusted,VDE$VDE.Adjusted)
cor(df)
# check the correlation between gold