set /p ticker="Ticker: "
set /p expiration="Expiration (YYMMDD): "
set /p option_type="Option Type (C/P): "
set /p strike_1="Strike 1: "
set /p strike_2="Strike 2: "
set /p sigma_1="Sigma 1: "
set /p sigma_2="Sigma 2: "
set /p offset="Offset amount: "
python get_spread_price.py %ticker% %expiration% %option_type% %strike_1% %strike_2% %sigma_1% %sigma_2% %offset%
pause