
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
import kafe
from kafe.function_library import gauss, linear_2par
from kafe import *
from matplotlib import gridspec
import pandas as pd
import time
import random
from numba import njit
from graphics_Utils import DataMonitoring , ChildWindow 
from analysis import logger
from pathlib import Path
from logging.handlers import RotatingFileHandler
import coloredlogs as cl
import verboselogs
log = logger.setup_derived_logger('analysis utils')


class BeamSpotScan(object):

    def __init__(self, parent=None):
       logger.extend_logging()
       verboselogs.install()
       self.logger = logging.getLogger(__name__)
       self.logger.setLevel(logging.DEBUG)
       self.logger.notice('Beam Spot Scanning ...')

    def compute_move(self,size_x=1, z=20,z_Delay=None, x_Delay=0, x=20, size_z=1, sourcemeter=False, directory=None):
        # Initial plot will be generated
        '''
        Assuming that the cabinet door is the -z
        1 mm is equivalent to 56.88888 step
        x : Number of movements to x direction
        z: Number of movements inside the cabinet
        Size_x: size of the step in  mm x direction
        Size_z: size of the step in  mm z direction
        '''
    #     size_x = size_x*57000
    #     size_z=size_z*57000
    #     if Sourcemeter:
    #         dut = Dut('Scanning_pyserial.yaml')
    #         dut.init()
    #         dut['sm'].write(":OUTP ON")
    #         #dut['sm'].write("*RST")
    #         #dut['sm'].write(":SOUR:VOLT:RANG 60")
    #         #dut['sm'].write('SENS:CURR:PROT ' + str(CurrentLimit))
    #         #print "The Protection Current limit is", dut['sm'].ask("SENS:CURR:PROT?")
    #         dut['sm'].write(":SOUR:FUNC VOLT")
    #         dut['sm'].write(':SOUR:VOLT 50')
    #     else:
    #         dut = Dut('motorstage_Pyserial.yaml')
    #         dut.init()
        def fill_snake_pattern(step_z=False,sourcemeter = sourcemeter, size_z=None, a=None, b=None , c=None, size_x=None, x_Delay=None, z_Delay=z_Delay, directory=None):            
             first_point = True
             for step_x in tqdm(np.arange(a, b, c) , unit='xstep'):
                 #if not first_point:
                 #    pass
                     # dut["ms"].read_write("MR%d" % (size_x), address=3) # x 50000,100,50 = 4.5 cm left/right
                 #first_point = False
                 time.sleep(x_Delay)
                 if sourcemeter:
                     val = dut['sm'].ask(":MEAS:CURR?")
                     current = val[15:-43]
                 else:
                     current = random.randint(0, 100)
                 # save for Monitoring 
                 self.set_data(x = current)
                 beamspot[step_z, step_x] = float(current)
                 try: 
                    save_to_h5(data=beamspot, outname='beamspot_Live.h5', directory= directory)
                 except IndexError:  #open file failure
                    pass
                 #beamshow  = plt.imshow(beamspot, aspect='auto', origin='upper',  cmap=plt.get_cmap('tab20c'))
                 #plt.pause(0.05)
             # dut["ms"].read_write("MR%d" % (-size_z), address=2)  # x# x 50000,100,50 = 4.5 cm in/out
             time.sleep(z_Delay)
        
        t0 = time.time()
        length = 20
        config_beamspot = define_configured_array(size_x=size_x, z=z, x=x, size_z=size_z)
        beamspot = np.zeros(shape=(z, x), dtype=np.float64)
        for step_z in tqdm(np.arange(z), unit='zstep'):
            a, b = config_beamspot[step_z].item(0) , config_beamspot[step_z].item(1)
            c , new_size_x = config_beamspot[step_z].item(2), config_beamspot[step_z].item(3)
            fill_snake_pattern(step_z=step_z , a=int(a), b=int(b) , c=int(c), size_x=int(new_size_x), x_Delay=x_Delay, z_Delay=z_Delay, directory = directory)
        #plt.show()
        outname='beamspot.h5'
        save_to_h5(data=beamspot, outname=outname, directory=directory) 
        log.info("The beamspot file is saved as " + os.path.join(directory, outname))
        t1 = time.time()
        log.info("The time Estimated is "+ np.str(t1 - t0)+" s")


    def set_data(self, x=None):
        self.data = x
     
    def get_data(self):
        return self.data 
        
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
    
