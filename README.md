# Hyprland dotfiles

Configuração pessoal de Hyprland em CachyOS, com Noctalia, UWSM e greetd usando
o Noctalia Greeter. Os arquivos foram copiados da configuração ativa; detalhes
locais como o caminho das wallpapers foram generalizados.

## Conteúdo

- `.config/hypr/`: configuração Lua do Hyprland e regras de screencopy.
- `.config/noctalia/config.toml`: barra, tema, atalhos e integração da sessão.
- `.config/uwsm/env`: variáveis de ambiente da sessão.
- `etc/greetd/`: configuração do greetd e ambientes de sessão.
- `packages/arch.txt`: pacotes diretamente usados por esta configuração, não
  uma exportação de todos os pacotes instalados no computador.

## Instalação

Em uma instalação Arch/CachyOS, instale os pacotes listados:

```sh
sudo pacman -S --needed $(grep -vE '^[[:space:]]*(#|$)' packages/arch.txt)
```

Faça backup das configurações existentes antes de copiar:

```sh
cp -a ~/.config/hypr ~/.config/hypr.backup
cp -a .config/hypr ~/.config/
mkdir -p ~/.config/noctalia ~/.config/uwsm
cp -a .config/noctalia/config.toml ~/.config/noctalia/
cp -a .config/uwsm/env ~/.config/uwsm/
```

Revise `~/.config/noctalia/config.toml` e ajuste `wallpaper.directory` para o
caminho absoluto da sua pasta de wallpapers. Os nomes dos monitores em
`.config/hypr/config/variables.lua` estão vazios de propósito; configure
`MONITOR1` (e os demais, se necessário) para o seu hardware.

Para usar o greetd, faça backup de `/etc/greetd/`, copie os arquivos de
`etc/greetd/` para `/etc/greetd/` e habilite o serviço:

```sh
sudo systemctl enable --now greetd
```

O greetd substitui o gerenciador de login atual; confirme que a configuração e
o greeter funcionam antes de reiniciar.
