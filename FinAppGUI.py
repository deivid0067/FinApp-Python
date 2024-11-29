from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import uuid
import re
import datetime
import os

users = []
user_db = 'users_db.txt'

# Funções que seriam chamadas para cada opção

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

def fazer_login():
    root.destroy()
    
    login = Tk()
    login.title("Tela de Login")
    login.geometry('500x300')
    
    title = Label(login, text="Bem-vindo à tela de Login", font=("Verdana", "10", "italic", "bold"), fg="red", bg="#d6d6d6")
    title.pack(pady=20)  

    username_or_email_label = Label(login, text="Nome de Usuário ou E-mail:")
    username_or_email_label.pack(pady=5)
    username_or_email = Entry(login, width=30)
    username_or_email.pack(pady=5)

    senha_label = Label(login, text="Digite sua senha:")
    senha_label.pack(pady=5)
    
    senha = Entry(login, width=30, show="*")
    senha.pack(pady=5)

    login_button = Button(login, text="Login", width=20, command=lambda: realizar_login(username_or_email, senha, login))
    login_button.pack(pady=20)

    login.mainloop()

def realizar_login(username_or_email, senha, login_window):
    if not username_or_email.get() or not senha.get():
        messagebox.showerror("Erro", "Por favor, preencha os campos de login e senha.")
        return

    current_user = None

    for user in users:
        authentication = (user['email'] == username_or_email.get() or user['username'] == username_or_email.get()) and user['senha'] == senha.get()
        if authentication:
            current_user = user
            break

    if current_user:
        account(current_user)
        login_window.destroy()  
    else:
        messagebox.showerror("Erro", "Credenciais Inválidas")

