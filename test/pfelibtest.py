# PFE library tests based on Python interface.
import unittest
from pypfe import *

class OrderedDocCoverTest(unittest.TestCase):
    '''Test OrderedDocCover.'''

    def setUp(self):
        self.v1    = LongVector([7,4,5,6,2,3,3])
        self.v2    = LongVector([6,7,8,9,10])
        self.ordc1 = OrderedDocCover(20, self.v1)
        self.ordc2 = OrderedDocCover(20, self.v2)
        self.ordc3 = OrderedDocCover(20, LongVector([6,7]))
        self.ordc4 = OrderedDocCover(20, LongVector([2,3,4,5,6,7,8,9,10]))
        self.ordc5 = OrderedDocCover(20)

    def test_consistency(self):
        '''Test that initializing OrderedDocCover really removes duplicates
           and keeps the cover elements in sorted order. We cannot trust
           the user to do that.'''
        self.assertEqual(list(sorted(set(self.v1))),
                         list(self.ordc1.indices()))
        self.assertEqual(list(sorted(set(self.v2))),
                         list(self.ordc2.indices()))

    def test_difference(self):
        ordc3 = self.ordc1 - self.ordc2
        ordc4 = self.ordc2 - self.ordc1
        self.assertEqual(list(ordc3.indices()), [2,3,4,5])
        self.assertEqual(list(ordc4.indices()), [8,9,10])

    def test_sym_difference(self):
        ordc3 = self.ordc1 ^ self.ordc2
        ordc4 = self.ordc2 ^ self.ordc1
        self.assertEqual(list(ordc3.indices()), [2,3,4,5,8,9,10])
        self.assertEqual(list(ordc4.indices()), [2,3,4,5,8,9,10])

    def test_intersection(self):
        ordc3 = self.ordc1 & self.ordc2;
        self.assertEqual(list(ordc3.indices()), list(self.ordc3.indices()))
        self.assertEqual(ordc3, self.ordc3)

    def test_union(self):
        ordc4 = self.ordc1 | self.ordc2
        self.assertEqual(list(ordc4.indices()), list(self.ordc4.indices()))
        self.assertEqual(ordc4, self.ordc4)

    def test_copy(self):
        oc = OrderedDocCover(OrderedDocCover(OrderedDocCover(self.ordc2)))
        self.assertEqual(oc, self.ordc2)


class BitsetDocCoverTest(unittest.TestCase):
    '''Test BitsetDocCover'''

    def setUp(self):
        self.v1 = BoolVector([False]*10 + [True]*10)
        self.v2 = BoolVector([False]*5  + [True]*10 + [False]*5)
        self.v3 = BoolVector([False]*10 + [True]*5  + [False]*5)
        self.v4 = BoolVector([False]*5  + [True]*15)

        self.bitc1 = BitsetDocCover(self.v1)
        self.bitc2 = BitsetDocCover(self.v2)
        self.bitc3 = BitsetDocCover(self.v3)
        self.bitc4 = BitsetDocCover(self.v4)

    def test_consistency(self):
        self.assertEqual(list(self.v1),
                         list(self.bitc1.bits()))
        self.assertEqual(list(self.v2),
                         list(self.bitc2.bits()))

    def test_difference(self):
        bitc5 = self.bitc1 - self.bitc2
        bitc6 = self.bitc2 - self.bitc1
        self.assertEqual(list(bitc5.bits()), [False]*15 + [True]*5)
        self.assertEqual(list(bitc6.bits()), [False]*5 + [True]*5 + [False]*10)

    def test_sym_difference(self):
        bitc5 = self.bitc1 ^ self.bitc2
        bitc6 = self.bitc2 ^ self.bitc1
        v    = [False]*5 + [True]*5 + [False]*5 + [True]*5
        bitc = BitsetDocCover(BoolVector(v))
        self.assertEqual(list(bitc5.bits()), v)
        self.assertEqual(bitc5, bitc)
        self.assertEqual(list(bitc6.bits()), v)
        self.assertEqual(bitc6, bitc)

    def test_interection(self):
        bitc3 = self.bitc1 & self.bitc2;
        self.assertEqual(list(bitc3.bits()), list(self.bitc3.bits()))
        self.assertEqual(bitc3, self.bitc3)

    def test_union(self):
        bitc4 = self.bitc1 | self.bitc2
        self.assertEqual(list(bitc4.bits()), list(self.bitc4.bits()))
        self.assertEqual(bitc4, self.bitc4)

    def test_copy(self):
        bc = BitsetDocCover(BitsetDocCover(BitsetDocCover(self.bitc2)))
        self.assertEqual(bc, self.bitc2)

