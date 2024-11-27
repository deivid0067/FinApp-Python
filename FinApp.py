#Projeto Conta Corrente
#Deivid Menezes da Silva - UMC
#Engenharia de Software - NOTURNO

#------------------------ Libs ------------------------# 

import os
import sys
import uuid
import textwrap
import re
import datetime
from prettytable import PrettyTable

#------------------------ Globals ------------------------# 
users = []
user_db = 'users_db.txt'

def clear_console():
    input('\nPressione Enter para finalizar...')
    os.system('cls' if os.name == 'nt' else 'clear')

def load_accounts(users):
    user_ids = set()

    try:
        with open(user_db, 'r') as db:
            for linha in db:
                dados = linha.rstrip().split(', ')
                if len(dados) == 6:
                    user_id, username, cpf, email, senha, saldo = dados
                    if user_id not in user_ids:
                        users.append({
                            'id': user_id,
                            'username': username,
                            'cpf': cpf,
                            'email': email,
                            'senha': senha,
                            'saldo': float(saldo)
                        })
                        user_ids.add(user_id)
    except FileNotFoundError:
        print("Banco de dados não encontrado, criando um novo arquivo...")
load_accounts(users)


def login():
    print('\nBem-vindo ao FinBank. Para fazer o login, digite seu nome de usuário ou e-mail e sua senha.')

    while True:
        username_or_email = input('Digite o nome de usuário ou email: ')
        senha = input('Digite sua senha: ')
        current_user = None
        for user in users:
            authentication = (user['email'] == username_or_email or user['username'] == username_or_email) and user[
                'senha'] == senha
            if authentication:
                current_user = user
                break
        if current_user:
            account(current_user)
            break
        else:
            print('\n Credenciais Inválidas')


def extract(current_user, deposit_values, statement):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for deposit_value in deposit_values:

        transaction = {
            'type': 'Deposito',
            'value': deposit_value,
            'user': current_user['username'],
            'id': str(uuid.uuid4()),  # Id da transação
            'date': current_datetime
        }

        statement.append(transaction)
        save_transaction(transaction)

def load_transactions(username):
    user_statement_file = f"extrato_{username}.txt"
    transactions = []

    try:
        with open(user_statement_file, 'r') as file:
            for line in file:
                transaction_data = line.strip().split(',')

                if len(transaction_data) == 5:
                    transaction = {
                        'id': transaction_data[0],
                        'type': transaction_data[1],
                        'value': float(transaction_data[2]),
                        'user': transaction_data[3],
                        'date': transaction_data[4]
                    }
                    transactions.append(transaction)

    except FileNotFoundError:
        print(f"Arquivo de extrato para o usuário {username} não encontrado.")

    return transactions

def save_transaction(transaction):
    user_statement_file = f"extrato_{transaction['user']}.txt"

    with open(user_statement_file, 'a') as file:
        line = f"{transaction['id']},{transaction['type']},{transaction['value']},{transaction['user']},{transaction['date']}\n"
        file.write(line)

def withdrawal(current_user, withdrawal_value, statement):

    if current_user['saldo'] < withdrawal_value:
        print('Seu saldo é insuficiente, não é possivel realizar um saque.')
    else:
        try:
            if withdrawal_value <= 0:
                raise ValueError("O valor do saque deve ser maior do que zero.")

            print(f"Depósito de R$ {withdrawal_value} realizado com sucesso.")
            extract(current_user, [-withdrawal_value], statement)

            current_user['saldo'] -= withdrawal_value
            save_account(users)

        except ValueError as vew:
            print(f'Erro: {ve}')

def deposit(current_user, deposit_value, statement): 

    try:
        if deposit_value <= 0:
            raise ValueError("O valor do depósito deve ser maior do que zero.")

        print(f"Depósito de R$ {deposit_value} realizado com sucesso.")
        extract(current_user, [deposit_value], statement)  # Passa o valor como lista.

        current_user['saldo'] += deposit_value
        save_account(users)  # Salva o usuário com o saldo novo.

    except ValueError as ve:
        print(f'Erro: {ve}')

def account(current_user):
    statement = []

    option = input(textwrap.dedent(f'''\nBem-vindo a aplicação FinApp!, {current_user['username']}
    
    Seu Saldo: {current_user['saldo']}
    
    Selecione a opção desejada:

    1 - Saque
    2 - Depósito
    3 - Extrato Bancário
    4 - Sair da Aplicação

    '''))
    
    if option not in ['1', '2', '3', '4']:

        print('\nSelecione uma opção Válida')
    elif option == '1':
        try:
            withdrawal_value = float(input('\n Digite um valor para realizar o saque'))
            withdrawal(current_user, withdrawal_value, statement)
        except ValueError:
            print("Erro: Por favor, digite um valor válido para o depósito (número).")


    elif option == '2':
        try:
            deposit_value = float(input('\nDigite o valor do depósito: '))
            deposit(current_user, deposit_value, statement)
        except ValueError:
            print("Erro: Por favor, digite um valor válido para o depósito (número).")

    elif option == '3':
        transactions = load_transactions(current_user['username'])  # Carrega as transações

        os.system('cls')

        print('\n-------------------- EXTRATO BANCARIO --------------------')

        if transactions:
            table_extract = PrettyTable()
            table_extract.field_names = ["ID", "Tipo", "Valor (R$)", "Data"]

            # Adiciona todas as transações à tabela
            for transaction in transactions:
                table_extract.add_row([transaction['id'], transaction['type'],
                                       f"R$ {transaction['value']:.2f}", transaction['date']])

            print(table_extract)  # Exibe a tabela inteira de transações

            # Pergunta se deseja continuar ou sair
            optionContinue = input('\nAperte Enter, se deseja retornar para o Menu principal, caso contrario pressione outra tecla')
            if optionContinue in ['', ' ']:
                account(current_user)  # Volta ao menu principal
            else:
                print('Finalizando')

        else:
            print('Nenhuma transação, Encontrada!')

    elif option == '4':
        print('teste')

