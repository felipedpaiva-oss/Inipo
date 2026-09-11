# Inipo — agente de lançamentos

Este repositório existe para um único fluxo: o usuário digita ou dita (voz já transcrita em
texto) um lançamento no chat, e o agente adiciona uma linha em `planilha/lancamentos.xlsx`.

## Convenção dos campos (ordem fixa, não alterar)

1. DATES (JJ/MM/AAAA)
2. DESIGNATION
3. N° du justificatif
4. MONTANT EN EUROS
5. Classe

## Quando o usuário descrever um lançamento em linguagem natural

1. Extraia os 5 campos acima da mensagem. Se um campo não ficar claro (ex: data ambígua,
   valor sem indicação clara), pergunte antes de adicionar — não adivinhe valores financeiros.
   Exceção: se o usuário não informar o N° du justificatif, preencha com "0" sem perguntar.
2. Rode:
   ```bash
   python3 scripts/add_lancamento.py "DATA" "DESIGNATION" "N_JUSTIFICATIF" "MONTANT" "CLASSE"
   ```
3. Confirme ao usuário a linha adicionada (todos os 5 campos) antes de commitar.
4. Faça commit e push da planilha atualizada para o branch de trabalho.

Não edite `planilha/lancamentos.xlsx` diretamente com outras ferramentas de spreadsheet — use
sempre `scripts/add_lancamento.py`, que mantém formatação e localiza a próxima linha vazia
corretamente.

## Grafias padronizadas da Classe

Antes de adicionar uma linha, verifique se a Classe informada já existe na planilha com outra
grafia (ex: "picnic" vs "pique nique") e use a grafia já em uso, em vez de introduzir uma nova
variação. Grafias confirmadas até agora:

- "FRAIS PIQUE-NIQUES" (não "picnic" nem "pique nique", renomeado em 11/09/2026)
- "FRAIS, TAXES DE SEJOUR, REPAS Accompagnateur" (não "repas accompagnateur", renomeado em 11/09/2026)
