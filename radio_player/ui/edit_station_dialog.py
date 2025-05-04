# /home/marcos/projeto1/radio_player/ui/edit_station_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class EditStationDialog(tk.Toplevel):
    """Janela de diálogo para editar nome e URL de uma estação existente."""

    def __init__(self, parent, old_name, old_url):
        """
        Inicializa o diálogo de edição.

        Args:
            parent: A janela principal (MainWindow) que abriu este diálogo.
            old_name: O nome atual da estação a ser editada.
            old_url: A URL atual da estação a ser editada.
        """
        super().__init__(parent)
        self.parent = parent # Referência à MainWindow
        self.old_name = old_name # Guarda o nome original para a atualização

        self.title(f"Editar Estação: {old_name}")
        # Define um tamanho fixo e impede redimensionamento
        self.geometry("450x150")
        self.resizable(False, False)

        # Variáveis Tkinter para os campos de entrada
        self.name_var = tk.StringVar(value=old_name)
        self.url_var = tk.StringVar(value=old_url)

        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Configura grid
        main_frame.columnconfigure(1, weight=1) # Coluna da Entry expande

        # Widgets
        name_label = ttk.Label(main_frame, text="Nome:")
        name_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)

        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)

        url_label = ttk.Label(main_frame, text="URL:")
        url_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W)

        url_entry = ttk.Entry(main_frame, textvariable=self.url_var)
        url_entry.grid(row=1, column=1, pady=5, sticky=tk.EW)

        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0), sticky=tk.E)

        save_button = ttk.Button(button_frame, text="Salvar", command=self._save_changes, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side=tk.LEFT)

        # Foco inicial
        name_entry.focus_set()
        name_entry.selection_range(0, tk.END) # Seleciona todo o texto inicial

        # Tornar modal
        self.grab_set()
        self.wait_window()

    def _save_changes(self):
        """Pega os novos valores e chama o método de confirmação na janela pai."""
        new_name = self.name_var.get().strip()
        new_url = self.url_var.get().strip()

        # Chama o método _confirm_edit da MainWindow para validar e salvar
        if self.parent._confirm_edit(self.old_name, new_name, new_url):
            self.destroy() # Fecha o diálogo se a confirmação for bem-sucedida
        # Se _confirm_edit retornar False (erro de validação), o diálogo permanece aberto