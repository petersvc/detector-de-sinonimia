class Node:
    def __init__(self, key):
        """Método construtor da classe."""
        self.key = key
        self.parent = None # pai
        self.lc = None # left child
        self.rc = None # right child
        self.h = 1 # height
        self.bf = 0 # balance factor

    def insert_l(self, key):
        """Insere dados nos nós filhos esquerdos e define seus nós pais."""
        self.lc = Node(key)
        self.lc.parent = self

    def insert_r(self, key):
         """Insere dados nos nós filhos direitos e define seus nós pais."""
         self.rc = Node(key)
         self.rc.parent = self
    
    def get_data(self):
        """Retorna os dados contidos nos nós."""
        return self.key
    
    def get_lc(self):
        """Retorna os nós filhos esquerdos."""
        return self.lc
    
    def get_rc(self):
        """Retorna os nós filhos direitos."""
        return self.rc
    
    def set_lc(self, node):
        """Atribui dados/valores em nós filhos esquerdos."""
        self.lc = node

    def set_rc(self, node):
        """Atribui dados/valores em nós filhos direitos."""
        self.rc = node

    def set_parent(self, node):
        """Atribui dados/valores em nós pais."""
        self.parent = node

    def __str__(self):
        return str(self.key)