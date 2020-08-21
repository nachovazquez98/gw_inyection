#%%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUARDAR NUMPY ARRAY A FORMATO NPZ
Created on Mon Oct  7 19:27:01 2019

@author: nacho
Para hacer las inyecciones en los 3 interferometros debemos de sumarlo con tiempo desfazado
investigar cuanto tiempo tarda en llegar de un sensor a otro.
1,10-100 kpc, es inversamente proporcional, hacer los kpc por cada sample

H1 Y L1, seleccionamos al azar una onda en los dos ruidos
en la misma posicion del tiempo y con el desface

Signal readme: The equation of state used during the evolution is either
the one of Shen et al. (Shen EoS) or the one by Lattimer
and Swesty (LS EoS).

guardar el ruido en cvs dos columnas

un segmento de ruido en los 3 ruidos en diferentes distancias tomando en cuenta 
el desface, en 32+-4. H1-L1: 10ms, L1-V1: ?


Un solo temlate convertido en 11 tipos de KPC, inyectados en L1 y H1 (em los 5 pares) cada 32+-u(-4,4) segundos
spn 20 archivos y 10 logs

cuando se haga la inyeccion, guardar , tipo de supernova, dist (kpc)

DATADIR = 
for file in os.listdir(DATADIR):
    
t = t/1000 #s     
h = h/2 #20 kpc

220 archivos

todas las inyeccciones van a tener la misma distancia del mismo sample, 
hacer un arreglo con todas las distancias kpc e iterar ese arreglo, 
y hacer un indice para guardar el tiempo en el que se esta inyectando
"""
import numpy as np 
import pandas as pd
import h5py
import matplotlib.pyplot as plt 
import pylab
import csv
from pandas import read_csv
import os
import tkinter
from tkinter import filedialog
import random
from pathlib import Path
root = tkinter.Tk()
root.withdraw()
############################################
def select_random_signal(strain_ts, strain_noise):
    gw_path = gwsignal_path + "/" + gw_folder[random.randrange(len(gw_folder))]
    gw_name = os.path.basename(gw_path)
    #timesample
    t = np.loadtxt(gw_path,usecols=(0)) # ms
    h = np.loadtxt(gw_path,usecols=(1)) # 10 Kpc
    #regla de tres
    t        = t / 1000    # s
    h        = h * 10      # 1 Kpc
    
    gw_ts = t[1] - t[0]
    #GUARDAR SAMPLE EN CSV
    cols = np.empty((len(t), 2))
    cols[:, 0] = t
    cols[:, 1] = h
    c = np.savetxt('%s.csv' % os.path.basename(gw_path), 
                   cols, delimiter =' ', header = "time, strain",
                   comments="")
    series = read_csv('%s.csv' % os.path.basename(gw_path), 
                      delim_whitespace=True)
    series.columns = ['time', 'strain']
    series.to_csv('%s.csv' % os.path.basename(gw_path), sep = ' ', index = False)
    #RESAMPLEAR EL ARCHIVO CSV
    series = read_csv('%s.csv' % os.path.basename(gw_path), delim_whitespace=True, index_col = 0)
    #lo convierte a datetime de segundos
    series.index = pd.to_datetime(series.index, unit='s')
    #downsample
    downsampled = series.resample('244140ns').ffill()
    sampled_y = downsampled['strain'].to_numpy()
    sampled_x = np.arange(0, strain_ts * len(sampled_y), strain_ts)
    #GENERAR CSV RESAMPLEADO
    cols = np.empty((len(sampled_x), 2))
    cols[:, 0] = sampled_x
    cols[:, 1] = sampled_y
    c = np.savetxt('%s_resampled.csv' % os.path.basename(gw_path), cols, delimiter =' ', header = "time, strain", comments="")
    series = read_csv('%s_resampled.csv' % os.path.basename(gw_path), delim_whitespace=True)
    series.columns = ['time', 'strain']
    series.to_csv('%s_resampled.csv' % os.path.basename(gw_path), sep = ' ', index = False)
    #AGREGAR RUIDO AL CSV RESAMPLEADO
    numSamples = len(sampled_x)
    return sampled_y, numSamples, gw_name, gw_path
#######################################################################
#random inyection
def random_dist_kpc():
    dist_kpc = (random.choice([1.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]))
    return dist_kpc

def random_hop_sec(): #agregar mas brincos
    hop_sec=(random.choice([32+(random.randrange(-4,+4)), 
                        100+(random.randrange(-30, +30)),]))
    return hop_sec

def hdf5_features(data_file):
        strain_noise = dataFile['strain']['Strain'][()]
        strain_ts = dataFile['strain']['Strain'].attrs['Xspacing']
        strain_meta = dataFile['meta']
        print("Noise Time Sample (s)", strain_ts)
        gpsStart = strain_meta['GPSstart'][()]
        duration_sec = strain_meta['Duration'][()]
        gpsEnd   = gpsStart + duration_sec
        time = np.arange(gpsStart, gpsEnd, strain_ts)
        return strain_noise, strain_ts, gpsStart, duration_sec, time
##############################################################
#########################INICIA###############################
##############################################################
#CREA EL ROOT DE TRABAJ0
path = "/home/nacho/Documents/GW/inyection2" #donde esta el codigo!!!!
#path = os.path.dirname(os.path.abspath(__file__)) #si lo corre en terminal y en otra direccion
os.chdir(path)
print("workingdir0: ", os.getcwd())
#CREA EL ROOT DE LAS PLANTILLAS
print("Seleccione la carpeta de las plantillas:")
gwsignal_path = filedialog.askdirectory()
gw_folder = os.listdir(gwsignal_path)
#############################################################
#hacer una iteracion de todas las carpetas adentro de la principal
print("Seleccione la carpeta de los segmentos de ruido:")
hdf5_pathdir = filedialog.askdirectory()
for subdir, dirs, files in os.walk(hdf5_pathdir): 
    os.chdir(path)  
    os.mkdir(os.path.basename(subdir)[-15:])
    os.chdir(os.getcwd() + "/" + os.path.basename(subdir)[-15:])
    try:
        hdf5_file = files[0]
        hdf5_path = subdir + "/" + files[0]
        print("\nnew hdf5 folder: ", hdf5_path)
        dataFile = h5py.File(hdf5_path, 'r')
##############IMPORTAR NOISE HDF5######################
        strain_noise, strain_ts, gpsStart, duration_sec, time = hdf5_features(dataFile)
        i_value = []
        i_dist_kpc = []
        i_gw_name = []
        i_sampled_y = []
        i_numSamples = []
        i=0
        while i <= (len(strain_noise)): #definir el tope porque no hay un numsample constante
            hop_sec=random_hop_sec()
            i += int((hop_sec * len(strain_noise)) / duration_sec) #validar no ahregar el ultimo si es menor a len(strain_noise)
            i_value.append(i)  
            sampled_y, numSamples, gw_name, gw_path = select_random_signal(strain_ts, strain_noise)  
            #lo guardo en una lista
            i_sampled_y.append(sampled_y)
            i_numSamples.append(numSamples)
            i_gw_name.append(gw_name)
            dist_kpc = random_dist_kpc()
            i_dist_kpc.append(dist_kpc)   
    except IndexError:
        pass
    for file in files:
#############crea carpetas de trabajo#####################
        print("workingdir2: ", os.getcwd())        
        #crear carpeta con el nombre del detector, y la asigno como workingdir
        #acceder a la direccion del codigo y no en la subcarpeta generada en la anterior iteracion
        os.mkdir(os.path.basename(file)[0:4] + "_" + os.path.basename(file)[22:32])
        os.chdir(os.getcwd() + "/" + os.path.basename(file)[0:4] + "_" + os.path.basename(file)[22:32])
        print("workingdir3: ", os.getcwd())
        #os.chdir('../') #para ver la esctructura de las carpetas antes de las inyecciones
####################genera strain_noise##################   
        hdf5_file = file
        hdf5_path = subdir + "/" + file
        print("file hdf5path: ", hdf5_path)
        dataFile = h5py.File(hdf5_path, 'r')
        strain_noise1, strain_ts, gpsStart, duration_sec, time = hdf5_features(dataFile)
#####################inyeccion###########################           
        for i in range(0,len(i_value)-1): #el ultimo elemento se pasa
            #agregrar adenrto del [] el tiempo de distancia de los detectores
            if os.path.basename(hdf5_path).find("H-H1") != -1:
                strain_noise1[i_value[i]: i_value[i]+i_numSamples[i]] += (np.multiply(i_sampled_y[i], 10.0/i_dist_kpc[i]))
            elif os.path.basename(hdf5_path).find("L-L1") != -1:
                strain_noise1[i_value[i]: i_value[i]+i_numSamples[i]] += (np.multiply(i_sampled_y[i], 10.0/i_dist_kpc[i])) + (((random.randrange(-10,10)) * len(strain_noise)) / duration_sec)
            else:
                pass #queda pendiente virgo
##############guardar log a csv#####################
        with open("log_" + ((os.path.basename(hdf5_path))[:4]) + '_' + str(gpsStart) + ".csv", mode ="w") as f:
            f_csv = csv.writer(f)
            f_csv.writerow(["time_inj strain(time_inj) index progenitor dist_kpc EoS"])
            for j in range(len(i_value)-1): #el ultimo elemento se pasa
                #esta linea es particular para el nombre de los archivosde las templates de dimelmeier
                line = str(time[i_value[j]]) + ' ' + str(strain_noise1[i_value[j]]) + ' ' + str(i_value[j]) + ' ' + str(i_gw_name[j][7:11]) + ' ' + str(i_dist_kpc[j]) + ' '
                if i_gw_name[j].find("shen") != -1:
                    line += 'shen'
                elif i_gw_name[j].find("ls") != -1:
                    line += 'ls'
                else:
                    pass
                f_csv.writerow([line])
        f.close()
#########guardar strain cpn inyecciones a csv################
        df = pd.DataFrame({"time" : time, "strain" : strain1})
        filename = (os.path.basename(hdf5_path)[:4]) + '_' + str(gpsStart)
        compression_options = dict(method='zip', archive_name=f'{filename}.csv')
        df.to_csv(f'{filename}.zip', index=False, compression=compression_options)
#################sale de la ultima carpeta####################
        os.chdir('../')















