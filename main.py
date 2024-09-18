import tkinter as tk
from tkinter import *
from tkinter import messagebox
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from functools import partial

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
            for i in range(3):
                cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('risco{i}', {id_objetivo})")
                conn.commit()
                cursor.execute(f"INSERT INTO impacto_probabilidade (id_objetivo_origem, nome_risco_origem, impacto, probabilidade, nivel) VALUES ({id_objetivo}, 'risco{i}', 0, 0, 0)")  
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
        self.title("Objetivos")
        self.geometry("800x600")
        self.resizable(False, False)
        
        self.frameObjetivos = tk.Frame(self)
        self.frameObjetivos.pack(expand=True)

        self.botaoAdicionar = tk.Button(self, text="Adicionar Objetivo", command=self.adicionaObjetivo)
        self.botaoAdicionar.pack(pady=10)
        self.botaoRemover = tk.Button(self, text="Remover Objetivo", command=self.removerObjetivo)
        self.botaoRemover.pack(pady=10)

        self.objetivos = self.carregaObjetivos()
        self.ticados = []
        self.atualizaObjetivos()

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.botaoRiscos = tk.Button(self, text="Adicionar Risco", command=self.adicionarRisco)
        self.botaoRiscos.pack(pady=10)

        self.removerRiscos = tk.Button(self, text="Remover Risco", command=self.removerRisco)
        self.removerRiscos.pack(pady=10)

        self.botaoProximo = tk.Button(self, text="🡆", command=self.excluiResto)
        self.botaoProximo.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def adicionarRisco(self):
        JanelaAddRisco(self)

    def removerRisco(self):
        JanelaRemoverRisco(self)

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

        for widget in self.frameObjetivos.winfo_children():
            widget.destroy()

        self.ticados = []

        for _, objetivo in self.objetivos:
            taTicado = tk.BooleanVar()
            checkBox = tk.Checkbutton(self.frameObjetivos, text=f"{objetivo.capitalize()}", variable=taTicado)
            checkBox.pack(anchor="w")
            self.ticados.append(taTicado)

    def adicionaObjetivo(self):
        JanelaAddObjetivo(self)
        self.atualizaObjetivos()
    
    def removerObjetivo(self):
        JanelaRemoverObjetivo(self)
        self.atualizaObjetivos()

    def excluiResto(self):
        self.ticados = [objetivo for objetivo, taTicado in zip(self.objetivos, self.ticados) if taTicado.get()]

        self.ticados_id = []
    
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
        self.geometry("400x300")
        self.parent = parent

        telas_disponiveis = ['AHP', 'Matriz de Risco']

        self.lb_telas = Listbox(self)
        for telas in telas_disponiveis:
            self.lb_telas.insert(END, telas)
        self.lb_telas.select_set(0)
        self.lb_telas.pack()

        Button(self, text="Confirmar", command=self.confirmar_tela).pack()

        self.transient(self.parent)
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
        
