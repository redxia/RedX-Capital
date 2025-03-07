from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from keras import backend as K
import os
import pandas_market_calendars as mcal
from datetime import datetime
from datetime import timedelta
import math
import pandas_ta as pta
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"

nyse=mcal.get_calendar("NYSE")
def market_model():
    market_etf=os.listdir(market_path)
    scaler=MinMaxScaler(feature_range=(0,1))

    def create_dataset(dataset, look_back = 1):
        dataX, dataY = [], []
        if(len(dataset) ==(look_back+forward_days)): # this is for test set to find mse
            dataX.append(dataset[0])
            dataY.append(dataset[forward_days,0])
            return np.array(dataX), np.array(dataY)
        for i in range(len(dataset) - forward_days):
            a = dataset[i:(i + look_back), 0]
            dataX.append(a)
            dataY.append(dataset[i + forward_days, 0])
        return np.array(dataX), np.array(dataY)

    def predict(num_prediction, model, penalty):
        prediction_list = data[-look_back:]
        for i in range(num_prediction):
            x = prediction_list[-look_back:]
            x = x.reshape((1, look_back, 1))
            # out = scaler.transform(scaler.inverse_transform(model.predict(x)) / penalty)[0][0]  #TODO the problem with this method it's very sensitive
            out = model.predict(x) [0][0]  #TODO the problem with this method it's very sensitive
            prediction_list = np.append(prediction_list, out)
        prediction_list = scaler.inverse_transform(prediction_list[look_back:].reshape(-1,1)) / penalty 
        return prediction_list.reshape(-1)

    num_hidden=8
    num_epochs=32
    look_back=1
    forward_days=1
    num_prediction=11
    tomorrow=datetime.now()+timedelta(days=1)
    two_weeks=nyse.schedule(tomorrow.strftime(r"%Y%m%d"), (tomorrow+timedelta(days=math.ceil(30*11/20))).strftime(r"%Y%m%d")).iloc[:11]
    #TODO Force this to be the first 11 days
    
    columns_array=np.append('Predicted',two_weeks.index.strftime('%Y-%m-%d').values)
    columns_array=np.append('Symbol',columns_array)
    columns_array=np.append(columns_array, 'RSI_7')
    columns_array=np.append(columns_array, 'RSI_21')
    columns_array=np.append(columns_array, 'Maxdrawdown')
    columns_array=np.append(columns_array, 'Maxdrawup')
    columns_array=np.append(columns_array, 'Ret_1')
    columns_array=np.append(columns_array, 'Ret_2')
    columns_array=np.append(columns_array, 'Ret_3')
    columns_array=np.append(columns_array, 'Ret_4')
    columns_array=np.append(columns_array, 'Ret_5')
    columns_array=np.append(columns_array, 'Ret_6')
    columns_array=np.append(columns_array, 'Ret_7')
    columns_array=np.append(columns_array, 'Ret_8')
    columns_array=np.append(columns_array, 'Ret_9')
    columns_array=np.append(columns_array, 'Ret_10')
    columns_array=np.append(columns_array, 'Ret_11')
    market_prediction=pd.DataFrame(columns=columns_array)

    for i in market_etf:
        print("Working on symbol: ", i.split('.')[0])
        market_prediction.loc[market_etf.index(i),'Symbol']=i.split('.')[0]
        df=pd.read_csv(market_path+'\\'+i)
        df.dropna(inplace=True)
        df['Close']=scaler.fit_transform(df['Close'].values.reshape(-1,1))
        data=df['Close'].values
        df['Close']=scaler.inverse_transform(df['Close'].values.reshape(-1,1))

        data= data.reshape(-1,1)
        train, test = data[0:-look_back], data[-(look_back+forward_days):]
        trainX, trainY = create_dataset(train, look_back)
        testX, testY = create_dataset(test, look_back)
        trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1],1))
        testX = np.reshape(testX, (testX.shape[0], testX.shape[1],1))

        model = Sequential()
        model.add(LSTM(num_hidden,input_shape = (trainX.shape[1], look_back)))
        model.add(Dense(1))
        model.compile(loss = 'mean_squared_error', optimizer = 'adam')
        model.fit(trainX,trainY, epochs = num_epochs, batch_size = 8, verbose = 0)
    
        train_fitX=scaler.inverse_transform(model.predict(trainX).reshape(-1,1)).reshape(-1)
        train_Y=scaler.inverse_transform(trainY.reshape(-1,1)).reshape(-1)

        penalty=(train_fitX[-63:]/train_Y[-63:] - 1).mean()+1 #63 is a quarter worth 
        #TODO try times two the panalty
        forecast = predict(num_prediction, model,penalty)
        market_prediction.loc[market_etf.index(i),'Predicted']=forecast[-1]
        market_prediction.iloc[market_etf.index(i),2:13]=forecast

        market_prediction.loc[market_etf.index(i),'RSI_7']=pta.rsi(df['Close'], length=7).iloc[-1]
        market_prediction.loc[market_etf.index(i),'RSI_21']=pta.rsi(df['Close'], length=21).iloc[-1]

        market_prediction.loc[market_etf.index(i),'Maxdrawdown']=(df['Close'] / df['Close'].rolling(252*2).max() - 1).iloc[-1]
        market_prediction.loc[market_etf.index(i),'Maxdrawup']=(df['Close'].rolling(252*2).max() / df['Close'] - 1).iloc[-1]
        market_prediction.loc[market_etf.index(i),['Ret_1', 'Ret_2', 'Ret_3', 'Ret_4', 'Ret_5','Ret_6', 'Ret_7', 'Ret_8', 'Ret_9', 'Ret_10', 'Ret_11']]=forecast / df['Close'].iloc[-1] - 1
        K.clear_session()
    
    market_prediction.sort_values('Ret_11', ascending=False, inplace=True)
    today=datetime.now().strftime('%Y%m%d')
    market_prediction.to_csv(r"C:\RedXCapital\Dividends\Data\Market Daily Predictions\market_prediction_"+today+".csv", index=False)
    return

