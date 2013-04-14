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

import numpy as np

def matthews_corrcoef(matrix):
    n, m = matrix.shape
    M = np.zeros([n, n], dtype=np.float)
    for i in range(n):
        a = matrix[i,:]
        for j in range(i, n):
            b = matrix[j,:]
            tp = np.count_nonzero((a == 1) & (a == b))
            fp = np.count_nonzero(a > b)
            fn = np.count_nonzero(a < b)
            tn = np.count_nonzero((a == 0) & (a == b))
            c = (tp*tn - fp*fn) / (np.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))+0.001)
            M[i,j] = c
            M[j,i] = c
        log.debug('{0}/{1}'.format(i, n))
    return M

def statistics(predicted_seq, true_seq, labels=None):
    assert (len(predicted_seq) == len(true_seq))
    # count the number of true positives, false positives and false negatives
    tp = dict()
    fp = dict()
    fn = dict()

    if labels == None:
        labels = set(predicted_seq) | set(true_seq)

    # compute true positives, false positives and false negatives and also the
    # confusion matrix
    for pred, true in zip(predicted_seq, true_seq):
        if pred == true:
            tp[pred] = tp.get(pred, 0.) + 1.
        else:
            fp[pred] = fp.get(pred, 0.) + 1.
            fn[true] = fn.get(true, 0.) + 1.

    # calculate precision, recall and fscore for all labels
    precisions = dict()
    recalls    = dict()
    fscores    = dict()

    for label in labels:
        precision = tp.get(label, 0.) / (tp.get(label, 0.) + fp.get(label, 0.0000001))
        recall    = tp.get(label, 0.) / (tp.get(label, 0.) + fn.get(label, 0.0000001))
        fscore    = 2 * precision * recall / (precision + recall + 0.0000001)
        precisions[label] = precision
        recalls[label]    = recall
        fscores[label]    = fscore

    return {'precision': precisions, 'recall': recalls, 'fscore': fscores}

