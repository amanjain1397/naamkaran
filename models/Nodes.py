class Node():

    def __init__(self, ch = ''):
        self.character = ch
        self.neighbors = []
    
    def get_character(self):
        return self.character
        
    def get_neighbors(self):
        return self.neighbors    

class TrieNode():
    
    def __init__(self, vocab):
        self.alphabet_mapping = vocab
        self.children = ['' for i in range(len(vocab))]
        
    def get_children(self, alpha):
        return self.children[self.alphabet_mapping[alpha]]
    
    def set_children(self, alpha, childNode):
        self.children[self.alphabet_mapping[alpha]] = childNode
