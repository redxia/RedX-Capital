@REM python update_data.py %1
@REM Rscript hmm_state.r
python main.py %2 %3
python implied_volatility.py
pause