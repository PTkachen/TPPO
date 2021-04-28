import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow import keras

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

        self.model.add(Dense(12, input_dim=6, activation='relu'))
        self.model.add(Dense(8, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy',
                           optimizer='adam', metrics=['accuracy'])
        self.model.fit(x, y, epochs=150, batch_size=10, verbose=0)

    def predict(self, X):
        predictions = self.model.predict(X)
        return predictions

    def save(self, path):
        self.model.save(path)