def cpf_validation(cpf):
    cpf = re.sub(r'[^0-9.-]', '', cpf)
    if len(cpf) != 14:
        return False

    if cpf == cpf[0] * 11:
        return False

    for userCpf in users:
        if userCpf['cpf'] == cpf:
            print('\nJá existe um usuário com esse CPF')
            return False

    return True

def email_validation(email):
    regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(regex, email))

def delete_user():
    print("\nPara excluir sua conta, por favor, digite seu CPF")

    cpf_user = input("Digite o nome de usuário ou email para confirmação: ")

    user_to_delete = None

    for user in users:
        if user['cpf'] == cpf_user :
            user_to_delete = user # Variavel de delete, recebe o valor do usuário atual.
            break

    if user_to_delete:
        confirmation = input(f"Tem certeza que deseja excluir a conta de {user_to_delete['username'],user_to_delete['cpf']} (sim/não)? ")

        if confirmation.lower() == 'sim':

            users.remove(user_to_delete)

            save_account(users)

            user_statement_file = f"extrato_{user_to_delete['username']}.txt"
            if os.path.exists(user_statement_file):
                os.remove(user_statement_file)

            print(f"\nUsuário {user_to_delete['username'],user_to_delete['cpf']} excluído com sucesso!")
        else:
            print("\nExclusão cancelada!")
    else:
        print("\nUsuário não encontrado!")

def create_account():
    print('\nSeja Bem-vindo ao FinBank, Preencha as informações abaixo para criar sua conta.')

    user_id = str(uuid.uuid4())

    while True:
        username = input('\nDigite seu nome: ')
        if username in ['', ' ']:
            print('\nVocê precisa inserir um nome de usuário válido!')
            continue

        cpf = input('\nDigite seu CPF: ')
        if not cpf_validation(cpf):
            print('\nCPF inválido, tente novamente!')
            continue

        email = input('\nInsira um Email: ')
        if not email_validation(email):
            print('\nE-mail inválido, insira o mesmo corretamente!')
            continue

        senha = input('\nDigite uma senha: ')
        if not senha.strip():
            print('\n Você não pode colocar espaços em branco na senha! ')
            continue

        break

    # Saldo inicial
    saldo_inicial = 0.0

    users.append({
        'id': user_id,
        'username': username,
        'cpf': cpf,
        'email': email,
        'senha': senha,
        'saldo': saldo_inicial
    })

    input(textwrap.dedent('''
    ========================================================
    |               Conta criada com sucesso!              |
    ========================================================

    Pressione Enter pra retornar ao inicio!
    '''))

    clear_console()
    save_account(users)
    menu()

def save_account(users):
    user_ids = set()  # Para armazenar os IDs dos usuários já salvos

    with open(user_db, 'w') as db:
        for user_information in users:
            # Verificar se o ID do usuário já foi gravado
            if user_information['id'] not in user_ids:
                linha = (f"{user_information['id']}, "
                         f"{user_information['username']}, "
                         f"{user_information['cpf']}, "
                         f"{user_information['email']}, "
                         f"{user_information['senha']}, "
                         f"{user_information['saldo']}\n")  # Salva o saldo junto
                db.write(linha)
                user_ids.add(user_information['id']) # Caso ele duplique o Id

def menu():

    while True:

        print('''
███████╗██╗███╗   ██╗██████╗  █████╗ ███╗   ██╗██╗  ██╗
██╔════╝██║████╗  ██║██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝
█████╗  ██║██╔██╗ ██║██████╔╝███████║██╔██╗ ██║█████╔╝ 
██╔══╝  ██║██║╚██╗██║██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ 
██║     ██║██║ ╚████║██████╔╝██║  ██║██║ ╚████║██║  ██╗
╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                                                       ''')

        selectOption = input(textwrap.dedent('''
    Bem Vindo ao FinBank. Selecione uma das opções para continuar:

    (1) - Fazer Login
    (2) - Criar Conta
    (3) - Relatório de Usuários Cadastrados
    (4) - Pesquisar usuarios por CPF
    (5) - Excluir Usuário 
    (6) - Sair da aplicação
    ===> '''))

        if selectOption not in ['1', '2', '3', '4', '5', '6']:
            print('\nEscolha uma opção válida!')
        elif selectOption == '1':
            login()
            break
        elif selectOption == '2':
            create_account()
            break
        elif selectOption == '3':
            for user in users:
                print(user)
            clear_console()
        elif selectOption == '4':

            search = input('Digite o CPF Pra receber informações do Usuário')
            for searchUser in users:
                if searchUser['cpf'] == search:
                    print(textwrap.dedent(f'''
                        Pesquisa de Usuário Concluída!

                        |{searchUser['username']} | {searchUser['email']} | {searchUser['saldo']} | <----- Resultado
                        '''))
            clear_console()        
            
        elif selectOption == '5':
            delete_user()
            sys.exit(0)
menu()
