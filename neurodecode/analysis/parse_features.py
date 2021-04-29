# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals

"""
Parse features generated by Random Forest classifier and
compute feature importance distribution.

@author: Kyuhwa Lee
Swiss Federal Institute of Technology Lausanne (EPFL)

"""

import os
import sys
import neurodecode
import scipy.io
import numpy as np
from neurodecode import logger

def get_feature_scores(featfile, channels=None, freq_ranges=None, matfile=None):
    """
    Parse feature importance scores generated by decoder.trainer.run_trainer() and
    compute feature importance distribution. The raw scores are importance ratio
    per feature to all features.

    Input
    -----
    featfile: Feature importance distribution file computed by Random Forests.
              Each line contains 3 columns separated by tab: Score Channel Frequency
              e.g. 66.6\tCz\t18
    channels: List of channel names. If None, all channels in featfile will be used.
    freq_ranges: Per-band frequency range. dict:{band_name:[fq_low, fq_high]}
                 fq_high is inclusive in the range.
                 if None, predefined bands will be used.

    Output
    ------
    data: Feature importance score. {band_name:percentage}
          'channel' field contains the sum of all scores per channel.
          'raw' field contains raw scores of all channels and frequency bins
    """

    # default ranges
    if freq_ranges is None:
        freq_ranges = dict(
            delta=[1, 4],
            theta=[4, 8],
            alpha=[8, 13],
            beta1=[13, 18],
            beta2=[18, 24],
            beta3=[24, 30],
            gamma=[31, 49])

    # find all channels first if needed
    if channels is None:
        channels = []
        with open(featfile) as f:
            f.readline()
            for l in f:
                ch = l.strip().split('\t')[1]
                if ch not in channels:
                    channels.append(ch)
        channels.sort()

    # build channel index lookup table
    ch2index = {ch:i for i, ch in enumerate(channels)}

    # initialise data structure
    data = {'channel':np.zeros(len(channels)), 'ch_names':channels,
        'raw':{ch:{} for ch in channels}, 'freq_ranges':freq_ranges}
    for band in freq_ranges:
        data[band] = np.zeros(len(channels))

    # start parsing
    f = open(featfile)
    f.readline()
    for l in f:
        token = l.strip().split('\t')
        importance = float(token[0])
        ch = token[1]
        if ch not in channels:
            continue
        fq = float(token[2])
        data['raw'][ch][fq] = importance
        for band in freq_ranges:
            if freq_ranges[band][0] <= fq <= freq_ranges[band][1]:
                data[band][ch2index[ch]] += importance
        data['channel'][ch2index[ch]] += importance

    # MATLAB export
    if matfile is not None:
        # matvar = [fq] x [ch]
        matvar = np.zeros([len(data['raw'][channels[0]]), len(channels)])
        fqlist = sorted(list(data['raw'][channels[0]].keys()))
        fq2index = {fq:i for i, fq in enumerate(fqlist)}
        for ch in channels:
            for fq in fqlist:
                try:
                    matvar[fq2index[fq]][ch2index[ch]] = data['raw'][ch][fq]
                except KeyError:
                    matvar[fq2index[fq]][ch2index[ch]] = 0
        scipy.io.savemat(matfile, {'scores':matvar, 'channels':channels, 'frequencies':fqlist})
        logger.info('Data exported to %s\n' % matfile)

    return data

def print_feature_scores(data, num_cols=8):
    """
    print features with number of channels per line set by num_cols (default=8)

    """
    print('-- Feature importance distribution --')
    channels = data['ch_names']
    channels_split = []
    for i in range(len(channels)):
        if i % num_cols == 0:
            channels_split.append([])
        channels_split[-1].append(i)
    for i, chs in enumerate(channels_split):
        channels_subset = ['%6s' % channels[ch] for ch in chs]
        txt = 'bands   | ' + ' '.join(channels_subset)
        if i == (len(channels_split) - 1):
            txt += ' | per band'
        rowlen = len(txt)
        print('=' * rowlen)
        print(txt)
        print('-' * rowlen)
        for band in data:
            if band in ['channel', 'raw', 'freq_ranges', 'ch_names']:
                continue
            band_name = '%d-%d' % (data['freq_ranges'][band][0], data['freq_ranges'][band][1])
            band_scores = []
            for ch_i in chs:
                band_scores.append('%6.2f' % data[band][ch_i])
            txt = '%-7s | %s' % (band_name, ' '.join(band_scores))
            if i == (len(channels_split) - 1):
                txt += ' | %6.2f' % np.sum(data[band])
            print(txt)
        txt = []
        for ch_i in chs:
            txt.append('%6.2f' % data['channel'][ch_i])
        if i == (len(channels_split) - 1):
            txt.append('| %6.2f' % sum(data['channel']))
        print('-' * rowlen)
        print('per chan| %s' % ' '.join(txt))

def feature_info(featfile, channels=None, freq_ranges=None, matfile=None):
    """
    Wrapper function to get feature importance and print statistics
    """
    data = get_feature_scores(featfile, channels, freq_ranges, matfile)
    print_feature_scores(data)


def config_run(featfile=None):
    if featfile is None or len(featfile.strip()) == 0:
        if os.path.exists('good_features.txt'):
            featfile = os.path.realpath('good_features.txt').replace('\\', '/')
            logger.info('Found %s in the current folder.' % featfile)
        else:
            featfile = input('Feature file path? ')
    feature_info(featfile)

# sample code
if __name__ == '__main__':
    FEATFILE = r'D:\data\MI\z2\LR\classifier\good_features.txt'
    CHANNELS = ['C3', 'C4', 'Cz']
    FREQ_RANGES = dict(
        delta=[1, 4],
        theta=[4, 8],
        alpha=[8, 13],
        beta=[13, 30],
        lgamma=[30, 49])

    MATFILE = None
    feature_info(FEATFILE, CHANNELS, FREQ_RANGES, MATFILE)
