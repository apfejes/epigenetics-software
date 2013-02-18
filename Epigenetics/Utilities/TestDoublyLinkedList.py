'''
Created on 2013-01-31

@author: fejes
'''
import unittest
import DoublyLinkedList


class Test(unittest.TestCase):

    

    def setUp(self):
        '''Nothing Specific.'''
        pass

    def tearDown(self):
        pass


    def test_append(self):
        '''setup'''
        LL = DoublyLinkedList.DLL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        '''test order of items in LL'''
        string = LL.getAll()
        self.assertEqual(string, "thing1thing2thing3")
        self.assertEqual(LL.size(), 3)

    def test_insert_before(self):
        '''setup'''
        LL = DoublyLinkedList.DLL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        '''move one item in, then insert a new node'''
        pointer = LL.head.next
        LL.insert_before(pointer, "thingX")
        '''test order of items in LL'''
        string = LL.getAll()
        self.assertEqual(string, "thing1thingXthing2thing3")
        self.assertEqual(LL.size(), 4)

    def test_insert_at_head(self):
        '''setup'''
        LL = DoublyLinkedList.DLL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        '''insert one item at head of list'''
        LL.insert_at_head("thing4")
        '''test order of items in LL'''
        string = LL.getAll()
        self.assertEqual(string, "thing4thing1thing2thing3")
        self.assertEqual(LL.size(), 4)
        
    def test_pop_head(self):
        '''setup'''
        LL = DoublyLinkedList.DLL()
        LL.append("thing1")
        LL.append("thing2")
        LL.append("thing3")
        self.assertEqual(LL.size(), 3)
        '''insert one item at head of list'''
        p = LL.pop_head()
        self.assertEqual(p, "thing1")
        self.assertEqual(LL.size(), 2)
        '''test order of items in LL'''
        string = LL.getAll()
        self.assertEqual(string, "thing2thing3")
        self.assertEqual(LL.size(), 2)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()