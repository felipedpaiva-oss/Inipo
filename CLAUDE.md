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
- "FRAIS VISITES" (não "visitas", renomeado em 11/09/2026)
- "FRAIS TRANSPORT DU GROUPE (tickets de bus,…)" (não "transport", renomeado em 11/09/2026)
- "NOTE DE FRAIS HORS SEJOUR" (não "hors séjour", renomeado em 11/09/2026)

## Estrutura da planilha (a partir de 12/09/2026)

`planilha/lancamentos.xlsx` tem 1 aba:

- **Dépenses** (antes "Lançamentos"): linha 1 = título do relatório, linha 2 = cabeçalho,
  linhas seguintes = lançamentos agrupados por classe com subtotais ("Sous-total"), seguidos
  de "TOTAL GÉNÉRAL", "Avance reçue" (adiantamento) e "MONTANT À REMBOURSER". Novos
  lançamentos adicionados por `scripts/add_lancamento.py` entram sempre depois da última linha
  usada (ou seja, no fim de tudo, sem respeitar os grupos por classe).

(A aba "Légende" existiu, mas foi removida a pedido do usuário em 12/09/2026.)

Todo texto estrutural da planilha (nomes de aba, cabeçalhos, "Sous-total", "TOTAL GÉNÉRAL",
"Avance reçue", "MONTANT À REMBOURSER") deve ficar em francês. O conteúdo dos lançamentos em
si (DESIGNATION) NÃO deve ser traduzido — é o texto literal do comprovante/descrição que o
usuário informou.
