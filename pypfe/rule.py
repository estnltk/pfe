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

import numpy as np
from sklearn.decomposition import PCA

def _create_conjunction(toks):
    '''Toks is a array of pos1, rule1, pos2, rule2 ...'''
    conjunction = []
    for i in range(0, len(toks), 2):
        conjunction.append(Rule(long(toks[i]), toks[i+1]))
    return Conjunction(sorted(conjunction))

def read_conjunctions(path):
    '''Load conjunctions from file specified by given path.'''
    conjunctions = []
    f = open(path, 'rb')
    line = f.readline()
    while line != '':
        toks = line.rstrip('\n').split('\t')
        conjunctions.append(_create_conjunction(toks))
        line = f.readline()
    f.close()
    return ConjunctionVector(conjunctions)

def write_conjunctions(conjunctions, path):
    f = open(path, 'wb')
    for c in conjunctions:
        f.write('\t'.join(['{0}\t{1}'.format(pos, attr) for pos, attr in c]))
        f.write('\n')
    f.close()

def conjunction_covers(conjunctions, basiccovers):
    covers = []
    for c in conjunctions:
        cover = conjunctionCover(Conjunction(c), basiccovers)
        covers.append(cover)
    return covers

def conjunction_metrics(conjunctions, basiccovers, truecover):
    metrics = []
    for c in conjunctions:
        cover = conjunctionCover(Conjunction(c), basiccovers)
        metrics.append(cover.metrics(truecover))
    return metrics

def conjunction_docmetrics(conjunctions, basiccovers, truecover):
    metrics = []
    for c in conjunctions:
        cover = conjunctionCover(Conjunction(c), basiccovers)
        metrics.append(cover.documentMetrics(truecover))
    return metrics

def metric_matrix(ruledocmetrics, docnames, metric='recall'):
    '''Given a list of StrDocMetrics instances, create a numpy matrix, where
       each row represents a single rule and each column a single document.
       Matrix elements are specified metric for that particular rule and
       document.

       The values are extracted in alphabetical order of document names.
       '''
    n = len(ruledocmetrics)
    m = len(docnames)
    M = np.zeros(shape=(n, m), dtype=float)
    for colidx, name in enumerate(sorted(docnames)):
        for rowidx in range(n):
            M[rowidx, colidx] = ruledocmetrics[rowidx][name].all()[metric]
    return M

def matthews_matrices(conjunction_covers, docnames, keep_diagonal=False):
    '''Compute a matrix, where for each document we compute matrix
    of Matthew correlation coefficients.'''
    n = len(conjunction_covers)
    matrices = dict()
    for name in docnames:
        matrices[name] = np.zeros(shape=(n, n), dtype=float)
    for i in range(n):
        for j in range(i, n):
            m = conjunction_covers[i].documentMetrics(conjunction_covers[j])
            for name in docnames:
                if name not in m:
                    matrices[name][i,j] = -1
                    matrices[name][j,i] = -1
                else:
                    v = m[name].matthews()
                    matrices[name][i,j] = v
                    matrices[name][j,i] = v
    if keep_diagonal:
        for name in docnames:
            matrices[name] = np.triu(matrices[name])
    return matrices

def conj_corr_matrix(mats):
    '''Compute a matrix, where each row represents a document and each
       column a correlation between some two conjunctions.
       The matrix can be used as input to PCA or other similar methods.

       `mats` is the output of `matthews_matrices`.
    '''
    mats = tuple([np.reshape(np.triu(mats[docname]), -1)
                    for docname in sorted(mats.keys())])
    X = np.vstack(mats)
    return X

def remove_nan_columns(X):
    return X[:,~np.isnan(X).any(axis=0)]

def pca_transform(conj_matrix, scale_to_variance=True):
    n = conj_matrix.shape[0]
    pca = PCA(n_components=n-1, whiten=True)
    pca.fit(conj_matrix)
    X = pca.transform(conj_matrix)
    # now scale to variance (useful for later computing distances)
    if scale_to_variance:
        ratios = pca.explained_variance_ratio_
        for col in range(len(ratios)):
            X[:,col] *= ratios[col]
    return X

def euc_dist(X):
    '''Given a matrix of points, compute the matrix of Euclidian distances.'''
    n = X.shape[0]
    Z = np.zeros(shape=[n,n])
    for i in range(n):
        for j in range(i, n):
            Y = X[i,:] - X[j,:]
            Y = Y*Y
            Z[i,j] = np.sqrt(np.sum(Y))
            Z[j,i] = Z[i,j]
    return Z

def compute_mses(X):
    '''Compute MSE values between documents. X should be a matrix, where
       each row represents a documetn and each column correlation between
       same features.'''
    n = X.shape[0]
    Z = np.zeros(shape=[n,n])
    for i in range(n):
        for j in range(i, n):
            Y = X[i,:] - X[j,:]
            Z[i,j] = np.std(Y)
            Z[j,i] = Z[i,j]
    return Z
