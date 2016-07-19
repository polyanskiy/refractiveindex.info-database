
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import sys
reload(sys)  
sys.setdefaultencoding('utf-8')

import matplotlib as mpl
mpl.rc('lines', linewidth=2,markersize=10)
mpl.rc('font', size=16)
e1=np.loadtxt('mos2-e1.csv',delimiter=',')
e2=np.loadtxt('mos2-e2.csv',delimiter=',')
from scipy import interpolate
evtoum=1.2398
e1f=interpolate.interp1d(evtoum/e1[:,0],e1[:,1])
e2f=interpolate.interp1d(evtoum/e2[:,0],e2[:,1])
plt.subplot(211)
plt.plot(evtoum/e1[:,0],e1[:,1],marker='s')
plt.plot(evtoum/e1[:,0],e1f(evtoum/e1[:,0]))
plt.plot(evtoum/e2[:,0],e2[:,1],marker='s')
plt.plot(evtoum/e2[:,0],e2f(evtoum/e2[:,0]))

plt.subplot(212)
xgrid=np.linspace(evtoum/e1[-3,0],evtoum/e1[0,0],100)
nn=lambda l:np.sqrt(e1f(l)+1j*e2f(l))
n=np.real(nn(xgrid))
k=np.imag(nn(xgrid))
k[np.where(k<0)]=0
plt.plot(xgrid,n)
plt.plot(xgrid,k)

np.savetxt('mos2-nk.csv',np.transpose((xgrid,n,k)),)

plt.savefig('e1.pdf')
