# Animação deslizante para saída do terminal

## Intenção

Exibir com um deslizamento suave a saída textual comum de comandos executados
no Fish, tanto no Alacritty quanto no Kitty. O efeito não deve depender da pasta
atual nem de um comando específico do projeto do robô.

## Abordagens consideradas

1. **Comando Fish opcional:** anima somente comandos invocados por esse comando;
   simples e seguro, mas não automático. Não foi escolhido.
2. **Intermediário de saída/PTY:** tenta animar automaticamente a saída textual
   finita nos dois terminais. É a abordagem escolhida por atender ao
   comportamento pedido, mas sua viabilidade precisa ser comprovada antes de
   habilitá-la por padrão.
3. **Substituir ou modificar os emuladores:** poderia alterar a renderização
   para qualquer programa, mas aumenta muito o custo de manutenção e pode
   divergir entre Alacritty e Kitty. Não foi escolhido.

## Escopo e restrições

- Animar apenas saída textual comum de comandos executados em uma sessão Fish
  interativa, de forma consistente nos dois emuladores.
- Não animar entrada digitada, prompt, saudação Fastfetch, programas de tela
  cheia/TUI, fluxos contínuos ou dados enviados por pipe/redirecionamento.
- Preservar códigos de controle ANSI, código de saída, ordem da saída e
  comportamento de terminal. Não reter saída ilimitada nem atrasar
  indefinidamente comandos longos.
- Não alterar a saída do projeto `obr-2026-robot`; a animação é uma preferência
  da sessão do usuário.
- As configurações atuais do Alacritty e do Kitty não oferecem um ajuste para
  animar automaticamente texto novo. Ambos iniciam o mesmo shell Fish.

## Plano de validação

Antes de habilitar o efeito globalmente, prototipar a interceptação e verificar
saída curta e longa, saída ANSI, código de saída, pipelines, redirecionamentos,
um fluxo contínuo e um programa TUI. O efeito só pode ser ativado se os casos
fora do escopo permanecerem inalterados. Se não for possível distinguir ou
preservar esses casos com segurança, não instalar um intermediário automático;
voltar à decisão com uma alternativa opcional.

## Decisões restantes para implementação

- Escolher o mecanismo de interceptação mais simples que passe à validação.
- Usar uma animação discreta, curta e com duração total limitada para saídas
  grandes, sem alterar a saída original.
- Manter uma forma simples de desativar o efeito e restaurar a configuração
  anterior.
