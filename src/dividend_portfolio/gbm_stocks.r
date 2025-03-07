S0=375
days=30
intraday=0
alpha_mean=.00003
alpha_median=.0009
std_direction=.009
# alpha=(alpha_mean+alpha_median)/2+std_direction/2
alpha=(alpha_mean+alpha_median)/2
# alpha=alpha_mean
std_overall=.0137
sigma_iv=.28 /sqrt(252)
lower_bound=348
upper_bound=390


sigma_historical=(std_direction+std_overall)/2
T=(13*days+intraday)/13
sigma=max(sigma_historical, sigma_iv)
# sigma=(sigma_historical+ sigma_iv)/2
# sigma=std_overall
# sigma=sigma_historical
N=1000
time_step=1000

gbm <- function(S0, alpha, sigma, T) { #TODO run historical methods with probabbility and run your own probability histogram
  # alpha=alpha/time_step
  sigma=sigma/sqrt(time_step)
  dt=T/time_step
  dw=rnorm(1)*sqrt(dt)
  st=numeric(time_step)
  st[1]=S0
  for (i in 2:time_step){
    st[i]=st[i-1]+alpha*st[i-1]*dt+sigma*st[i-1]*dw
  }
  return(st)
} # neeed to apply variance reduction methods

stock_paths=matrix(0,N,N)

upper_prob=numeric(50)
lower_prob=numeric(50)
for (k in 1:50) {
  for (i in 1:N){
    stock_paths[,i]=gbm(S0,alpha, sigma,T)
  }
  upper_prob[k]=sum(stock_paths[N,]>upper_bound)/N
  lower_prob[k]=sum(stock_paths[N,]<lower_bound)/N  
}
cat("Lower bound Return:", round(lower_bound/S0-1,4))
cat("Upper bound Return :", round(upper_bound/S0-1,4))
cat("Probability Upper bound :", round(mean(upper_prob),4))
cat("Probability Lower bound :", round(mean(lower_prob),4))
cat("Probability Middle bound :", round(1-mean(upper_prob)-mean(lower_prob),2))
#TODO sigma is max of the two iv. use date. get probaility charting from bull bear spread