class JanelaRemoverRisco(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Remover Risco")
        self.geometry("400x300")
        self.parent = parent

        self.show_first_window()

        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    def show_first_window(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]

        lista_objetivos = nomes_objetivos
        conn.close()

        self.lb_objetivos = Listbox(self)
        for objetivos in lista_objetivos:
            self.lb_objetivos.insert(END, objetivos)
        self.lb_objetivos.select_set(0)
        self.lb_objetivos.pack()

        tk.Button(self, text="Selecionar Objetivo", command=self.select_risks).pack()

    def select_risks(self):
        objetivo_selecionado = self.lb_objetivos.get(ACTIVE)

        if objetivo_selecionado == "":
            show_custom_messagebox(self, "Erro", "Você precisa selecionar um objetivo")
            return

        self.clear_window()

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{objetivo_selecionado}'")
        self.id_objetivo_selecionado = cursor.fetchall()
        self.id_objetivo_selecionado = convert_to_int(self.id_objetivo_selecionado)
        conn.commit()
        cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {self.id_objetivo_selecionado}")
        riscos_query = cursor.fetchall()
        riscos_array = [list(item) for item in riscos_query]
        nomes_riscos = [risco[0] for risco in riscos_array]
        conn.commit()
        conn.close()

        self.lb_riscos = Listbox(self)
        for risco in nomes_riscos:
            self.lb_riscos.insert(END, risco)
        self.lb_riscos.select_set(0)
        self.lb_riscos.pack()

        tk.Button(self, text="Remover", command=self.remove_risk).pack()

    def remove_risk(self):
        
        risk_to_remove = self.lb_riscos.get(ACTIVE)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM riscos WHERE nome_risco = '{risk_to_remove}' AND id_objetivo_origem = {self.id_objetivo_selecionado}")
        conn.commit()
        conn.close()
        self.update_db_removing_old_risks(risk_to_remove)
        self.destroy()

    def update_db_removing_old_risks(self, risk):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT id, nome_combinacao FROM pesos WHERE id_objetivo_origem = {self.id_objetivo_selecionado}")
        except:
            conn.close()
            return
        
        pesos_query = cursor.fetchall()
        pesos_array = [list(item) for item in pesos_query]
        
        try:
            conn.commit()
            cursor.execute(f"DELETE FROM impacto_probabilidade WHERE id_objetivo_origem = {self.id_objetivo_selecionado} AND nome_risco_origem = '{risk}'")
            conn.commit()
        except Exception as e:
            conn.close()
            return

        if pesos_array == []:
            return

        for peso in pesos_array:
            peso_id = peso[0]
            nome_peso = peso[1]

            nome1, nome2 = nome_peso.split("X")

            if nome1 == risk or nome2 == risk:
                cursor.execute(f"DELETE FROM pesos WHERE id = {peso_id}")
                conn.commit()
        
        conn.close()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

class JanelaAddRisco(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Adicionar Risco")
        self.geometry("400x300")
        self.parent = parent

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]

        lista_objetivos = nomes_objetivos

        self.lb_objetivos = Listbox(self)
        for objetivo in lista_objetivos:
            self.lb_objetivos.insert(END, objetivo)
        self.lb_objetivos.select_set(0)
        self.lb_objetivos.pack()

        self.entryRisco = Entry(self)
        self.entryRisco.pack(pady=5)

        self.botaoAdicionarRisco = tk.Button(self, text="Adicionar", command=self.adicionarRisco)
        self.botaoAdicionarRisco.pack(pady=10)

        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    def adicionarRisco(self):
        objetivo_marcado = self.lb_objetivos.get(ACTIVE)
        novo_risco = self.entryRisco.get()
        if objetivo_marcado == "" or novo_risco.replace(" ", "") == "":
            string = ""
            if objetivo_marcado == "":
                string = "Você precisa marcar um objetivo"
            else:
                string = "Você precisa preencher o nome do risco"

            show_custom_messagebox(self, "Erro", string)
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

        cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('{novo_risco}', {id_objetivo})")
        cursor.execute(f"INSERT INTO impacto_probabilidade (id_objetivo_origem, nome_risco_origem, impacto, probabilidade, nivel) VALUES ({id_objetivo}, '{novo_risco}', 0, 0, 0)")
        conn.commit()
        conn.close()
        self.destroy()

    def check_risk_exists(self, risk):
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE nome_risco = '{risk}' AND id_objetivo_origem = {self.id_objetivo}")
        cursor.fetchall()
        row = cursor.rowcount
        conn.close()
        
        return row > 0

class JanelaRemoverObjetivo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Remover Objetivo")
        self.geometry("300x250")
        self.parent = parent

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()
        conn.close()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]
    
        self.lb_objetivos_remove = Listbox(self)
        for objetivo in nomes_objetivos:
            self.lb_objetivos_remove.insert(END, objetivo)
        self.lb_objetivos_remove.select_set(0)
        self.lb_objetivos_remove.pack()

        Button(self, text="Remover Objetivo", command=self.remove_objetivo).pack()

        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    def remove_objetivo(self):
        objetivo_to_remove = self.lb_objetivos_remove.get(ACTIVE)

        if objetivo_to_remove == "":
            show_custom_messagebox(self, "Erro", "Você precisa selecionar um objetivo")
            return
        
        self.remove_all_from_db(objetivo_to_remove)
        self.parent.atualizaObjetivos()

        self.destroy()

    def remove_all_from_db(self, nome_objetivo):
        try: 
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{nome_objetivo}'")
            id = cursor.fetchall()
            id = convert_to_int(id)
            cursor.execute(f"DELETE FROM pesos WHERE id_objetivo_origem = {id}")
            cursor.execute(f"DELETE FROM riscos WHERE id_objetivo_origem = {id}")
            cursor.execute(f"DELETE FROM objetivos WHERE nome_objetivo = '{nome_objetivo}'")
            cursor.execute(f"DELETE FROM impacto_probabilidade WHERE id_objetivo_origem = {id}")
            conn.commit()
            conn.close()
        except Exception:
            return

