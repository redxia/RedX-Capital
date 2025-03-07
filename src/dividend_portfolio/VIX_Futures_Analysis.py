import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

vix=pd.read_excel('VIX.xlsx')
# could put on market hedge when this occurs
vix['QQQ_Deviation']=vix['QQQ Close'] - vix['QQQ Close'].rolling(21).mean()
vix['QQQ_Ret1mo_plus_1']=vix['QQQ_Ret1mo']+1
#vix['Ratio_minus_1']=((vix['Ratio']-1) -(vix['Ratio']-1).mean())
vix['Ratio_minus_1']=vix['Ratio']-1

ax=vix.tail(int(252*1.3)).plot(x='Date', y=['Ratio_minus_1','QQQ_Ret1_5mo'], kind='line', figsize=(24,16))
ax.set_title("Line Plot of Multiple Columns")
ax.set_xlabel("Date")
ax.set_ylabel("Values")
ax.axhline(0, color='gray')
ax.axhline(.17, color='gray')

training_df=vix[['Date','Ratio','QQQ_Ret1_5mo']].tail(int(252*1.3)).dropna()
X = training_df[['Ratio']]
y = training_df['QQQ_Ret1_5mo']

# Split the data into train and test sets
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0, random_state=42)

# Create the KNN regressor
knn = KNeighborsRegressor(n_neighbors=3)

# Fit the model to the training data
#knn.fit(X_train, y_train)
knn.fit(X, y)

# Make predictions on the test set
y_pred = knn.predict(X)
knn.predict(np.array([1.173]).reshape(-1,1))
print(knn.predict(np.array([vix['Ratio'].iloc[-1]]).reshape(-1,1)))

vix['Knn Pred']=knn.predict(vix[['Ratio']])
# Calculate the mean squared error
mse = mean_squared_error(y, y_pred)
print("Mean Squared Error:", mse)

ax=vix.tail(int(252*1.3)).plot(x='Ratio_minus_1', y='QQQ_Ret1_5mo', kind='scatter', figsize=(24,16))
ax.set_xlabel("Ratio_minus_1")
ax.set_ylabel("QQQ_Ret1_5mo")
ax.axhline(0, color='gray')
#ax.axhline(.17, color='gray')
ax.axvline(.173, color='gray')


ax=vix.tail(int(252*1.3)).plot(x='Ratio', y='Knn Pred', kind='scatter', figsize=(24,16))
ax.axhline(0, color='gray')
#ax.axhline(.17, color='gray')
ax.axvline(1.173, color='gray')

vix[['Date','Ratio','QQQ_Ret1_5mo','Knn Pred']].tail(42)