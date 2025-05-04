# /home/marcos/projeto1/radio_player/ui/main_window.py
import tkinter as tk
from tkinter import ttk, PhotoImage, Listbox, Scrollbar, messagebox, simpledialog
import logging
import vlc # Para verificar vlc.State
import os # Para os.path.basename

# Tenta importar o tema sv_ttk
try:
    import sv_ttk
except ImportError:
    sv_ttk = None

# Importar componentes da aplicação
from radio_player.audio.player_handler import RadioPlayer
from radio_player.core.stations import StationManager
from radio_player.constants import get_data_path # <<< Usar get_data_path para ícone/padrões

# Importar diálogos customizados (com tratamento de erro)
try:
    from .search_dialog import SearchDialog
except ImportError as e:
    SearchDialog = None
    logging.warning(f"Não foi possível importar SearchDialog: {e}. Funcionalidade de busca online desabilitada.")

try:
    # Certifique-se que o nome da classe está correto no arquivo edit_station_dialog.py
    from .edit_station_dialog import EditStationDialog
except ImportError as e:
    EditStationDialog = None
    # Log mais detalhado para o erro de importação
    logging.warning(f"Não foi possível importar EditStationDialog: {e}. Usando diálogo simples para edição.", exc_info=True)


logger = logging.getLogger(__name__)