class JanelaAddObjetivo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Adicionar Objetivo")
        self.geometry("300x150")
        self.parent = parent

        self.label = tk.Label(self, text="Insira um novo objetivo:")
        self.label.pack(pady=10)

        self.entryObjetivo = tk.Entry(self)
        self.entryObjetivo.pack(pady=5)

        self.botaoAdicionar = tk.Button(self, text="Adicionar", command=self.adicionarObjetivo)
        self.botaoAdicionar.pack(pady=10)

        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    def adicionarObjetivo(self):
        novoObjetivo = self.entryObjetivo.get()

        if novoObjetivo.replace(" ", "") == "":
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
        
        conn.close()

        self.page_frame = tk.Frame(self)
        self.page_frame.pack(fill=tk.BOTH, expand=True)

        
        Label(self.page_frame, text="Risco").place(x=self.window_width/2 - 120, y=10)

        Label(self.page_frame, text="Impacto").place(x=self.window_width/2, y=10)
        
        Label(self.page_frame, text="Probabilidade").place(x=self.window_width/2 + 120, y=10)

        i = 0
        for i, risco in enumerate(all_risk_table):
            if len(risco) >= 18:
                risco = risco[:18]
                risco+="..."
            Label(self.page_frame, text=risco).place(x=self.window_width/2 - 130, y=75 + (i * 50))

            impacto_entry = tk.Entry(self.page_frame, width=3)
            impacto_entry.place(x=self.window_width/2 + 20, y=75 + (i * 50))
            impacto_entry.insert(0, all_impact_table[i])

            probabilidade_entry = tk.Entry(self.page_frame, width=3)
            probabilidade_entry.place(x=self.window_width/2 + 120, y=75 + (i * 50))
            probabilidade_entry.insert(0, all_probability_table[i])

            self.entries[risco] = (impacto_entry, probabilidade_entry)

            i += 1

        if self.page < len(self.objetivos)-1:
            Button(self.page_frame, text="Next", command=self.next_page).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        if self.page > 0:
            Button(self.page_frame, text="Previous", command=self.previous_page).pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

        if self.page == len(self.objetivos)-1:
            Button(self.page_frame, text="Montar Matriz", command=self.last_page).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        Button(self.page_frame, text="Help", command=self.show_help_info).place(x=self.window_width/2 - 20, y=self.window_height - 45)

        if self.page == 0:
            Button(self.page_frame, text="Home", command=self.back_home).place(x=15, y=self.window_height - 45)

    def back_home(self):
        self.destroy()
        telaObjetivos()

    def last_page(self):
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
    
    def show_help_info(self):
        help_window = tk.Toplevel(self)
        help_window.title("Informações de valores")
        help_window.geometry("400x200")
        help_window.resizable(False, False)
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, 
        """
            Impacto    -    Probabilidade
        1 → Leve            Rara
        2 → Menor           Pouco provável
        3 → Moderado        Possível
        4 → Maior           Provável
        5 → Extremo         Muito provável
        """)
        text_widget.configure(state='disabled')
        text_widget.pack(expand=True, fill=tk.BOTH)

        close_button = tk.Button(help_window, text="Fechar", command=help_window.destroy)
        close_button.pack(pady=10)

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
        self.page = 1
        self.current_page = 1

        self.page_frame = tk.Frame(self)
        self.page_frame.pack(fill=tk.BOTH, expand=True)

        self.show_page(self.page)
    
    def show_page(self, page):
        # Limpar o conteúdo da página anterior
        for widget in self.page_frame.winfo_children():
            widget.destroy()

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE id_objetivo_origem = {self.objetivos_id[page - 1]}")
        all_risks = cursor.fetchall()
        conn.close()

        risks_array = [list(item) for item in all_risks]
        nomes_riscos_array = [risco[1] for risco in risks_array]

        nomes_riscos_array.sort()

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {self.objetivos_id[page-1]}")
        nome_obj = cursor.fetchall()
        conn.close()

        Label(self.page_frame, text=convert_to_str(nome_obj), font=("Arial", 24), wraplength=250).place(x=self.window_width/2 - 370, y=10)

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
            tk.Label(self.page_frame, text=risco1).place(x=self.window_width/2 - 100, y=10 + (i * 50))
            
            entry = tk.Entry(self.page_frame, width=3)
            entry.place(x=self.window_width/2, y=10 + (i * 50))
            entry.insert(0, str(peso))
            
            tk.Label(self.page_frame, text=risco2).place(x=self.window_width/2 + 100, y=10 + (i * 50))
            
            self.entries[combinacao] = entry
            i += 1

        if self.current_page <= self.total_pages:
            if self.total_pages != 1:
                self.next_button = tk.Button(self.page_frame, text="Next", command=self.change_pages_next)
                self.next_button.place(x=self.window_width-300, y=self.window_height-100)
            self.home_button = tk.Button(self.page_frame, text="Home", command=self.back_to_home)
            self.home_button.place(x=250, y=self.window_height-100)
        if self.current_page > 1:
            self.back_button = tk.Button(self.page_frame, text="Previous", command=self.change_pages_previous)
            self.back_button.place(x=250, y=self.window_height-100)
        if self.current_page == self.total_pages:
            self.compute_button = tk.Button(self.page_frame, text="Finish", command=self.finish_settings)
            self.compute_button.place(x=self.window_width-300, y=self.window_height-100)

        self.peso_info = tk.Button(self.page_frame, text="Help", command=self.show_help_info)
        self.peso_info.place(x=self.window_width/2 - 10, y=self.window_height - 100)

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

        if self.current_page > 1:
            self.update_database()
            self.current_page -= 1
            self.show_page(self.current_page)

    def show_help_info(self):
        help_window = tk.Toplevel(self)
        help_window.title("Informações de valores")
        help_window.geometry("400x200")
        help_window.resizable(False, False)
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, 
        """
        1 → Igual importância
        3 → Pouco mais importante
        5 → Muito mais importante
        7 → Bastante mais importante
        9 → Extremamente mais importante
        2, 4, 6, 8 → Valores intermediários
        """)
        text_widget.configure(state='disabled')
        text_widget.pack(expand=True, fill=tk.BOTH)

        close_button = tk.Button(help_window, text="Fechar", command=help_window.destroy)
        close_button.pack(pady=10)

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
            full_query += f"UPDATE pesos SET peso_combinacao = {value} WHERE nome_combinacao = '{key}' AND id_objetivo_origem = {self.objetivos_id[self.current_page - 1]}; commit; "
        cursor.execute(full_query)
        conn.close()
        return

    def check_values(self, value):
        range_aceito = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return value in range_aceito

    def finish_settings(self):
        self.update_database()
        # Próxima página
        messagebox.showinfo("showinfo", "Próxima pagina!")
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
        colors = ["green", "yellow", "red"]
        cmap = ListedColormap(colors)

        # Definir os limites para cada faixa de cores
        bounds = [1, 5, 15, 25]
        norm = BoundaryNorm(bounds, cmap.N)

        # Configuração da visualização
        teste = plt.figure(figsize=(8, 6))
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

        plt.title('Matriz de Risco - ' + str(convert_to_str(nome_obj)))
        plt.xlabel('Impacto')
        plt.ylabel('Probabilidade')

        canvas = FigureCanvasTkAgg(teste, master=self)
        canvas.get_tk_widget().pack()

        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(anchor="w", fill=tk.X)

        for i in range(len(self.id_objetivos)):
            Button(self, text=objetivos[i][0], command=partial(self.change_matrix, self.id_objetivos[i])).pack(side=tk.LEFT)

    def change_matrix(self, id):
        self.clear_window()
        self.show_matrix(id)

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