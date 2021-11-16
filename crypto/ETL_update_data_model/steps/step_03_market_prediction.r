# setwd("D:/RedXCapital/crypto/Data")
# crypto_mkt <- read.csv("D:/RedXCapital/crypto/Data/Crypto_DJ.csv")

# library(forecast)

# model=auto.arima(crypto_mkt$index, max.d = 1, max.D = 0, max.order = 25)
# summary(model)
# #mean(crypto_mkt$returns, na.rm = TRUE)

# future=forecast(model, h=365)
# plot(future)

# 
# model_ret=auto.arima(crypto_mkt$returns, max.order = 10)
# forecast_model_ret=forecast(model_ret, h=300)
# plot(forecast_model_ret)
# # plot(forecast_model_ret$mean, type='l')
# # 
# # # example of while loop
# # x = 0 
# # while (x <= 10) {
# #   print(x)
# #   x = x+1
# # }
# 
# # example of for loop
# for (i in 1:10) {
#   print(i)
# }