class MainWindow(tk.Tk):
    """Janela principal da aplicação Radio Player."""

    def __init__(self, player: RadioPlayer, station_manager: StationManager):
        super().__init__()

        # Aplica o tema se disponível
        if sv_ttk:
            try:
                sv_ttk.set_theme("dark") # Ou "light"
                logger.debug("Tema sv_ttk aplicado.")
            except Exception as e:
                logger.warning(f"Falha ao aplicar tema sv_ttk: {e}")

        self.player = player
        self.station_manager = station_manager

        # --- Configuração da Janela ---
        self.title("Rádio Player Simples")
        try:
            # Usa get_data_path para encontrar o ícone
            icon_path_obj = get_data_path("assets/radio_icon.png") # <<< Usando get_data_path
            icon_path = str(icon_path_obj) # Converte para string para PhotoImage
            if icon_path and os.path.exists(icon_path):
                 # Guarda a referência da imagem em self._app_icon para evitar garbage collection
                self._app_icon = PhotoImage(file=icon_path)
                self.iconphoto(True, self._app_icon) # Usa a referência guardada
                logger.debug(f"Ícone carregado de: {icon_path}")
            else:
                logger.warning(f"Arquivo de ícone não encontrado ou caminho inválido: {icon_path}")
                self._app_icon = None
        except tk.TclError as e:
            logger.error(f"Erro de Tkinter ao carregar o ícone '{icon_path}': {e}")
            self._app_icon = None
        except Exception as e:
            logger.error(f"Erro inesperado ao definir ícone: {e}")
            self._app_icon = None

        # Define um tamanho inicial mínimo e permite redimensionar
        self.minsize(500, 350)
        self.geometry("550x400") # Tamanho inicial um pouco maior

        # --- Variáveis de Controle Tkinter ---
        self.volume_var = tk.IntVar(value=self.player.get_volume() if self.player else 70)
        self.volume_percent_var = tk.StringVar(value=f"{self.volume_var.get()}%")
        self.status_var = tk.StringVar(value="Pronto")
        self.selected_station_var = tk.StringVar()

        # --- Estado Interno ---
        self._is_muted = False
        self._volume_before_mute = self.volume_var.get()
        self._status_check_job = None # ID do job 'after' para checagem de status
        self._has_reached_playing = False # Flag para saber se já atingiu o estado 'Playing'

        # --- Criação dos Widgets ---
        self._create_widgets() # <<< Chamada para o método

        # --- Configurações Finais ---
        self._update_station_list() # Popula a combobox
        self._update_nav_buttons_state() # Atualiza estado dos botões de navegação
        self.volume_var.set(self.player.get_volume()) # Garante que o slider reflita o volume inicial do player
        self._update_volume_label() # Atualiza o label de porcentagem

        # Configura o fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("Janela principal criada e configurada.")


    def _create_widgets(self): # <<< Definição do método (indentação correta)
        """Cria e organiza os widgets na janela principal."""
        logger.debug("Criando widgets da UI...")
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Configura grid para expandir
        main_frame.columnconfigure(0, weight=1) # Coluna 0 (Play/Stop)
        main_frame.columnconfigure(1, weight=1) # Coluna 1 (Gerenciar)
        main_frame.columnconfigure(2, weight=1) # Coluna 2 (Gerenciar)
        # Dar peso às linhas 1 e 2 para que os botões Play/Stop e Gerenciar compartilhem o espaço
        main_frame.rowconfigure(1, weight=1) # Linha 1 (Play, Add, Edit)
        main_frame.rowconfigure(2, weight=1) # Linha 2 (Stop, Remove, Search)

        # --- Frame de Navegação e Seleção ---
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=0, column=0, columnspan=3, sticky=tk.EW, pady=(0, 10))
        nav_frame.columnconfigure(1, weight=1) # Faz a combobox expandir

        self.prev_button = ttk.Button(nav_frame, text="◀ Anterior", command=self._select_prev_station)
        self.prev_button.grid(row=0, column=0, padx=(0, 5))

        self.station_combobox = ttk.Combobox(
            nav_frame,
            textvariable=self.selected_station_var,
            state="readonly", # Impede digitação direta
            postcommand=self._update_station_list # Atualiza a lista antes de mostrar
        )
        self.station_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.station_combobox.bind("<<ComboboxSelected>>", self._on_station_select)

        self.next_button = ttk.Button(nav_frame, text="Próxima ▶", command=self._select_next_station)
        self.next_button.grid(row=0, column=2, padx=(5, 0))


        # --- Controles de Playback (Direto no main_frame) ---
        self.play_button = ttk.Button(main_frame, text="▶ Play", command=self._play_radio, style="Accent.TButton") # Pai é main_frame
        # Coluna 0, Linha 1. Sticky nsew para preencher a célula
        self.play_button.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=(5, 2))

        self.stop_button = ttk.Button(main_frame, text="■ Stop", command=self._stop_radio, state=tk.DISABLED) # Pai é main_frame
        # Coluna 0, Linha 2. Sticky nsew para preencher a célula
        self.stop_button.grid(row=2, column=0, sticky='nsew', padx=(0, 5), pady=(2, 5))

        # --- Frame de Gerenciamento de Estações ---
        manage_frame = ttk.LabelFrame(main_frame, text="Gerenciar Estações", padding="10")
        # Coluna 1, Linha 1, ocupando 2 linhas e 2 colunas
        manage_frame.grid(row=1, column=1, rowspan=2, columnspan=2, sticky=tk.NSEW, padx=(5, 0), pady=5)
        manage_frame.columnconfigure(0, weight=1) # Coluna interna 0 (Add, Remove)
        manage_frame.columnconfigure(1, weight=1) # Coluna interna 1 (Edit, Search)

        self.add_button = ttk.Button(manage_frame, text="Adicionar", command=self._add_station_dialog)
        self.add_button.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5), pady=2) # Linha 0, Coluna 0 (dentro do manage_frame)

        self.edit_button = ttk.Button(manage_frame, text="Editar", command=self._edit_station_dialog)
        self.edit_button.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0), pady=2) # Linha 0, Coluna 1 (dentro do manage_frame)

        self.remove_button = ttk.Button(manage_frame, text="Remover", command=self._remove_station_dialog)
        self.remove_button.grid(row=1, column=0, sticky=tk.EW, padx=(0, 5), pady=2) # Linha 1, Coluna 0 (dentro do manage_frame)

        search_state = tk.NORMAL if SearchDialog else tk.DISABLED
        self.search_button = ttk.Button(manage_frame, text="Buscar Online", command=self._open_search_dialog, state=search_state)
        self.search_button.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0), pady=2) # Linha 1, Coluna 1 (dentro do manage_frame)


        # --- Frame de Volume ---
        volume_frame = ttk.Frame(main_frame)
        # Mover para linha 3, abaixo dos botões
        volume_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(10, 0))
        volume_frame.columnconfigure(1, weight=1) # Slider expande

        ttk.Label(volume_frame, text="Volume:").grid(row=0, column=0, padx=(0, 5))

        self.volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self._set_volume # Chama _set_volume quando o valor muda
        )
        self.volume_slider.grid(row=0, column=1, sticky=tk.EW, padx=5)

        self.volume_label = ttk.Label(volume_frame, textvariable=self.volume_percent_var, width=4)
        self.volume_label.grid(row=0, column=2, padx=5)

        self.mute_button = ttk.Button(volume_frame, text="Mudo", command=self._toggle_mute)
        self.mute_button.grid(row=0, column=3, padx=(5, 0))

        # --- Barra de Status ---
        status_bar = ttk.Frame(self, relief=tk.SUNKEN, padding=(5, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_label = ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X)

        logger.debug("Widgets criados.")

    # --- Métodos de Atualização da UI ---

    def _update_station_list(self):
        """Atualiza a lista de estações na Combobox."""
        logger.debug("Atualizando lista de estações na Combobox.")
        current_selection = self.selected_station_var.get()
        station_names = self.station_manager.get_station_names()
        self.station_combobox['values'] = station_names

        if station_names:
            if current_selection in station_names:
                # Mantém a seleção se ainda existir
                self.selected_station_var.set(current_selection)
            elif not self.selected_station_var.get(): # Se nada estiver selecionado
                 # Seleciona a primeira estação se a lista não estiver vazia e nada selecionado
                 self.selected_station_var.set(station_names[0])
        else:
            # Limpa a seleção se não houver estações
            self.selected_station_var.set("")

        self._update_management_buttons_state() # Atualiza botões Editar/Remover
        logger.debug(f"Lista de estações atualizada. Selecionada: '{self.selected_station_var.get()}'")


    def _update_nav_buttons_state(self):
        """Habilita/desabilita botões de navegação Anterior/Próxima."""
        station_names = self.station_manager.get_station_names()
        num_stations = len(station_names)
        state = tk.NORMAL if num_stations > 1 else tk.DISABLED
        self.prev_button.config(state=state)
        self.next_button.config(state=state)
        logger.info(f"Atualizando estado botões Navegação: {num_stations} estações -> Estado={state}") # Log mais visível

    def _update_management_buttons_state(self):
        """Habilita/desabilita botões Editar/Remover baseado na seleção."""
        state = tk.NORMAL if self.selected_station_var.get() else tk.DISABLED
        self.edit_button.config(state=state)
        self.remove_button.config(state=state)
        logger.debug(f"Estado dos botões Editar/Remover atualizado para: {state}")

    def _update_volume_label(self, value=None):
        """Atualiza o label de porcentagem do volume."""
        if value is None:
            value = self.volume_var.get()
        self.volume_percent_var.set(f"{int(value)}%")
        # Atualiza texto do botão Mudo
        if self._is_muted:
            self.mute_button.config(text="Som")
        else:
            self.mute_button.config(text="Mudo")


    def _reset_ui_to_stopped_state(self):
        """Reseta a UI para o estado 'parado'."""
        logger.debug("Resetando UI para o estado 'Parado'.")
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.station_combobox.config(state="readonly")
        self.add_button.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL if SearchDialog else tk.DISABLED)
        self._update_management_buttons_state() # Habilita/desabilita Ed/Rm baseado na seleção
        self._update_nav_buttons_state() # Habilita/desabilita Prev/Next
        self.status_var.set("Parado")
        self._has_reached_playing = False # Reseta a flag


    # --- Callbacks de Eventos ---

    def _on_station_select(self, event=None):
        """Chamado quando uma estação é selecionada na Combobox."""
        station_name = self.selected_station_var.get()
        if station_name:
            logger.info(f"Estação '{station_name}' selecionada pelo usuário.")
            self._update_management_buttons_state() # Atualiza Ed/Rm
            # Decide se toca automaticamente ao selecionar (opcional)
            # self._play_radio() # Descomente para tocar ao selecionar
        else:
            logger.debug("Seleção da Combobox limpa.")
            self._update_management_buttons_state() # Atualiza Ed/Rm

    def _on_closing(self):
        """Chamado quando a janela é fechada."""
        logger.info("Sinal de fechamento da janela recebido.")
        self._cancel_status_check() # Para a checagem de status
        if self.player:
            logger.info("Liberando recursos do player VLC...")
            self.player.release() # Libera recursos do VLC
            logger.info("Recursos do player liberados.")
        else:
            logger.warning("Objeto Player não encontrado durante o fechamento.")
        logger.info("Destruindo a janela principal.")
        self.destroy() # Fecha a janela Tkinter

    # --- Ações de Playback ---

    def _play_radio(self):
        """Inicia a reprodução da estação selecionada."""
        station_name = self.selected_station_var.get()
        if not station_name:
            messagebox.showwarning("Nenhuma Estação", "Selecione uma estação para tocar.")
            logger.warning("Tentativa de Play sem estação selecionada.")
            return

        station_url = self.station_manager.get_station_url(station_name)
        if not station_url:
            messagebox.showerror("Erro", f"Não foi possível encontrar a URL para '{station_name}'.")
            logger.error(f"URL não encontrada para a estação '{station_name}'.")
            return

        logger.info(f"Tentando tocar '{station_name}' - URL: {station_url}")
        self.status_var.set(f"Conectando a {station_name}...")
        self._has_reached_playing = False # Reseta flag antes de tentar tocar

        # Desabilita controles enquanto conecta
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL) # Habilita Stop imediatamente
        self.station_combobox.config(state=tk.DISABLED)
        self.add_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)
        self.remove_button.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        # self.prev_button.config(state=tk.DISABLED) # Não desabilitar durante play
        # self.next_button.config(state=tk.DISABLED) # Não desabilitar durante play

        try:
            if self.player.play(station_url):
                logger.info(f"Comando play enviado para VLC com URL: {station_url}")
                # Inicia a checagem de status para atualizar a UI
                self._schedule_status_check()
            else:
                # Se player.play() retornar False imediatamente
                raise RuntimeError("Falha ao iniciar a mídia no player VLC.")

        except Exception as e:
            logger.error(f"Erro ao tentar tocar a estação '{station_name}': {e}", exc_info=True)
            messagebox.showerror("Erro de Reprodução", f"Não foi possível tocar a estação '{station_name}'.\nVerifique a URL e sua conexão.\n\nDetalhe: {e}")
            self._reset_ui_to_stopped_state() # Volta ao estado parado

    def _stop_radio(self):
        """Para a reprodução atual."""
        logger.info("Comando Stop recebido.")
        self._cancel_status_check() # Para a checagem de status
        if self.player:
            self.player.stop()
            logger.info("Comando stop enviado para VLC.")
        self._reset_ui_to_stopped_state()


    # --- Controle de Volume ---

    def _set_volume(self, value):
        """Define o volume do player e atualiza a UI."""
        volume_level = int(float(value)) # Valor do slider pode ser float
        logger.debug(f"Slider movido para: {volume_level}")
        if self.player:
            if self.player.set_volume(volume_level):
                logger.info(f"Volume definido para {volume_level}%")
                # Se estava mudo e o usuário mexeu no slider, desmuta
                if self._is_muted and volume_level > 0:
                    self._is_muted = False
                    self._volume_before_mute = volume_level # Atualiza volume pré-mute
                    logger.info("Desmutado automaticamente ao mover o slider.")
                elif not self._is_muted:
                     self._volume_before_mute = volume_level # Atualiza volume pré-mute se não estiver mudo
                self._update_volume_label(volume_level)
            else:
                logger.warning(f"Falha ao definir volume para {volume_level}% no player.")
        else:
             logger.warning("Tentativa de definir volume sem player inicializado.")
        # Atualiza a variável Tkinter explicitamente (embora já deva estar ligada)
        self.volume_var.set(volume_level)


    def _toggle_mute(self):
        """Alterna o estado Mudo/Som."""
        if not self.player:
            logger.warning("Tentativa de mutar/desmutar sem player.")
            return

        if self._is_muted:
            # Desmutar: Volta ao volume anterior
            logger.info(f"Desmutando. Voltando para volume {self._volume_before_mute}%.")
            self.player.set_volume(self._volume_before_mute)
            self.volume_var.set(self._volume_before_mute) # Atualiza slider
            self._is_muted = False
        else:
            # Mutar: Guarda o volume atual e define para 0
            self._volume_before_mute = self.player.get_volume() # Guarda o volume atual do player
            logger.info(f"Mutando. Volume anterior era {self._volume_before_mute}%. Definindo para 0%.")
            self.player.set_volume(0)
            self.volume_var.set(0) # Atualiza slider
            self._is_muted = True

        self._update_volume_label() # Atualiza label e texto do botão


    # --- Navegação de Estações ---

    def _select_station_by_index_offset(self, offset):
        """Seleciona e toca uma estação baseado no índice atual + offset."""
        station_names = self.station_manager.get_station_names()
        if len(station_names) < 2: # Não faz nada se tiver 0 ou 1 estação
            logger.debug("Navegação ignorada: menos de 2 estações.")
            return

        current_name = self.selected_station_var.get()
        try:
            current_index = station_names.index(current_name)
        except ValueError:
            # Se a estação atual não está na lista (improvável, mas seguro)
            current_index = 0 # Vai para a primeira

        new_index = (current_index + offset) % len(station_names)
        new_station_name = station_names[new_index]

        logger.info(f"Navegando para estação índice {new_index}: '{new_station_name}'")
        self.selected_station_var.set(new_station_name)
        self._play_radio() # Toca a nova estação selecionada

    def _select_prev_station(self):
        """Seleciona a estação anterior."""
        logger.debug("Botão Anterior pressionado.")
        self._select_station_by_index_offset(-1)

    def _select_next_station(self):
        """Seleciona a próxima estação."""
        logger.debug("Botão Próxima pressionado.")
        self._select_station_by_index_offset(1)


    # --- Checagem de Status do Player ---

    def _schedule_status_check(self):
        """Agenda a próxima verificação de status do player."""
        # Cancela qualquer job anterior para evitar duplicação
        self._cancel_status_check()
        # Agenda para rodar _check_playback_status após 1000ms (1 segundo)
        self._status_check_job = self.after(1000, self._check_playback_status)
        logger.debug(f"Checagem de status agendada. Job ID: {self._status_check_job}")

    def _cancel_status_check(self):
        """Cancela a verificação de status agendada, se houver."""
        if self._status_check_job:
            logger.debug(f"Cancelando checagem de status agendada. Job ID: {self._status_check_job}")
            self.after_cancel(self._status_check_job)
            self._status_check_job = None

    def _check_playback_status(self):
        """Verifica o status do player e atualiza a UI. Reagenda se necessário."""
        if not self.player:
            logger.warning("Checagem de status abortada: player não existe.")
            self._reset_ui_to_stopped_state()
            return

        try:
            current_state = self.player.get_state()
            logger.debug(f"Checando status do player. Estado atual: {current_state}")

            # Atualiza o texto da barra de status
            self._update_status_text(current_state)

            # Lógica de reagendamento e UI
            active_states = {
                vlc.State.Playing,
                vlc.State.Buffering,
                vlc.State.Opening
            }

            if current_state in active_states:
                # Se atingiu o estado Playing pela primeira vez, ajusta o volume inicial
                if current_state == vlc.State.Playing and not self._has_reached_playing:
                    logger.info("Estado 'Playing' detectado pela primeira vez. Ajustando volume inicial.")
                    self._set_volume(self.volume_var.get()) # Aplica o volume do slider
                    self._has_reached_playing = True

                # Continua tocando ou tentando, reagenda a verificação
                self._schedule_status_check()
            else:
                # Estado não ativo (Stopped, Ended, Error, etc.)
                logger.info(f"Player não está mais em estado ativo ({current_state}). Parando checagem de status.")
                if current_state == vlc.State.Error:
                    logger.error("Player VLC reportou estado de Erro.")
                    messagebox.showerror("Erro de Reprodução", "Ocorreu um erro durante a reprodução da estação.")
                elif current_state != vlc.State.Stopped: # Se parou por outro motivo (Ended, etc)
                    logger.info(f"Playback finalizado com estado: {current_state}")

                # Para a checagem e reseta a UI (exceto se já foi explicitamente parado)
                # Verifica se o botão stop já está desabilitado para evitar reset duplo
                if self.stop_button['state'] != tk.DISABLED:
                     self._reset_ui_to_stopped_state()

        except Exception as e:
            logger.error(f"Erro durante a checagem de status do player: {e}", exc_info=True)
            # Para a checagem em caso de erro e reseta a UI
            self._reset_ui_to_stopped_state()


    def _update_status_text(self, state):
        """Atualiza o texto da barra de status baseado no estado do VLC."""
        station_name = self.selected_station_var.get()
        status_text = "Status desconhecido"

        if state == vlc.State.Opening:
            status_text = f"Abrindo {station_name}..."
        elif state == vlc.State.Buffering:
            # Tenta obter a porcentagem do buffer (pode não funcionar sempre)
            try:
                media = self.player._player.get_media()
                if media:
                    # A forma de obter buffer pode variar; get_stats() pode ser útil
                    # Exemplo: stats = media.get_stats(); buffer_percent = stats.demux_read_bytes # Ajustar
                    status_text = f"Bufferizando {station_name}..." # Simplificado por enquanto
                else:
                    status_text = f"Bufferizando {station_name}..."
            except Exception:
                 status_text = f"Bufferizando {station_name}..."
        elif state == vlc.State.Playing:
            # Tenta obter metadados (título da música, etc.)
            metadata = "Metadados não disponíveis"
            try:
                media = self.player._player.get_media()
                if media:
                    # media.parse_if_needed() # Removido
                    title = media.get_meta(vlc.Meta.Title)
                    artist = media.get_meta(vlc.Meta.Artist)
                    now_playing = media.get_meta(vlc.Meta.NowPlaying) # Comum em streams

                    if now_playing:
                        metadata = now_playing
                    elif title and artist:
                        metadata = f"{artist} - {title}"
                    elif title:
                        metadata = title
                    else:
                         # Tenta pegar o nome do arquivo/URL como fallback
                         mrl = media.get_mrl()
                         if mrl:
                             metadata = os.path.basename(mrl) # Mostra nome do arquivo ou URL

                status_text = f"Tocando: {station_name} ({metadata})"

            except Exception as e:
                logger.warning(f"Não foi possível obter metadados: {e}")
                status_text = f"Tocando: {station_name}"

        elif state == vlc.State.Paused: # Embora não tenhamos botão de pause
            status_text = f"Pausado: {station_name}"
        elif state == vlc.State.Stopped:
            status_text = "Parado"
        elif state == vlc.State.Ended:
            status_text = f"Stream finalizado: {station_name}"
        elif state == vlc.State.Error:
            status_text = f"Erro ao tocar {station_name}"
        else:
            status_text = f"Estado: {state}" # Fallback para outros estados

        self.status_var.set(status_text)


    # --- Gerenciamento de Estações (Diálogos) ---

    def _add_station_dialog(self):
        """Abre um diálogo para adicionar uma nova estação."""
        logger.debug("Abrindo diálogo para adicionar estação.")
        name = simpledialog.askstring("Adicionar Estação", "Nome da Estação:", parent=self)
        if name:
            url = simpledialog.askstring("Adicionar Estação", f"URL da Rádio para '{name}':", parent=self)
            if url:
                try:
                    if self.station_manager.add_station(name, url):
                        logger.info(f"Estação '{name}' adicionada com URL: {url}")
                        self._update_station_list()
                        self.selected_station_var.set(name) # Seleciona a nova estação
                        messagebox.showinfo("Sucesso", f"Estação '{name}' adicionada.")
                    else:
                        # add_station retorna False se o nome já existe
                        messagebox.showwarning("Nome Duplicado", f"Já existe uma estação com o nome '{name}'.")
                        logger.warning(f"Tentativa de adicionar estação com nome duplicado: '{name}'")
                except Exception as e:
                    logger.error(f"Erro ao adicionar estação '{name}': {e}", exc_info=True)
                    messagebox.showerror("Erro", f"Não foi possível adicionar a estação:\n{e}")
            else:
                logger.debug("Adição cancelada (URL não fornecida).")
        else:
            logger.debug("Adição cancelada (Nome não fornecido).")


    def _edit_station_dialog(self):
        """Abre um diálogo para editar a estação selecionada."""
        old_name = self.selected_station_var.get()
        if not old_name:
            messagebox.showwarning("Nenhuma Seleção", "Selecione uma estação para editar.")
            return

        old_url = self.station_manager.get_station_url(old_name)
        if not old_url:
             messagebox.showerror("Erro Interno", f"Não foi possível encontrar a URL para '{old_name}' para edição.")
             logger.error(f"URL não encontrada para edição da estação '{old_name}'.")
             return

        logger.debug(f"Abrindo diálogo para editar estação: '{old_name}'")

        if EditStationDialog:
            # Usa o diálogo customizado se disponível
            # O diálogo customizado chama self._confirm_edit internamente
            EditStationDialog(self, old_name, old_url)
            # A atualização da lista acontece dentro de _confirm_edit se for bem sucedida
        else:
            # Fallback para simpledialog (menos ideal)
            logger.warning("Usando simpledialog como fallback para edição.")
            new_name = simpledialog.askstring("Editar Estação", "Novo nome:", initialvalue=old_name, parent=self)
            if new_name:
                new_url = simpledialog.askstring("Editar Estação", "Nova URL:", initialvalue=old_url, parent=self)
                if new_url:
                    # Chama a lógica de confirmação/atualização diretamente
                    if self._confirm_edit(old_name, new_name, new_url):
                         messagebox.showinfo("Sucesso", f"Estação '{old_name}' atualizada para '{new_name}'.")
                    # Mensagens de erro/aviso são mostradas dentro de _confirm_edit
                else:
                    logger.debug("Edição cancelada (URL não fornecida).")
            else:
                logger.debug("Edição cancelada (Nome não fornecido).")


    def _confirm_edit(self, old_name, new_name, new_url) -> bool:
        """
        Lógica para validar e salvar as alterações da edição.
        Chamado pelo EditStationDialog ou pelo fallback.
        Retorna True se bem sucedido, False caso contrário (para manter o diálogo aberto).
        """
        logger.debug(f"Confirmando edição: '{old_name}' -> '{new_name}', URL: '{new_url}'")
        if not new_name or not new_url:
             messagebox.showwarning("Entrada Inválida", "Nome e URL não podem estar vazios.", parent=self)
             return False # Mantém o diálogo aberto

        # Verifica se o novo nome já existe (e não é o nome antigo)
        if new_name != old_name and self.station_manager.get_station_url(new_name) is not None:
            messagebox.showwarning("Nome Duplicado", f"Já existe uma estação com o nome '{new_name}'.", parent=self)
            logger.warning(f"Tentativa de renomear para nome duplicado: '{new_name}'")
            return False # Mantém o diálogo aberto

        try:
            if self.station_manager.update_station(old_name, new_name, new_url):
                logger.info(f"Estação '{old_name}' atualizada para '{new_name}'.")
                self._update_station_list()
                # Garante que a estação (possivelmente renomeada) continue selecionada
                self.selected_station_var.set(new_name)
                return True # Fecha o diálogo
            else:
                 # update_station pode retornar False se old_name não for encontrado (improvável aqui)
                 messagebox.showerror("Erro", f"Não foi possível encontrar a estação original '{old_name}' para atualizar.", parent=self)
                 logger.error(f"Erro ao atualizar: estação original '{old_name}' não encontrada.")
                 return False # Mantém o diálogo aberto (ou fecha, dependendo do caso)
        except Exception as e:
            logger.error(f"Erro ao atualizar estação '{old_name}': {e}", exc_info=True)
            messagebox.showerror("Erro", f"Não foi possível atualizar a estação:\n{e}", parent=self)
            return False # Mantém o diálogo aberto


    def _remove_station_dialog(self):
        """Pede confirmação e remove a estação selecionada."""
        station_name = self.selected_station_var.get()
        if not station_name:
            messagebox.showwarning("Nenhuma Seleção", "Selecione uma estação para remover.")
            return

        logger.debug(f"Tentando remover estação: '{station_name}'")
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover a estação '{station_name}'?", parent=self):
            try:
                if self.station_manager.remove_station(station_name):
                    logger.info(f"Estação '{station_name}' removida.")
                    # Para a reprodução se a estação removida estava tocando
                    if self.player and self.player.is_playing() and self.status_var.get().startswith(f"Tocando: {station_name}"):
                         self._stop_radio()
                    self._update_station_list() # Atualiza a combobox (selecionará a primeira ou ficará vazia)
                    messagebox.showinfo("Removida", f"Estação '{station_name}' removida com sucesso.")
                else:
                    # remove_station retorna False se não encontrou
                     messagebox.showerror("Erro", f"Não foi possível encontrar a estação '{station_name}' para remover.")
                     logger.error(f"Erro ao remover: estação '{station_name}' não encontrada.")
            except Exception as e:
                 logger.error(f"Erro ao remover estação '{station_name}': {e}", exc_info=True)
                 messagebox.showerror("Erro", f"Não foi possível remover a estação:\n{e}")
        else:
            logger.debug("Remoção cancelada pelo usuário.")


    def _open_search_dialog(self):
        """Abre a janela de busca de rádios online."""
        if SearchDialog:
            logger.debug("Abrindo diálogo de busca online.")
            # Passa apenas 'self' (a MainWindow) como 'parent'
            search_dialog = SearchDialog(self) # <<< Já corrigido na versão anterior
            # O diálogo de busca acessará o station_manager via self.parent.station_manager
            # e chamará self.parent._update_station_list() se adicionar algo.
        else:
            logger.error("Funcionalidade de busca online não está disponível (SearchDialog não importado).")
            messagebox.showerror("Não Disponível", "A funcionalidade de busca online não pôde ser carregada.")


# Bloco para teste direto da janela (opcional)
if __name__ == '__main__':
    print("Executando MainWindow diretamente para teste...")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Cuidado: Precisa de instâncias funcionais de Player e StationManager
    try:
        test_player = RadioPlayer()
        # Cria um arquivo temporário para teste ou usa o padrão
        test_station_manager = StationManager()
        # Adiciona algumas estações de teste se o arquivo estiver vazio
        if not test_station_manager.get_station_names():
             print("Adicionando estações de teste...")
             test_station_manager.add_station("Teste Rádio Rock", "http://stream.examplerock.com/live")
             test_station_manager.add_station("Teste Rádio News", "http://stream.examplenews.com/live")

        main_app = MainWindow(test_player, test_station_manager)
        main_app.mainloop()
    except RuntimeError as e:
         print(f"Erro de Runtime ao iniciar teste: {e}")
    except Exception as e:
        print(f"Erro inesperado no teste: {e}")