class DocCoverTest(unittest.TestCase):
    '''Test interopability of OrderedDocCover and BitsetDocCover'''

    def setUp(self):
        self.bits1 = BoolVector([True, False]*100)
        self.bits2 = BoolVector([False, True]*100)
        self.bits3 = BoolVector([True]*200)
        self.bits4 = BoolVector([False]*200)
        self.rang1 = LongVector([i for i in range(200) if i%2 == 0])
        self.rang2 = LongVector([i for i in range(200) if i%2 == 1])
        self.rang3 = LongVector(list(range(200)))
        self.rang4 = LongVector([])

    def test_interopability(self):
        bitc1 = BitsetDocCover(self.bits1)
        bitc2 = BitsetDocCover(self.bits2)
        bitc3 = BitsetDocCover(self.bits3)
        bitc4 = BitsetDocCover(self.bits4)

        ordc1 = OrderedDocCover(bitc1)
        ordc2 = OrderedDocCover(bitc2)
        ordc3 = OrderedDocCover(bitc3)
        ordc4 = OrderedDocCover(bitc4)

        # make some unions
        bitc5 = bitc1 | bitc2
        ordc5 = ordc1 | ordc2

        self.assertEqual(bitc5, bitc3)
        self.assertEqual(ordc5, ordc3)
        self.assertEqual(BitsetDocCover(ordc5), bitc3)
        self.assertEqual(OrderedDocCover(bitc5), ordc3)

        # make some intersections
        bitc6 = bitc1 & bitc3
        bitc7 = bitc2 & bitc4
        ordc6 = ordc1 & ordc3
        ordc7 = ordc2 & ordc4

        self.assertEqual(bitc6, bitc1)
        self.assertEqual(ordc6, ordc1)
        self.assertEqual(BitsetDocCover(ordc6), bitc1)
        self.assertEqual(OrderedDocCover(bitc6), ordc1)

        self.assertEqual(bitc7, bitc4)
        self.assertEqual(ordc7, ordc4)
        self.assertEqual(BitsetDocCover(ordc7), bitc4)
        self.assertEqual(OrderedDocCover(bitc7), ordc4)