def extract(current_user, deposit_values, statement):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for value in deposit_values:
        if value < 0:
            transaction = {
                'type': 'Saque',
                'value': value,
                'user': current_user['username'],
                'id': str(uuid.uuid4()),  
                'date': current_datetime
            }
        else:
            transaction = {
                'type': 'Deposito',
                'value': value,
                'user': current_user['username'],
                'id': str(uuid.uuid4()),  
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
        messagebox.showerror("Erro", 'Saldo insuficiente para realizar o saque.')
    else:
        try:
            if withdrawal_value <= 0:
                raise ValueError("O valor do saque deve ser maior que zero.")

            print(f"Saque de R$ {withdrawal_value} realizado com sucesso.")
            extract(current_user, [-withdrawal_value], statement)

            current_user['saldo'] -= withdrawal_value
            update_balance_label(current_user)

        except ValueError as vew:
            messagebox.showerror("Erro", str(vew))

def deposit(current_user, deposit_value, statement): 
    try:
        if deposit_value <= 0:
            raise ValueError("O valor do depósito deve ser maior do que zero.")

        print(f"Depósito de R$ {deposit_value} realizado com sucesso.")
        extract(current_user, [deposit_value], statement)  

        current_user['saldo'] += deposit_value
        update_balance_label(current_user)  

    except ValueError as vew:
        messagebox.showerror("Erro", str(vew))

def update_balance_label(current_user):
    saldo_label.config(text=f"Saldo Atual: R$ {current_user['saldo']:.2f}")
    atualizar_treeview(current_user)

def atualizar_treeview(current_user):
    for i in tree.get_children():
        tree.delete(i)
    
    statement = load_transactions(current_user['username'])
    for transacao in statement:
        tree.insert('', 'end', values=(transacao['type'], transacao['value'], transacao['date']))

def account(current_user):
    global saldo_label, tree
    statement = []

    conta = Toplevel()
    conta.title(f"Conta de {current_user['username']}")
    conta.geometry('600x500')

    title = Label(conta, text=f"Bem-vindo, {current_user['username']}", font=("Verdana", "10", "italic", "bold"), fg="blue")
    title.pack(pady=20)

    saldo_label = Label(conta, text=f"Saldo Atual: R$ {current_user['saldo']:.2f}", font=("Verdana", "12", "bold"), fg="green")
    saldo_label.pack(pady=10)

    valor_label = Label(conta, text="Digite o valor:")
    valor_label.pack(pady=5)
    valor_entry = Entry(conta, width=30)
    valor_entry.pack(pady=5)

    def depositar():
        try:
            valor = float(valor_entry.get())
            deposit(current_user, valor, statement)
            valor_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor válido para o depósito.")

    def sacar():
        try:
            valor = float(valor_entry.get())
            withdrawal(current_user, valor, statement)
            valor_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor válido para o saque.")

    depositar_button = Button(conta, text="Depositar", width=20, command=depositar)
    depositar_button.pack(pady=5)

    sacar_button = Button(conta, text="Sacar", width=20, command=sacar)
    sacar_button.pack(pady=5)

    sair_button = Button(conta, text="Sair", width=20, command=conta.destroy)
    sair_button.pack(pady=5)

    extrato_label = Label(conta, text="Extrato de Transações", font=("Verdana", "10", "italic", "bold"))
    extrato_label.pack(pady=10)

    columns = ('Tipo de Transação', 'Valor', 'Data')
    tree = ttk.Treeview(conta, columns=columns, show='headings')

    tree.heading('Tipo de Transação', text='Tipo de Transação')
    tree.heading('Valor', text='Valor')
    tree.heading('Data', text='Data')

    tree.pack(pady=20, padx=20)

    atualizar_treeview(current_user)

    conta.mainloop()

def cpf_validation(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    for userCpf in users:
        if userCpf['cpf'] == cpf:
            messagebox.showerror("Erro", "Já existe um Usuário cadastrado com esse CPF!")
            return False

    return True

def email_validation(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def save_account(users):
    user_ids = set()  # Caso haja duplicidade nos dados

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

def create_account():
    user_id = str(uuid.uuid4())

    # Pegando os valores diretamente das entradas sem usar .get()
    username = username_entry.get()
    cpf = cpf_entry.get()
    email = email_entry.get()
    senha = senha_entry.get()

    # Valida os campos
    if username in ['', ' ']:
        messagebox.showerror("Erro", "Você precisa inserir um nome de usuário válido!")
        return

    if not cpf_validation(cpf):
        messagebox.showerror("Erro", "CPF inválido, tente novamente!")
        return

    if not email_validation(email):
        messagebox.showerror("Erro", "E-mail inválido, insira o mesmo corretamente!")
        return

    if not senha.strip():
        messagebox.showerror("Erro", "Você não pode colocar espaços em branco na senha!")
        return


    saldo_inicial = 0.0

    # Adiciona os dados ao banco de dados (ou lista de usuários, por exemplo)
    users.append({
        'id': user_id,
        'username': username,
        'cpf': cpf,
        'email': email,
        'senha': senha,
        'saldo': saldo_inicial
    })

    print(users)

    messagebox.showinfo("Sucesso", "Conta criada com sucesso!")

    save_account(users)

    # Limpa os campos após a criação
    username_entry.delete(0, END)
    cpf_entry.delete(0, END)
    email_entry.delete(0, END)
    senha_entry.delete(0, END)

def criar_conta():
    cadastro = Tk()
    cadastro.title("Tela de Cadastro")
    cadastro.geometry('500x450')

    title = Label(cadastro, text="Bem-vindo à tela de Cadastro", font=("Verdana", "10", "italic", "bold"), fg="blue", bg="#d6d6d6")
    title.pack(pady=20)

    username_label = Label(cadastro, text="Nome de Usuário:")
    username_label.pack(pady=5)
    global username_entry
    username_entry = Entry(cadastro, width=30)
    username_entry.pack(pady=5)

    cpf_label = Label(cadastro, text="CPF:")
    cpf_label.pack(pady=5)
    global cpf_entry
    cpf_entry = Entry(cadastro, width=30)
    cpf_entry.pack(pady=5)

    email_label = Label(cadastro, text="Email:")
    email_label.pack(pady=5)
    global email_entry
    email_entry = Entry(cadastro, width=30)
    email_entry.pack(pady=5)


    senha_label = Label(cadastro, text="Senha:")
    senha_label.pack(pady=5)
    global senha_entry
    senha_entry = Entry(cadastro, width=30, show="*")
    senha_entry.pack(pady=5)


    create_button = Button(cadastro, text="Criar Conta", width=20, command=create_account)
    create_button.pack(pady=20)

    return_menu = Button(cadastro, text="Retornar ao Menu", width=20, command=cadastro.destroy)
    return_menu.pack(pady=5)

    cadastro.mainloop()

def relatorio_usuarios():

    relatorio = Tk()
    relatorio.title('Relatorio de Usuários')
    relatorio.geometry('1400x400')

    title = Label(relatorio, text="Relatorio de Usuários", font=("Verdana", "10", "italic", "bold"), fg="blue", bg="#d6d6d6")
    title.place(x=0, y=0)

    columns = ('ID', 'Username', 'CPF', 'Email', 'Senha', 'Saldo')
    tree = ttk.Treeview(relatorio, columns=columns, show='headings')

    tree.heading('ID', text='ID')
    tree.heading('Username', text='Username')
    tree.heading('CPF', text='CPF')
    tree.heading('Email', text='Email')
    tree.heading('Senha', text='Senha')
    tree.heading('Saldo', text='Saldo')

    for user in users:
        tree.insert('', 'end', values=(user['id'], user['username'], user['cpf'], user['email'], user['senha'], user['saldo']))

    tree.pack(pady=30, padx=30)

    btn_sair_relatorio = Button(relatorio, text="Sair", width=20, command=relatorio.destroy)
    btn_sair_relatorio.pack(pady=30, padx=30)

    relatorio.mainloop()

def search():
    cpf_busca = username_user.get()  
    for user in users:
        if user['cpf'] == cpf_busca:
            # Limpar as entradas anteriores
            for row in tree.get_children():
                tree.delete(row)
            # Inserir os dados encontrados na Treeview
            tree.insert("", "end", values=(user['username'], user['email'], user['saldo']))
            break
    else:
        print("Usuário não encontrado.")

def pesquisar_usuario():
    pesquisa = Tk()
    pesquisa.title('Pesquisar Usuário')
    pesquisa.geometry('700x450')
    
    
    search_label = Label(pesquisa, text="CPF")
    search_label.pack(pady=5)

    
    global username_user
    username_user = Entry(pesquisa, width=30)
    username_user.pack(pady=5)

    
    title = Label(pesquisa, text="Relatório de Usuários", font=("Verdana", 10, "italic", "bold"), fg="blue", bg="#d6d6d6")
    title.place(x=0, y=0)

    
    columns = ('Username', 'Email', 'Saldo')
    global tree
    tree = ttk.Treeview(pesquisa, columns=columns, show='headings')

    tree.heading('Username', text='Username')
    tree.heading('Email', text='Email')
    tree.heading('Saldo', text='Saldo')

    tree.pack(pady=30, padx=30)

    
    btn_pesquisar = Button(pesquisa, text="Pesquisar", width=20, command=search)
    btn_pesquisar.pack(side=LEFT, padx=10, pady=10)  # Alinhado à esquerda

    btn_sair_relatorio = Button(pesquisa, text="Sair", width=20, command=pesquisa.destroy)
    btn_sair_relatorio.pack(side=LEFT, padx=10, pady=10)  # Alinhado à esquerda

    pesquisa.mainloop()

def excluir_conta():
    cpf_user = cpf_entry.get()  
    user_to_delete = None

    for user in users:
        if user['cpf'] == cpf_user:
            user_to_delete = user
            break

    if user_to_delete:
        confirmation = messagebox.askquestion("Confirmar exclusão", 
                                             f"Tem certeza que deseja excluir a conta de {user_to_delete['username']} ({user_to_delete['cpf']})?")
        if confirmation == 'yes':
            users.remove(user_to_delete)
            save_account(users)

            user_statement_file = f"extrato_{user_to_delete['username']}.txt"
            if os.path.exists(user_statement_file):
                os.remove(user_statement_file)

            messagebox.showinfo("Sucesso", f"Usuário {user_to_delete['username']} ({user_to_delete['cpf']}) excluído com sucesso!")
        else:
            messagebox.showinfo("Cancelado", "Exclusão cancelada!")
    else:
        messagebox.showerror("Erro", "Usuário não encontrado!")
    
def excluir_usuario():
    excluir = Tk()
    excluir.title("Exclusão de Conta")
    excluir.geometry('400x200')
    
    cpf_label = Label(excluir, text="Digite seu CPF para excluir sua conta:")
    cpf_label.pack(pady=10)

    global cpf_entry
    cpf_entry = Entry(excluir, width=30)
    cpf_entry.pack(pady=10)

    btn_excluir = Button(excluir, text="Excluir Conta", width=20, command=excluir_conta)
    btn_excluir.pack(padx=10, pady=10)

    btn_cancelar = Button(excluir, text="Cancelar", width=20, command=excluir.destroy)
    btn_cancelar.pack( padx=10, pady=10)

def search_and_update_password(cpf_entry, new_password_entry, top_window):
    searchAlteration = cpf_entry.get()  
    found = False  
    
    for searchCPF in users:
        if searchCPF['cpf'] == searchAlteration:
            newPassword = new_password_entry.get()  
            searchCPF['senha'] = newPassword
            messagebox.showinfo("Sucesso", f"A senha de {searchCPF['username']} foi atualizada com sucesso!")
            save_account(users)
            found = True  # Marca que o CPF foi encontrado
            top_window.destroy()  
            break 

    if not found:
        messagebox.showerror("Erro", "CPF não encontrado, operação cancelada!")

def open_password_update_window():
    top_window = Toplevel()
    top_window.title("Alterar Senha")
    top_window.geometry("400x300")

    cpf_label = Label(top_window, text="Digite o CPF do Usuário:")
    cpf_label.pack(pady=10)

    cpf_entry = Entry(top_window, width=30)
    cpf_entry.pack(pady=5)

    new_password_label = Label(top_window, text="Digite a nova senha:")
    new_password_label.pack(pady=10)

    new_password_entry = Entry(top_window, width=30, show="*")  # "show" mascara a senha
    new_password_entry.pack(pady=5)

    update_button = Button(top_window, text="Alterar Senha", width=20, 
                              command=lambda: search_and_update_password(cpf_entry, new_password_entry, top_window))
    update_button.pack(pady=20)

    top_window.mainloop()

def sair():
    root.quit()

root = Tk()
root.title("FinBank")

ascii_art = '''
███████╗██╗███╗   ██╗██████╗  █████╗ ███╗   ██╗██╗  ██╗
██╔════╝██║████╗  ██║██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝
█████╗  ██║██╔██╗ ██║██████╔╝███████║██╔██╗ ██║█████╔╝ 
██╔══╝  ██║██║╚██╗██║██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ 
██║     ██║██║ ╚████║██████╔╝██║  ██║██║ ╚████║██║  ██╗
╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
'''
label_ascii = Label(root, text=ascii_art, font=("Courier", 10), padx=10, pady=10)
label_ascii.pack()

btn_login = Button(root, text="Fazer Login", width=20, command=fazer_login)
btn_login.pack(pady=5)

btn_criar_conta = Button(root, text="Criar Conta", width=20, command=criar_conta)
btn_criar_conta.pack(pady=5)

btn_relatorio = Button(root, text="Relatório de Usuários", width=20, command=relatorio_usuarios)
btn_relatorio.pack(pady=5)
 
btn_pesquisar = Button(root, text="Pesquisar por CPF", width=20, command=pesquisar_usuario)
btn_pesquisar.pack(pady=5)

btn_excluir = Button(root, text="Excluir Usuário", width=20, command=excluir_usuario)
btn_excluir.pack(pady=5)

btn_excluir = Button(root, text="Alterar Senha", width=20, command=open_password_update_window)
btn_excluir.pack(pady=5)

btn_sair = Button(root, text="Sair", width=20, command=sair)
btn_sair.pack(pady=5)


root.mainloop()
