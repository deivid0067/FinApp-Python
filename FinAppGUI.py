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
    
    # Título centralizado
    title = Label(login, text="Bem-vindo à tela de Login", font=("Verdana", "10", "italic", "bold"), fg="red", bg="#d6d6d6")
    title.pack(pady=20)  

    # Campo de Nome de Usuário ou E-mail
    username_or_email_label = Label(login, text="Nome de Usuário ou E-mail:")
    username_or_email_label.pack(pady=5)
    username_or_email = Entry(login, width=30)
    username_or_email.pack(pady=5)

    # Campo de Senha
    senha_label = Label(login, text="Digite sua senha:")
    senha_label.pack(pady=5)
    
    senha = Entry(login, width=30, show="*")
    senha.pack(pady=5)

    # Botão de Login
    login_button = Button(login, text="Login", width=20)
    login_button.pack(pady=20)

    login.mainloop()

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

def sair():
    root.quit()

# Criação da janela principal
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

# Adicionando as opções de menu com botões
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

btn_sair = Button(root, text="Sair", width=20, command=sair)
btn_sair.pack(pady=5)


root.mainloop()