def plot_spline_masking(calibrated_file=False, PdfPages=PdfPages):
    with tb.open_file(calibrated_file, 'r') as in_file:
        spline_mask = in_file.root.configuration.spline_mask[:]
        enabled_pixels = len(spline_mask[spline_mask == True])
    plt.figure()
    ax = plt.gca()
    hist_masked = np.ma.masked_where(spline_mask == False, spline_mask)
    plt.imshow(hist_masked.T, origin='lower')
    ax.set_title('Enabled pixels after interpolation: (%d) pixels' % enabled_pixels)
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    plt.tight_layout()
    PdfPages.savefig()


def source_test(PdfPages=PdfPages, directory=False, tdc_data=False, tests_title=False, test="tdc_value",
                ylabel=r'Counts', scan_parameter_range=False):
    # au.create_tdc_injection_calibration(scan_id=scan_id, data_file=data_file, run_config=run_config, chunk_size=80000, title="Am", cols=selected_columns, rows=selected_rows, spline_file=directory + "UnivariateSpline.npy", directory=directory)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    hist_data, edges = np.histogram(tdc_data, bins=np.arange(scan_parameter_range[0], scan_parameter_range[-1], 1))  #
    x, y = edges[:-1], hist_data
    plt.fill_between(x, y, color='#F5A9BC', label="Data")
    ax.set_title(tests_title)
    ax.set_xlabel(test)
    ax.set_ylabel(ylabel)
    plt.savefig(directory + tests_title + "_.png")
    PdfPages.savefig()


def distribution(Hist, PdfPages=PdfPages, directory=None, binwidth=1000, title="tdc_timestamp"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scaling = 1
    selection = Hist["tdc_value"] == 1
    plt.hist(Hist[title], bins=range(min(Hist[title]), max(Hist[title]) + binwidth, binwidth))
    ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x * scaling))
    ax.xaxis.set_major_formatter(ticks_x)
    # ax.set_ylim(ymax=1200)
    ax.set_xlabel('TDC cycle')
    ax.set_ylabel("Counts")
    # ax.text(0.05, 0.95, "$\Delta$VCAL = %d" % (scan_param_id * 100), transform=ax.transAxes, fontsize=13, fontweight='bold', va='top')
    plt.title(title, fontsize=11)
    plt.tight_layout()
    fig.savefig(directory + title + "_.png")
    PdfPages.savefig()


def plot_calibration_line_kafe(x, y, y_err=0.0, x_err=0.0, directory=False, PdfPages=False, suffix='Calibration',
                               xlabel='$\gamma$-peak position from literature [keV]', ylabel=r'$\Delta$VCAL'):
    hdataset = kafe.build_dataset(x, y, yabserr=y_err, xabserr=x_err, title="Data", axis_labels=[xlabel, ylabel])
    hfit = kafe.Fit(hdataset, linear_2par)
    hfit.do_fit()
    hplot = kafe.Plot(hfit)
    hplot.plot_all()
    hplot.save(directory + "tdc_calibrated_data_kafe_%s.png" % suffix)
    PdfPages.savefig()


