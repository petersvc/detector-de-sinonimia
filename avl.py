from node import Node


class AVL_Tree:
    
    def __init__(self):
        """Método construtor da classe."""
        self.__root = None
        self.__apical_leaf = None # ultima folha da árvove
        self.__size = 0 # contador de nodes
        self.rb = 0 # contador de rebalanceamentos
        self.__words = 0 # contador de palavras

    def insert(self, key, degree):
        """Método indermediário que invoca o método de inserção recursivo __insert()
        e conta a quantidade de palavras presente na base de dados.
        """
        if self.__root != None:
            self.__insert(key, self.__root, degree)        
        else:
            self.__root = Node(key)

        for col in key[1:]:
            self.__words += 1

            for i in range(len(col)):
                if col[i] == ' ':
                    self.__words += 1

        self.__size += 1

    def __insert(self, key, node, degree):
        """Método recursivo que insere dados em nós filhos esquerdos ou direitos."""
        if key[degree] < node.key[degree]: # inserção à esquerda
            if node.lc != None:
                self.__insert(key, node.lc, degree)
            else:
                node.insert_l(key)
        else: # inserção à direita
            if node.rc != None:
                self.__insert(key, node.rc, degree)
            else:
                node.insert_r(key)
        
        self.update_h(node) # atualiza a altura do nó
        self.update_bf(node) # atualiza o fator de equilibrio do nó
        
        if abs(node.bf) > 1: # verifica o fator de balanço
            self.rb += 1
            self.rebalance(node) # equilibra a arvore
              
    def rebalance(self, node):
        """Equilibra a árvore."""
        if node.bf > 1: # bf positivo = sub arvore esquerda está mais pesada
            if node.lc.bf < 0: # bf do filho é negativo = rotação dupla à direita
                self.rotate_l(node.lc) # rotação à esquerda
                return self.rotate_r(node) # rotação à direita
            else:               
                return self.rotate_r(node) # rotação à direita
            
        elif node.bf < -1: # bf negativo = sub arvore direita está mais pesada
            if node.rc.bf > 0: # rotação direita e esquerda
                self.rotate_r(node.rc) # rotação à direita
                return self.rotate_l(node) # rotação à esquerda
            else:
                return self.rotate_l(node) # rotação à esquerda
        else:
            return node

    def rotate_r(self, z):
        """Rotaciona o nó para a direita."""
        sub_root = z.parent
        y = z.lc
        t3 = y.rc
        y.rc = z
        z.parent = y
        z.lc = t3

        if t3 != None: 
            t3.parent = z

        y.parent = sub_root

        if y.parent == None:
            self.__root = y
        else:
            if y.parent.lc == z:
                y.parent.lc = y
            else:
                y.parent.rc = y

        self.update_h(z)
        self.update_h(y)
        self.update_bf(z)
        self.update_bf(y)       
    
    def rotate_l(self, z):
        """Rotaciona o nó para a esquerda."""
        sub_root = z.parent 
        y = z.rc
        t2 = y.lc
        y.lc = z
        z.parent = y
        z.rc = t2

        if t2 != None:
            t2.parent = z

        y.parent = sub_root

        if y.parent == None: 
            self.__root = y
        else:
            if y.parent.lc == z:
                y.parent.lc = y
            else:
                y.parent.rc = y

        self.update_h(z)
        self.update_h(y)
        self.update_bf(z)
        self.update_bf(y)
    
    def inorder(self):
        """Método indermediário que invoca o método recursivo '__inorder().'"""
        return self.__inorder(self.__root)
              
    def __inorder(self, node):
        """Método recursivo que exibe os dados dos nós em ordem."""
        if node != None:
            if self.__apical_leaf.rc == None:
                self.__inorder(node.lc)
                print(f'{node.key}')
                self.__inorder(node.rc)
                return
            elif node.get_data()[1] != self.__apical_leaf.rc.get_data()[1]:
                self.__inorder(node.lc)
                print(f'{node.key}')
                self.__inorder(node.rc)
                return
    
    def update_apical_leaf(self):
        """Método indermediário que invoca o método recursivo __update_apical_leaf()."""
        return self.__update_apical_leaf(self.__root, 'ZZ')        

    def __update_apical_leaf(self, node, key):
        """Define qual é o ultimo nó em ordem da árvore."""
        if node != None:
            self.__apical_leaf = node            
            if node.get_data()[1] < key: 
                self.__update_apical_leaf(node.rc, key)            
            else:
                self.__update_apical_leaf(node.lc, key)

    def tree_info(self):
        """Exibe as informações relevantes da árvore."""
        infos = 'Root: ' + str(self.get_root().get_data()[1])
        infos += '\nApical leaf: ' + str(self.get_apical_leaf().get_data()[1])
        infos += '\nAltura da árvore: ' + str(self.tree_h())
        infos += '\nNº de nodes (currículos): ' + str(self.__size)
        infos += '\nNº de palavras: ' + str(self.__words)
        infos += '\nMax_nodes(h): ' + str(self.max_nodes())
        infos += '\nMin_nodes(h): ' + str(self.min_nodes(self.tree_h()))
        infos += '\nRebalanceamentos: ' + str(self.rb) + '\n'
        print(infos)

    def min_nodes(self, h):
        """Retorna qual a quantidade mínima de nodes que a árvore pode ter
        para manter seu equilibrio como árvore AVL."""
        if h <= 1:
            return h
        else:
            return 1 + (self.min_nodes(h-1) + self.min_nodes(h-2))
    
    def max_nodes(self):
        """Retorna qual a quantidade máxima de nodes que a árvore pode ter
        para manter seu equilibrio como árvore AVL."""
        return (2 ** self.tree_h()) - 1

    def tree_h(self):
        """Retorna a altura da árvore."""
        return self.get_h(self.__root) - 1

    def get_h(self, node):
        """Retorna a altura do nó."""
        if node != None:
            return node.h        
        else:
            return 0

    def update_h(self, node):
        """Atualiza a altura do nó."""
        if node != None:
            node.h = 1 + max(self.get_h(node.lc), self.get_h(node.rc))
            return
        return 0

    def update_bf(self, node):
        """Atualiza o fator de equilíbrio do nó."""
        if node != None:
            node.bf = self.get_h(node.lc) - self.get_h(node.rc)
            return
        return 0

    def get_root(self):
        """Retorna o nó raiz da árvore."""
        return self.__root

    def get_apical_leaf(self):
        """Retorna o ultimo nó em ordem da árvore."""
        return self.__apical_leaf

    def get_size(self):
        """Retorna o tamanho da árvore."""
        return self.__size
    
    def get_words(self):
        """Retorna a quantidade de palavras armazenadas na árvore."""
        return self.__words

    def __str__(self):
        return str(self.__root.key)