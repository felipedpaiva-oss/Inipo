# Inipo

Agente para registrar lançamentos financeiros por chat (texto ou voz já transcrita) em uma planilha.

## Como funciona

1. Abra uma sessão do Claude Code neste repositório.
2. Digite (ou dite, se sua entrada de voz já chega como texto) o lançamento em linguagem natural, por exemplo:

   > lançamento: 06/09/2026, achat fournitures de bureau, comprovante F2026-0002, 32,90 euros, classe 2

3. O agente extrai os 5 campos, na ordem fixa abaixo, e adiciona uma linha em
   `planilha/Notes de frais Pouilles du Sud 06-09-26.xlsx`:

   | Coluna | Descrição |
   |---|---|
   | DATES (JJ/MM/AAAA) | Data do lançamento |
   | DESIGNATION | Descrição do gasto |
   | N° du justificatif | Número do comprovante |
   | MONTANT EN EUROS | Valor em euros |
   | Classe | Classe/categoria contábil |

4. As alterações são commitadas e enviadas para o branch de trabalho.

## Adicionar uma linha manualmente

```bash
python3 scripts/add_lancamento.py "DATA" "DESIGNATION" "N_JUSTIFICATIF" "MONTANT" "CLASSE"
```
