'''
Created on 2013-01-29

@author: fejes
'''




class Node(object):
    def type(self):
        print ("DoublyLinkedList.Node")
    
    def __init__(self, thing):
        self.holding = thing
        self.next = None
        self.prev = None


class DLL(object):
    '''
    classdocs
    '''
    
    def type(self):
        print ("DoublyLinkedList")
    
    head = None
    tail = None
        
    def __init__(self):        
        self.__len = 0
        DLL.head = None
        DLL.tail = None

    def size(self):
        return self.__len

    ''''thing must be of type Node.
        Adds to the end of the list'''
    def append(self, thing):  
        node = Node(thing)
        if self.__len == 0:
            DLL.head = node
            DLL.tail = node 
        else:
            node.prev = DLL.tail
            DLL.tail.next = node
            DLL.tail = node
        self.__len +=1
    
        ''''thing must be of type Node.
        Adds to the front of the list'''
    def insert_at_head(self, thing):
        newnode = Node(thing)
        if self.__len == 0:
            DLL.head = newnode
            DLL.tail = newnode
        else:
            newnode.next = DLL.head
            DLL.head.prev = newnode
            DLL.head = newnode
        self.__len +=1
    
    def insert_before(self, node, thing):
        #test if first node
        if node == DLL.head:
            DLL.insert_at_head(thing)
            return None
        else:
            newnode = Node(thing)
            newnode.prev = node.prev
            newnode.next = node
            node.prev = newnode
            newnode.prev.next = newnode  
            self.__len +=1  
    
    def insert_after(self, node, thing):
        #test if first node
        if node == DLL.tail:
            DLL.append(self,thing)
            return None
        else:
            newnode = Node(thing)
            newnode.prev = node
            newnode.next = node.next
            node.next = newnode
            newnode.next.prev = newnode  
            self.__len +=1  
    
    def pop_head(self):
        if DLL.head == None:    #empty list
            return None
        elif DLL.head.next == None: #Single Item in the list
            p = DLL.head.holding
            DLL.head = None
            self.__len -=1  
            return p
        else:
            p = DLL.head.holding
            DLL.head = DLL.head.next
            DLL.head.prev = None
            self.__len -=1  
            return p

    
    '''Walk the list and get the order of things in the list'''
    def getAll(self):
        pointer = DLL.head
        str_list = []
        while not pointer == None:
            str_list.append(pointer.holding)
            pointer = pointer.next
        return ''.join(str_list)

    '''destroy everything in the linked list - shouldn't be necessary'''        
    def destroy(self):
        while not DLL.head == None: 
            N = DLL.head.next
            DLL.head.next = None
            DLL.head.prev = None
            DLL.head.holding = None
            DLL.head = N
        self.__len =0
        