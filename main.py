import re as regex

from aux import check_libs
from tree import ResumeTree


resumes = ResumeTree()

if check_libs():
    resumes.options['stemmer'] = True
    resumes.check_options('multivalue')

print('\n', '*' * 110)
print('\n\n', ' ' * 56, '- CURRÍCULOS -\n')

menu = '\n- MENU - \n\n'
menu += '(M) MENU\n(C) CARREGAR DADOS\n(E) ESTATÍSTICAS DA BASE\n'
menu += '(P) MOSTRAR TODOS OS CURRÍCULOS\n(B) BUSCA\n(O) OPÇÕES\n'
menu += '(S) SOBRE\n(Q) SAIR'

print(menu)

option = input('\nDigite a opção desejada: ')

while regex.match("^[qQ]$", option) == None:
    try:
        assert regex.match("^[qQcCpPbBeEmMoOsS]$", option)

        if regex.match("^[cC]$", option):
            resumes.load()
        elif regex.match("^[pP]$", option):
            print('\n- CURRÍCULOS -\n')
            resumes.inorder()
        elif regex.match("^[bB]$", option):
            print('\n- RESULTADO DA PESQUISA -\n')
            resumes.find()
        elif regex.match("^[eE]$", option):
            print('\n- ESTATÍSTICAS DA BASE -\n')
            resumes.resume_tree_info() 
        elif regex.match("^[sS]$", option):
            print('\n- SOBRE -\n')
            resumes.about()          
        elif regex.match("^[oO]$", option):
            resumes.options_func()
            print(menu)
        elif regex.match("^[mM]$", option):
            print(menu)
    except AssertionError:
        print('Opção inválida')
    finally:
        option = input('\nDigite a opção desejada: ')