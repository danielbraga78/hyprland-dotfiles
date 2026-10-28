# Hyprland dotfiles

Configuração pessoal de Hyprland em CachyOS, com Noctalia, UWSM e greetd usando
o Noctalia Greeter. Os arquivos foram copiados da configuração ativa; detalhes
locais como o caminho das wallpapers foram generalizados.

## Conteúdo

- `.config/hypr/`: configuração Lua do Hyprland e regras de screencopy.
- `.config/hypr/scripts/dynamic_workspaces.py`: mantém três workspaces base,
  compacta os workspaces ocupados para não deixar lacunas, cria um espaço vazio
  ao final quando os atuais estão ocupados e remove espaços extras vazios.
- `.config/noctalia/config.toml`: barra, tema, atalhos e integração da sessão.
- `.config/uwsm/env`: variáveis de ambiente da sessão.
- `.config/alacritty/`: preferências do Alacritty e tema Noctalia.
- `.config/fish/`: configuração do Fish; `fish_variables` (estado local do
  shell) foi intencionalmente excluído.
- `.config/fastfetch/`: configuração e logo do Fastfetch.
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
mkdir -p ~/.config/noctalia ~/.config/uwsm ~/.config/fish/conf.d
cp -a .config/noctalia/config.toml ~/.config/noctalia/
cp -a .config/uwsm/env ~/.config/uwsm/
cp -a .config/alacritty ~/.config/
cp -a .config/fish/config.fish ~/.config/fish/
cp -a .config/fish/conf.d/copilot.fish ~/.config/fish/conf.d/
cp -a .config/fastfetch ~/.config/
```

O gerenciador de workspaces dinâmicos inicia junto com a sessão Hyprland.
Os três primeiros workspaces permanecem disponíveis; depois que todos tiverem
janelas, um workspace vazio é mantido como espaço de reserva.

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
