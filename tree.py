from time import time
import re as regex
import csv
import os

from aux import fix_data, normalizer, tokenizer
from aux import edit_distance, stemmer
from aux import prefix_similarity, stopwords
from avl import AVL_Tree
from node import Node


class ResumeTree: 
    """Pseudo árvore formada por 4 árvores AVLs conectadas entre si, que contêm 
    os currículos lattes dos professores do IFPB.
    """
    def __init__(self):
        """Construtor da classe."""      
        self.__root = None
        self.__apical_leaf = None
        self.__size = 0
        self.__words = 0
        self.__tree = {}  # sub-árvores AVL
        self.count = {'result': 0, 'not_null': 0, 'general': 0, 'no_qualifications': [[], 0]}       
        self.options = {'stemmer': False, 'ed_max': 0.8}
        
    def options_func(self):
        """Fornece acesso à ativação/desativação do filtro de pesquisa e o estemizador,
        assim como exibe o estado dos mesmos e a distância de edição máxima.   
        """        
        space = (' ' * 4)  # identação do sub menu
        menu = '\n' + space +  'CONFIGURAÇÕES - \n\n'
        menu += space + '(S) STEMMER\n'
        menu += space + '(D) DETALHES\n' + space + '(Q) SAIR'

        print(menu)

        option = input('\n' + space + 'Digite a opção desejada: ')

        while regex.match("^[qQ]$", option) == None:
            try:
                assert regex.match("^[qQsSdD]$", option)

                if regex.match("^[sS]$", option):
                    self.options['stemmer'] ^= True
                    print(space + 'Stemmer:', self.options['stemmer'])                
                elif regex.match("^[dD]$", option):
                    print(space + 'Stemmer:', self.options['stemmer'])
                    print(space + 'DE max:', self.options['ed_max'])

                self.check_options('multivalue')

            except AssertionError:
                print(space + 'Opção inválida')            
            finally:
                option = input('\n' + space + 'Digite a opção desejada: ')
                if regex.match("^[qQ]$", option):
                    print(space + 'Stemmer:', self.options['stemmer'])
                    #print(space + 'DE max:', self.options['ed_max'])
                    print(space + 'Saiu')

    def check_options(self, mode):
        """Verifica as configurações escolhidas e otimiza o valor da distancia de edição máxima."""
        if mode == "multivalue":          
            if self.options['stemmer']:
                self.options['ed_max'] = 0.82 
            else:
                self.options['ed_max'] = 0.87
        else:  # "mode: monovalue"      
            if self.options['stemmer']:
                self.options['ed_max'] = 0.78
            else:
                self.options['ed_max'] = 0.8        

    def load(self):
        """Carrega os dados utilizados pelo programa."""
        start = time()  # marca o horario em que o método começou a ser executado
        try:

            if self.__root == None:
                dir_path = os.path.dirname(os.path.abspath(__file__))  # endereço da pasta do programa
                csv_path = dir_path + '/cp.csv'  # endereço da base de dados original
                csv2_path = dir_path + '/cp2.csv'  # endereço da base de dados normalizada

                try:
                    self.__read_database(csv2_path)
                except IOError:
                    print('O arquivo "cp2.csv" não existe, o programa', end=' ')
                    print('tentará criá-lo')
                    self.__create_base(csv_path, csv2_path)
                    self.__read_database(csv2_path)

            else: print('Os dados já foram carregados')

        except IOError:
            print('O arquivo "cp.csv" não existe, assegure-se', end=' ')
            print('de tê-lo salvo na mesma pasta do programa')
        
        end = time()  # marca o horario em que o método foi finalizado 
        exec_time = str(round((end - start) * 1000)) + 'ms' # tempo o método demorou para ser executado
        print('Tempo de execução:', exec_time)

    def __create_base(self, csv_path, csv2_path):
        """Cria a base de dados normalizada a partir da base de dados original, caso não exista."""
        with open(csv_path, "r", encoding='UTF8') as csv_file:
            data = csv.reader(csv_file)
            with open(csv2_path, 'w') as csv2_file: 
                for row in data:
                    resume = [row[0], row[1], row[4], row[6], row[8], row[10]]  # colunas julgadas relevantes
                    fix_data(resume)
                    csv2_writer = csv.writer(csv2_file, delimiter=',')
                    csv2_writer.writerow(resume)

        print('Arquivo criado com sucesso')

    def __read_database(self, csv2_path):
        """Carrega a base de dados normalizada, cria as sub-àrvores e atualiza os atributos da classe."""
        with open((csv2_path), "r", encoding='UTF8') as csv2_file:
            data2 = csv.reader(csv2_file)
            next(data2)  # pula o header da planilha

            self.__tree['Doutorado'] = AVL_Tree()
            self.__tree['Mestrado'] = AVL_Tree() 
            self.__tree['Especializacao'] = AVL_Tree()
            self.__tree['Graduacao'] = AVL_Tree()

            for row in data2:
                self.__insert(row)
                self.count['general'] = 0                     
       
        self.__update_size() 
        self.__update_words()
        self.__merge_trees()

        print('\nDados carregados com sucesso')
        #print(self.count['no_qualifications'])

    def __insert(self, key):
        """Direciona e insere o currículo na sua devida sub-árvore."""         
        for i in range(len(key)):
            if key[i] == 'null':
                self.count['general'] += 1

        if self.count['general'] == 4:  # Verifica se as quatro colunas são nulas ou seja
            self.count['no_qualifications'][0].append(key)  # se a pessoa não tem nenhuma qualificação pesquisável
            self.count['no_qualifications'][1] += 1  # se sim, não será incluída na árvore
            return        
        # O segundo parametro do método insert(param1, param2) informa qual indice ditará a ordem
        # da sub-árvore, no entando devido a natureza dos dados e objetivo do programa só é 
        # possível ordena-los com base no indice [0] ou [1], respectivamente objectID e Nome.
        elif key[5] != 'null':
            return self.__tree['Doutorado'].insert(key, 1)        
        elif key[4] != 'null':
            return self.__tree['Mestrado'].insert(key, 1)        
        elif key[3] != 'null' or key[2] == 'null':
            return self.__tree['Especializacao'].insert(key, 1)
        else:
            self.__tree['Graduacao'].insert(key, 1)     

    def inorder(self):
        """Invoca o método recursivo que exibe os currículos em ordem."""
        start = time()
        self.__inorder(self.__root)
        #self.__tree['Graduacao'].inorder()
        end = time()
        exec_time = str(round((end - start) * 1000)) + 'ms'
        print('Tempo de execução:', exec_time)

    def __inorder(self, node):
        """Percorre as árvores recursivamente e exibe seus dados em ordem."""
        if node != None:
            self.__inorder(node.lc)
            print(node.key)
            self.__inorder(node.rc)

    def find(self):
        """Captura a chave que será pesquisada e invoca o método recursivo de busca __find()."""
        space = (' ' * 4)  # identação do sub menu
        menu = '\n' + space +  'QUALIFICAÇÕES - \n\n'
        menu += space + '(1) GRADUAÇÃO\n'
        menu += space + '(2) ESPECIALIZAÇÃO\n'
        menu += space + '(3) MESTRADO\n'
        menu += space + '(4) DOUTORADO\n'
        print(menu)
        degree = input('Digite a qualificação: ')

        while regex.match('^[1234]$', degree) == None:
            print('Opção inválida, digite um dos números acima')
            degree = input('Digite a qualificação: ')
            
        degree = int(degree) + 1 # a primeira coluna relevante para pesquisa é a 2 por isso degree + 1
        key_input = input('Digite a area do conhecimento: ')
        
        while regex.match('[a-zA-Z][a-zA-Z][a-zA-Z]', key_input) == None:
            print('Opção inválida, digite um dos números acima')
            key_input = input('Digite a area do conhecimento: ')

        start = time()
        key = {'string': key_input}
        
        if self.__size > 0:
            if degree == 5:
                header_degree = 'Doutorado'
            if degree == 4:
                header_degree = 'Mestrado'
            if degree == 3:
                header_degree = 'Especializacao'
            if degree == 2:
                header_degree = 'Graduacao'

            print('\nQualificação: ' + header_degree)
            print('Area do Conhecimento: ' + key['string'])
           
            key['string'] = normalizer(key['string'], 'lower') 
            key['tokens'] = tokenizer(key['string'])
            key['tokens'] = stopwords(key['tokens'])
            key['string'] = ' '.join(key['tokens'])
            key['string'] = regex.sub(r'[\s][\s]', ' ', key['string'])
            key['tokens'] = tokenizer(key['string'])
            
            if self.options['stemmer']:         
                key['tokens'] = stemmer(key['tokens'])
                key['string'] = ' '.join(key['tokens'])

            if len(key['tokens']) == 1:  # Caso a chave seja formada por apenas uma palavra
                self.check_options('monovalue')  # alterada para diminuir o número de falsos sinonimos

            print('\n\n\nDE' +  ' ' * 10 , end='')
            print('DOCENTE' + " " * 50 + 'AREA DE FORMAÇÃO\n')

            cursor = self.__tree[header_degree].get_root()
            
            self.__find(key, cursor, degree)           

            print('\nA pesquisa encontrou', self.count['result'], 'currículo(s)')
            print('\nNão nulos:', self.count['not_null'])

            self.count['result'] = 0
            self.count['not_null'] = 0
            
        else: print('Não há currículos registrados') 

        end = time()
        exec_time = str(round((end - start) * 1000)) + 'ms'
        print('\nTempo de execução:', exec_time)

    def __find(self, key, cursor, degree):
        """Busca recursivamente dados sinonímicos à chave de pesquisa."""
        if cursor != None:
            temp = cursor.get_data()
            # O bloco de if e elifs logo abaixo possui condicionais que verificam se o dado no cursor é
            # equivalente ao primeiro dado armazenado na sub-árvore, o nó raiz (root)
            # dessa forma, os currículos são exibidos agrupados por qualificações
            if temp[1] == self.__tree['Graduacao'].get_root().get_data()[1]:
                space = ' ' * 12
                print('\n' + space + 'Graduados* \n')
            if temp[1] == self.__tree['Especializacao'].get_root().get_data()[1]:
                space = ' ' * 12
                print('\n' + space + 'Especializados* \n')
            if temp[1] == self.__tree['Mestrado'].get_root().get_data()[1]:
                space = ' ' * 12
                print('\n' + space + 'Mestres* \n')
            if temp[1] == self.__tree['Doutorado'].get_root().get_data()[1]:
                space = ' ' * 12
                print('\n' + space + 'Doutores* \n')

            self.__find(key, cursor.lc, degree)
            
            temp = temp[degree]
            
            if temp != 'null': 
                self.count['not_null'] += 1                
                ed = prefix_similarity(key, temp, self.options)                        
                
                if ed >= self.options['ed_max']:                                                                             
                    self.count['result'] += 1                                  
                    temp = cursor.get_data()[degree]                           
                    space = ' ' * 8
                    space2 = ' ' * (57 - (len(cursor.get_data()[1])))
                    result = "%.2f" % round(ed, 2)
                    result += space + cursor.get_data()[1] 
                    result += space2 + cursor.get_data()[degree]
                    print(result)
                
            self.__find(key, cursor.rc, degree)
            
    def resume_tree_info(self):
        """Exibe informações sobre os dados registrados e sobre a estrutura de dados utilizada."""
        if self.__size > 0:
            print('Avl Tree: Graduacao')
            self.__tree['Graduacao'].tree_info()
            print('Avl Tree: Especializacao')
            self.__tree['Especializacao'].tree_info()
            print('Avl Tree: Mestrado')
            self.__tree['Mestrado'].tree_info()
            print('Avl Tree: Doutorado')
            self.__tree['Doutorado'].tree_info()        
            print('Total de nodes: '+ str(self.__size))
            print('Total de palavras: '+ str(self.__words))
        else:
            print('A base de dados ainda não foi carregada')

    def __merge_trees(self):
        """Conecta as sub-árvores entre si."""        
        self.__tree['Graduacao'].update_apical_leaf() 
        self.__tree['Especializacao'].update_apical_leaf()
        self.__tree['Mestrado'].update_apical_leaf()
        self.__tree['Doutorado'].update_apical_leaf()        
        # definição dos ponteiros que criarão a conexão entre as sub-árvores
        pointer0 = self.__tree['Graduacao'].get_root()
        pointer1 = self.__tree['Graduacao'].get_apical_leaf()
        pointer2 = self.__tree['Especializacao'].get_root()
        pointer3 = self.__tree['Especializacao'].get_apical_leaf() 
        pointer4 = self.__tree['Mestrado'].get_root()
        pointer5 = self.__tree['Mestrado'].get_apical_leaf()
        pointer6 = self.__tree['Doutorado'].get_root() 
        pointer7 = self.__tree['Doutorado'].get_apical_leaf()

        pointer1.set_rc(pointer2)  # Conecta a sub-árvore Graduação com a Especialização 
        pointer3.set_rc(pointer4)  # ...Especialização com a Mestrado
        pointer5.set_rc(pointer6)  # ...Mestrado com a Doutorado
        
        self.__root = pointer0
        self.__apical_leaf = pointer7

    def __update_size(self):
        """Atualiza o tamanho da árvore."""
        size1 = self.__tree['Graduacao'].get_size()
        size2 = self.__tree['Especializacao'].get_size()
        size3 = self.__tree['Mestrado'].get_size()
        size4 = self.__tree['Doutorado'].get_size()

        self.__size = size1 + size2 + size3 + size4
    
    def __update_words(self):
        """Atualiza a quantidade de palavras encontradas nos currículos."""
        words1 = self.__tree['Graduacao'].get_words()
        words2 = self.__tree['Especializacao'].get_words()
        words3 = self.__tree['Mestrado'].get_words()
        words4 = self.__tree['Doutorado'].get_words()

        self.__words = words1 + words2 + words3 + words4

    def about(self):
        """Exibe informações sobre o programa."""
        print('''
        Título da aplicação: Framework de Detecção de Sinonímia
        Autor: Peter Costa
        Tema 2: Coleção de currículos lattes de docentes do IFPB
        Dependências: pip3, python3 e o módulo nltk 
        \n
        - Após o teste de 4 medidas de similaridade, sendo elas, Jaro, Damerau-Levenshtein,
        Levenshtein e coseno da similaridade, a Jaro foi adotada como medida para este projeto.
        As demais mesmo otimizadas para alterar dinamicamente o limite máximo da distancia de
        edição, apresentaram um número considerável de falsos positivos e as vezes como no caso
        da Damerau e Levenshetein, falsos positivos apresentaram uma similaridade maior do que
        palavras com valor sinonímico maior, exemplo: ciencias economicas apresentou mais similaridade
        com ciencias sociais do que com economia. De acordo com o artigo do Peter Christen (2006)
        e outros artigos meta-analíticos que comparam várias medidas de similaridade, a Jaro possui
        uma eficiente taxa de precisão para comparação de nomes ou frases curtas e é até 6x
        mais leve que a Damerau, além disso,a etapa de transposição de caracteres presentes na
        intercessão das strings é mais relevante no calculo da similaridade.\n
        Foi criado um filtro nomeado de "prefix_similarity" que vefifica a existencia das três primeiras letras
        ou as duas primeiras seguidas de um ".", para aplicar a Jaro somente em strings com grande
        propabilidade de serem sinonímicas, porém isso trouxe problemas de falsos sinônimos outra vez
        como: "física" e "educação física", ou economia, e biblioteconomia.
        Para lidar com isso foi implementado no filtro uma etapa que checa se anterior ao indice do prefixo há um
        espaço ou uma letra, caso haja, o mesmo toma medidas para modificar o indice inicial da string.
        O algoritmo analisador sinonímico desse projeto então combina a Jaro, um filtro inspirado nos 
        melhoramentos da Jaro Wrinkler e na medida do Coseno da Similaridade e o estemizador de palavras
        presente no módulo de processamento de linguagem natural "nltk".
        ''')

    def __str__(self):
        return str(self.__root.get_data())
    