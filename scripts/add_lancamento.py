"""Adiciona uma linha de lançamento à planilha ativa (ver planilha/.current).

Uso:
    python3 scripts/add_lancamento.py "DATA" "DESIGNATION" "N_JUSTIFICATIF" "MONTANT" "CLASSE"

Exemplo:
    python3 scripts/add_lancamento.py "06/09/2026" "Achat fournitures" "F2026-0002" 32.90 "Classe 2"

Os 5 argumentos devem seguir sempre esta ordem, que corresponde às colunas fixas da planilha:
DATES (JJ/MM/AAAA) | DESIGNATION | N° du justificatif | MONTANT EN EUROS | Classe

A planilha alvo é a apontada por planilha/.current (criado por
scripts/nova_planilha.py). Se não existir, rode nova_planilha.py primeiro.
"""

import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, Border, Side

PLANILHA_DIR = Path(__file__).resolve().parent.parent / "planilha"
CURRENT_POINTER = PLANILHA_DIR / ".current"

HEADER_MARKER = "DATES (JJ/MM/AAAA)"


def get_xlsx_path() -> Path:
    if not CURRENT_POINTER.exists():
        sys.exit(
            "Nenhuma planilha ativa (planilha/.current não existe). "
            'Rode primeiro: python3 scripts/nova_planilha.py "nome da viagem"'
        )
    filename = CURRENT_POINTER.read_text(encoding="utf-8").strip()
    path = PLANILHA_DIR / filename
    if not path.exists():
        sys.exit(f"Planilha ativa aponta para {path}, mas o arquivo não existe.")
    return path


def find_header_row(ws) -> int:
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 5)):
        if row[0].value == HEADER_MARKER:
            return row[0].row
    sys.exit(f"Não encontrei a linha de cabeçalho ({HEADER_MARKER!r}) na planilha.")


def main() -> None:
    if len(sys.argv) != 6:
        sys.exit(
            "Uso: python3 add_lancamento.py DATA DESIGNATION N_JUSTIFICATIF MONTANT CLASSE"
        )

    data, designation, justificatif, montant_raw, classe = sys.argv[1:6]

    try:
        montant = float(str(montant_raw).replace(",", "."))
    except ValueError:
        sys.exit(f"MONTANT inválido: {montant_raw!r} (use um número, ex: 45.50)")

    xlsx_path = get_xlsx_path()
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb["Dépenses"]

    header_row = find_header_row(ws)

    last_used_row = header_row
    for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row):
        if row[0].value not in (None, ""):
            last_used_row = row[0].row
    next_row = last_used_row + 1
    values = [data, designation, justificatif, montant, classe]

    thin = Side(style="thin", color="B7B7B7")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    font = Font(name="Arial")

    for col, value in enumerate(values, start=1):
        cell = ws.cell(row=next_row, column=col, value=value)
        cell.font = font
        cell.border = border
        if col == 4:
            cell.number_format = "#,##0.00"

    wb.save(xlsx_path)
    print(f"Linha {next_row} adicionada em {xlsx_path.relative_to(xlsx_path.parent.parent)}")


if __name__ == "__main__":
    main()
