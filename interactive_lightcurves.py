"""
Creates interactive lightcurve and periodograms that can be controlled by
Jupyter notebook widgets. 
"""

import lightkurve as lk

from lightkurve import search_targetpixelfile, search_lightcurve 
from lightkurve.periodogram import LombScarglePeriodogram

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

import astropy.units as u

import ipywidgets as widgets
from ipywidgets import (interactive_output, IntSlider, FloatSlider, Layout, Text,
                        jslink, GridBox, Dropdown, Button, FloatText, IntText, Combobox, Label)

# Read in data for comparing period estimates
data = pd.read_csv('lurie_ebs.csv') 
data_short = data[data['Porb'] < 10] # Limiting to Porb less than 10 days for now

# The combobox widget demands a list of strings. Probably not the most elegant solution.
kic_list = data_short['KIC'].tolist()
kic_list = list(map(str, kic_list))


def generate_plots(KIC, period, bin_size):
    """
    Queries for lightcurve from Kepler, plots lightcurve and periodograms
    
    Keyword arguments:
    KIC -- numeric part of a KIC ID
    period -- period of the folded lightcurve
    bin_size -- time bin size of the folded lightcurve
    """
    # Format ID for lightkurve functions
    KIC_ID = 'KIC ' + str(KIC)
    
    # Get Porb from data
    p_orb = data[data['KIC'] == KIC]['Porb'] 
    
    # Check for valid KIC ID before plotting
    try:
        tpf = search_targetpixelfile(KIC_ID, author="Kepler", cadence="long").download()
        lc = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask).flatten(window_length=401)
        folded_lc = lc.remove_nans().remove_outliers().fold(period=period*u.day).bin(time_bin_size=bin_size)

        periodogram = LombScarglePeriodogram.from_lightcurve(lc)

        fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(25,10))
        lc.plot(ax=ax[0,0])
        folded_lc.plot(ax=ax[0,1])
        periodogram.plot(ax=ax[1,0])
        periodogram.plot(ax=ax[1,1], view='period', scale='log')
        ax[1,1].add_artist(AnchoredText(f'Period at max power: {periodogram.period_at_max_power:.4f}\n'
                                        + f'Period from literature: {p_orb}',
                                        prop=dict(size=15), loc = 'lower right'))
        
        plt.tight_layout()
        plt.show()
    
    except AttributeError:
        fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(25,10))
        ax[1,1].add_artist(AnchoredText('Target not found',prop=dict(size=15), loc = 'lower right'))
        plt.tight_layout()
        plt.show()


#Create widgets
style = {'description_width': 'initial'}


KIC_box = Combobox(value=kic_list[0],
                   placeholder='',
                   options=kic_list,        # Match options to entries in data set
                   description='KIC ID',
                   style=style,
                   disabled=False,
                   grid_area = 'KIC_box',
                   continuous_update=False)
period_box = FloatText(value='5',
                       placeholder='',
                       description='Period (days)',
                       style=style, disabled=False,
                       grid_area = 'period_box',
                       step = 0.001,
                       continuous_update=False)
bin_box = FloatText(value='0.02',
                    placeholder='',
                    description='Bin size',
                    style=style,
                    disabled=False,
                    grid_area = 'bin_box',
                    step = 0.001,
                    continuous_update=False)

widgridet = GridBox(children = [KIC_box, period_box, bin_box],
                  layout=Layout(
                  width ='1400px',
                  align_items = 'flex-start',
                  grid_template_rows = 'auto',
                  grid_template_columns = '33% 34% 33%',
                  grid_template_areas = '''
                  "KIC_box period_box bin_box"
                  ''')
                 )


def plots():
    """Displays widgets and plots"""
    out = interactive_output(generate_plots, {'KIC':KIC_box, 'period':period_box,'bin_size':bin_box})
    return display(widgridet, out)


