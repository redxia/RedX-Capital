from keras.preprocessing.sequence import TimeseriesGenerator
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
from keras import backend as K
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"
import math
#TODO grab the market dates and actually use those as future time.

num_hidden=8
num_epochs=10
look_back=1
forward_days=1


df=pd.read_csv(market_path+'\\'+i)
df['Date']=pd.to_datetime(df['Date'])
df.set_axis(df['Date'], inplace=True) #TODO maybe model upgrade HMM_State
df.drop(columns=['Date','Volume','Returns'], inplace=True) #, 'HMM_State'
df.dropna(inplace=True)
df.drop(columns='Date', inplace=True)

scaler=MinMaxScaler(feature_range=(0,1))
df['Close']=scaler.fit_transform(df['Close'].values.reshape(-1,1))
data=df[['Close','HMM_State']].values
data=df['Close'].values
data[:,0]=scaler.fit_transform(data[:,0].astype('float64'))
data=np.reshape(data,(-1,1)) # need to do this transform minmax scaler
data=scaler.fit_transform(data)
pred=[]

#TODO later input HMM_LAYERS
train, test = data[0:10,:], data[(10-1):(10+2),]

def create_dataset(dataset, look_back = 1):
    dataX, dataY = [], []
    if(len(dataset) ==3): # this is for test set to find mse
        dataX.append(dataset[0])
        dataY.append(dataset[2,0])
        return np.array(dataX), np.array(dataY)
    for i in range(len(dataset) - 2):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + 2, 0])
    return np.array(dataX), np.array(dataY)

trainX, trainY=create_dataset(train)
testX, testY=create_dataset(test)


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

train, test = data[0:10,:], data[(10-1):(10+forward_days),]

def create_dataset(dataset, look_back = 1):
    dataX, dataY = [], []
    if(len(dataset) ==(look_back+forward_days)): # this is for test set to find mse
        dataX.append(dataset[0])
        dataY.append(dataset[forward_days,0])
        return np.array(dataX), np.array(dataY)
    for i in range(len(dataset) - forward_days):
        a = dataset[i:(i + look_back), 0]
        b = dataset[i:(i + look_back), 1]
        dataX.append([a, b])
        dataY.append(dataset[i + forward_days, 0])
    return np.array(dataX), np.array(dataY)

forward_days=1
pred=[]
true=[]

pred_1=[]
true_1=[] #TODO this with the state space and  different look_back with different structure. add more layers # then look father ahead with state space. iknput my bullish or bearish view. for practical use
for i in range(len(df)-1000,len(data) - forward_days + look_back - 1):
    train, test = data[0:i,:], data[(i-look_back):(i+forward_days),]
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1],1))
    testX = np.reshape(testX, (testX.shape[0], testX.shape[1],1))
    model = Sequential()
    model.add(LSTM(num_hidden,input_shape = (trainX.shape[1], look_back)))
    model.add(Dense(1))
    model.compile(loss = 'mean_squared_error', optimizer = 'adam')
    model.fit(trainX,trainY, epochs = 5, batch_size = 32, verbose = 0)
    testPredict = model.predict(testX)
    # invert predictions
    testPredict = scaler.inverse_transform(testPredict)
    trueValue=scaler.inverse_transform(testY.reshape(-1,1))
    pred_1.append(testPredict)
    true_1.append(trueValue)
    print('Just completed iteration: ', i-(len(df)-1000))
    K.clear_session()

pred_1=np.reshape(pred_1,-1)
true_1=np.reshape(true_1,-1)
np.sqrt(mean_squared_error(pred_1,true_1))

figure(figsize=(12,8), dpi=180)
plt.plot(true_1,label = "SP500")
plt.plot(pred_1, label = "Predicted SP500")
plt.ylabel('SP500 Levels')
plt.xlabel('Time Index')
plt.legend()
plt.title("S & P 500 over Time")

def model_fit(train, test): # don't know if want recursive 1 day forward or do a strict day prediction
    train_generator=TimeseriesGenerator(train, train, length=look_back, batch_size=16)
    # test_generator=TimeseriesGenerator(test, test, length=look_back, batch_size=1)
    model=Sequential()
    model.add(LSTM(num_hidden, input_shape=(look_back,1)))
    model.add(Dense(forward_days))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit_generator(close_train, epochs=num_epochs, verbose=1)
    prediction=model.predict_generator(test_generator)
    prediction=scaler.inverse_transform(prediction)
    prediction=prediction.reshape((-1))
    return prediction



# close_data = df['Close'].values.reshape((-1,1))
# close_data=scaler.fit_transform(close_data)

# close_data[0:5]

# TODO this is recursive algo
# 1 day forward recursive might be over fitting. 10 days out should technically be more accurate
def model_fit(train, test): # don't know if want recursive 1 day forward or do a strict day prediction
    train_generator=TimeseriesGenerator(train, train, length=look_back, batch_size=16)
    # test_generator=TimeseriesGenerator(test, test, length=look_back, batch_size=1)
    model=Sequential()
    model.add(LSTM(num_hidden, input_shape=(look_back,1)))
    model.add(Dense(forward_days))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit_generator(close_train, epochs=num_epochs, verbose=1)
    prediction=model.predict_generator(test_generator)
    prediction=scaler.inverse_transform(prediction)
    prediction=prediction.reshape((-1))
    return prediction

    
close_train=scaler.inverse_transform(close_train)
close_test=scaler.inverse_transform(close_test)
close_data=scaler.inverse_transform(close_data)
close_train=close_train.reshape((-1))
close_test=close_test.reshape((-1))
    
prediction_series=np.concatenate([close_train,prediction])
close_train.append(prediction)
figure(figsize=(12,8), dpi=180)
plt.plot(close_data[split:(split+32)], label='SP500')
plt.plot(prediction_series[split:(split+32)], label='Predicted')
plt.legend()

math.sqrt(mean_squared_error(close_test[1:30], prediction[1:30]))

close_data=close_data.reshape((-1))



num_prediction=11

def predict(num_prediction, model):
    prediction_list = close_data[-look_back:]
    for i in range(num_prediction):
        x = prediction_list[-look_back:]
        x = x.reshape((1, look_back, 1))
        out = model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
    prediction_list = prediction_list[look_back-1:]
    return prediction_list
    
def predict_dates(num_prediction):
    last_date = df['Date'].values[-1]
    prediction_dates = pd.date_range(last_date, periods=num_prediction+1).tolist()
    return prediction_dates

num_prediction = 30
forecast = predict(num_prediction, model)
forecast_dates = predict_dates(num_prediction)     