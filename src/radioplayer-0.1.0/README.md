# Rádio Player Simples

Um player de rádio simples e leve feito em Python, utilizando Tkinter para a interface gráfica e a biblioteca VLC para a reprodução de áudio.

## Funcionalidades

*   Interface gráfica simples e intuitiva.
*   Adicionar, editar e remover estações de rádio.
*   Salvar a lista de estações do usuário.
*   Controle de volume e botão de mudo.
*   Navegação entre estações (anterior/próxima).
*   (Opcional) Busca online de estações (se implementado no SearchDialog).
*   (Opcional) Tema claro/escuro (se `python-sv-ttk` estiver instalado).

## Instalação (Arch Linux)

Você pode instalar o Rádio Player Simples no Arch Linux e derivados (como Manjaro, EndeavourOS) usando um dos métodos manuais abaixo:

**1. Manualmente (via Git e `makepkg`):**

Se você prefere construir manualmente usando o Git:

1.  **Instale as dependências de compilação:**
    ```bash
    sudo pacman -S --needed git base-devel
    ```
2.  **Clone este repositório:**
    ```bash
    git clone https://github.com/marcossl10/radioplayer.git
    cd radioplayer
    ```
3.  **Construa e instale o pacote:**
    ```bash
    makepkg -si
    ```
    O comando `makepkg` baixará as fontes (se necessário), verificará as dependências, construirá o pacote e o `pacman` (`-i`) o instalará. `-s` instalará as dependências listadas no PKGBUILD automaticamente.

**2. Manualmente (via Tarball e `makepkg`):**

Se você não quer usar Git, pode baixar o código fonte e o `PKGBUILD` manualmente:

1.  **Instale as dependências de compilação:**
    ```bash
    sudo pacman -S --needed base-devel wget # wget ou curl para baixar
    ```
2.  **Crie um diretório de trabalho:**
    ```bash
    mkdir ~/radioplayer-build
    cd ~/radioplayer-build
    ```
3.  **Baixe o `PKGBUILD`:**
    *   Vá até a página do repositório no GitHub: https://github.com/marcossl10/radioplayer
    *   Encontre o arquivo `PKGBUILD.sh` (ou `PKGBUILD`).
    *   Clique nele e depois no botão "Raw".
    *   Copie a URL da página "Raw" (algo como `https://raw.githubusercontent.com/.../PKGBUILD.sh`).
    *   Baixe o arquivo no seu diretório de trabalho:
        ```bash
        wget <URL_DO_PKGBUILD_RAW> -O PKGBUILD
        # Exemplo: wget https://raw.githubusercontent.com/marcossl10/radioplayer/main/PKGBUILD.sh -O PKGBUILD
        ```
4.  **Baixe o Tarball da Release:**
    *   Vá para a seção "Releases" na página do GitHub: https://github.com/marcossl10/radioplayer/releases
    *   Encontre a release desejada (ex: `v0.1.0`).
    *   Baixe o arquivo `.tar.gz` (ex: `Source code (tar.gz)`) para o mesmo diretório de trabalho (`~/radioplayer-build`).
5.  **(Importante) Verifique o `PKGBUILD`:** Abra o arquivo `PKGBUILD` que você baixou e certifique-se de que a variável `pkgver` corresponde exatamente à versão do tarball que você baixou (ex: `pkgver=0.1.0`). Se não corresponder, edite o `PKGBUILD` para que a versão seja a correta.
6.  **Gere os Checksums (Recomendado):**
    *   O `PKGBUILD` atual usa `sha256sums=('SKIP')`, o que pula a verificação. Para mais segurança, execute `updpkgsums` antes de construir. Isso fará com que `makepkg` baixe o tarball definido na URL do `source` e preencha o checksum correto no `PKGBUILD`:
        ```bash
        updpkgsums
        ```
7.  **Construa e instale o pacote:**
    *   O `makepkg` usará o `PKGBUILD` para baixar o código fonte da URL especificada e construir o pacote.
    *   Use `-f` para forçar a construção se você já tentou antes.
    ```bash
    makepkg -fsi
    ```

## Dependências

Para rodar a aplicação, você precisará ter instalado:

*   `python` (versão 3.x)
*   `tk` (geralmente incluído com Python, mas pode ser um pacote separado como `tk` no Arch)
*   `python-vlc` (bindings Python para libVLC)
*   `libvlc` (a biblioteca VLC em si - `vlc` no Arch)
*   `python-requests` (para a funcionalidade de busca online, se utilizada)

O `PKGBUILD` cuidará da instalação dessas dependências (exceto `base-devel`, `git` ou `wget` para a construção manual) se você usar `makepkg -si`.

## Uso

Após a instalação, você pode iniciar o player de rádio pelo menu de aplicativos do seu ambiente de desktop (procure por "Rádio Player Simples") ou executando o seguinte comando no terminal:

```bash
radio-player-simples
