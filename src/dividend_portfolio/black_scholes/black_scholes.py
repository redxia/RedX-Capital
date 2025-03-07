import numpy as np
from scipy.stats import norm

def black_scholes(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    if option_type == 'call' or option_type.strip().upper() == 'C':
        option_price = spot_price * norm.cdf(d1) - strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    elif option_type == 'put' or option_type.strip().upper() == 'P':
        option_price = strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
    return option_price

def theta(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)    
    if option_type == 'call' or option_type.strip().upper() == 'C':
        theta = - (spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry)) - risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    elif option_type == 'put' or option_type.strip().upper() == 'P':
        theta = - (spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry)) + risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)
    return theta / 365

def delta(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    if option_type == 'call' or option_type.strip().upper() == 'C':
        delta = norm.cdf(d1)
    elif option_type == 'put' or option_type.strip().upper() == 'P':
        delta = norm.cdf(d1) - 1
    return delta

def gamma(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    if option_type == 'call' or option_type.strip().upper() == 'C':
        d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    elif option_type == 'put' or option_type.strip().upper() == 'P':
        d1 = (np.log(spot_price / strike_price) + (risk_free_rate - 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
    return gamma

def vega(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    N_prime_d1 = np.exp(-0.5 * d1**2) / np.sqrt(2 * np.pi)
    # N_prime_d1 = norm.pdf(-0.5 * d1**2/ np.sqrt(2 * np.pi)) #np.exp(-0.5 * d1**2) / (2 * np.pi)**0.5
    vega = spot_price * N_prime_d1 * np.sqrt(time_to_expiry)    
    return vega / np.sqrt(365)