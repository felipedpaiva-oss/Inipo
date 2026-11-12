# Inipo

## Processos

- [`processos/atendimento-agente-ia-smartyou.drawio`](processos/atendimento-agente-ia-smartyou.drawio): processo de atendimento do Agente IA da SmartYou, em BPMN com raias.
  - Pág. 1: fontes → canais → atendentes (associações editáveis)
  - Pág. 2: Agente IA Genérico em horário comercial
  - Pág. 3: Agente IA Genérico fora do horário
  - Pág. 4: subprocesso de inatividade
  - Leia-me: legenda

Para editar, abra em [app.diagrams.net](https://app.diagrams.net) → *Abrir de* → *Dispositivo* ou *GitHub*. Para levar ao Visio: *Arquivo → Exportar como → VSDX*.

`tools/gerar_processo.py` recria o arquivo do zero. Ele sobrescreve edições feitas no draw.io, então depois da primeira edição manual o `.drawio` passa a ser a fonte.
