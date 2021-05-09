import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping
from keras.layers import Dropout

class NN:
    model = Sequential()

    def __init__(self, path=''):
        if path:
            self.model = keras.models.load_model(path)
            print(f'loaded model {path}')

    def learn(self, x, y):
        # x: np.array(n, 6), y: np.array(n)
        if len(x) != len(y):
            print('error')
            return

        self.model.add(Dense(19, input_dim=6, activation='relu'))
        self.model.add(Dense(8, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(8, activation='relu'))
        #self.model.add(Dense(8, activation='relu'))
        #self.model.add(Dense(5, activation='softmax')) #В этих штуках ничего не меняется(как по мне )
        #self.model.add(Dense(15, activation='softplus')) #
        #self.model.add(Dense(5, activation='softsign')) #
        #self.model.add(Dense(25, activation='tanh')) #
        #self.model.add(Dense(20, activation='selu')) #
        self.model.add(Dense(1, activation='sigmoid'))
        es = EarlyStopping(monitor="val_accuracy", min_delta=0.01, patience=3)
        callback = [es]
        self.model.compile(loss='binary_crossentropy',
                           optimizer='adam', metrics=['accuracy'])
        self.model.fit(x, y, epochs=150, batch_size=10, verbose=1,callbacks=callback)

    def predict(self, X):
        predictions = self.model.predict(X)
        return predictions

    def save(self, path):
        self.model.save(path)