class CoverTest(unittest.TestCase):
    '''Test Cover instances.'''

    def setUp(self):
        self.cov1 = {'esimene': BoolVector([1,1,1,1,1]),
                     'teine':   BoolVector([1,1,1,1,1]),
                     'kolmas':  BoolVector([1,1,1,1,1]),
                     'neljas':  BoolVector([1,1,1,1,1])}
        self.cov2 = {'viies':   BoolVector([1,1,1,1,1]),
                     'teine':   BoolVector([1,0,1,0,1]),
                     'kolmas':  BoolVector([1,1,1,1,1]),
                     'neljas':  BoolVector([1,1,1,1,1])}
        self.cov3 = {'teine':   BoolVector([1,0,1,0,1]), # intersection
                     'kolmas':  BoolVector([1,1,1,1,1]),
                     'neljas':  BoolVector([1,1,1,1,1])}
        self.cov4 = {'esimene': BoolVector([1,1,1,1,1]), # union
                     'teine':   BoolVector([1,1,1,1,1]),
                     'kolmas':  BoolVector([1,1,1,1,1]),
                     'neljas':  BoolVector([1,1,1,1,1]),
                     'viies':   BoolVector([1,1,1,1,1])}
        self.cov5 = {'esimene': BoolVector([1,1,1,1,1]), # difference1
                     'teine':   BoolVector([0,1,0,1,0]),
                     'kolmas':  BoolVector([0,0,0,0,0]),
                     'neljas':  BoolVector([0,0,0,0,0])}
        self.cov6 = {'teine':   BoolVector([0,0,0,0,0]), # difference2
                     'kolmas':  BoolVector([0,0,0,0,0]),
                     'neljas':  BoolVector([0,0,0,0,0]),
                     'viies':   BoolVector([1,1,1,1,1])}
        self.cov7 = {'esimene': BoolVector([1,1,1,1,1]), # sym_difference
                     'teine':   BoolVector([0,1,0,1,0]),
                     'kolmas':  BoolVector([0,0,0,0,0]),
                     'neljas':  BoolVector([0,0,0,0,0]),
                     'viies':   BoolVector([1,1,1,1,1])}

        self.cov1 = StrMapBv(self.cov1)
        self.cov2 = StrMapBv(self.cov2)
        self.cov3 = StrMapBv(self.cov3)
        self.cov4 = StrMapBv(self.cov4)
        self.cov5 = StrMapBv(self.cov5)
        self.cov6 = StrMapBv(self.cov6)
        self.cov7 = StrMapBv(self.cov7)

    def test_convert(self):
        bitc1 = BitsetCover(asBc(self.cov1))
        ordc1 = OrderedCover(asOc(self.cov1))
        bitc2 = asBitsetCover(ordc1)
        ordc2 = asOrderedCover(bitc1)
        bitc3 = asBitsetCover(ordc2)
        ordc3 = asOrderedCover(bitc2)
        self.assertEqual(bitc1, bitc3)
        self.assertEqual(ordc1, ordc3)

    def test_bitset(self):
        bitc1 = BitsetCover(asBc(self.cov1))
        bitc2 = BitsetCover(asBc(self.cov2))
        bitc3 = BitsetCover(asBc(self.cov3)) # intersect
        bitc4 = BitsetCover(asBc(self.cov4)) # union
        bitc5 = BitsetCover(asBc(self.cov5)) # diff1
        bitc6 = BitsetCover(asBc(self.cov6)) # diff2
        bitc7 = BitsetCover(asBc(self.cov7)) # symdiff

        self.assertEqual(dict(self.cov3), dict(asBvFromBc((bitc1 & bitc2).map())))
        self.assertEqual(dict(self.cov4), dict(asBvFromBc((bitc1 | bitc2).map())))
        self.assertEqual(dict(self.cov5), dict(asBvFromBc((bitc1 - bitc2).map())))
        self.assertEqual(dict(self.cov6), dict(asBvFromBc((bitc2 - bitc1).map())))
        self.assertEqual(dict(self.cov7), dict(asBvFromBc((bitc1 ^ bitc2).map())))

        self.assertEqual(bitc3, bitc1 & bitc2)
        self.assertEqual(bitc3, bitc2 & bitc1)
        self.assertNotEqual(bitc4, bitc1 & bitc2)
        self.assertEqual(bitc4, bitc1 | bitc2)
        self.assertEqual(bitc4, bitc2 | bitc1)
        self.assertNotEqual(bitc3, bitc1 | bitc2)
        self.assertEqual(bitc5, bitc1 - bitc2)
        self.assertEqual(bitc6, bitc2 - bitc1)
        self.assertEqual(bitc7, bitc1 ^ bitc2)

    def test_ordered(self):
        ordc1 = OrderedCover(asOc(self.cov1))
        ordc2 = OrderedCover(asOc(self.cov2))
        ordc3 = OrderedCover(asOc(self.cov3)) # intersect
        ordc4 = OrderedCover(asOc(self.cov4)) # union
        ordc5 = OrderedCover(asOc(self.cov5)) # diff1
        ordc6 = OrderedCover(asOc(self.cov6)) # diff2
        ordc7 = OrderedCover(asOc(self.cov7)) # symdiff

        self.assertEqual(dict(asLvFromOc(asOc(self.cov3))), dict(asLvFromOc((ordc1 & ordc2).map())))
        self.assertEqual(dict(asLvFromOc(asOc(self.cov4))), dict(asLvFromOc((ordc1 | ordc2).map())))
        self.assertEqual(dict(asLvFromOc(asOc(self.cov5))), dict(asLvFromOc((ordc1 - ordc2).map())))
        self.assertEqual(dict(asLvFromOc(asOc(self.cov6))), dict(asLvFromOc((ordc2 - ordc1).map())))
        self.assertEqual(dict(asLvFromOc(asOc(self.cov7))), dict(asLvFromOc((ordc1 ^ ordc2).map())))

        self.assertEqual(ordc3, ordc1 & ordc2)
        self.assertEqual(ordc3, ordc2 & ordc1)
        self.assertNotEqual(ordc4, ordc1 & ordc2)
        self.assertEqual(ordc4, ordc1 | ordc2)
        self.assertEqual(ordc4, ordc2 | ordc1)
        self.assertNotEqual(ordc3, ordc1 | ordc2)
        self.assertEqual(ordc5, ordc1 - ordc2)
        self.assertEqual(ordc6, ordc2 - ordc1)
        self.assertEqual(ordc7, ordc1 ^ ordc2)

    def test_symdiff(self):
        bitc1 = BitsetCover(asBc(self.cov1))
        bitc2 = BitsetCover(asBc(self.cov2))
        bitc7 = BitsetCover(asBc(self.cov7)) # symdiff

        ordc1 = OrderedCover(asOc(self.cov1))
        ordc2 = OrderedCover(asOc(self.cov2))
        ordc7 = OrderedCover(asOc(self.cov7)) # symdiff

        #print dict(asBvFromBc(((bitc1 - bitc2) | (bitc2 - bitc1)).map()))
        self.assertEqual(bitc7, (bitc1 - bitc2) | (bitc2 - bitc1))
        self.assertEqual(ordc7, (ordc1 - ordc2) | (ordc2 - ordc1))
        self.assertEqual(bitc1 ^ bitc2, (bitc1 - bitc2) | (bitc2 - bitc1))
        self.assertEqual(ordc2 ^ ordc1, (ordc1 - ordc2) | (ordc2 - ordc1))


class CoverMetrics(unittest.TestCase):
    '''Test CoverMetrics calculations. '''
    pass


if __name__ == '__main__':
    unittest.main()
