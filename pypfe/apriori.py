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

'''Generic multi-core Apriori implementation.'''

import sys
from copy import copy
from random import sample
from multiprocessing import Process, Queue
from Queue import Empty
import logging as log

class Apriori(object):
    '''Class implementing Apriori frequent itemset mining.
    '''
    @staticmethod
    def _frequent_objects(objects, freq_op, join_op, **kwargs):
        num_cores = kwargs.get('num_cores', 1)
        # setup multiprocessing queues for transferring objects
        obj_queue     = Queue()
        frequent_queue = Queue()

        # create the processes
        processes = []
        for idx in range(num_cores):
            args = zip(kwargs.keys(), kwargs.values())
            p = Process(target=Apriori._frequent_objects_process, args=[obj_queue, frequent_queue, freq_op, join_op, args])
            processes.append(p)
            p.start()

        # feed the processes the objects
        for obj in objects:
            obj_queue.put(obj)
        for _ in range(num_cores): # put in some sentinels
            obj_queue.put(None)

        # get the frequent objects
        frequent_objects = []
        sentinel_count = 0
        while True:
            obj = frequent_queue.get()
            if obj == None:
                sentinel_count += 1
                if sentinel_count >= num_cores:
                    break
            else:
                frequent_objects.append(obj)
        for p in processes:
            p.join()

        return set(frequent_objects)

    @staticmethod
    def _frequent_objects_process(obj_queue, frequent_queue, freq_op, join_op, args):
        # reconstruct key-word arguments
        kwargs = dict()
        for key, value in args:
            kwargs[key] = value

        frequents = []
        while True:
            obj = obj_queue.get()
            if obj != None and freq_op(obj, **kwargs):
                frequent_queue.put(obj)
                continue
            elif obj == None:
                break

        # send the frequent objects to the queue
        frequent_queue.put(None)
        frequent_queue.close()

    @staticmethod
    def create_conjunctions(candidates, freq_objects, join_op, parents, **kwargs):
        conjunctions = set()
        for candidate in candidates:
            for freq in freq_objects:
                conj = join_op(candidate, freq, **kwargs)
                if conj == None:
                    continue
                conjunctions.add(conj)
                # store the parents of the conjunctions
                parents.add((candidate, conj))
                parents.add((freq, conj))
        return conjunctions

    @staticmethod
    def keep_maximal(objects, parents):
        maximal = set(objects)
        for parent, child in parents:
            if parent != child and child in objects and parent in maximal:
                maximal.remove(parent)
        return maximal

    @staticmethod
    def mine(objects, freq_op, join_op, **kwargs):
        '''Mine frequent objects using Apriori.
        objects - given seed objects.
        freq_op(obj, **kwargs) - function that must return True/False if
                                 given object instance is frequent.
        join_op(o1, o2, **kwargs) - must create a new object out of two
                                    frequent objects o1 and o2.
        It is ok for join_op to return none in cases two frequent objects
        cannot be joined (or this is not desireable)

        keyword arguments:
        num_cores      - the number of cores the mining process will use.
        keep_maximal   - if False, keep all frequent (default True)
        max_candidates - if given, use a random sample of candidates of
                         given size each iteration.
        '''
        num_cores      = kwargs.get('num_cores', 1)
        max_candidates = kwargs.get('max_candidates', None)
        log.info('Apriori using {0} processes.'.format(num_cores))
        if max_candidates != None:
            log.info('Max candidates per iteration is {0}'.format(max_candidates))

        # initiate the mining procedure
        freq_objects = Apriori._frequent_objects(objects, freq_op, join_op, **kwargs)
        candidates = set(freq_objects)
        if max_candidates != None:
            candidates = sample(candidates, min(max_candidates, len(candidates)))
        resulting_objects = set(freq_objects)
        parents = set()

        while len(candidates) > 0:
            log.debug('Have {0} candidates in iteration.'.format(len(candidates)))
            candidates = Apriori._frequent_objects(candidates, freq_op, join_op, **kwargs)
            resulting_objects |= set(candidates)
            candidates = Apriori.create_conjunctions(candidates, freq_objects, join_op, parents, **kwargs)
            candidates -= resulting_objects
            if max_candidates != None:
                candidates = sample(candidates, min(max_candidates, len(candidates)))

        log.debug('Mined {0} frequent objects.'.format(len(resulting_objects)))
        if kwargs.get('keep_maximal', True):
            resulting_objects = Apriori.keep_maximal(resulting_objects, parents)
            log.debug('Have {0} maximal objects.'.format(len(resulting_objects)))
        return resulting_objects

    @staticmethod
    def mine_n_best(objects, freq_op, join_op, weight_op, n, **kwargs):
        resulting_objects = Apriori.mine(objects, freq_op, join_op, **kwargs)

        # get best n objects using weight operator
        resulting_objects = reversed(sorted([(weight_op(obj, **kwargs), obj) for obj in resulting_objects]))
        resulting_objects = [obj for _, obj in resulting_objects][-n:]

        log.debug('Returing {0} most frequent objects.'.format(len(resulting_objects)))
        return resulting_objects


