'''
Created on 2013-01-29

@author: fejes
'''




class Node(object):
    '''A simple class describing a node in the linked list'''

    @staticmethod
    def type():
        '''print LinkedList.Node when asked'''
        print ("LinkedList.Node")

    def __init__(self, thing):
        '''initialize a node object'''
        self.holding = thing
        self.next = None


class LL(object):
    '''
    A simple LinkedList implementation
    '''

    @staticmethod
    def type():
        '''Print type LinkedList when asked'''
        print ("LinkedList")

    def __init__(self):
        self.__len = 0
        LL.head = None
        LL.tail = None

    def size(self):
        '''return the size of the linkedlist'''
        return self.__len


    def append(self, thing):
        ''''thing must be of type Node.  Adds to the end of the list'''
        node = Node(thing)
        if self.__len == 0:
            LL.head = node
            LL.tail = node
        else:
            LL.tail.next = node
            LL.tail = node
        self.__len += 1


    def insert_at_head(self, thing):
        ''''thing must be of type Node. Adds to the front of the list'''
        newnode = Node(thing)
        if self.__len == 0:
            LL.head = newnode
            LL.tail = newnode
        else:
            newnode.next = LL.head
            LL.head = newnode
        self.__len += 1

    def pop_head(self):
        '''remove the head value, and return it at the same time'''
        if LL.head is None:    # empty list
            return None
        elif LL.head.next is None:    # Single Item in the list
            p = LL.head.holding
            LL.head = None
            self.__len -= 1
            return p
        else:
            p = LL.head.holding
            LL.head = LL.head.next
            self.__len -= 1
            return p

    def insert_at_tail(self, thing):
        '''insert an object at the end of the linked list'''
        if LL.tail is None:
            self.insert_at_head(thing)
        else:
            newnode = Node(thing)
            LL.tail.next = newnode
            LL.tail = newnode
            self.__len += 1
        return None

    @staticmethod
    def getAll():
        '''Walk the list and get the order of things in the list'''
        pointer = LL.head
        str_list = []
        while not pointer is None:
            str_list.append(pointer.holding)
            pointer = pointer.next
        return ''.join(str_list)


    def destroy(self):
        '''destroy everything in the linked list - shouldn't be necessary'''
        while not LL.head is None:
            N = LL.head.next
            LL.head.next = None
            LL.head.holding = None
            LL.head = N
        self.__len = 0
