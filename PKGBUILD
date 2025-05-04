# PKGBUILD for radio-player-simples (Release Version)

# Maintainer: Marcos <marcosslprado@gmail.com>
_pkgname=radio-player-simples
pkgname=python-${_pkgname} # Nome final do pacote

# Defina a versão EXATAMENTE igual à tag criada no Git (sem o 'v')
pkgver=0.1.0
pkgrel=1 # Resetar para 1 para a primeira release desta versão
pkgdesc="Um player de rádio simples feito em Python com Tkinter e VLC."
arch=('any')
url="https://github.com/marcossl10/radioplayer" # URL do repositório
license=('MIT') # Ou a licença que você colocou no arquivo LICENSE
# Mover python-sv-ttk para depends se o tema escuro for obrigatório
depends=('python' 'tk' 'python-vlc' 'python-requests') # python-requests pode ser necessário para SearchDialog
optdepends=() # Vazio agora
makedepends=('python-setuptools') # Git não é mais estritamente necessário para build

# Fonte agora aponta para o tarball da tag específica no GitHub
# Renomeia o tarball baixado para <nome-repo>-<versao>.tar.gz
source=(
    "radioplayer-${pkgver}.tar.gz::https://github.com/marcossl10/radioplayer/archive/refs/tags/v${pkgver}.tar.gz"
    # Assumindo que LICENSE e .desktop estão no repositório.
)
# Checksums devem ser gerados com 'updpkgsums' após salvar este PKGBUILD
sha256sums=('SKIP')

# Não precisamos mais da função pkgver()

prepare() {
    # O diretório extraído do tarball geralmente é <nome-repo>-<versao>
    cd "$srcdir/radioplayer-${pkgver}"
    echo "Verificando diretório de preparação: $(pwd)"
    ls -la # Lista o conteúdo para depuração
    echo "Preparando fontes em $(pwd)"
}

build() {
    # Nada a compilar para Python puro
    cd "$srcdir/radioplayer-${pkgver}"
    echo "Nada a compilar para Python puro em $(pwd)"
    ls -la # Lista o conteúdo para depuração
    # Aqui você poderia adicionar comandos para rodar testes, se tivesse
    : # Comando no-op
}

package() {
    # Entra no diretório onde o código fonte foi extraído
    cd "$srcdir/radioplayer-${pkgver}"
    echo "Iniciando empacotamento de $(pwd) para $pkgdir"

    # Diretório de instalação dos módulos Python
    _pythondir="$pkgdir$(python -c 'import site; print(site.getsitepackages()[0])')"
    echo "Diretório Python site-packages: $_pythondir"

    # Instalar os módulos Python (o diretório radio_player inteiro)
    # Copia o diretório radio_player que está dentro de $srcdir/radioplayer-<versao>/radioplayer/
    install -d "$_pythondir"
    cp -r radioplayer/radio_player "$_pythondir/"
    echo "Módulo 'radio_player' copiado para $_pythondir"

    # Instalar arquivos de recurso (stations.json padrão)
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

    # Instalar arquivo de licença (busca de dentro do diretório extraído)
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    echo "Arquivo de licença copiado para $pkgdir/usr/share/licenses/$pkgname/"

    # Instalar arquivo .desktop (busca de dentro do diretório extraído)
    # Assumindo que o .desktop está em 'data/' dentro do repositório
    install -Dm644 data/radio-player-simples.desktop "$pkgdir/usr/share/applications/$_pkgname.desktop"
    echo "Arquivo .desktop copiado para $pkgdir/usr/share/applications/"

    # Instalar ícone para o menu de aplicativos
    # Copia o ícone de dentro do código fonte extraído
    install -Dm644 assets/radio_icon.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/$_pkgname.png"
    echo "Ícone copiado para $pkgdir/usr/share/icons/hicolor/scalable/apps/"

    echo "Empacotamento concluído."
}

# vim: set ft=sh ts=4 sw=4 et:

