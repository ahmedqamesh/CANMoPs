
from __future__ import division
from tqdm import tqdm
from scipy.optimize import curve_fit
import logging
import os
import logging
import argparse
import yaml
import json
import ast
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
from scipy import interpolate
import tables as tb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import pandas as pd
import time
import random
from numba import njit
from pathlib import Path
from logging.handlers import RotatingFileHandler
import coloredlogs as cl
import verboselogs
        
def define_configured_array(size_x=1, z=20, x=20, size_z=1):
    #log.info('Creating a confiiguration array for the snake pattern')
    config_beamspot = np.zeros(shape=(z, 5), dtype=np.float64)
    for step_z in np.arange(0, z):
        if step_z % 2 == 0:
            a, b, c = 0, x, 1
        else:
            size_x = size_x * -1
            a, b, c = x - 1, -1, -1
        config_beamspot[step_z] = a, b, c, size_x, size_z
    return config_beamspot

def save_to_h5(data=None, outname=None, directory=None, title = "Beamspot scan results"):
    if not os.path.exists(directory):
            os.mkdir(directory)
    filename = os.path.join(directory, outname)
    with tb.open_file(filename, "w") as out_file_h5:
        out_file_h5.create_array(out_file_h5.root, name='data', title = title, obj=data)  

def open_yaml_file( directory=None , file=None):
    filename = os.path.join(directory, file)
    with open(filename, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

def save_to_csv(data=None, outname=None, directory=None):
    df = pd.DataFrame(data)
    if not os.path.exists(directory):
            os.mkdir(directory)
    filename = os.path.join(directory, outname)    
    df.to_csv(filename, index=True)


def open_h5_file(outname=None, directory=None):
    filename = os.path.join(directory, outname)
    with tb.open_file(filename, 'r') as in_file:
        data = in_file.root.data[:]
    return data


def get_subindex_description_yaml(dictionary = None, index =None, subindex = None):
    index_item = [dictionary[i] for i in [index] if i in dictionary]
    subindex_items = index_item[0]["subindex_items"]
    subindex_description_items = subindex_items[subindex]
    return subindex_description_items

def get_info_yaml(dictionary = None, index =None, subindex = "description_items"):
    index_item = [dictionary[i] for i in [index] if i in dictionary]
    index_description_items = index_item[0][subindex]
    return index_description_items
            
def get_subindex_yaml(dictionary = None, index =None, subindex = "subindex_items"):
    index_item = [dictionary[i] for i in [index] if i in dictionary]
    subindex_items = index_item[0][subindex]
    return subindex_items.keys()

def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent
def save_adc_date(directory = None,channel = None):
    File = tb.open_file(directory + "ch_"+channel+ ".h5", 'w')
    description = np.zeros((1,), dtype=np.dtype([("TimeStamp", "f8"), ("Channel", "f8"), ("Id", "f8"), ("Flg", "f8"), ("DLC", "f8"), ("ADCChannel", "f8"), ("ADCData", "f8"),("ADCDataConverted", "f8")])).dtype
    table = File.create_table(File.root, name='ADC_results', description=description)
    table.flush()
    row = table.row
    for i in np.arange(length_v):
        row["TimeStamp"] = voltage_array[i]
        row["Channel"] = mean
        row["Id"] = std
        row["DLC"] = voltage_array[i]
        row["ADCChannel"] = mean
        row["ADCData"] = std
        row["ADCDataConverted"] = std
        row.append()
    File.create_array(File.root, 'current_array', current_array, "current_array")
    File.close()
    logging.info("Start creating table")     
