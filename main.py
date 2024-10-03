import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from functools import partial

verde_opet = '#174311'
laranja_opet = '#F24F13'

def img2botao(imagem, canvas, comando, spacing=0):
        imagem = Image.open(f"images/{imagem}.png")
        imagem = imagem.resize((250, 45))
        photoimage = ImageTk.PhotoImage(imagem)
        canvas.configure(highlightthickness=0)
        button = tk.Button(canvas.frame_botoes, image=photoimage, compound=tk.TOP, bg='white', highlightthickness=0, borderwidth=0)
        button.image = photoimage  # Armazena a imagem para evitar garbage collection
        if spacing > 0:
            button.place(relx=0, rely=0, y=0)
        else:
            button.pack(fill=tk.X, expand=True)
        button.pack(fill=tk.X, expand=True)
        button.bind('<Button-1>', lambda event: comando())

def show_custom_messagebox(root, title, message, geometry=("300x150")):
    # Cria uma nova janela de diálogo
    dialog = tk.Toplevel(root)
    dialog.title(title)

    # Define o tamanho inicial da janela
    dialog.geometry(geometry)

    # Adiciona uma label para a mensagem
    label = tk.Label(dialog, text=message, wraplength=400)
    label.pack(padx=10, pady=10)

    # Adiciona um botão para fechar a janela
    button = tk.Button(dialog, text="OK", command=dialog.destroy)
    button.pack(pady=(0, 10))

    # Faz a janela modal, bloqueando a interação com a janela principal
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

def create_connection():
    #Conexão com o banco de dados MySQL
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'root',
        database = 'renault'
    )
    return connection

def convert_tuplelist_to_array(tuple_list, index=0):
    array = [list(item) for item in tuple_list]
    result_array = [risco[index] for risco in array]

    return result_array

def convert_tuplelist_to_dict(tuple_list):
    # Usa dict comprehension para converter a lista de tuplas em dicionário
    dicionario = {chave: valor for chave, valor in tuple_list}
    return dicionario

def convert_to_int(tuple_list):
    #Conversor de tupla de 1 digito em int ex: (2,) 🠞 2 (int)
    if len(tuple_list) == 1 and len(tuple_list[0]) == 1:
        return tuple_list[0][0]
    else:
        raise ValueError("Input must be a list containing a single tuple with a single integer.")

def convert_to_str(tuple_list):
    return tuple_list[0][0]

def check_array_same_value(*arrays):
    # Verifica se a lista está vazia ou contém apenas um array
    if not arrays or len(arrays) == 1:
        return True

    # Compara cada array com o primeiro
    primeiro_array = arrays[0]
    return all(sorted(array) == sorted(primeiro_array) for array in arrays)

def default_values_column(id_objetivo):
    # Cria 3 riscos com nomes aleatorios
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            riscos = ['Relações de negócios', 'ESG', 'TI', 'Finanças', 'Produção']

            for risco in riscos:
                cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('{risco}', {id_objetivo})")
                conn.commit()

                cursor.execute(f"INSERT INTO impacto_probabilidade (id_objetivo_origem, nome_risco_origem, impacto, probabilidade, nivel) VALUES ({id_objetivo}, '{risco}', 0, 0, 0)")
                conn.commit()

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
    finally:
        if conn.is_connected():
            conn.close()

