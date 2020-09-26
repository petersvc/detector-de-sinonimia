from importlib import util
import unicodedata
import re as regex 
import subprocess
import platform
import json
import os


def check_libs():
    """Verifica se as dependências do programa estão instaladas no computador"""
    if platform.system() == 'Linux':
        if util.find_spec("pip"):  # checa se o pip está instalado
            if util.find_spec("nltk"):
                return True
            else:
                print('A dependência "nltk" não está instalada',end=', ')
                print('sem ela o programa não poderá executar', end=' ')
                print('o algoritimo de estemização', end=', ')
                permission = input('concorda em a instalar? s/n: ')

                if regex.match('^[sS]$', permission):
                    print('\n' + '*' *  5 + ' Tentando importar a biblioteca ' + '*' * 5 + '\n')
                    install_nltk = subprocess.call(['pip3', 'install', 'nltk'])                
                    if install_nltk == 0:  # 0 é igual a True, está instalada
                        import nltk
                        nltk.download('rslp')  # baixa o stemmer português
                        print('dependencia instalada com sucesso')
                        print('Reinicie o programa')
                        exit()
                    else:
                        print('O programa não conseguiu instalar a dependencia "nltk"')
                else:
                    print('o estemizador ficará desabilitado')
                    return

        else:
            print('a dependência "pip" não está instalada')
            permission = input('Concorda em a instalar? s/n: ')
            if regex.match('[sS]', permission):
                install_pip = subprocess.call(['sudo', 'apt', 'install', 'python3-pip'])            
                if install_pip == 0:
                    print('Dependencia "pip" instalada com sucesso')
                    print('Reinicie o programa')
                    exit()  # invoca a função recursivamente para checar as demais dependencias
                else:
                    print('A dependencia "pip" não foi instalada')
            else:
                print('o estemizador ficará desabilitado')
    else:
        print('Não está no linux')

try:
    from nltk.stem import RSLPStemmer
except ModuleNotFoundError:
    print('Módulo "nltk" não encontrado')

def fix_data(resume):
    """Atribui o valor 'null' à strings/células vazias, invoca a
    função normalizer() e remove um prefixo indesejado, presente na primeira coluna da base de dados.
    """
    for i in range(2, len(resume)):
        if resume[i] == '----' or resume[i] == '': 
            resume[i] = 'null'

        if resume[i] != 'null':
            resume[i] = normalizer(resume[i], 'lower')
            
    resume[1] = normalizer(resume[1], 'none')
    
    if resume[0] != '_id': # remove o prefixo "ObjectId contido nas strings das primeiras colunas
        resume[0] = resume[0][9:-1]

def normalizer(string, case_type): 
    """Remove os acentos dos caracteres das strings e as minusculariza ou maiusculariza."""
    result = unicodedata.normalize("NFD", string)
    result = result.encode("ascii", "ignore")
    result = result.decode("utf-8")

    if case_type == 'lower':
        result = result.lower() # minusculariza
    elif case_type == 'upper':
        result = result.lower() # maiusculariza
    
    return result

def damerau_levenshtein(s1, s2):
    """Calcula a distância de Damerau-Levenshtein."""
    len_s1 = len(s1)
    len_s2 = len(s2)

    d = {}
    len_s1 = len(s1)
    len_s2 = len(s2)
    for i in range(-1, len_s1+1):
        d[(i, -1)] = i + 1
    for j in range(-1, len_s2+1):
        d[(-1, j)] = j + 1

    for i in range(len_s1):
        for j in range(len_s2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[i-1, j] + 1,  # Deleta
                d[i, j-1] + 1,  # Insere
                d[i-1, j-1] + cost,  # Substitui
            )

            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[i, j] = min(d[i, j], d[i-2, j-2] + cost)  # transpõe
    return d[len_s1-1, len_s2-1] / max(len_s1, len_s2)

