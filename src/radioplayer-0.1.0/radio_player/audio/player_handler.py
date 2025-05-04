import vlc
import time
import logging

# A configuração de logging é feita no ponto de entrada (main.py)
logger = logging.getLogger(__name__)

class RadioPlayer:
    """
    Gerencia a reprodução de streams de rádio online usando VLC.
    """
    def __init__(self):
        """Inicializa a instância do VLC e o player."""
        try:
            # '--no-xlib' pode ser útil em ambientes sem GUI direta (como alguns Linux)
            # Você pode adicionar outras opções do VLC aqui se necessário
            self._instance = vlc.Instance('--no-xlib --quiet')
            self._player = self._instance.media_player_new()
            logger.info("Instância VLC e player criados com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar o VLC: {e}", exc_info=True)
            # Você pode querer levantar a exceção ou ter um estado de erro na classe
            self._instance = None
            self._player = None
            raise RuntimeError("Falha ao inicializar o backend de áudio VLC.") from e

    def play(self, stream_url) -> bool:
        """
        Toca um stream de rádio a partir da URL fornecida.

        Args:
            stream_url (str): A URL do stream de rádio online.

        Returns:
            bool: True se o comando play foi enviado com sucesso, False caso contrário.
        """
        if not self._player:
            logger.error("Player não inicializado. Não é possível tocar.")
            return False

        logger.info(f"Tentando tocar URL: {stream_url}")
        try:
            media = self._instance.media_new(stream_url)
            # Opcional: Ajustar o cache de rede (em milissegundos)
            # media.add_option('network-caching=1000')
            self._player.set_media(media)
            self._player.play()
            # Pequena pausa para dar tempo ao VLC de iniciar o buffering/play
            time.sleep(0.5) # Considerar usar eventos VLC para mais robustez
            logger.debug(f"Comando play enviado para: {stream_url}")
            return True
        except Exception as e:
            logger.error(f"Erro ao tentar tocar {stream_url}: {e}", exc_info=True)
            return False

    def stop(self):
        """Para a reprodução atual."""
        if self._player:
            logger.info("Parando a reprodução.")
            self._player.stop()

    def get_state(self):
        """Retorna o estado atual do player VLC."""
        if self._player:
            # Retorna um objeto vlc.State
            return self._player.get_state()
        # Poderia retornar um estado específico para 'não inicializado' ou 'erro'
        return None

    # --- Métodos adicionais que podem ser úteis ---

    def set_volume(self, volume: int):
        """Define o volume (0 a 100)."""
        if self._player:
            # Garante que o volume esteja no range válido do VLC (0-100)
            vol = max(0, min(100, int(volume))) # Converte para int por segurança
            result = self._player.audio_set_volume(vol)
            if result == 0: # Sucesso
                logger.debug(f"Volume definido para {vol}")
            else: # Erro
                logger.warning(f"Falha ao definir volume para {vol} (Código de erro: {result})")
            return result == 0 # Retorna True se sucesso, False se falha
        return False # Player não existe

    def get_volume(self) -> int:
        """Retorna o volume atual (0 a 100), ou -1 se não disponível."""
        if self._player:
            return self._player.audio_get_volume()
        return -1 # Indica erro ou não disponível

    def is_playing(self) -> bool:
        """Verifica se o estado atual é 'Playing'."""
        if self._player:
            # Compara o estado atual com o estado vlc.State.Playing
            # vlc.State é uma enumeração, então precisamos importar vlc para usá-la
            return self._player.get_state() == vlc.State.Playing
        return False # Player não existe ou não inicializado

    def release(self):
        """Libera os recursos do VLC quando não for mais necessário."""
        if self._player:
            # Garante que parou antes de liberar
            current_state = self._player.get_state()
            if current_state != vlc.State.Stopped and current_state != vlc.State.Error:
                 self.stop()
            self._player.release()
            self._player = None
            logger.info("Player VLC liberado.")
        if self._instance:
            self._instance.release()
            self._instance = None
            logger.info("Instância VLC liberada.")
