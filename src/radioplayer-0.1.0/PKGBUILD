# PKGBUILD for radio-player-simples (Development Version)

# Maintainer: Marcos <marcosslprado@gmail.com>
_pkgname=radio-player-simples
pkgname=python-${_pkgname} # Nome final do pacote

# pkgver será gerado dinamicamente pela função pkgver() abaixo
pkgrel=1 # Resetar para 1 para versões de desenvolvimento
pkgdesc="Um player de rádio simples feito em Python com Tkinter e VLC."
arch=('any')
url="https://github.com/marcossl10/radioplayer" # URL do novo repositório
license=('MIT') # Ou a licença que você colocou no arquivo LICENSE
# Mover python-sv-ttk para depends se o tema escuro for obrigatório
depends=('python' 'tk' 'python-vlc' 'python-requests') # python-requests pode ser necessário para SearchDialog
optdepends=() # Vazio agora
makedepends=('python-setuptools' 'git') # Git é essencial agora

# Fonte agora clona o repositório Git diretamente
# O formato é: [nome-diretorio::]git+url[#fragmento]
# O fragmento pode ser #branch=..., #tag=..., #commit=...
# Se omitido, clona o branch padrão (main/master)
source=(
    "git+https://github.com/marcossl10/radioplayer.git"
    # Assumindo que LICENSE e .desktop estão no repositório.
    # Se não estiverem, adicione-os aqui como fontes separadas.
)
# Checksums para fontes Git são 'SKIP' por padrão
sha256sums=('SKIP')

# Função para gerar a versão dinamicamente a partir do Git
pkgver() {
  cd "$srcdir/radioplayer" # Entra no diretório clonado
  # Formato: <ultima_tag>.<commits_desde_tag>.g<hash_curto_commit> (ex: 0.1.0.r5.gabc123)
  # Ou se não houver tags: r<numero_total_commits>.g<hash_curto_commit> (ex: r15.gfed456)
  git describe --long --tags | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

prepare() {
    # O diretório clonado será $srcdir/radioplayer (nome do repo)
    cd "$srcdir/radioplayer"
    echo "Verificando diretório de preparação: $(pwd)"
    ls -la # Lista o conteúdo para depuração
    echo "Preparando fontes em $(pwd)"
}

build() {
    # Nada a compilar para Python puro
    cd "$srcdir/radioplayer"
    echo "Nada a compilar para Python puro em $(pwd)"
    ls -la # Lista o conteúdo para depuração
    # Aqui você poderia adicionar comandos para rodar testes, se tivesse
    : # Comando no-op
}

package() {
    # Entra no diretório onde o código fonte foi clonado
    cd "$srcdir/radioplayer"
    echo "Iniciando empacotamento de $(pwd) para $pkgdir"

    # Diretório de instalação dos módulos Python
    _pythondir="$pkgdir$(python -c 'import site; print(site.getsitepackages()[0])')"
    echo "Diretório Python site-packages: $_pythondir"

    # Instalar os módulos Python (o diretório radio_player inteiro)
    # Copia o diretório radio_player que está dentro de $srcdir/radioplayer/radioplayer/
    install -d "$_pythondir"
    cp -r radioplayer/radio_player "$_pythondir/"
    echo "Módulo 'radio_player' copiado para $_pythondir"

    # Instalar arquivos de recurso (stations.json padrão)
    # O ícone agora será instalado no diretório de ícones padrão
    _datadir="$pkgdir/usr/share/$_pkgname"
    install -d "$_datadir/assets"
    install -Dm644 assets/stations.json "$_datadir/assets/stations.json"
    echo "Recursos de dados copiados para $_datadir/assets"

    # Cria o diretório para executáveis
    install -d "$pkgdir/usr/bin"

    # Cria o script wrapper executável
    cat > "$pkgdir/usr/bin/$_pkgname" <<EOF
#!/bin/sh
# Wrapper para executar o módulo Python
exec python -m radio_player.main "\$@"
EOF
    chmod +x "$pkgdir/usr/bin/$_pkgname"

    # Instalar arquivo de licença (busca de dentro do diretório clonado)
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    echo "Arquivo de licença copiado para $pkgdir/usr/share/licenses/$pkgname/"

    # Instalar arquivo .desktop (busca de dentro do diretório clonado)
    # Assumindo que o .desktop está em 'data/' dentro do repositório
    install -Dm644 data/radio-player-simples.desktop "$pkgdir/usr/share/applications/$_pkgname.desktop"
    echo "Arquivo .desktop copiado para $pkgdir/usr/share/applications/"

    # Instalar ícone para o menu de aplicativos
    # Copia o ícone de dentro do código fonte clonado
    install -Dm644 assets/radio_icon.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/$_pkgname.png"
    echo "Ícone copiado para $pkgdir/usr/share/icons/hicolor/scalable/apps/"

    echo "Empacotamento concluído."
}

# vim: set ft=sh ts=4 sw=4 et:
