import numpy as np 
import pylab

fullpath = 'signal_e15a_ls.dat'

t        = np.loadtxt(fullpath,usecols=(0)) # ms
hp       = 0*t
hx       = 0*t
h        = np.loadtxt(fullpath,usecols=(1)) # 10 Kpc

t        = t/1000    # s
h        = h*10      # 1 Kpc

gw_ts = t[1] - t[0]
print("Signal Time Sample (s):", gw_ts)

pylab.figure(2)
pylab.plot(t,h,linewidth=2.0)
pylab.xlabel('Time (s)',fontsize=18,color='black')
pylab.ylabel('Strain',fontsize=18,color='black')
pylab.grid(True)

pylab.show()
