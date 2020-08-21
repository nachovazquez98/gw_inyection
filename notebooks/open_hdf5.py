#%%
"""
-meta: Meta-data for the file. This is basic information such as the GPS times covered, which instrument, etc.
-quality: Refers to data quality. The main item here is a 1 Hz time series describing the data quality for each 
second of data. This is an important topic, and we'll devote a whole step of the tutorial to working with data quality information.
-strain: Strain data from the interferometer. In some sense, this is "the data", the main measurement performed by LIGO. 
"""
#el eje x es meta>GPSstart
#el eje y es strain>strain
import numpy as np 
import pandas as pd
import h5py
import matplotlib.pyplot as plt

hdf5_path = fileName = 'L-L1_GWOSC_O2_4KHZ_R1-1185669120-4096.hdf5'
#%%
with h5py.File(hdf5_path, 'r') as hdf:
    ls = list(hdf.keys()) #tiene llaves cada archivo 
    print('List of datasets in this file: \n', ls)

#contenido de strain
with h5py.File(hdf5_path, 'r') as hdf:
    key_strain = list(hdf.keys())[2]
    data_strain = list(hdf[key_strain])
print("Data in strain: ", data_strain)

#contenido de meta
#gpsstart
#GPSstart es el tiempo, eje x 
with h5py.File(hdf5_path, 'r') as hdf:
    key_meta = list(hdf.keys())[0]
    data_meta = list(hdf[key_meta]) 
print("Data in meta: ", data_meta)

#contenido de quality
with h5py.File(hdf5_path, 'r') as hdf:
    key_quality = list(hdf.keys())[1]
    data_quality = list(hdf[key_quality]) 
print("Data in quality: ", data_quality)

#%%
##########################################################################
#contenido 
dataFile = h5py.File(fileName, 'r')

for key in dataFile.keys():
    print (key) 
#%%    
strain = dataFile['strain']['Strain'][()]
#time sample (tiempo de muestreo)
ts = dataFile['strain']['Strain'].attrs['Xspacing']

print ("\n\n")
metaKeys = dataFile['meta'].keys()
meta = dataFile['meta']
for key in metaKeys:
    print (key), (meta[key][()])
#%%    
gpsStart = meta['GPSstart'][()]
duration = meta['Duration'][()]
gpsEnd   = gpsStart + duration

print ("\n\n")
strainKeys = dataFile['strain'].keys()
strain = dataFile['strain']
##accede al contenido de strain
for key in strainKeys:
    print ((key), (strain[key][()]))
#almacena el arreglo de strain en strain1 (vector y)
strain1 = (strain[key][()])
#print ("Strain: ",strain1)
#%%
#crea el vector x
time = np.arange(gpsStart, gpsEnd, ts)

print("Time sample: ", ts)

print("\n\metaKey: ",metaKeys)
print("\n\meta: ",meta)
print ("\n\ngpsStart: ",gpsStart)
print ("\n\ngpsEnd: ",gpsEnd)

plt.plot(time, strain1)
plt.xlabel('GPS Time (s)')
plt.ylabel('H1 Strain')
plt.show()
#%%




#%%
#