# -*- coding: utf-8 -*-
# Python 2.7
#  Pattern based fact extraction library.
#    Copyright (C) 2013 University of Tartu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pfe import *

import tempfile
import numpy as np
from scipy.stats.mstats import normaltest
import matplotlib.pyplot as plt
import os

def figure_as_binary(figure, format='pdf'):
    '''Take a matplotlib figure and get it as binary data.'''
    import tempfile
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'image')
    figure.savefig(path, format=format)
    f = open(path, 'rb')
    data = f.read()
    f.close()
    return data

def normaltest_plot(matrix):
    '''Plot the distributions of metrics of rules on a set of documents.
    Rows of the matrix should represent each conjunction, while columns
    represent respective documents. Each value is either recall, support,
    precision or something else.'''

    # first normalize the matrix conjunction-wise
    normalized = np.zeros(shape=matrix.shape)
    means = np.mean(matrix, 1)
    stds  = np.std(matrix, 1)
    for i in range(matrix.shape[0]):
        normalized[i,:] = (matrix[i,:] - means[i])/stds[i]

    # now create a cumulative histogram
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    # disable ticks for big subplot
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    # create smaller subplots
    ax1.grid(True)
    ax2.grid(True)
    tmp = ax1.hist(normalized, 100, histtype='step', normed=True, cumulative=False)
    tmp = ax2.hist(normalized, 100, histtype='step', normed=True, cumulative=True)
    ax1.set_ylim(0, 1)
    ax2.set_ylim(0, 1)
    ax1.set_ylabel('density')
    ax2.set_ylabel('cumulative density')
    ax.set_xlabel('normalized values, where $\mu = 0$, $\sigma = 1$ for each pattern')
    A = figure_as_binary(fig)

    # first normalize the matrix document-wise
    normalized = np.transpose(matrix)
    means = np.mean(normalized, 1)
    stds  = np.std(normalized, 1)
    for i in range(normalized.shape[0]):
        normalized[i,:] = (normalized[i,:] - means[i])/stds[i]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    # disable ticks for big subplot
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    # create smaller subplots
    ax1.grid(True)
    ax2.grid(True)
    tmp = ax1.hist(normalized, 100, histtype='step', normed=True, cumulative=False)
    tmp = ax2.hist(normalized, 100, histtype='step', normed=True, cumulative=True)
    ax1.set_ylim(0, 1)
    ax2.set_ylim(0, 1)
    ax1.set_ylabel('density')
    ax2.set_ylabel('cumulative density')
    ax.set_xlabel('normalized values, where $\mu = 0$, $\sigma = 1$ for each document')
    B = figure_as_binary(fig)

    return (A, B)

