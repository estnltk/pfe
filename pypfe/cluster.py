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

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.cluster import KMeans
import scipy.cluster.hierarchy as sch
import numpy as np
import tempfile
import os.path

import pylab
import matplotlib.pyplot as plt

import sys

def tfidf_matrix(X, **kwargs):
     # get the tf-idf counts
    count_vect = CountVectorizer(**kwargs)
    counts     = count_vect.fit_transform(X)
    tf_transformer = TfidfTransformer().fit(counts)
    counts_tfidf   = tf_transformer.transform(counts)
    # compute cosine similarity
    matrix         = linear_kernel(counts_tfidf, counts_tfidf)
    return matrix

def hierarchial_sentences(X, **kwargs):
    '''Perform hierarchial clustering on a vector of sentences.'''

    matrix = tfidf_matrix(X, **kwargs)
    # hierarchial clustering
    linkage     = sch.linkage(matrix, method = 'complete')
    cutoff      = kwargs.get('cutoff_coef', 0.45)*max(linkage[:,2])
    # create the plot
    fig = pylab.figure()
    axdendro  = fig.add_axes([0.09,0.1,0.2,0.8])

    denodrogram = sch.dendrogram(linkage, orientation='right', color_threshold=cutoff)

    axdendro.set_xticks([])
    axdendro.set_yticks([])

    # extract the indices
    indices  = denodrogram['leaves']

    matrix = matrix[indices,:]
    matrix = matrix[:,indices]

    axmatrix = fig.add_axes([0.3,0.1,0.6,0.8])

    im = axmatrix.matshow(matrix, aspect='auto', origin='lower')
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])

    axcolor = fig.add_axes([0.91,0.1,0.02,0.8])
    pylab.colorbar(im, cax=axcolor)

    # flatten the clusters
    flat_clusters = sch.fcluster(linkage, cutoff, 'distance')
    leaders       = sch.leaders(linkage, flat_clusters)

    return {'fig': fig, 'flat': flat_clusters, 'leaders': leaders[1]}

def kmeans_sentences(X, n_clusters, **kwargs):
    '''Cluster sentences using kmeans.
    kwargs is forwarded to count_vectorizer.'''
    matrix = tfidf_matrix(X, **kwargs)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(matrix)
    return kmeans.predict(matrix)


