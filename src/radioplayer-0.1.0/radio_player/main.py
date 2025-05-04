# /home/marcos/projeto1/radio_player/main.py
import logging
import sys
import tkinter as tk # Necessário para capturar exceções do Tkinter
# Importar messagebox para mostrar erros na inicialização, se possível
from tkinter import messagebox

# Importar as classes principais da aplicação
# Note os caminhos relativos agora que main.py está dentro de radio_player
from .audio.player_handler import RadioPlayer
from .ui.main_window import MainWindow
from .core.stations import StationManager

# Configuração básica de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)] # Garante saída no console
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para iniciar a aplicação."""
    logger.info("Iniciando a aplicação Radio Player Simples...")

    player = None # Inicializa como None
    try:
        # Inicializa os componentes principais
        player = RadioPlayer() # Pode levantar RuntimeError
        station_manager = StationManager() # Agora lida com caminhos de usuário/sistema
        logger.info("Gerenciador de estações carregado.")

        # Cria e executa a janela principal da UI
        logger.info("Criando a janela principal...")
        app = MainWindow(player, station_manager)
        app.mainloop() # Inicia o loop de eventos do Tkinter

    except RuntimeError as e:
        logger.critical(f"Erro fatal de runtime ao inicializar: {e}", exc_info=True)
        # Tenta mostrar uma mensagem de erro gráfica se o Tkinter básico funcionar
        try:
            root = tk.Tk()
            root.withdraw() # Esconde a janela raiz principal
            messagebox.showerror("Erro Crítico", f"Não foi possível iniciar o player de áudio (VLC está instalado e acessível?):\n{e}")
            root.destroy()
        except tk.TclError:
            pass # Ignora se nem o Tkinter básico puder ser iniciado
        sys.exit(f"Erro crítico: {e}")
    except tk.TclError as e:
        logger.critical(f"Erro fatal de Tkinter/Tcl: {e}", exc_info=True)
        # Não podemos usar messagebox aqui, pois o Tkinter falhou
        sys.exit(f"Erro crítico de interface gráfica: {e}")
    except Exception as e:
        logger.critical(f"Erro inesperado na inicialização: {e}", exc_info=True)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado:\n{e}")
            root.destroy()
        except tk.TclError:
            pass
        sys.exit(f"Erro inesperado: {e}")
    finally:
        # Limpeza de recursos é feita principalmente no _on_closing da MainWindow
        # Mas garantimos que o player seja liberado se a inicialização falhar antes do mainloop
        if player and 'app' not in locals(): # Se player foi criado mas app não (erro antes do mainloop)
             logger.info("Liberando recursos do player devido a erro na inicialização.")
             player.release()
        logger.info("Aplicação finalizada.")

# Ponto de entrada padrão do Python
if __name__ == "__main__":
    main()
