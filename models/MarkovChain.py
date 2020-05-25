from models.Nodes import Node, TrieNode

class MarkovChain():
    
    def __init__(self, order, corpus):
        self.order = order
        self.vocab = {v:k for (k,v) in enumerate(list(set(corpus)))}
        self.duplicates = TrieNode(self.vocab)
        self.start =  Node()
        self.mapper = {}
    
    def addWordToChain(self, word):
        self.addToDuplicatesTrie(word, self.duplicates)
        previous = self.start
        key = ''
        
        for alpha in word:
            ch = alpha
            key += ch
            if(len(key) > self.order):
                key = key[1:]
            
            newNode = self.mapper.get(key, '') 
            if not newNode:
                newNode = Node(ch)
                self.mapper[key] = newNode
                
            previous.neighbors.append(newNode)
            previous = newNode
        #link to end node.
        previous.neighbors.append('')
    
    def addToDuplicatesTrie(self, word, duplicates):
        if len(word) > 1:
            self.addToDuplicatesTrie(word[1:], duplicates)

        currentNode = duplicates
        for alpha in word:
            childNode = currentNode.get_children(alpha)

            if not childNode:
                childNode = TrieNode(self.vocab)
                currentNode.set_children(alpha, childNode)

            currentNode = childNode     
    
    def isDuplicate(self, word, duplicates):
        #word = word.lower()
        currentNode = duplicates

        for alpha in word:
            childNode = currentNode.get_children(alpha)

            if not childNode:
                return False
            currentNode = childNode

        return True

    def returnDuplicates(self):
        return self.duplicates
    
    def generateWord(self, minLength = 0, maxLength = -1, allowDuplicates = True,
                    maxAttempts = 25):
        
        import numpy as np
        
        attempts = 0
        while True:
            repeat = False
            nextNodeIndex = int(np.floor(np.random.random() * len(self.start.neighbors)))
            currentNode = self.start.neighbors[nextNodeIndex]
            word = ''
            while ((type(currentNode)!= str) & ((maxLength < 0) | (len(word) <= maxLength))):
                word+=currentNode.character
                nextNodeIndex = int(np.floor(np.random.random() * len(currentNode.neighbors)))
                currentNode = currentNode.neighbors[nextNodeIndex]

            if (((maxLength >= 0) & (len(word) > maxLength)) | (len(word) < minLength)):
                repeat = True
            
            attempts += 1
            if not (repeat | ((not allowDuplicates) & (attempts < maxAttempts) & self.isDuplicate(word, self.duplicates))):
                break
        
        if attempts >= maxAttempts:
            raise Exception('Unable to generate a word with the given parameters after '+attempts)
        
        
        return word