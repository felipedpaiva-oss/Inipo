"""Finaliza a planilha ativa: agrupa os lançamentos por Classe (ordenados por
data dentro de cada grupo), adiciona subtotais, título, e opcionalmente
adiantamento/saldo a reembolsar — nos mesmos moldes da planilha
"Notes de frais Pouilles du Sud 06-09-26".

Uso:
    python3 scripts/finalizar_planilha.py --titulo "TÍTULO" [--adiantamento VALOR]

Exemplo:
    python3 scripts/finalizar_planilha.py \\
        --titulo "Séjour Costa Amalfitana - 20/10/2026 à 27/10/2026 - Acc. Felipe DINIZ PAIVA" \\
        --adiantamento 800

Por padrão as classes aparecem na ordem em que surgiram na planilha. Para uma
ordem diferente, peça ao Claude para reordenar depois (como fizemos da
primeira vez) — é só editar a lista DESIRED_ORDER manualmente ou pedir para
reordenar as linhas já finalizadas.

Este script SOBRESCREVE a planilha ativa (planilha/.current) com a versão
finalizada. Depois de rodar, renomeie o arquivo (via git mv) se quiser um
nome definitivo diferente do nome de trabalho.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, Border, Side, PatternFill, Alignment

PLANILHA_DIR = Path(__file__).resolve().parent.parent / "planilha"
CURRENT_POINTER = PLANILHA_DIR / ".current"

HEADERS = [
    "DATES (JJ/MM/AAAA)",
    "DESIGNATION",
    "N° du justificatif",
    "MONTANT EN EUROS",
    "Classe",
]
HEADER_MARKER = HEADERS[0]


def get_xlsx_path() -> Path:
    if not CURRENT_POINTER.exists():
        sys.exit("Nenhuma planilha ativa (planilha/.current não existe).")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--titulo", required=True)
    parser.add_argument("--adiantamento", type=float, default=None)
    args = parser.parse_args()

    xlsx_path = get_xlsx_path()
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb["Dépenses"]

    header_row = find_header_row(ws)

    data_rows = []
    for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row, values_only=True):
        if row[0] in (None, ""):
            continue
        data_rows.append(row[:5])

    if not data_rows:
        sys.exit("Nenhum lançamento encontrado para finalizar.")

    by_classe = {}
    order = []
    for r in data_rows:
        classe = r[4]
        if classe not in by_classe:
            by_classe[classe] = []
            order.append(classe)
        by_classe[classe].append(r)

    for classe in order:
        by_classe[classe].sort(key=lambda r: datetime.strptime(r[0], "%d/%m/%Y"))

    for merged_range in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(merged_range))
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for cell in row:
            cell.value = None
            cell.font = Font(name="Arial")
            cell.fill = PatternFill(fill_type=None)
            cell.border = Border()
            cell.number_format = "General"
            cell.alignment = Alignment()

    thin = Side(style="thin", color="B7B7B7")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    data_font = Font(name="Arial")
    header_font = Font(name="Arial", bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4472C4")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    title_font = Font(name="Arial", bold=True, size=13)
    classe_font = Font(name="Arial", bold=True, color="FFFFFF")
    classe_fill = PatternFill("solid", fgColor="808080")
    subtotal_font = Font(name="Arial", bold=True)
    subtotal_fill = PatternFill("solid", fgColor="D9D9D9")
    grand_font = Font(name="Arial", bold=True, color="FFFFFF")
    grand_fill = PatternFill("solid", fgColor="203864")
    neg_format = "#,##0.00;(#,##0.00)"

    ws.cell(row=1, column=1, value=args.titulo)
    ws.cell(row=1, column=1).font = title_font
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
    ws.row_dimensions[1].height = 22

    for col, title in enumerate(HEADERS, start=1):
        cell = ws.cell(row=2, column=col, value=title)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = border

    widths = [20, 45, 20, 20, 15]
    for col, w in zip("ABCDE", widths):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A3"

    r = 3
    subtotal_cells = []
    for classe in order:
        ws.cell(row=r, column=1, value=classe)
        for c in range(1, 6):
            cell = ws.cell(row=r, column=c)
            cell.font = classe_font
            cell.fill = classe_fill
            cell.border = border
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        r += 1

        first_data_row = r
        for entry in by_classe[classe]:
            for c, v in enumerate(entry, start=1):
                cell = ws.cell(row=r, column=c, value=v)
                cell.font = data_font
                cell.border = border
                if c == 4:
                    cell.number_format = "#,##0.00"
            r += 1
        last_data_row = r - 1

        ws.cell(row=r, column=1, value="Sous-total")
        ws.cell(row=r, column=4, value=f"=SUM(D{first_data_row}:D{last_data_row})")
        for c in range(1, 6):
            cell = ws.cell(row=r, column=c)
            cell.font = subtotal_font
            cell.fill = subtotal_fill
            cell.border = border
        ws.cell(row=r, column=4).number_format = "#,##0.00"
        subtotal_cells.append(f"D{r}")
        r += 2

    grand_row = r
    ws.cell(row=grand_row, column=1, value="TOTAL GÉNÉRAL")
    ws.cell(row=grand_row, column=4, value="=" + "+".join(subtotal_cells))
    for c in range(1, 6):
        cell = ws.cell(row=grand_row, column=c)
        cell.font = grand_font
        cell.fill = grand_fill
        cell.border = border
    ws.cell(row=grand_row, column=4).number_format = "#,##0.00"
    ws.merge_cells(start_row=grand_row, start_column=1, end_row=grand_row, end_column=3)

    if args.adiantamento is not None:
        r_adiant = grand_row + 2
        ws.cell(row=r_adiant, column=1, value="Avance reçue")
        ws.cell(row=r_adiant, column=4, value=-abs(args.adiantamento))
        for c in range(1, 6):
            cell = ws.cell(row=r_adiant, column=c)
            cell.font = subtotal_font
            cell.fill = PatternFill("solid", fgColor="FCE4D6")
            cell.border = border
        ws.cell(row=r_adiant, column=4).number_format = neg_format
        ws.merge_cells(start_row=r_adiant, start_column=1, end_row=r_adiant, end_column=3)

        r_reembolso = r_adiant + 1
        ws.cell(row=r_reembolso, column=1, value="MONTANT À REMBOURSER")
        ws.cell(row=r_reembolso, column=4, value=f"=D{grand_row}+D{r_adiant}")
        for c in range(1, 6):
            cell = ws.cell(row=r_reembolso, column=c)
            cell.font = grand_font
            cell.fill = grand_fill
            cell.border = border
        ws.cell(row=r_reembolso, column=4).number_format = neg_format
        ws.merge_cells(start_row=r_reembolso, start_column=1, end_row=r_reembolso, end_column=3)

    wb.save(xlsx_path)
    print(f"Planilha finalizada: {xlsx_path.relative_to(xlsx_path.parent.parent)}")
    print(f"Classes (nesta ordem): {order}")


if __name__ == "__main__":
    main()