def jaro_distance(string1, string2):
    """Calcula a distância de Jaro."""
    string1_len = len(string1)
    string2_len = len(string2)
 
    if string1_len == 0 and string2_len == 0:
        return 1
 
    match_distance = (max(string1_len, string2_len) // 2) - 1
 
    string1_matches = [False] * string1_len
    string2_matches = [False] * string2_len
 
    matches = 0
    transpositions = 0
 
    for i in range(string1_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, string2_len)
 
        for j in range(start, end):
            if string2_matches[j]:
                continue
            if string1[i] != string2[j]:
                continue
            string1_matches[i] = True
            string2_matches[j] = True
            matches += 1
            break
 
    if matches == 0:
        return 0
 
    k = 0
    for i in range(string1_len):
        if not string1_matches[i]:
            continue
        while not string2_matches[k]:
            k += 1
        if string1[i] != string2[k]:
            transpositions += 1
        k += 1
 
    return ((matches / string1_len) +
            (matches / string2_len) +
            ((matches - transpositions / 2) / matches)) / 3

def tokenizer(data):
    """Divide strings em palavras (tokens)."""
    tokens = []
    
    if type(data) == str and data[-1] == ']':
        tokens = data.split('","')
    if type(data) == str and data[-1] != ']':
        tokens = data.split(' ')
    if type(data) == list:
        for i in range(len(data)): 
            tokens.append(data[i].split(' '))

    return tokens

def cleaner(tokens):
    """Remove caracteres não alfa-numéricos indesejados de strings."""
    for i in range(len(tokens)-1, -1, -1):
        tokens[i] = regex.sub(r'[^,\w]+', ' ', tokens[i]) # substitui por espaço, os caracteres não alfa-numéricos com excessão da vírgula
        if len(tokens[i]) < 2: # strings com tamanho menor q 2, não são palavras válidas ou relevantes...
            del tokens[i] # deleta a string irrelevante que possivelmente é um espaço seguido de espaço
    return tokens

def stopwords(tokens):
    """Função intermediária que invoca a __stopwords()."""
    if type(tokens) == list:  
        for i in range(len(tokens)):
            if tokens[i].find(' ') != -1:
                tokens[i] = tokenizer(tokens[i])
                tokens[i] = __stopwords(tokens[i])
            else:
                tokens[i] = __stopwords(tokens[i])
    return tokens

def __stopwords(tokens):
    """Remove palavras não relevantes das strings."""
    dir_path = os.path.dirname(os.path.abspath(__file__)) # endereço da pasta do programa
    json_path = dir_path + '/stopwords.json'
    result = tokens
    with open(json_path, 'r', encoding='UTF8') as json_file:
        data = json.load(json_file)
        if type(tokens) == list:  
            for i in tokens:
                if regex.match(r"[\d]", i):
                    result.remove(i)
                for key in data:
                    if i == data[key]:
                        result.remove(i)
            return ' '.join(result)
        else:
            for key in data:
                if result == data[key]:
                    result = ''
            return result

    #if len(result)

def stemmer(data):
    """Reduz as palavras das strings monovaloradas aos seus radicais."""
    rslp = RSLPStemmer().stem # estemizador português

    if type(data) == list:
        for i in range(len(data)):
            data[i] = rslp(data[i]) # estemiza a palavra (a reduz ao seu radical/raiz)
    else:
        data = rslp(data)

    return data

def stemmer2(data):
    """Reduz as palavras das strings multivaloradas aos seus radicais."""
    data = tokenizer(data)

    for i in range(len(data)): # percorre o array de strings monovaloradas
        for j in range(len(data[i])): # percorre o array de palavras das strings monovaloradas
            if len(data[i][j]) > 0: # checa se o tamanho da palavra é maior que zero               
                if data[i][j][0] == '[': # verifica se a string da primeira palavra contem o caracter especial '['
                    data[i][j] = data[i][j][2:] # faz a string começar a partir da palavra de fato

                if data[i][j][-1] == ']': # verifica se a string da ultima palavra contem o caracter especial ']'
                    data[i][j] = data[i][j][0:-2] # faz a string terminar no fim da palavra contida nela
                #print(data[i][j])
                data[i][j] = stemmer(data[i][j]) # aplica o stemmer na palavra da string monovalorada extraída da string multivalorada

        data[i] = ' '.join(data[i]) # junta novamente em uma única string as palavras da string monovalorada
    
    return data

def edit_distance(key, temp, options):
    """Invoca sequencialmente as funções:
    tokenizer(), cleaner(), stopwords(), stemmer() e retorna a jaro_distance().
    """
    ed = 0.0
    ed2 = 0.0
    temp = tokenizer(temp) 
    temp = cleaner(temp)
    temp = stopwords(temp)

    if options['stemmer']:
        temp = stemmer2(temp)
    
    if temp[-1] == ']':  # "]" indica que a string é multivalorada (contem várias formações)
        for token in temp:
            ed2 = jaro_distance(key, token)
            ed = max(ed, ed2)
    
    else:
        temp = ' '.join(temp)
        temp = regex.sub(r'[\s][\s]', ' ', temp)
        ed = jaro_distance(key, temp)
    
    #print('2',temp, ed)
    return ed

def prefix_similarity(key, temp, options):
    """Determina se a chave possivelmente existe em uma string
    e se a a mesma é um falso sinônimo da string.
    """
    check = False
    search_path = [] 
    starts = 0 
    index = 0

    for i in range(len(key['tokens'])):
        temp2 = temp[index:] 
        finder = temp2.find(key['tokens'][i][:3])        
        if finder != -1:          
            index += finder
            search_path.append(index)

    similarity = len(search_path) / len(key['tokens'])
    check = similarity >= 0.5     
    
    if check:
        starts = search_path[0]        
        if regex.match(r'[a-zA-Z]', temp[starts-1]) and starts != 0:
            temp = temp[starts:]
            for i in range(len(temp)):
                if regex.match(r'["]', temp[i]):
                    temp = temp[i:]
                    break
                elif i == len(temp) - 3:
                    return 0            
        elif regex.match(r'[\s]', temp[starts-1]) and starts != 0:       
            for i in range(starts-2, 0, -1):
                if regex.match(r'[,"\s]', temp[i]):
                    temp = temp[i:]
                    break                        
                elif i == 1:
                    return 0
        else:
            temp = temp[starts:]
        
        ed = edit_distance(key['string'], temp, options)
        
        if len(key['tokens']) > 1 and similarity > 0.6:
            similarity_bonus = 0.150
            if ed + similarity_bonus > 1:
                ed = 1
            else:
                ed += similarity_bonus
        elif len(key['tokens']) == 1 and similarity > 0.6:
            similarity_bonus = 0.1
            if ed + similarity_bonus > 1:
                ed = 1
            else:
                ed += similarity_bonus
        
        return ed
    else:
        return 0
        
               
