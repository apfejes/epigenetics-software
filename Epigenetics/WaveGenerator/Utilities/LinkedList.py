'''
Created on 2013-01-29

@author: fejes
'''




class Node(object):
    def type(self):
        print ("LinkedList.Node")

    def __init__(self, thing):
        self.holding = thing
        self.next = None


class LL(object):
    '''
    classdocs
    '''

    def type(self):
        print ("LinkedList")

    def __init__(self):
        self.__len = 0
        LL.head = None
        LL.tail = None

    def size(self):
        return self.__len

    ''''thing must be of type Node.
        Adds to the end of the list'''
    def append(self, thing):
        node = Node(thing)
        if self.__len == 0:
            LL.head = node
            LL.tail = node
        else:
            node.prev = LL.tail
            LL.tail.next = node
            LL.tail = node
        self.__len += 1

        ''''thing must be of type Node.
        Adds to the front of the list'''
    def insert_at_head(self, thing):
        newnode = Node(thing)
        if self.__len == 0:
            LL.head = newnode
            LL.tail = newnode
        else:
            newnode.next = LL.head
            LL.head = newnode
        self.__len += 1

    def pop_head(self):
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
        if LL.tail is None:
            self.insert_at_head(thing)
        else:
            newnode = Node(thing)
            LL.tail.next = newnode
            LL.tail = newnode
            self.__len += 1
        return None

    '''Walk the list and get the order of things in the list'''
    def getAll(self):
        pointer = LL.head
        str_list = []
        while not pointer is None:
            str_list.append(pointer.holding)
            pointer = pointer.next
        return ''.join(str_list)

    '''destroy everything in the linked list - shouldn't be necessary'''
    def destroy(self):
        while not LL.head is None:
            N = LL.head.next
            LL.head.next = None
            LL.head.holding = None
            LL.head = N
        self.__len = 0