def plot_tdc_gamma_spectrum_kafe(cluster_hist=False, p0=None, scan_parameter_range=False, cols=[0], rows=[0], title=False, cluster_background=False, background=True,
                                 PdfPages=False, directory=None):

    Delta_Vcal_max = scan_parameter_range[-1]
    Delta_Vcal_min = 0  # scan_parameter_range[0]
    bin_size = 1
    tdc_data = au.get_pixel_data(cluster_hist, cols, rows, test="delta_vcal")
    hist_data, edges = np.histogram(tdc_data, bins=np.arange(Delta_Vcal_min, Delta_Vcal_max, bin_size))
    x, y = edges[:-1], hist_data
    y_err = np.sqrt(y)
    hdataset = kafe.build_dataset(x, y, yabserr=y_err, title="Data for %s source" % title, axis_labels=['x', 'y'])
    # error for bins with zero contents is set to 1.
    covmat = hdataset.get_cov_mat("y")
    for i in range(0, len(covmat)):
        if covmat[i, i] == 0.:
            covmat[i, i] = 1.
    hdataset.set_cov_mat('y', covmat)  # write it back

    # Create the Fit instance
    if len(p0) > 3:
        # hfit1 = kafe.Fit(hdataset, gauss, fit_label="Fit of a Gaussian to histogram data 1")
       # hfit1.set_parameters(mean=p0[2], sigma=p0[4], scale=p0[0], no_warning=True)
        hfit2 = kafe.Fit(hdataset, gauss, fit_label="Fit of a Gaussian to histogram data 2")
        hfit2.set_parameters(mean=p0[3], sigma=p0[5], scale=p0[1], no_warning=True)
        # hfit1.do_fit()
        hfit2.do_fit()
        hplot = kafe.Plot(hfit2)
    else:
        hfit = kafe.Fit(hdataset, gauss, fit_label="Fit of a Gaussian to histogram data")
        hfit.set_parameters(mean=p0[1], sigma=p0[2], scale=p0[0], no_warning=True)
        # perform an initial fit with temporary errors (minimal output)
        hfit.call_minimizer(final_fit=True, verbose=False)
        hfit.do_fit()
        hplot = kafe.Plot(hfit)
        hfit.get_parameter_values()

    # re-set errors using model at pre-fit parameter values:
    #        sigma_i^2=cov[i, i]=n(x_i)
    # fdata = hfit.fit_function.evaluate(hfit.xdata, hfit.current_parameter_values)
    # np.fill_diagonal(covmat, fdata)
    # hfit.current_cov_mat = covmat  # write back new covariance matrix

    # now do final fit with full output
    hplot.plot_all()
    hplot.save(directory + "\h5_files" + "tdc_calibrated_data_kafe_%s.png" % title)
    PdfPages.savefig()


def plot_calibration_distribution(x, y, directory=False, PdfPages=False, ticks=False, suffix='vcal_energy_calibration', xlabel='$\gamma$-peak position from literature [keV]', ylabel=r'$\Delta$VCAL',
                                  line_color="lightblue", bar_color="gray", bar_width=0.5, difference=None):
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
    ax = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax.bar(x, y, align='center', width=bar_width, color=line_color, label="mean " + ylabel + "=%0.2f$\pm$%0.2f" % (np.mean(y), np.absolute(np.std(y)) / np.sqrt(len(y))))
    ax.set_ylabel(ylabel, fontsize=9)
    ax.get_xaxis().set_visible(False)
    ax.grid(True)
    ax2.bar(x, difference, align='center', width=bar_width, color=bar_color, label="mean offset=%0.2f$\pm$%0.2f" % (np.mean(difference), np.absolute(np.std(difference)) / np.sqrt(len(difference))))

    ax2.grid(True)
    ax2.set_ylim((-np.amax(np.abs(difference))) - 1, (np.amax(np.abs(difference))) + 1)
    ax2.set_ylabel('Offset [$\Delta$VCAL]', fontsize=9)
    ax2.set_xlabel(xlabel)
    ax2.plot(plt.xlim(), [0, 0], '-', color='black')  # black line
    plt.xticks(x, ticks)
    ax.legend(loc="upper right")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(directory + suffix + ".png", bbox_inches='tight')
    PdfPages.savefig()
    return np.mean(y), np.absolute(np.mean(y)) ** 0.5, np.mean(difference), np.absolute(np.mean(difference)) ** 0.5


