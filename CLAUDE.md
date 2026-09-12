# Inipo — agente de lançamentos

Este repositório existe para um único fluxo: o usuário digita ou dita (voz já transcrita em
texto) um lançamento no chat, o agente adiciona uma linha na planilha ativa, e ao final de uma
viagem o agente "finaliza" a planilha (agrupa por classe, soma subtotais, adiciona título e
saldo a reembolsar).

## Convenção dos campos (ordem fixa, não alterar)

1. DATES (JJ/MM/AAAA)
2. DESIGNATION
3. N° du justificatif
4. MONTANT EN EUROS
5. Classe

## Fluxo por viagem

Cada viagem é um ciclo: começar uma planilha nova → ir adicionando lançamentos → finalizar.

### 1. Começar uma viagem nova

Quando o usuário disser que vai começar os lançamentos de uma nova viagem, rode:

```bash
python3 scripts/nova_planilha.py "nome de trabalho da planilha"
```

Isso cria `planilha/<nome>.xlsx` (lista simples, só cabeçalho) e grava esse nome em
`planilha/.current` — é essa a planilha que `add_lancamento.py` usa a partir daí. Não crie a
planilha nova manualmente com outras ferramentas.

### 2. Adicionar lançamentos (a cada mensagem do usuário)

1. Extraia os 5 campos da mensagem. Se um campo não ficar claro (ex: data ambígua, valor sem
   indicação clara), pergunte antes de adicionar — não adivinhe valores financeiros. Exceção:
   se o usuário não informar o N° du justificatif, preencha com "0" sem perguntar.
2. Antes de adicionar, verifique se a Classe informada corresponde a uma classe oficial já
   definida — a fonte da verdade das grafias oficiais é a última planilha **finalizada** (a de
   envio, gerada por `finalizar_planilha.py`; ver "Histórico de grafias de Classe já usadas"),
   não a planilha de lançamento em andamento nem o texto cru que o usuário digitou. Se a classe
   citada corresponder a uma classe oficial (mesmo com grafia/maiúsculas diferentes), use a
   grafia oficial. Se for realmente uma classe nova, pergunte antes de criar.
3. Rode:
   ```bash
   python3 scripts/add_lancamento.py "DATA" "DESIGNATION" "N_JUSTIFICATIF" "MONTANT" "CLASSE"
   ```
4. Confirme ao usuário a linha adicionada (todos os 5 campos) antes de commitar.
5. Faça commit e push da planilha atualizada para o branch de trabalho.

Não edite a planilha ativa diretamente com outras ferramentas de spreadsheet — use sempre
`scripts/add_lancamento.py`, que mantém formatação e localiza a próxima linha vazia
corretamente.

### 3. Finalizar a viagem

Quando o usuário pedir para finalizar, pergunte (se ainda não souber): o título do relatório
(padrão observado: "Séjour <destino> - <data início> à <data fim> - Acc. <nome>") e o valor do
adiantamento recebido, se houver. Depois rode:

```bash
python3 scripts/finalizar_planilha.py --titulo "TÍTULO" --adiantamento VALOR
```

(Omita `--adiantamento` se não houver adiantamento a deduzir.) Isso agrupa os lançamentos por
Classe (ordenados por data dentro de cada grupo, classes na ordem em que apareceram), adiciona
título, subtotal por classe ("Sous-total"), "TOTAL GÉNÉRAL" e, se houver adiantamento, "Avance
reçue" e "MONTANT À REMBOURSER" — tudo com fórmulas, não valores fixos. Depois:

1. Confira os subtotais e o total geral por conta própria em Python antes de entregar (some os
   valores e compare) — não dependa do LibreOffice para validar, pode dar timeout no sandbox.
2. Se o usuário pedir uma ordem específica de classes diferente da ordem de aparição, reordene
   manualmente (mova os blocos de linhas) e corrija os ranges das fórmulas SUM.
3. Se o usuário quiser renomear o arquivo para o nome definitivo, use `git mv`.
4. Envie o arquivo final ao usuário.

Todo texto estrutural da planilha (cabeçalhos, "Sous-total", "TOTAL GÉNÉRAL", "Avance reçue",
"MONTANT À REMBOURSER", nome da aba "Dépenses") deve ficar em francês. O conteúdo dos
lançamentos em si (DESIGNATION) NÃO deve ser traduzido — é o texto literal do
comprovante/descrição que o usuário informou.

## Histórico de grafias de Classe já usadas

- Viagem "Notes de frais Pouilles du Sud 06-09-26": "FRAIS PIQUE-NIQUES", "FRAIS, TAXES DE
  SEJOUR, REPAS Accompagnateur", "FRAIS VISITES", "FRAIS TRANSPORT DU GROUPE (tickets de
  bus,…)", "NOTE DE FRAIS HORS SEJOUR". Essas grafias foram definidas pelo usuário para
  aquela viagem especificamente — não presuma que a próxima viagem usa as mesmas classes;
  pergunte se não estiver claro.
