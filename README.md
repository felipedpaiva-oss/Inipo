# Inipo

Agente para registrar lançamentos financeiros por chat (texto ou voz já transcrita) em uma
planilha, viagem por viagem.

## Como funciona

1. **Começar uma viagem nova**: peça ao agente para criar a planilha (ele roda
   `scripts/nova_planilha.py`).
2. **Ir lançando**: digite (ou dite, se sua entrada de voz já chega como texto) cada lançamento
   em linguagem natural, por exemplo:

   > lançamento: 06/09/2026, achat fournitures de bureau, comprovante F2026-0002, 32,90 euros, classe 2

   O agente extrai os 5 campos, na ordem fixa abaixo, e adiciona uma linha na planilha ativa:

   | Coluna | Descrição |
   |---|---|
   | DATES (JJ/MM/AAAA) | Data do lançamento |
   | DESIGNATION | Descrição do gasto |
   | N° du justificatif | Número do comprovante |
   | MONTANT EN EUROS | Valor em euros |
   | Classe | Classe/categoria contábil |

   As alterações são commitadas e enviadas para o branch de trabalho a cada lançamento.

3. **Finalizar**: quando a viagem terminar, peça ao agente para finalizar a planilha. Ele agrupa
   os lançamentos por classe, soma subtotais, adiciona um título e (se houver) o adiantamento
   recebido e o saldo a reembolsar — tudo em francês, como no exemplo
   `planilha/Notes de frais Pouilles du Sud 06-09-26.xlsx`.

## Rodar os scripts manualmente

```bash
python3 scripts/nova_planilha.py "nome de trabalho da planilha"
python3 scripts/add_lancamento.py "DATA" "DESIGNATION" "N_JUSTIFICATIF" "MONTANT" "CLASSE"
python3 scripts/finalizar_planilha.py --titulo "TÍTULO" --adiantamento VALOR
```
