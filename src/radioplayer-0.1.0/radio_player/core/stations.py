# /home/marcos/projeto1/radio_player/core/stations.py
import json
import logging
import os
import pathlib # Usar pathlib para manipulação de caminhos mais moderna

# Importar constantes e as funções de busca de caminho
from radio_player.constants import get_data_path, get_user_data_path # <<< Importar novas funções

logger = logging.getLogger(__name__)


class StationManager:
    """Gerencia o carregamento, salvamento e acesso às estações de rádio."""

    def __init__(self):
        """
        Inicializa o StationManager.
        Define os caminhos corretos e carrega as estações.
        """
        # Define os caminhos usando as funções de constants.py
        self.user_stations_path = get_user_data_path("stations.json") # Onde salvar/ler dados do usuário
        self.default_stations_path = get_data_path("assets/stations.json") # De onde carregar o padrão

        logger.info(f"Caminho padrão das estações (pacote): {self.default_stations_path}")
        logger.info(f"Caminho das estações do usuário: {self.user_stations_path}")

        # A função get_user_data_path já garante que o diretório exista

        self.stations = self._load_stations() # Carrega as estações (do usuário ou padrão)


    def _load_stations(self) -> list[dict]:
        """
        Carrega as estações do arquivo do usuário.
        Se não existir, tenta copiar do arquivo padrão do pacote.
        Retorna uma lista de dicionários de estações ou uma lista vazia em caso de erro.
        """
        stations_data = []
        try:
            # 1. Tenta carregar do arquivo do usuário
            logger.debug(f"Tentando carregar estações de: {self.user_stations_path}")
            with open(self.user_stations_path, 'r', encoding='utf-8') as f:
                stations_data = json.load(f)
            logger.info(f"Estações carregadas com sucesso de '{self.user_stations_path}'.")

        except FileNotFoundError:
            logger.info(f"Arquivo de estações do usuário '{self.user_stations_path}' não encontrado.")
            # 2. Se o arquivo do usuário não existe, tenta carregar do padrão do pacote
            try:
                logger.debug(f"Tentando carregar estações padrão de: {self.default_stations_path}")
                if self.default_stations_path.exists(): # Usa .exists() de pathlib
                    with open(self.default_stations_path, 'r', encoding='utf-8') as f_default:
                        stations_data = json.load(f_default)
                    logger.info(f"Estações padrão carregadas de '{self.default_stations_path}'.")

                    # 3. Tenta copiar o arquivo padrão para o local do usuário na primeira vez
                    try:
                        # Garante que o diretório pai exista antes de escrever
                        self.user_stations_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(self.user_stations_path, 'w', encoding='utf-8') as f_user:
                            json.dump(stations_data, f_user, indent=4, ensure_ascii=False)
                        logger.info(f"Estações padrão copiadas para '{self.user_stations_path}'.")
                    except IOError as e_copy:
                        logger.error(f"Falha ao copiar estações padrão para '{self.user_stations_path}': {e_copy}")
                        # Continua com os dados carregados do padrão, mas não foram salvos para o usuário
                else:
                    logger.warning(f"Arquivo de estações padrão '{self.default_stations_path}' também não encontrado. Iniciando com lista vazia.")
                    stations_data = [] # Inicia vazio se nem o padrão existe

            except json.JSONDecodeError as e_json_default:
                logger.error(f"Erro ao decodificar JSON do arquivo padrão '{self.default_stations_path}': {e_json_default}. Iniciando com lista vazia.")
                stations_data = []
            except IOError as e_io_default:
                logger.error(f"Erro de I/O ao ler arquivo padrão '{self.default_stations_path}': {e_io_default}. Iniciando com lista vazia.")
                stations_data = []
            except Exception as e: # Captura outras exceções ao carregar o padrão
                logger.error(f"Erro inesperado ao carregar/copiar estações padrão de '{self.default_stations_path}': {e}", exc_info=True)
                stations_data = []


        except json.JSONDecodeError as e_json:
            logger.error(f"Erro ao decodificar JSON do arquivo do usuário '{self.user_stations_path}': {e_json}. Backup pode estar corrompido ou arquivo inválido. Iniciando com lista vazia.")
            # Poderia tentar carregar um backup aqui se implementado
            stations_data = []
        except IOError as e_io:
            logger.error(f"Erro de I/O ao ler arquivo do usuário '{self.user_stations_path}': {e_io}. Iniciando com lista vazia.")
            stations_data = []
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar estações de '{self.user_stations_path}': {e}", exc_info=True)
            stations_data = []

        # Validação básica da estrutura carregada
        if not isinstance(stations_data, list) or not all(isinstance(item, dict) and "name" in item and "url" in item for item in stations_data):
            logger.warning(f"Dados carregados de '{self.user_stations_path}' não são uma lista de dicionários válida (esperado 'name' e 'url'). Resetando para lista vazia.")
            stations_data = []
            # Tenta salvar a lista vazia para corrigir o arquivo corrompido (se possível)
            self._save_stations(stations_data)


        return stations_data

    def _save_stations(self, stations_list=None):
        """
        Salva a lista de estações atual no arquivo do usuário.
        Sempre salva em ~/.local/share/..., nunca em /usr/share/...
        """
        if stations_list is None:
            stations_list = self.stations

        logger.debug(f"Tentando salvar {len(stations_list)} estações em: {self.user_stations_path}")
        try:
            # Garante que o diretório pai exista antes de escrever
            self.user_stations_path.parent.mkdir(parents=True, exist_ok=True)
            # Cria um arquivo temporário para escrita segura (evita corromper em caso de falha)
            temp_file_path = self.user_stations_path.with_suffix(".tmp")
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(stations_list, f, indent=4, ensure_ascii=False) # ensure_ascii=False para nomes com acentos

            # Renomeia o arquivo temporário para o final (operação atômica na maioria dos sistemas)
            os.replace(temp_file_path, self.user_stations_path) # Use os.replace para atomicidade
            logger.info(f"Estações salvas com sucesso em '{self.user_stations_path}'.")
            return True
        except IOError as e:
            logger.error(f"Erro de I/O ao salvar estações em '{self.user_stations_path}': {e}", exc_info=True)
            # Tenta remover o arquivo temporário se ele existir
            if temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except OSError:
                    pass
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar estações: {e}", exc_info=True)
            if 'temp_file_path' in locals() and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except OSError:
                    pass
            return False

    def get_station_names(self) -> list[str]:
        """Retorna uma lista com os nomes de todas as estações."""
        return [station.get("name", "Nome Inválido") for station in self.stations]

    def get_station_url(self, name: str) -> str | None:
        """Retorna a URL da estação com o nome fornecido, ou None se não encontrada."""
        for station in self.stations:
            if station.get("name") == name:
                return station.get("url")
        return None

    def add_station(self, name: str, url: str) -> bool:
        """Adiciona uma nova estação à lista e salva. Retorna False se o nome já existe."""
        if not name or not url:
            logger.warning("Tentativa de adicionar estação com nome ou URL vazios.")
            return False
        if self.get_station_url(name) is not None:
            logger.warning(f"Tentativa de adicionar estação com nome duplicado: '{name}'")
            return False

        new_station = {"name": name, "url": url}
        self.stations.append(new_station)
        logger.info(f"Estação '{name}' adicionada à lista em memória.")
        return self._save_stations() # Salva a lista atualizada

    def update_station(self, old_name: str, new_name: str, new_url: str) -> bool:
        """Atualiza o nome e/ou URL de uma estação existente e salva."""
        if not new_name or not new_url:
             logger.warning("Tentativa de atualizar estação com nome ou URL vazios.")
             return False

        # Verifica duplicidade do novo nome (se for diferente do antigo)
        if new_name != old_name and self.get_station_url(new_name) is not None:
             logger.warning(f"Tentativa de renomear para nome duplicado: '{new_name}'")
             return False

        updated = False
        for station in self.stations:
            if station.get("name") == old_name:
                station["name"] = new_name
                station["url"] = new_url
                updated = True
                logger.info(f"Estação '{old_name}' atualizada para '{new_name}' em memória.")
                break # Para após encontrar e atualizar

        if updated:
            return self._save_stations() # Salva a lista atualizada
        else:
            logger.error(f"Estação '{old_name}' não encontrada para atualização.")
            return False

    def remove_station(self, name: str) -> bool:
        """Remove uma estação pelo nome e salva."""
        original_length = len(self.stations)
        self.stations = [station for station in self.stations if station.get("name") != name]

        if len(self.stations) < original_length:
            logger.info(f"Estação '{name}' removida da lista em memória.")
            return self._save_stations() # Salva a lista atualizada
        else:
            logger.warning(f"Estação '{name}' não encontrada para remoção.")
            return False
