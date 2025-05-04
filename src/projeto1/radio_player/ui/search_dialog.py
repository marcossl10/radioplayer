# /home/marcos/projeto1/radio_player/ui/search_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar, END
import logging
import requests # Para fazer as requisições HTTP
import json # Para tratar possíveis erros de JSON

logger = logging.getLogger(__name__)

# URL base da API do Radio Browser
RADIO_BROWSER_API_URL = "https://de1.api.radio-browser.info/json/stations/byname/"

class SearchDialog(tk.Toplevel):
    """Janela de diálogo para buscar e adicionar estações de rádio online."""

    def __init__(self, parent):
        """
        Inicializa o diálogo de busca.

        Args:
            parent: A janela principal (MainWindow) que abriu este diálogo.
                    Usado para acessar o station_manager e atualizar a lista.
        """
        super().__init__(parent)
        self.parent = parent # Referência à MainWindow
        self.title("Buscar Rádios Online")
        # Manter altura aumentada por enquanto
        self.geometry("500x430")

        # Variável para status da busca
        self.status_var = tk.StringVar(value="")

        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Widgets de Busca ---
        search_frame = ttk.Frame(main_frame)
        # Usar grid - Linha 0, Coluna 0, sticky=EW para preencher largura
        search_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))

        search_label = ttk.Label(search_frame, text="Buscar por nome:")
        # Usar grid - Coluna 0
        search_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        # Usar grid - Coluna 1, sticky=EW para preencher horizontalmente
        self.search_entry.grid(row=0, column=1, padx=(0, 5), sticky=tk.EW)
        self.search_entry.bind("<Return>", self._perform_search) # Permite buscar com Enter

        self.search_button = ttk.Button(search_frame, text="Buscar", command=self._perform_search)
        # Usar grid - Coluna 2
        self.search_button.grid(row=0, column=2)

        # Configurar a coluna 1 (do Entry) para expandir
        search_frame.columnconfigure(1, weight=1)

        # --- Widgets de Resultados ---
        results_frame = ttk.Frame(main_frame)
        # Usar grid - Linha 1, Coluna 0, sticky=NSEW para preencher tudo
        results_frame.grid(row=1, column=0, sticky=tk.NSEW)

        # Listbox para exibir resultados (dentro do results_frame)
        self.results_listbox = Listbox(results_frame, height=15)
        self.results_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Scrollbar para a Listbox (dentro do results_frame)
        scrollbar = Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=scrollbar.set)

        # Armazenar os dados completos das estações encontradas (nome -> url)
        self._search_results_data = {}

        # --- Botões de Ação ---
        action_frame = ttk.Frame(main_frame)
        # Usar grid - Linha 2, Coluna 0, sticky=EW
        action_frame.grid(row=2, column=0, sticky=tk.EW, pady=(10, 5))


        self.add_button = ttk.Button(action_frame, text="Adicionar Selecionada", command=self._add_selected_station)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.add_button.config(state=tk.DISABLED) # Habilitar apenas quando algo for selecionado

        self.close_button = ttk.Button(action_frame, text="Fechar", command=self.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        # --- Status Label ---
        # Usar grid - Linha 3, Coluna 0, sticky=EW
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_label.grid(row=3, column=0, sticky=tk.EW, pady=(5, 0))

        # Configurar expansão da linha/coluna principal do main_frame
        main_frame.rowconfigure(1, weight=1) # Linha 1 (results_frame) expande verticalmente
        main_frame.columnconfigure(0, weight=1) # Coluna 0 expande horizontalmente

        # Bind para habilitar/desabilitar botão Add ao selecionar/deselecionar
        self.results_listbox.bind('<<ListboxSelect>>', self._on_result_select)

        # Foco inicial no campo de busca
        self.search_entry.focus_set()

    def _perform_search(self, event=None):
        """Executa a busca na API do Radio Browser."""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Busca Vazia", "Por favor, digite um nome para buscar.", parent=self)
            return

        logger.info(f"Buscando estações online com termo: '{search_term}'")
        self.status_var.set("Buscando...") # Atualiza status
        self.search_button.config(state=tk.DISABLED)
        self.results_listbox.delete(0, END) # Limpa resultados anteriores
        self._search_results_data.clear()
        self.add_button.config(state=tk.DISABLED)

        response = None # Inicializa response para o finally
        try:
            # Monta a URL da API
            api_url = f"{RADIO_BROWSER_API_URL}{requests.utils.quote(search_term)}"
            headers = {'User-Agent': 'RadioPlayerApp/1.0'} # Boa prática incluir User-Agent
            logger.debug(f"Request URL: {api_url}")

            response = requests.get(api_url, headers=headers, timeout=10) # Timeout de 10s
            logger.debug(f"Response Status Code: {response.status_code}")
            response.raise_for_status() # Levanta exceção para erros HTTP (4xx, 5xx)

            stations = response.json()

            if not stations:
                messagebox.showinfo("Nenhum Resultado", f"Nenhuma estação encontrada para '{search_term}'.", parent=self)
                self.status_var.set(f"Nenhum resultado para '{search_term}'")
                logger.info("Nenhuma estação encontrada.")
                # Não precisa de return aqui, o finally cuidará do botão
            else:
                logger.info(f"Encontradas {len(stations)} estações.")
                count = 0
                for station in stations:
                    # Pega nome e URL (ignora estações sem URL válida)
                    name = station.get('name', '').strip()
                    # Tenta url_resolved primeiro, depois url normal
                    url = station.get('url_resolved') or station.get('url')

                    if name and url and url.startswith(('http://', 'https://')):
                        # Adiciona à lista visível (evita duplicatas de nome na exibição)
                        # Verifica se o nome já existe nos dados para evitar duplicatas visuais
                        if name not in self._search_results_data:
                             display_text = f"{name}"
                             # Opcional: adicionar mais info como país ou tags
                             country = station.get('countrycode')
                             # tags = station.get('tags') # Descomente se quiser mostrar tags
                             if country:
                                 display_text += f" ({country})"
                             # if tags:
                             #     display_text += f" [{tags[:30]}]" # Limita tamanho das tags
                             self.results_listbox.insert(END, display_text)
                             # Armazena URL associada ao nome exato
                             self._search_results_data[name] = url
                             count += 1

                logger.info(f"{count} estações válidas adicionadas aos resultados.")
                self.status_var.set(f"{count} estações encontradas para '{search_term}'.")
                if count == 0 and stations: # Se houve resposta mas nenhuma válida
                     messagebox.showinfo("Nenhum Resultado Válido", "Nenhuma estação com URL válida encontrada nos resultados.", parent=self)


        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao buscar estações: {search_term}", exc_info=True)
            self.status_var.set("Tempo esgotado ao buscar.")
            messagebox.showerror("Erro de Rede", "A busca demorou muito para responder (timeout). Tente novamente.", parent=self)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede ao buscar estações: {e}", exc_info=True)
            self.status_var.set("Erro de rede ao buscar.")
            messagebox.showerror("Erro de Rede", f"Não foi possível conectar à API de rádios:\n{e}", parent=self)
        except json.JSONDecodeError as e:
             logger.error(f"Erro ao decodificar resposta JSON da API: {e}", exc_info=True)
             # Verifica se response existe antes de acessar .text
             raw_text = response.text[:500] + "..." if response else "N/A"
             logger.debug(f"Raw response text: {raw_text}")
             self.status_var.set("Erro ao processar resposta da API.")
             messagebox.showerror("Erro de API", "A resposta da API de rádios não é válida.", parent=self)
        except Exception as e:
            logger.error(f"Erro inesperado durante a busca: {e}", exc_info=True)
            self.status_var.set("Erro inesperado durante a busca.")
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro:\n{e}", parent=self)
        finally:
            # Garante que o botão de busca seja reabilitado
            self.search_button.config(state=tk.NORMAL)


    def _on_result_select(self, event=None):
        """Chamado quando um item é selecionado na lista de resultados."""
        if self.results_listbox.curselection():
            self.add_button.config(state=tk.NORMAL)
        else:
            self.add_button.config(state=tk.DISABLED)

    def _add_selected_station(self):
        """Adiciona a estação selecionada ao StationManager."""
        selected_indices = self.results_listbox.curselection()
        if not selected_indices:
            return # Nada selecionado

        selected_index = selected_indices[0]
        # Pega o texto exibido na listbox
        display_text = self.results_listbox.get(selected_index)

        # Extrai o nome real (antes do parêntese, se houver)
        station_name = display_text.split(' (')[0].strip()

        # Pega a URL correspondente do nosso dicionário interno
        station_url = self._search_results_data.get(station_name)

        if not station_url:
            logger.error(f"URL não encontrada nos dados internos para '{station_name}' (Texto: {display_text})")
            messagebox.showerror("Erro Interno", "Não foi possível obter a URL para a estação selecionada.", parent=self)
            return

        logger.info(f"Tentando adicionar estação via busca: Nome='{station_name}', URL='{station_url}'")

        # Usa o station_manager da janela pai para adicionar
        if self.parent.station_manager.add_station(station_name, station_url):
            logger.info(f"Estação '{station_name}' adicionada com sucesso pelo diálogo de busca.")
            messagebox.showinfo("Estação Adicionada", f"A estação '{station_name}' foi adicionada à sua lista.", parent=self)
            # Atualiza a lista na janela principal!
            self.parent._update_station_list()
            # Opcional: fechar o diálogo após adicionar?
            # self.destroy()
            # Opcional: Limpar seleção e desabilitar botão Add após adicionar
            self.results_listbox.selection_clear(0, END)
            self.add_button.config(state=tk.DISABLED)
        else:
            logger.error(f"Falha ao salvar a estação '{station_name}' via diálogo de busca.")
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a estação '{station_name}'. Verifique os logs.", parent=self)
