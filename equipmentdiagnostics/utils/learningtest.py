#!/usr/bin/python3

from equipmentdiagnostics.ediag.ediag import EDiag
import sys
import numpy as np
from equipmentdiagnostics.ediag.nn import NN
import matplotlib.pyplot as plt

app = EDiag('bearing1')
app.loaddata('/media/teadr1nker/94AC9FC8AC9FA2F2/dataset/2nd_test')
data, out = app.preparation()
n = NN('model')
got = n.predict(data)
for i in range(len(got)):
    print(f'Got: {got[i]}, expected: {out[i]}')

plt.plot(got)
plt.plot(out)
plt.legend(['got','expected'])
plt.savefig('got-expected.png')
