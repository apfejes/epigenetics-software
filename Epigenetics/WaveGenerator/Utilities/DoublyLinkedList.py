'''
Created on 2013-01-29

@author: fejes
'''


class Node(object):
    '''A simple node object used by the doubly linked list'''

    @staticmethod
    def type():
        '''print out DoulblyLinkedList.Node when asked the type'''
        print ("DoublyLinkedList.Node")

    def __init__(self, thing):
        '''initialize the linked list.'''
        self.holding = thing
        self.next = None
        self.prev = None


class DLL(object):
    '''
    A doubly linked list implementation.
    '''

    @staticmethod
    def type():
        '''print out DoulblyLinkedList when asked the type'''
        print ("DoublyLinkedList")

    def __init__(self):
        self.__len = 0
        DLL.head = None
        DLL.tail = None

    def size(self):
        '''get length of list'''
        return self.__len

    def append(self, thing):
        ''''thing must be of type Node.   Adds to the end of the list'''
        node = Node(thing)
        if self.__len == 0:
            DLL.head = node
            DLL.tail = node
        else:
            node.prev = DLL.tail
            DLL.tail.next = node
            DLL.tail = node
        self.__len += 1


    def insert_at_head(self, thing):
        ''''thing must be of type Node.  Adds to the front of the list'''
        newnode = Node(thing)
        if self.__len == 0:
            DLL.head = newnode
            DLL.tail = newnode
        else:
            newnode.next = DLL.head
            DLL.head.prev = newnode
            DLL.head = newnode
        self.__len += 1

    def insert_before(self, node, thing):
        '''method for inserting an object (thing) before a specific node'''
        # test if first node, then use convenience method:#
        if node == DLL.head:
            DLL.insert_at_head(thing)
            return None
        else:
            newnode = Node(thing)
            newnode.prev = node.prev
            newnode.next = node
            node.prev = newnode
            newnode.prev.next = newnode
            self.__len += 1

    def insert_after(self, node, thing):
        ''' test if last node, then use convenience method.'''
        if node == DLL.tail:
            DLL.append(self, thing)
            return None
        else:
            newnode = Node(thing)
            newnode.prev = node
            newnode.next = node.next
            node.next = newnode
            newnode.next.prev = newnode
            self.__len += 1

    def pop_head(self):
        '''remove the head of the list, and return it's value'''
        if DLL.head is None:    # empty list
            return None
        elif DLL.head.next is None:    # Single Item in the list
            p = DLL.head.holding
            DLL.head = None
            self.__len -= 1
            return p
        else:
            p = DLL.head.holding
            DLL.head = DLL.head.next
            DLL.head.prev = None
            self.__len -= 1
            return p


    @staticmethod
    def getAll():
        '''Walk the list and get the order of things in the list'''
        pointer = DLL.head
        str_list = []
        while not pointer is None:
            str_list.append(pointer.holding)
            pointer = pointer.next
        return ''.join(str_list)


    def destroy(self):
        '''destroy everything in the linked list - shouldn't be necessary'''
        while not DLL.head is None:
            N = DLL.head.next
            DLL.head.next = None
            DLL.head.prev = None
            DLL.head.holding = None
            DLL.head = N
        self.__len = 0
