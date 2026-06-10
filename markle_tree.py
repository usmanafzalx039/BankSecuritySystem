import hashlib
import math

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def isFull(self):
        return self.left and self.right

    def __str__(self):
        return self.data

    def isLeaf(self):
        return ((self.left == None) and (self.right == None))

class merkleTree:
    def __init__(self):
        self.root = None
        self._merkleRoot = ''
  
    def __returnHash(self, x):
        return (hashlib.sha256(x.encode()).hexdigest())
   
    def makeTreeFromArray(self, arr):
        
        def __noOfNodesReqd(arr):
            x = len(arr)
            return (2*x - 1)

        def __buildTree(arr, root, i, n): 
            if i < n: 
                temp = Node(str(arr[i]))  
                root = temp  
                root.left = __buildTree(arr, root.left, 2 * i + 1, n)  
                root.right = __buildTree(arr, root.right, 2 * i + 2, n) 
            return root
   
        def __addLeafData(arr, node):
            if not node:
                return
            
            __addLeafData(arr, node.left)
            if node.isLeaf():
                if arr:
                    # Pop from end, so arr must be reversed beforehand
                    node.data = self.__returnHash(arr.pop())
            else:
                node.data = ''
            __addLeafData(arr, node.right)

        if not arr:
            return

        nodesReqd = __noOfNodesReqd(arr)
        nodeArr = [num for num in range(1, nodesReqd+1)]
        
        # --- CRITICAL FIX: Pass all 4 arguments ---
        self.root = __buildTree(nodeArr, None, 0, nodesReqd)
        
        # Reverse array so pop() works in correct order
        import copy
        arr_copy = copy.deepcopy(arr)
        arr_copy.reverse()
        __addLeafData(arr_copy, self.root)
  
    def inorderTraversal(self, node):
        if not node:
            return
        self.inorderTraversal(node.left)
        print(node)
        self.inorderTraversal(node.right)
 
    def calculateMerkleRoot(self):
        def __merkleHash(node):
            if node.isLeaf():
                return node
            
            left = __merkleHash(node.left)
            right = __merkleHash(node.right)
            
            # Handle empty children safely
            left_data = left.data if left else ''
            right_data = right.data if right else ''
            
            node.data = self.__returnHash(left_data + right_data)
            return node
        
        if not self.root:
            return ''

        merkleRoot = __merkleHash(self.root)
        self._merkleRoot = merkleRoot.data
        return self._merkleRoot 

    def getMerkleRoot(self):
        return self._merkleRoot

    def verifyUtil(self, arr1):
        hash1 = self.getMerkleRoot()
        new_tree = merkleTree()
        new_tree.makeTreeFromArray(arr1)
        new_tree.calculateMerkleRoot()
        hash2 = new_tree.getMerkleRoot()
        if hash1 == hash2 :
            return True
        else:
            return False