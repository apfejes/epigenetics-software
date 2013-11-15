'''
Created on 2013-01-29

@author: fejes
'''

import unittest
import LinkedList


class FakeAlignedRead():

    def type(self):
        print ("FakeAlignedRead")

    def __init__(self, aend, alen, rev):
        self.aend = aend
        self.alen = alen
        self.is_reverse = rev

class Test(unittest.TestCase):


    def type(self):
        print ("TestLinkedList")

    def setUp(self):
        '''Nothing Specific.'''
        pass

    def tearDown(self):
        pass


    def test_append(self):
        '''setup'''
        LL = LinkedList.LL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        # test order of items in LL
        string = LL.getAll()
        self.assertEqual(string, "thing1thing2thing3")
        self.assertEqual(LL.size(), 3)


    def test_insert_at_head(self):
        ''''thing must be of type Node. Adds to the end of the list'''
        # setup
        LL = LinkedList.LL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        # insert one item at head of list
        LL.insert_at_head("thing4")
        # test order of items in LL
        string = LL.getAll()
        self.assertEqual(string, "thing4thing1thing2thing3")
        self.assertEqual(LL.size(), 4)

    def test_pop_head(self):
        '''setup'''
        LL = LinkedList.LL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        self.assertEqual(LL.size(), 3)
        # insert one item at head of list
        p = LL.pop_head()
        self.assertEqual(p, "thing1")
        self.assertEqual(LL.size(), 2)
        # test order of items in LL
        string = LL.getAll()
        self.assertEqual(string, "thing2thing3")
        self.assertEqual(LL.size(), 2)