def plot_calibration_lines(x=0.0, y=0.0, y_err=0.0, x_err=0.0, m=0.0, m_error=0.0, c=0.0, c_error=0.0, point_label=None, scipy_fit2=True, directory=False, PdfPages=False, suffix='vcal_energy_calibration',
                           xlabel='$\gamma$-peak position from literature [keV]', ylabel=r'Charge [$\Delta$VCAL]'):

    def lin(x, *p):
        m, b = p
        return m * x + b

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if point_label is not None:
        for X, Y, Z in zip(x, y, point_label):
            ax.annotate('{}'.format(Z), xy=(X, Y), xytext=(-4, 5), ha='right', textcoords='offset points', fontsize=7)
    ax.errorbar(x, y, xerr=x_err, yerr=y_err, fmt='o', color='black', markersize=3)  # plot points
    popt, pcov_fit = curve_fit(lin, x, y, sigma=y_err, absolute_sigma=True, maxfev=5000, p0=(10, 1))
    scipy_fit = 'Original Fit: ax + b\n a=%.2f$\pm$%.2f\n b=%.2f$\pm$ %.2f' % (popt[0], np.absolute(pcov_fit[0][0]) ** 0.5, popt[1], np.absolute(pcov_fit[1][1]) ** 0.5)
    ax.plot(x, lin(x, *popt), linestyle="--", color="blue", label=scipy_fit)
    if scipy_fit2:
        scipy_fit2 = 'Corrected fit: ax + b\n a=%.2f$\pm$%.2f\n b=%.2f$\pm$ %.2f' % (m, m_error, c, c_error)
        x_space = x  # np.linspace(x[0], x[-1], 10)
        ax.plot(x_space, lin(x_space, m, c), linestyle="--", color="red", label=scipy_fit2)
    ax.legend()
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.grid(True)
    plt.savefig(directory + suffix + ".png", bbox_inches='tight')
    PdfPages.savefig()


def dose_current(directory=False, PdfPages=False):

    def linear(x, m, c):
        return m * x + c

    fig = plt.figure()
    ax = fig.add_subplot(111)
    dac = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900])  # dac_data["dac"]
    voltage = np.array([19.9, 39.6, 59.4, 79.2, 99.1, 118.8, 138.6, 158.3, 178.2])
    y1 = [9.18 * dac[l] + 257.46 for l in range(len(dac))]
    y2 = [9.18 * dac[l] - 363.82 for l in range(len(dac))]
    x1 = voltage
    stdev = 0.01
    xlabel = 'Dac settings [$\Delta$VCAL]'
    ylabel = r'Voltage [mV]'
    sig1 = [stdev * y1[k] for k in range(len(y1))]
    popt1, pcov = curve_fit(linear, x1, y1, sigma=sig1, absolute_sigma=True, maxfev=5000, p0=(1, 1))
    ax.errorbar(x1, y1, yerr=sig1, color="Black", fmt='o')
    label1 = "Sensor 1"
    ax.plot(x1, linear(x1, *popt1), linestyle="-", color="blue", label=label1)

    sig2 = [stdev * y2[k] for k in range(len(y2))]
    popt2, pcov = curve_fit(linear, x1, y2, sigma=sig2, absolute_sigma=True, maxfev=5000, p0=(1, 1))
    ax.errorbar(x1, y2, yerr=sig2, color="Black", fmt='o')
    label2 = "Sensor 2"
    ax.plot(x1, linear(x1, *popt2), linestyle="-",
            color="red", label=label2)
    plt.ticklabel_format(useOffset=False)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(True)
    ax.legend()  # prop={'size': 8}
    plt.tight_layout()
    plt.savefig(directory + "Capacitance.png", bbox_inches='tight')
    PdfPages.savefig()

def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent

