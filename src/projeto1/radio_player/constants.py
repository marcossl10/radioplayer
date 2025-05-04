# /home/marcos/projeto1/radio_player/constants.py
import os
import sys
import logging
import pathlib # Use pathlib para manipulação de caminhos

# Nome do pacote (deve corresponder ao pkgname no PKGBUILD)
PACKAGE_NAME = "radio-player-simples"
VERSION = "0.1.0" # Defina a versão aqui

logger = logging.getLogger(__name__)

# Caminho base para dados compartilhados (instalado)
# Corresponde ao _datadir no PKGBUILD
INSTALLED_DATA_DIR = pathlib.Path('/usr/share') / PACKAGE_NAME
# Caminho base para dados do usuário (padrão Freedesktop)
USER_DATA_DIR = pathlib.Path.home() / ".local" / "share" / PACKAGE_NAME

def is_running_from_source():
    """Verifica se o script está rodando do código fonte."""
    # Verifica se um arquivo/diretório típico do source tree existe no nível superior
    # Usa pathlib para tornar mais robusto
    project_root_marker = pathlib.Path(__file__).resolve().parent.parent / "LICENSE"
    return project_root_marker.exists()

def get_data_path(relative_path):
    """
    Retorna o caminho absoluto para um arquivo de dados padrão
    (ex: ícone, stations.json padrão).
    No modo dev, busca relativo à raiz do projeto.
    No modo instalado, busca em /usr/share/PACKAGE_NAME/.

    Args:
        relative_path: Caminho relativo ao diretório de dados
                       (ex: "assets/icon.png").

    Returns:
        O caminho absoluto (pathlib.Path) para o recurso de dados.
    """
    if is_running_from_source():
        # Rodando do código fonte
        project_root_dev = pathlib.Path(__file__).resolve().parent.parent
        source_path = project_root_dev / relative_path
        logger.debug(f"Modo Dev: Buscando data em {source_path}")
        return source_path
    else:
        # Rodando instalado
        installed_path = INSTALLED_DATA_DIR / relative_path
        logger.debug(f"Modo Instalado: Buscando data em {installed_path}")
        return installed_path

def get_user_data_path(relative_path):
    """
    Retorna o caminho absoluto para um arquivo de dados do usuário
    (ex: stations.json modificado).
    Sempre retorna um caminho dentro de ~/.local/share/PACKAGE_NAME/.

    Args:
        relative_path: Caminho relativo dentro do diretório de dados do usuário
                       (ex: "stations.json").

    Returns:
        O caminho absoluto (pathlib.Path) para o arquivo de dados do usuário.
    """
    # Garante que o diretório do usuário exista ao solicitar o caminho
    try:
        # Cria o diretório ~/.local/share/radio-player-simples se não existir
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Diretório de dados do usuário '{USER_DATA_DIR}' verificado/criado.")
    except OSError as e:
        logger.error(f"Não foi possível criar/verificar diretório de dados do usuário '{USER_DATA_DIR}': {e}")
        # Retorna o caminho mesmo assim, mas operações de escrita podem falhar

    user_path = USER_DATA_DIR / relative_path
    logger.debug(f"Caminho de dados do usuário solicitado: {user_path}")
    return user_path

# Exemplo de como usar (não necessário aqui, mas ilustrativo):
# ICON_PATH = get_data_path("assets/radio_icon.png")
# DEFAULT_STATIONS_PATH = get_data_path("assets/stations.json")
# USER_STATIONS_PATH = get_user_data_path("stations.json")