def create_tables():
    # Criação das tabelas objetivos, riscos e pesos
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `objetivos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_objetivo` varchar(75) NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `riscos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_risco` varchar(75) DEFAULT NULL,
            `id_objetivo_origem` int NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `pesos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_combinacao` varchar(75) DEFAULT NULL,
            `peso_combinacao` int NOT NULL,
            `id_objetivo_origem` int DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `impacto_probabilidade` (
        `id` int NOT NULL AUTO_INCREMENT,
        `id_objetivo_origem` INT NOT NULL,
        `nome_risco_origem` varchar(75) NOT NULL,
        `impacto` INT NOT NULL,
        `probabilidade` INT NOT NULL,
        `nivel` INT NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.close()

class telaObjetivos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.h = "600" #v
        self.w = "800" #v
        self.tamanho_tela = f'{self.w}x{self.h}' #v
        self.title("Objetivos")
        self.geometry(self.tamanho_tela)
        self.resizable(False, False)

        verde_opet = '#174311'
        laranja_opet = '#F24F13'

        #self.frameObjetivos = tk.Frame(self)
        #self.frameObjetivos.pack(expand=True)

        self.canvas = tk.Canvas(self, bg='white', width=self.w, height=self.h)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.retangulo_cabecalho = self.canvas.create_rectangle(0, 0, self.w, 50, fill=verde_opet, outline=verde_opet)

        self.titulo_cabecalho = self.canvas.create_text(int(self.w)//2, 25, text="Gestão de Riscos", font=('Open Sans', 12), fill='white')

        #nao ta mostrando mas da pra clicar kkkk
        #self.img_xis = img2botao("images/setaXis.png", 20, 20, self.canvas, int(self.w) - 30, 25, self.destroy)

        self.frame_botoes = tk.Frame(self.canvas, bg = 'white')
        self.frame_botoes.place(relx=0.25 , rely=0.75, relwidth=0.5, relheight=0.2)
        
        img2botao('botaoobjetivos', self, lambda: JanelaAddObjetivo(self))
        img2botao('botaoriscos', self, lambda : JanelaAddRisco(self))

        #self.main_frame = tk.Frame(self.canvas, bg='white')
        #self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)

        self.objetivos = self.carregaObjetivos()
        self.ticados = []
        self.atualizaObjetivos()

        self.botaoProximo = tk.Button(self.canvas, text="🡆", command=self.excluiResto)
        self.botaoProximo.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def adicionarRisco(self):
        JanelaAddRisco(self)

    def carregaObjetivos(self):
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT id, nome_objetivo FROM objetivos"
        cursor.execute(query)
        objetivos = cursor.fetchall()
        conn.close()

        objetivos_array = []

        for item in objetivos:
            objetivos_array.append(list(item))

        return objetivos_array

    def atualizaObjetivos(self):
        self.objetivos = self.carregaObjetivos()

        self.frame_objetivos = tk.Frame(self.canvas, bg='white')
        self.frame_objetivos.place(relx=0.35, rely=0.35, relwidth=0.40, relheight=0.35)

        self.ticados = []

        y_pos = 0
        for _, objetivo in self.objetivos:
            taTicado = tk.BooleanVar(value=False)
            checkbox = tk.Checkbutton(self.frame_objetivos, text=f"{objetivo.capitalize()}", variable=taTicado, bg='white', highlightthickness=0)
            checkbox.grid(row=y_pos, column=0, sticky="w", padx=75)
            self.ticados.append(taTicado)
            y_pos += 1

    def adicionaObjetivo(self):
        JanelaAddObjetivo(self)
        self.atualizaObjetivos()

    def excluiResto(self):
        self.ticados = [objetivo for objetivo, taTicado in zip(self.objetivos, self.ticados) if taTicado.get()]

        self.ticados_id = []

        if len(self.ticados) == 0:
            show_custom_messagebox(self, "Erro", "Selecione ao menos um objetivo", "300x100")
            self.atualizaObjetivos()
            return

        infos = []

        for tick in self.ticados:
            self.ticados_id.append(tick[0])

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {tick[0]}")
            all_info = cursor.fetchall()
            transform_to_list = [item for final_info in all_info for item in final_info]
            infos.append(transform_to_list)
            conn.close()

        if not check_array_same_value(*infos):
            full_str = "Os objetivos possuem riscos diferentes: "

            for i in range(len(self.ticados_id)):
                full_str += f"\nRisco: {self.ticados[i][1]} - {infos[i]}"

            self.ticados = []
            self.atualizaObjetivos()

            show_custom_messagebox(self, "Erro de conflito", full_str, "400x150")
            return

        self.escolha_prox_tela()

    def wrong_data(self):
        messagebox.showwarning("showwarning", "Dados insuficientes")

    def escolha_prox_tela(self):
        self.ticados = []
        self.atualizaObjetivos()
        JanelaProximaTela(self)

class JanelaProximaTela(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Escolha sua ação")
        verde_opet = '#174311'
        laranja_opet = '#F24F13'
        self.config(bg=verde_opet)
        self.geometry("350x250")
        self.parent = parent

        telas_disponiveis = ['AHP', 'Matriz de Risco']

        self.lb_telas = Listbox(self)
        for telas in telas_disponiveis:
            self.lb_telas.insert(END, telas)
        self.lb_telas.select_set(0)
        self.lb_telas.pack()

        Button(self, text="Confirmar", command=self.confirmar_tela, bg=laranja_opet).pack()

        self.transient(self.parent)
        self.wait_visibility()
        self.grab_set()
        self.parent.wait_window(self)

    def confirmar_tela(self):
            tela = self.lb_telas.get(ACTIVE)
            self.nova_tela(tela)

    def nova_tela(self, tela):
        self.parent.destroy()

        if tela.lower().replace(' ', '') == "ahp":
            telaPeso(self.parent.ticados_id)
        elif tela.lower().replace(' ', '') == "matrizderisco":
            telaMatriz(self.parent.ticados_id)

class JanelaAddRisco(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Adicionar Risco")
        self.parent = parent

        verde_opet = '#174311'
        laranja_opet = '#F24F13'

        self.config(bg=verde_opet)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM objetivos")
        self.rowcount = len(cursor.fetchall())
        conn.close()

        self.show_page()

        self.transient(self.parent)
        self.wait_visibility()
        self.grab_set()
        self.parent.wait_window(self)

    def show_page(self):
        if self.rowcount > 0:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nome_objetivo FROM objetivos")
            objetivos_query = cursor.fetchall()
            conn.close()

            verde_opet = '#174311'
            laranja_opet = '#F24F13'

            objetivos_array = [list(item) for item in objetivos_query]
            nomes_objetivos = [risco[0] for risco in objetivos_array]

            lista_objetivos = nomes_objetivos
            Label(self, text="Objetivos", bg=verde_opet).pack(padx=100)
            self.lb_objetivos = Listbox(self, selectmode=tk.BROWSE, exportselection=False)
            for objetivo in lista_objetivos:
                self.lb_objetivos.insert(END, objetivo)
                self.lb_objetivos.bind('<<ListboxSelect>>', self.on_change)
            self.lb_objetivos.select_set(0)
            self.lb_objetivos.pack()

            self.atualiza_altura_listbox(self.lb_objetivos)

            Label(self, text="Riscos", bg=verde_opet).pack()
            self.lb_riscos = Listbox(self, selectmode=tk.BROWSE, exportselection=False)
            self.update_risks(self.lb_objetivos.get(ACTIVE))

            self.entryRisco = Entry(self, fg="gray")
            self.entryRisco.insert(0, "Digite um novo risco...")
            self.entryRisco.bind("<FocusIn>", self.on_entry_click)
            self.entryRisco.bind("<FocusOut>", self.on_focusout)
            self.entryRisco.pack(pady=5)

            self.botaoAdicionarRisco = tk.Button(self, text="Adicionar/Remover", command=self.adicionarRisco, bg=laranja_opet)
            self.botaoAdicionarRisco.pack(pady=10)
        else:
            self.geometry("300x100")
            Label(self, text="Você não possui objetivos cadastrados").pack()

    def atualiza_altura_listbox(self, listbox):
            # Obtém o número de itens
            num_itens = listbox.size()
            # Define a altura da Listbox, limitando a um máximo de 6
            altura = num_itens
            listbox.config(height=altura)
    
    def clear_window(self):
        # Remove todos os itens da Listbox de riscos
        self.lb_riscos.delete(0, END)

    def update_risks(self, nome_obj):

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{nome_obj}'")
        id_response = cursor.fetchall()
        id_response = convert_to_int(id_response)
        cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {id_response}")
        riscos_response = cursor.fetchall()
        conn.close()

        nome_riscos = convert_tuplelist_to_array(riscos_response)

        for riscos in nome_riscos:
            self.lb_riscos.insert(END, riscos)
        self.lb_riscos.pack()
        self.lb_riscos.select_set(0)

        self.atualiza_altura_listbox(self.lb_riscos)


    def on_change(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            data = widget.get(index)
            self.clear_window()
            self.update_risks(data)


    def adicionarRisco(self):
        objetivo_marcado = self.lb_objetivos.get(ACTIVE)

        novo_risco = self.entryRisco.get()
        if objetivo_marcado == "" or novo_risco.replace(" ", "") == "" or novo_risco == "Digite um novo risco...":
            string = ""
            if objetivo_marcado == "":
                string = "Você precisa marcar um objetivo"
                show_custom_messagebox(self, "Erro", string)
            else:
                self.delete_risk(self.lb_riscos.get(ACTIVE), self.lb_objetivos.get(ACTIVE))

            return

        #pegando o id do objetivo da lista
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{objetivo_marcado}'")
        id_objetivo = cursor.fetchall()
        id_objetivo = convert_to_int(id_objetivo)
        self.id_objetivo = id_objetivo

        if self.check_risk_exists(novo_risco):
            show_custom_messagebox(self, "Erro", "Já existe um risco com esse nome")
            return
        
        if novo_risco == "Digite um novo risco...":
            show_custom_messagebox(self, "Erro", "Coloque um nome para seu risco")
            return

        cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('{novo_risco}', {id_objetivo})")
        cursor.execute(f"INSERT INTO impacto_probabilidade (id_objetivo_origem, nome_risco_origem, impacto, probabilidade, nivel) VALUES ({id_objetivo}, '{novo_risco}', 0, 0, 0)")
        conn.commit()
        conn.close()
        self.destroy()

    def delete_risk(self, risk, nome_obj):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{nome_obj}'")
        id_response = cursor.fetchall()
        id_response = convert_to_int(id_response)
        cursor.execute(f"DELETE FROM riscos WHERE nome_risco = '{risk}' AND id_objetivo_origem = {id_response}")
        conn.commit()
        conn.close()
        
        self.destroy()
        return

    def check_risk_exists(self, risk):

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE nome_risco = '{risk}' AND id_objetivo_origem = {self.id_objetivo}")
        cursor.fetchall()
        row = cursor.rowcount
        conn.close()

        return row > 0
    
    def on_entry_click(self, event):
        if self.entryRisco.get() == "Digite um novo risco...":
            self.entryRisco.delete(0, "end") 
            self.entryRisco.config(fg='black') 

    def on_focusout(self, event):
        if self.entryRisco.get() == "":
            self.entryRisco.insert(0, "Digite um novo risco...")  
            self.entryRisco.config(fg='gray') 

class JanelaAddObjetivo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Objetivos")
        self.parent = parent

        verde_opet = '#174311'
        laranja_opet = '#F24F13'

        self.config(bg=verde_opet)
        # parte dos objetivos

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_objetivo FROM objetivos")
        obj_response = cursor.fetchall()
        conn.close()

        obj_id_response = convert_tuplelist_to_array(obj_response, 0)
        obj_nome_response = convert_tuplelist_to_array(obj_response, 1)

        for i, obj in enumerate(obj_nome_response, start=1):
            frame = Frame(self, bg='white', bd=1, relief='solid')
            frame.grid(row=i, column=0, padx=4, pady=5, sticky='ew')
            Label(frame, text=obj, font='green', bg='white').pack(side='left', padx=5)
            Button(frame, text="X", command=partial(self.removerObjetivo, obj_id_response[i-1]), bg=laranja_opet).pack(side='right', padx=4)


        self.entryObjetivo = Entry(self, fg="gray")
        self.entryObjetivo.insert(0, "Digite um novo objetivo...")
        self.entryObjetivo.bind("<FocusIn>", self.on_entry_click)
        self.entryObjetivo.bind("<FocusOut>", self.on_focusout)
        self.entryObjetivo.grid(row=len(obj_nome_response)+2, column=0, pady=10)


        self.botaoAdicionar = tk.Button(self, text="Adicionar", command=self.adicionarObjetivo, bg=laranja_opet)
        self.botaoAdicionar.grid(row=len(obj_nome_response)+3, column=0, pady=10)

        self.transient(self.parent)
        self.wait_visibility()
        self.grab_set()
        self.parent.wait_window(self)

    def removerObjetivo(self, id):
        self.remove_all_from_db(id)

        self.parent.carregaObjetivos()
        self.parent.atualizaObjetivos()
        self.destroy()

    def adicionarObjetivo(self):
        novoObjetivo = self.entryObjetivo.get()

        if novoObjetivo.replace(" ", "") == "" or novoObjetivo == "Digite um novo objetivo...":
            show_custom_messagebox(self, "Erro", "Você precisa dar um nome ao objetivo")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            query = "SELECT id, nome_objetivo FROM objetivos"
            cursor.execute(query)
            dados = []

            for item in cursor.fetchall():
                dados.append(list(item))

            repetido = False

            for dado in dados:
                if novoObjetivo == dado[1]:
                    repetido = True

            if repetido == False:
                query = f"INSERT INTO objetivos (nome_objetivo) VALUES ('{novoObjetivo}')"
                cursor.execute(query)
            else:
                messagebox.showwarning("showwarning", "Objetivo já cadastrado")
                return

            conn.commit()

            cursor.execute(f"SELECT id FROM objetivos where nome_objetivo = '{novoObjetivo}'")
            id = cursor.fetchall()
            id = convert_to_int(id)
            conn.commit()
            conn.close()
            self.parent.objetivos.append(novoObjetivo)
            self.parent.atualizaObjetivos()
            default_values_column(id)   
            self.destroy()
        except Exception as e:
            print(e)

    def remove_all_from_db(self, id):
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM pesos WHERE id_objetivo_origem = {id}")
            cursor.execute(f"DELETE FROM riscos WHERE id_objetivo_origem = {id}")
            cursor.execute(f"DELETE FROM objetivos WHERE id = '{id}'")
            cursor.execute(f"DELETE FROM impacto_probabilidade WHERE id_objetivo_origem = {id}")
            conn.commit()
            conn.close()
        except Exception:
            return
        
    def on_entry_click(self, event):
        if self.entryObjetivo.get() == "Digite um novo objetivo...":
            self.entryObjetivo.delete(0, "end") 
            self.entryObjetivo.config(fg='black') 

    def on_focusout(self, event):
        if self.entryObjetivo.get() == "":
            self.entryObjetivo.insert(0, "Digite um novo objetivo...")  
            self.entryObjetivo.config(fg='gray') 


class telaMatriz(tk.Tk):
    def __init__(self, objetivos_id):
        super().__init__()
        self.resizable(False, False)
        self.title("Atribua impactos e probabilidades aos riscos")
        self.window_height = 600
        self.window_width = 800
        self.geometry(f"{self.window_width}x{self.window_height}")

        self.objetivos = objetivos_id

        self.page = 0

        self.objetivo_id = self.objetivos[self.page]

        self.entries = {}

        self.show_info()

    def show_info(self):
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT nome_risco_origem, impacto, probabilidade, nivel FROM impacto_probabilidade WHERE id_objetivo_origem = {self.objetivo_id}")
        allinfo = cursor.fetchall()

        all_risk_table = convert_tuplelist_to_array(allinfo, 0)
        all_impact_table = convert_tuplelist_to_array(allinfo, 1)
        all_probability_table = convert_tuplelist_to_array(allinfo, 2)

        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {self.objetivo_id}")
        nome_obj = convert_to_str(cursor.fetchall())

        conn.close()

        # Cor padrão
        verde_opet = '#174311'
        laranja_opet = '#F24F13'

        # Adicionando um frame para a barra superior
        barra_superior = tk.Frame(self, bg=verde_opet, padx=15, pady=15)  # Adicionando padding
        barra_superior.pack(side=tk.TOP, fill=tk.X)

        # Adicionando botão de voltar (seta)
        homeButton = Image.open("images/homeicon.png")
        homeButton = homeButton.resize((20, 20), Image.Resampling.LANCZOS)

        homeButtonTk = ImageTk.PhotoImage(homeButton)
        botao_home = tk.Button(barra_superior, image=homeButtonTk, bg=verde_opet, borderwidth=0, command=self.back_home)
        botao_home.image = homeButtonTk  # Manter referência
        botao_home.pack(side=tk.LEFT)

        # Adicionando título "Gestão de Riscos" no frame
        titulo = tk.Label(barra_superior, text=f"Gestão de Riscos - {nome_obj}", font=('Open Sans', 16), bg=verde_opet, fg='white')
        titulo.pack(side=tk.LEFT, expand=True)  # Centraliza o título na barra

        # Container principal que vai dividir a tela em duas colunas
        container_principal = tk.Frame(self)
        container_principal.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configurando a barra lateral (aside) com os valores de Impacto e Probabilidade
        aside_frame = tk.Frame(container_principal, bg='white')
        aside_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Configurando o frame do card
        card_frame = tk.Frame(aside_frame, bg=verde_opet, padx=10, pady=10)
        card_frame.pack(padx=10, pady=10, fill=tk.Y)  # Adicionando padding externo ao card

        # Título do Aside
        aside_title = tk.Label(card_frame, text="VALORES", font=('Open Sans', 12), bg=verde_opet, fg='white')
        aside_title.pack(pady=10)

        # Texto explicativo sobre Impacto
        impacto_label = tk.Label(card_frame, 
                                text="Impacto:\n\n1 🠊 Leve\n2 🠊 Menor\n3 🠊 Moderado\n4 🠊 Maior\n5 🠊 Extremo", 
                                font=('Open Sans', 10),
                                bg=verde_opet, 
                                fg='white',
                                anchor='w',  # Alinha à esquerda
                                justify='left',
                                width=20)  # Define uma largura fixa
        impacto_label.pack(pady=10)

        # Texto explicativo sobre Probabilidade
        prob_label = tk.Label(card_frame, 
                            text="Probabilidade:\n\n1 🠊 Rara\n2 🠊 Pouco Provável\n3 🠊 Possível\n4 🠊 Provável\n5 🠊 Muito Provável", 
                            font=('Open Sans', 10), 
                            bg=verde_opet, 
                            fg='white',
                            anchor='w',  # Alinha à esquerda
                            justify='left', width=20)  # Define uma largura fixa
        prob_label.pack(pady=10)

        # Frame principal para a tabela de riscos (lado esquerdo)
        main_frame = tk.Frame(container_principal, bg='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)

        # Container para a tabela com rolagem
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        # Configurando o scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Adicionando a barra de rolagem
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adicionando cabeçalho
        header = tk.Frame(scrollable_frame, bg='white')
        header.pack(fill=tk.X)

        # Configurando os rótulos do cabeçalho
        tk.Label(header, text="Riscos", bg='white', font=('Open Sans', 12), width=20).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(header, text="Impacto", bg='white', font=('Open Sans', 12), width=10).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(header, text="Probabilidade", bg='white', font=('Open Sans', 12), width=15).grid(row=0, column=2, padx=10, pady=5)

        # Adicionando dados de exemplo (os riscos serão importados do banco)
        risks_from_db = all_risk_table

        # Loop para adicionar os riscos e os campos de entrada
        for i, risk in enumerate(risks_from_db, start=1):
            risk_frame = tk.Frame(scrollable_frame, bg='white')
            risk_frame.pack(fill=tk.X, padx=20, pady=5)

            # Adicionando rótulos e entradas no grid
            tk.Label(risk_frame, text=risk, bg='white', width=20).grid(row=0, column=0, padx=10)
            impacto_entry = Entry(risk_frame, width=10)  # Entry para Impacto
            impacto_entry.insert(0, all_impact_table[i-1])
            impacto_entry.grid(row=0, column=1, padx=40)
            probabilidade_entry = Entry(risk_frame, width=10)  # Entry para Probabilidade
            probabilidade_entry.insert(0, all_probability_table[i-1])
            probabilidade_entry.grid(row=0, column=2, padx=40)

            self.entries[risk] = (impacto_entry, probabilidade_entry)

        if self.page > 0:
            botao_previous = tk.Button(aside_frame, text="PREVIOUS", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.previous_page, width=20)
            botao_previous.pack(pady=10)

        if self.page < len(self.objetivos)-1:
            botao_next = tk.Button(aside_frame, text="NEXT", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.next_page, width=20)
            botao_next.pack(pady=10)

        if self.page == len(self.objetivos)-1:
            botao_gerar = tk.Button(aside_frame, text="GERAR MATRIZ", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.last_page, width=20)
            botao_gerar.pack(pady=10)

    def back_home(self):
        self.destroy()
        telaObjetivos()

    def last_page(self):
        if self.update_info_in_bd() != False:
            self.update_info_in_bd()
            self.montar_matriz()

    def update_info_in_bd(self):

        conn = create_connection()
        cursor = conn.cursor()

        for risco, (impacto_entry, probabilidade_entry) in self.entries.items():

            impacto_text = impacto_entry.get().strip()
            probabilidade_text = probabilidade_entry.get().strip()

            if not (impacto_text.isdigit() and probabilidade_text.isdigit()):
                show_custom_messagebox(self, "Erro", "As entradas precisam ser números inteiros", "300x100")
                conn.close()
                return False

            impacto = int(impacto_entry.get())
            probabilidade = int(probabilidade_entry.get())

            if not self.check_values(impacto) or not self.check_values(probabilidade):
                show_custom_messagebox(self, "Erro", "Entradas inválidas", "300x100")
                conn.close()
                return False

            cursor.execute(f"UPDATE impacto_probabilidade SET impacto = {impacto}, probabilidade = {probabilidade} WHERE nome_risco_origem = '{risco}' AND id_objetivo_origem = {self.objetivo_id};")
            conn.commit()

        conn.close()

    def next_page(self):
        if self.update_info_in_bd() != False:
            self.update_info_in_bd()
            self.page += 1
            self.objetivo_id = self.objetivos[self.page]
            self.clear_window()
            self.show_info()

    def previous_page(self):
        if self.update_info_in_bd() != False:
            self.update_info_in_bd()
            self.page -= 1
            self.objetivo_id = self.objetivos[self.page]
            self.clear_window()
            self.show_info()


    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def montar_matriz(self):
        MatrizMontada(self.objetivos)
        self.destroy()

    def check_values(self, value):
        range_aceito = [1, 2, 3, 4, 5]
        return value in range_aceito
    
class telaPeso(tk.Tk):
    def __init__(self, objetivos):
        super().__init__()
        self.resizable(False, False)
        self.title("Atribua pesos aos riscos")
        self.window_height = 600
        self.window_width = 800
        self.geometry(f"{self.window_width}x{self.window_height}")

        self.objetivos_id = objetivos

        self.total_pages = len(objetivos)
        self.page =  1
        self.current_page = 1

        self.page_frame = tk.Frame(self)
        self.page_frame.pack(fill=tk.BOTH, expand=True)

        self.show_page(self.page)

    def show_page(self, page):
        # Limpar o conteúdo da página anterior
        for widget in self.winfo_children():
            widget.destroy()

        # Adicionando um frame para a barra superior
        verde_opet = '#174311'
        laranja_opet = '#F24F13'

        barra_superior = tk.Frame(self, bg=verde_opet, padx=15, pady=15)
        barra_superior.pack(side=tk.TOP, fill=tk.X)

        # Adicionando botão de voltar (seta)
        homeButton = Image.open("images/homeicon.png")
        homeButton = homeButton.resize((20, 20), Image.Resampling.LANCZOS)

        homeButtonTk = ImageTk.PhotoImage(homeButton)
        botao_home = tk.Button(barra_superior, image=homeButtonTk, bg=verde_opet, borderwidth=0, command=self.back_home)
        botao_home.image = homeButtonTk  # Manter referência
        botao_home.pack(side=tk.LEFT)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {self.objetivos_id[self.current_page-1]}")
        nome_obj = convert_to_str(cursor.fetchall())
        conn.close()

        # Adicionando título "Gestão de Riscos" no frame
        titulo = tk.Label(barra_superior, text=f"Gestão de Riscos - {nome_obj}", font=('Open Sans', 16), bg=verde_opet, fg='white')
        titulo.pack(side=tk.LEFT, expand=True)
        
        # Container principal que vai dividir a tela em duas colunas
        container_principal = tk.Frame(self)
        container_principal.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configurando a barra lateral (aside) com os valores de Impacto e Probabilidade
        aside_frame = tk.Frame(container_principal, bg='white')
        aside_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Configurando o frame do card
        card_frame = tk.Frame(aside_frame, bg=verde_opet, padx=20, pady=10)
        card_frame.pack(padx=10, pady=10, fill=tk.Y)

        # Título do Aside
        aside_title = tk.Label(card_frame, text="VALORES", font=('Open Sans', 12), bg=verde_opet, fg='white')
        aside_title.pack(pady=10)
        # Texto explicativo sobre Impacto
        impacto_label = tk.Label(card_frame, 
                                text="1→ Igual importância \n3→ Pouco\n mais importante \n5→ Muito\n mais importante \n7→ Bastante\n mais importante \n9→ Extremamente \n mais importante", 
                                font=('Open Sans', 9), 
                                bg=verde_opet, 
                                fg='white',
                                anchor='w',  # Alinha à esquerda
                                justify='left',
                                width=20)  # Define uma largura fixa
        impacto_label.pack(pady=10)

        # Texto explicativo sobre Probabilidade
        prob_label = tk.Label(card_frame, 
                            text="Valores intermediários\n 2, 4, 6, 8",
                            font=('Open Sans', 9), 
                            bg=verde_opet, 
                            fg='white',
                            anchor='w',  # Alinha à esquerda
                            justify='left', width=20)  # Define uma largura fixa
        prob_label.pack(pady=10)

        # Frame principal para a tabela de comparação de riscos (lado esquerdo)
        main_frame = tk.Frame(container_principal, bg='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)

        # Container para a tabela com rolagem
        canvas = Canvas(main_frame, bg='white')
        scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        # Configurando o scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Adicionando a barra de rolagem
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adicionando cabeçalho
        header = tk.Frame(scrollable_frame, bg='white')
        header.pack(fill=tk.X)

        tk.Label(header, text="Risco", bg='white', font=('Open Sans', 12), width=20).pack(side=tk.LEFT, pady=5)
        tk.Label(header, text="Nível", bg='white', font=('Open Sans', 12), width=20).pack(side=tk.LEFT, pady=5)
        tk.Label(header, text="Risco", bg='white', font=('Open Sans', 12), width=20).pack(side=tk.LEFT, pady=5)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE id_objetivo_origem = {self.objetivos_id[page-1]}")
        all_risks = cursor.fetchall()
        conn.close()

        risks_array = [list(item) for item in all_risks]
        nomes_riscos_array = [risco[1] for risco in risks_array]

        nomes_riscos_array.sort()

        combinacoes = []
        comb_inversa = []
        self.entries = {}

        # Checando todas as combinações
        for risco_primario in nomes_riscos_array:
            for risco_secundario in nomes_riscos_array:
                if risco_primario != risco_secundario:
                    comb = f"{risco_primario}X{risco_secundario}"
                    comb_inversa = f"{risco_secundario}X{risco_primario}"
                    if comb_inversa not in combinacoes:
                        combinacoes.append(comb)

        # Pegando a info de todas as combinações salvas no banco de dados
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_combinacao, peso_combinacao FROM pesos WHERE id_objetivo_origem = {self.objetivos_id[page - 1]}")
        pesos_info_response = cursor.fetchall()
        conn.close()

        pesos_lista = {item[0]: item[1] for item in pesos_info_response}

        # Novamente uma checagem das combinações, criando ela caso não exista com o peso 1 (default)

        i = 0
        for combinacao in combinacoes:
            if combinacao not in pesos_lista:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO pesos (nome_combinacao, peso_combinacao, id_objetivo_origem) VALUES ('{combinacao}', 1, {self.objetivos_id[page - 1]}); ")
                conn.commit()
                conn.close()

            peso = pesos_lista.get(combinacao, 1)

            risco1, risco2 = combinacao.split('X')

            lim = 18

            if len(risco1) >= lim:
                risco1 = risco1[:lim]
                risco1+="..."

            if len(risco2) >= lim:
                risco2 = risco2[:lim]
                risco2+="..."

            risk_frame = tk.Frame(scrollable_frame, bg='white')
            risk_frame.pack(fill=tk.X, pady=5)

            tk.Label(risk_frame, text=risco1, bg='white', width=20).pack(side=tk.LEFT, padx=25)

            entry = tk.Entry(risk_frame, width=20)
            entry.pack(side=tk.LEFT, padx=25)
            entry.insert(0, str(peso))

            tk.Label(risk_frame, text=risco2, bg='white', width=20).pack(side=tk.LEFT, padx=25)

            self.entries[combinacao] = entry
            i += 1

        if self.current_page > 1:
            botao_previous = tk.Button(aside_frame, text="PREVIOUS", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.change_pages_previous, width=20)
            botao_previous.pack(pady=10)

        if self.current_page < len(self.objetivos_id):
            botao_next = tk.Button(aside_frame, text="NEXT", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.change_pages_next, width=20)
            botao_next.pack(pady=10)

        if self.current_page == len(self.objetivos_id):
            botao_gerar = tk.Button(aside_frame, text="GERAR MATRIZ", font=('Open Sans', 12), bg=laranja_opet, fg='white', command=self.finish_settings, width=20)
            botao_gerar.pack(pady=10)

    def back_to_home(self):
        self.destroy()
        telaObjetivos()
        return

    def change_pages_next(self):
        dados = self.get_entries_values()
        for valor in dados.values():
            if self.check_values(valor) == False:
                messagebox.showwarning("showwarning", "Dados incorretos")
                return

        if self.current_page < self.total_pages:
            self.update_database()
            self.current_page += 1
            self.show_page(self.current_page)

    def change_pages_previous(self):
        dados = self.get_entries_values()

        for valor in dados.values():
            if self.check_values(valor) == False:
                messagebox.showwarning("showwarning", "Dados incorretos")
                return

        if self.current_page > 0:
            self.update_database()
            self.current_page -= 1
            self.show_page(self.current_page)

    def get_entries_values(self):
        valores = {}
        for combinacao, entry in self.entries.items():
            try:
                valor = int(entry.get())
                if self.check_values(valor):
                    valores[combinacao] = valor
                else:
                    valores[combinacao] = None
            except ValueError:
                valores[combinacao] = None
        return valores

    def update_database(self):
        values = self.get_entries_values()

        conn = create_connection()
        cursor = conn.cursor()
        full_query = ""
        for key, value in values.items():
            full_query += f"UPDATE pesos SET peso_combinacao = {value} WHERE nome_combinacao = '{key}' AND id_objetivo_origem = {self.objetivos_id[self.current_page - 1]};"
        full_query += " commit;"
        cursor.execute(full_query)
        conn.close()
        return

    def check_values(self, value):
        range_aceito = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return value in range_aceito

    def back_home(self):
        self.destroy()
        telaObjetivos()

    def finish_settings(self):
        dados = self.get_entries_values()

        for valor in dados.values():
            if self.check_values(valor) == False:
                messagebox.showwarning("showwarning", "Dados incorretos")
                return
        self.update_database()

        self.montar_ahp()

    def montar_ahp(self):
        AhpMontado(self.objetivos_id)
        self.destroy()

class MatrizMontada(tk.Tk):
    def __init__(self, objetivos):
        super().__init__()

        self.resizable(False, False)
        self.title("Matriz")

        self.id_objetivos = objetivos
        self.id_objetivo = self.id_objetivos[0]

        self.show_matrix(self.id_objetivo)

    def show_matrix(self, id_obj):
        # Adicionando um frame para a barra superior
        barra_superior = tk.Frame(self, bg=verde_opet, padx=15, pady=15)  # Adicionando padding
        barra_superior.pack(side=tk.TOP, fill=tk.X)

        # Configura o fechamento correto do programa
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Criar uma matriz para armazenar os valores de impacto * probabilidade
        matriz_risco = np.zeros((5, 5), dtype=int)

        # Preencher a matriz com os valores de impacto * probabilidade
        for i in range(1, 6):
            for j in range(1, 6):
                matriz_risco[i-1, j-1] = i * j

        # Criar uma matriz de strings para armazenar os nomes dos riscos
        matriz_riscos_nomes = np.full((5, 5), '', dtype=object)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_risco_origem, impacto, probabilidade FROM impacto_probabilidade WHERE id_objetivo_origem = {id_obj}")
        riscos = cursor.fetchall()
        tupla_id = tuple(self.id_objetivos)

        if len(tupla_id) == 1:
            tupla_id = f"({id_obj})"

        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id in {tupla_id}")
        objetivos = cursor.fetchall()
        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {id_obj}")
        nome_obj = cursor.fetchall()
        conn.close()

        # Popula a matriz com os nomes dos riscos (concatenando caso mais de um risco caia na mesma célula)
        for risco, probabilidade, impacto in riscos:
            if matriz_riscos_nomes[probabilidade-1, impacto-1] == '':
                matriz_riscos_nomes[probabilidade-1, impacto-1] = risco
            else:
                matriz_riscos_nomes[probabilidade-1, impacto-1] += f', {risco}'

        # Definir o colormap personalizado (verde, amarelo, vermelho)
        colors = [(0.09, 0.26, 0.06, 1), (0.94, 0.61, 0.07, 1), (0.85, 0.17, 0.01, 1)]
        cmap = ListedColormap(colors)

        # Definir os limites para cada faixa de cores
        bounds = [1, 5, 15, 25]
        norm = BoundaryNorm(bounds, cmap.N)

        # Configuração da visualização
        fig = plt.figure(figsize=(8, 6))
        ax = sns.heatmap(matriz_risco, annot=True, fmt="d", cmap=cmap, norm=norm, cbar=True, linewidths=0.5)

        # Adicionar os nomes dos riscos diretamente nas células, se houver risco
        for i in range(matriz_risco.shape[0]):
            for j in range(matriz_risco.shape[1]):
                if matriz_riscos_nomes[i, j] != '':  # Só exibe se houver risco
                    ax.text(j + 0.5, i + 0.35, f'{matriz_riscos_nomes[i, j]}',
                            ha='center', va='bottom', color='black', fontsize=8)

        # Ajuste dos rótulos dos eixos para iniciar em 1
        ax.set_xticklabels([1, 2, 3, 4, 5])
        ax.set_yticklabels([1, 2, 3, 4, 5])

        # Botão de voltar
        homeButton = tk.Button(barra_superior, text="🏠", bg=laranja_opet, command=self.back_home)
        homeButton.pack(side="left")

        

        titulo = tk.Label(barra_superior, text='Matriz de Risco - ' + str(convert_to_str(nome_obj)), font=('Open Sans', 16), bg=verde_opet, fg='white')
        titulo.pack(side=tk.LEFT, expand=True)  # Centraliza o título na barra
        plt.xlabel('Impacto')
        plt.ylabel('Probabilidade')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack()

        for i in range(len(self.id_objetivos)):
            button = tk.Button(self, width=20, height=2, text=objetivos[i][0], bg=laranja_opet, fg='black',
                               command=lambda id=self.id_objetivos[i]: self.change_matrix(id))
            button.pack(side="left", padx=5, pady=5)

    def change_matrix(self, id):
        plt.close()
        self.clear_window()
        self.show_matrix(id)

    def on_closing(self):
        # Limpa recursos e fecha a janela
        self.quit()
        self.destroy()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def back_home(self):
        plt.close()
        self.destroy()
        telaObjetivos() 

class AhpMontado(tk.Tk):
    def __init__(self, objetivos):
        super().__init__()
        self.resizable(False, False)
        self.title("AHP")
        #self.geometry("800x600")
        self.objetivos = objetivos
        self.id_objetivo = objetivos[0]

        conn = create_connection()
        cursor = conn.cursor()

        tupla_id = tuple(self.objetivos)

        if len(tupla_id) == 1:
            tupla_id = f"({self.objetivos[0]})"

        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id in {tupla_id}")
        self.objetivos_response = cursor.fetchall()
        cursor.close()

        self.array_nomes = convert_tuplelist_to_array(self.objetivos_response)

        self.show_page(self.id_objetivo)

    # Função para criar o gráfico de radar
    def criar_grafico_radar(self, valores, categorias, objetivo):

        # Número de categorias
        N = len(categorias)

        # Ângulo para cada eixo
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

        # Fechar o gráfico
        valores = np.concatenate((valores, [valores[0]]))
        angles += angles[:1]

        # Criar o gráfico
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))  # Aumentar o tamanho do gráfico

        # Desenhar uma grade com labels em negrito
        ax.fill(angles, valores, color='blue', alpha=0.25)
        ax.plot(angles, valores, color='blue', linewidth=2)

        # Adicionar rótulos
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])

        # Ajustar o espaçamento dos rótulos
        ax.set_xticklabels(categorias, fontsize=12, fontweight='bold', ha='center', rotation=45)

        barra_superior = tk.Frame(self, bg=verde_opet, padx=15, pady=15)  # Adicionando padding
        barra_superior.pack(side=tk.TOP, fill=tk.X)

        homeButton = tk.Button(barra_superior, text="🏠", bg=laranja_opet, command=self.back_home)
        homeButton.pack(side=tk.LEFT)

        titulo = tk.Label(barra_superior, text='AHP - ' + str(objetivo), font=('Open Sans', 16), bg=verde_opet, fg='white')
        titulo.pack(side=tk.RIGHT, expand=True)


        # Melhorar estética com grid de fundo
        ax.spines['polar'].set_visible(False)
        ax.grid(color='gray', linestyle=':', linewidth=0.5)

        # Ajustar layout para melhor responsividade
        plt.tight_layout()

        frame = tk.Frame(self)
        frame.pack(expand=True)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def show_page(self, id):

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {id}")
        objetivo_response = cursor.fetchall()
        cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {id}")
        riscos_response = cursor.fetchall()
        cursor.execute(f"SELECT nome_combinacao, peso_combinacao FROM pesos WHERE id_objetivo_origem = {id}")
        pesos_response = cursor.fetchall()
        conn.close()

        objetivo = convert_to_str(objetivo_response)
        riscos = convert_tuplelist_to_array(riscos_response)
        pesos_resp = convert_tuplelist_to_dict(pesos_response)

        n = len(riscos)

        matriz = np.ones((n, n))

        control = 0
        for i in range(n):
            for j in range(i+1, n):
                _, value = list(pesos_resp.items())[control]

                matriz[i, j] = value
                matriz[j, i] = 1/value
                control += 1

        matrizNormalizada = self.normalizaMatriz(matriz)
        peso = self.calculaPeso(matriz)

        self.criar_grafico_radar(peso, riscos, objetivo)

        for i in range(len(self.objetivos)):
            button = tk.Button(self, width=20, height=2, text=self.array_nomes[i], bg=laranja_opet, fg='black',
                               command=lambda id=self.objetivos[i]: self.change_ahp(id))
            button.pack(side="left", padx=5, pady=5)

    def back_home(self):
        self.destroy()
        telaObjetivos()

    def change_ahp(self, id):
        plt.close()
        self.clear_window()
        self.show_page(id)

    #normalizando as matrizes(dividindo cada valor pela soma da coluna(tipo um mmc) serve pra calcular os pesos)
    def normalizaMatriz(self, matriz):
        somaColunas = np.sum(matriz, axis=0)
        return matriz / somaColunas

    #calculando os pesos(a soma de cada linha tem que dar 1)
    def calculaPeso(self, matrizNormalizada):
        return matrizNormalizada.mean(axis=1)

    def on_closing(self):
        # Limpa recursos e fecha a janela
        self.quit()
        self.destroy()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    create_tables()
    tela = telaObjetivos()
    tela.mainloop()