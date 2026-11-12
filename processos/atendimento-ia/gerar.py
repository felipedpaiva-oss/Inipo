#!/usr/bin/env python3
"""Gera o diagrama BPMN do processo de atendimento do agente de IA da SmartYou.

Saída: processo-atendimento-ia.html (3 páginas A3 paisagem) -> PDF via render_pdf.js
"""
from pathlib import Path

OUT = Path(__file__).with_name("processo-atendimento-ia.html")

INK = "#1f2933"
MUTED = "#52606d"
FILL = {
    "agent": "#e3f0fb",
    "service": "#eceff3",
    "user": "#fdf1dc",
    "send": "#e3f0fb",
    "none": "#ffffff",
}

# ---------------------------------------------------------------- primitivas


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, label, anchor="middle", size=12, weight=400, color=INK, italic=False):
    lines = label.split("\n")
    lh = size * 1.22
    y0 = y - (len(lines) - 1) * lh / 2
    style = "font-style:italic;" if italic else ""
    out = [f'<text x="{x}" y="{y0:.1f}" text-anchor="{anchor}" font-size="{size}" '
           f'font-weight="{weight}" fill="{color}" dominant-baseline="middle" style="{style}">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out.append(f'<tspan x="{x}" dy="{dy:.1f}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def icon(kind, x, y):
    if kind == "service":  # engrenagem
        return (f'<circle cx="{x+7}" cy="{y+7}" r="5.5" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="2.2 1.6"/>'
                f'<circle cx="{x+7}" cy="{y+7}" r="2" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    if kind == "user":  # pessoa
        return (f'<circle cx="{x+7}" cy="{y+4}" r="3.2" fill="none" stroke="{INK}" stroke-width="1.3"/>'
                f'<path d="M{x+1},{y+14} q0,-6 6,-6 q6,0 6,6 z" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    if kind == "send":  # envelope cheio
        return (f'<rect x="{x}" y="{y+2}" width="15" height="10" fill="{INK}"/>'
                f'<path d="M{x},{y+2} l7.5,5.5 l7.5,-5.5" fill="none" stroke="#fff" stroke-width="1.2"/>')
    if kind == "agent":  # robô
        return (f'<rect x="{x+1}" y="{y+3}" width="13" height="10" rx="2" fill="none" stroke="{INK}" stroke-width="1.3"/>'
                f'<circle cx="{x+5}" cy="{y+8}" r="1.3" fill="{INK}"/><circle cx="{x+10}" cy="{y+8}" r="1.3" fill="{INK}"/>'
                f'<line x1="{x+7.5}" y1="{y}" x2="{x+7.5}" y2="{y+3}" stroke="{INK}" stroke-width="1.3"/>')
    return ""


def task(cx, cy, w, h, label, kind="agent", call=False, size=12):
    x, y = cx - w / 2, cy - h / 2
    sw = 3.2 if call else 1.4
    fill = FILL.get(kind, "#fff")
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>']
    if not call:
        s.append(icon(kind, x + 6, y + 6))
    if call:
        s.append(f'<rect x="{cx-6}" y="{y+h-14}" width="12" height="12" fill="#fff" stroke="{INK}" stroke-width="1.2"/>'
                 f'<path d="M{cx-3.5},{y+h-8} h7 M{cx},{y+h-11.5} v7" stroke="{INK}" stroke-width="1.4"/>')
    ty = cy - (5 if call else 0)
    s.append(text(cx + (7 if not call else 0), ty, label, size=size))
    return "".join(s)


def marker_svg(marker, cx, cy, throw=False):
    if marker == "msg":
        f = INK if throw else "#fff"
        st = "#fff" if throw else INK
        return (f'<rect x="{cx-8}" y="{cy-5.5}" width="16" height="11" fill="{f}" stroke="{INK}" stroke-width="1.2"/>'
                f'<path d="M{cx-8},{cy-5.5} l8,6 l8,-6" fill="none" stroke="{st}" stroke-width="1.2"/>')
    if marker == "timer":
        ticks = "".join(
            f'<line x1="{cx}" y1="{cy-9}" x2="{cx}" y2="{cy-7}" stroke="{INK}" stroke-width="1" transform="rotate({a} {cx} {cy})"/>'
            for a in range(0, 360, 30))
        return (f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="{INK}" stroke-width="1.3"/>{ticks}'
                f'<path d="M{cx},{cy} L{cx},{cy-6} M{cx},{cy} L{cx+4.5},{cy+1.5}" stroke="{INK}" stroke-width="1.3"/>')
    if marker == "link":
        f = INK if throw else "#fff"
        return (f'<path d="M{cx-8},{cy-3.5} h8 v-5 l8,8.5 l-8,8.5 v-5 h-8 z" fill="{f}" stroke="{INK}" stroke-width="1.2"/>')
    if marker == "terminate":
        return f'<circle cx="{cx}" cy="{cy}" r="9.5" fill="{INK}"/>'
    if marker == "escalation":
        f = INK if throw else "#fff"
        return f'<path d="M{cx},{cy-9} l7,16 l-7,-6 l-7,6 z" fill="{f}" stroke="{INK}" stroke-width="1.2"/>'
    return ""


def event(cx, cy, kind="start", marker=None, label=None, lpos="below", interrupting=True, r=17, lsize=11):
    s = []
    dash = '' if interrupting else ' stroke-dasharray="4 3"'
    if kind == "start":
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.6"{dash}/>')
    elif kind == "end":
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="4.2"/>')
    else:  # intermediário (catch/throw/boundary)
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.4"{dash}/>'
                 f'<circle cx="{cx}" cy="{cy}" r="{r-3.5}" fill="none" stroke="{INK}" stroke-width="1.4"{dash}/>')
    throw = kind in ("end", "throw")
    s.append(marker_svg(marker, cx, cy, throw=throw))
    if label:
        off = r + 6
        if lpos == "below":
            n = label.count("\n")
            s.append(text(cx, cy + off + 7 + n * 6.7, label, size=lsize))
        elif lpos == "above":
            n = label.count("\n")
            s.append(text(cx, cy - off - 7 - n * 6.7, label, size=lsize))
        elif lpos == "left":
            s.append(text(cx - off, cy, label, anchor="end", size=lsize))
        else:
            s.append(text(cx + off, cy, label, anchor="start", size=lsize))
    return "".join(s)


def gateway(cx, cy, gtype="x", label=None, lpos="above", d=25, lsize=11):
    s = [f'<path d="M{cx},{cy-d} L{cx+d},{cy} L{cx},{cy+d} L{cx-d},{cy} Z" fill="#fff" stroke="{INK}" stroke-width="1.5"/>']
    if gtype == "x":
        s.append(f'<path d="M{cx-7},{cy-7} L{cx+7},{cy+7} M{cx+7},{cy-7} L{cx-7},{cy+7}" stroke="{INK}" stroke-width="3"/>')
    elif gtype == "+":
        s.append(f'<path d="M{cx-9},{cy} H{cx+9} M{cx},{cy-9} V{cy+9}" stroke="{INK}" stroke-width="3"/>')
    elif gtype == "event":
        pts = []
        import math
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            pts.append(f"{cx+6*math.cos(a):.1f},{cy+6*math.sin(a):.1f}")
        s.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="none" stroke="{INK}" stroke-width="1.1"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="9.5" fill="none" stroke="{INK}" stroke-width="1.1"/>'
                 f'<polygon points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    if label:
        n = label.count("\n")
        if lpos == "above":
            s.append(text(cx, cy - d - 8 - n * 6.7, label, size=lsize, weight=600))
        elif lpos == "below":
            s.append(text(cx, cy + d + 8 + n * 6.7, label, size=lsize, weight=600))
        elif lpos == "left":
            s.append(text(cx - d - 6, cy, label, anchor="end", size=lsize, weight=600))
        else:
            s.append(text(cx + d + 6, cy, label, anchor="start", size=lsize, weight=600))
    return "".join(s)


def flow(points, kind="seq", label=None, lx=None, ly=None, anchor="middle", lsize=11):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    if kind == "seq":
        s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.4" marker-end="url(#seq)"/>'
    elif kind == "msg":
        s = (f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="6 4" '
             f'marker-start="url(#msgstart)" marker-end="url(#msgend)"/>')
    else:
        s = f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="2 3"/>'
    if label:
        s += f'<rect x="0" y="0" width="0" height="0"/>'
        s += text(lx, ly, label, anchor=anchor, size=lsize, color=MUTED if kind != "seq" else INK, italic=kind != "seq")
    return s


def annotation(x, y, w, h, label, size=11):
    return (f'<path d="M{x+14},{y} H{x} V{y+h} H{x+14}" fill="none" stroke="{MUTED}" stroke-width="1.3"/>'
            + text(x + 8, y + h / 2, label, anchor="start", size=size, color=MUTED))


DEFS = f"""
<defs>
  <marker id="seq" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
    <path d="M0,0 L10,5 L0,10 z" fill="{INK}"/>
  </marker>
  <marker id="msgend" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="10" markerHeight="10" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M0,0 L10,5 L0,10 z" fill="#fff" stroke="{MUTED}" stroke-width="1.2"/>
  </marker>
  <marker id="msgstart" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="9" markerHeight="9" orient="auto" markerUnits="userSpaceOnUse">
    <circle cx="5" cy="5" r="3.8" fill="#fff" stroke="{MUTED}" stroke-width="1.2"/>
  </marker>
</defs>
"""


def lanes(x0, y0, width, lane_defs, pool_label, label_w=110, pool_w=34):
    """lane_defs: lista de (rótulo, altura)."""
    total = sum(h for _, h in lane_defs)
    s = [f'<rect x="{x0}" y="{y0}" width="{width}" height="{total}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>',
         f'<line x1="{x0+pool_w}" y1="{y0}" x2="{x0+pool_w}" y2="{y0+total}" stroke="{INK}" stroke-width="1.6"/>',
         f'<text x="{x0+pool_w/2}" y="{y0+total/2}" font-size="13" font-weight="700" fill="{INK}" text-anchor="middle" '
         f'dominant-baseline="middle" transform="rotate(-90 {x0+pool_w/2} {y0+total/2})">{esc(pool_label)}</text>']
    y = y0
    for i, (lab, h) in enumerate(lane_defs):
        if i > 0:
            s.append(f'<line x1="{x0+pool_w}" y1="{y}" x2="{x0+width}" y2="{y}" stroke="{INK}" stroke-width="1.1"/>')
        s.append(f'<line x1="{x0+pool_w+label_w}" y1="{y}" x2="{x0+pool_w+label_w}" y2="{y+h}" stroke="{INK}" stroke-width="1.1"/>')
        s.append(text(x0 + pool_w + label_w / 2, y + h / 2, lab, size=12.5, weight=600))
        y += h
    return "".join(s)


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
            f'font-family="Inter, Helvetica, Arial, sans-serif">{DEFS}{"".join(body)}</svg>')


# ---------------------------------------------------------------- página 1: processo principal

def pagina1():
    W, H = 2080, 1080
    b = []
    X0 = 10
    POOLX = X0
    LABEL_END = X0 + 34 + 110  # início da área de conteúdo = 154

    # Etapas do funil (Kommo) — cabeçalho de colunas
    cols = [
        ("Prospect", LABEL_END, 800),
        ("Em atendimento (IA)", 800, 1565),
        ("Alinhamento de projeto", 1565, 1790),
        ("Aguardando atendimento humano", 1790, W - 10),
    ]
    b.append(text(LABEL_END - 8, 30, "Etapa no funil\ndo Kommo →", anchor="end", size=11, color=MUTED, weight=600))
    for i, (lab, a, z) in enumerate(cols):
        b.append(f'<rect x="{a}" y="12" width="{z-a}" height="38" fill="{"#f3f6f9" if i % 2 == 0 else "#e8edf2"}" stroke="#c5ced8"/>')
        b.append(text((a + z) / 2, 31, lab, size=13.5, weight=700))

    # Pool Lead (caixa-preta)
    b.append(f'<rect x="{POOLX}" y="64" width="{W-20}" height="52" fill="#f7f7f7" stroke="{INK}" stroke-width="1.6"/>')
    b.append(text(POOLX + 16, 90, "Lead  (Instagram · Facebook Messenger · WhatsApp)", anchor="start", size=13, weight=700))

    # Pool SmartYou
    PY = 150
    lane_defs = [("Agente de IA\n(Salesbot)", 360), ("Kommo CRM\n(automação)", 170), ("Equipe\ncomercial", 150), ("Subprocessos\nde evento\n(valem em\nqualquer etapa)", 180)]
    b.append(lanes(POOLX, PY, W - 20, lane_defs, "SmartYou — Atendimento de leads"))
    # separadores de etapa (tracejado leve)
    for _, a, z in cols[1:]:
        b.append(f'<line x1="{a}" y1="12" x2="{a}" y2="{PY+680}" stroke="#b7c2cd" stroke-width="1" stroke-dasharray="3 5"/>')

    R0, R1, R2 = 205, 290, 400          # linhas da raia do agente
    K = 595                              # raia Kommo
    C = 755                              # raia comercial

    # ---------------- Coluna Prospect
    b.append(event(200, K, "start", "msg", "Mensagem\nrecebida", "below"))
    b.append(flow([(200, 116), (200, K - 17)], "msg", "1ª mensagem", 206, 135, anchor="start"))
    b.append(task(290, K, 112, 56, "Criar lead\nem Prospect", "service"))
    b.append(flow([(217, K), (234, K)]))
    b.append(gateway(395, K, "x", "Horário\ncomercial?", "below"))
    b.append(flow([(346, K), (370, K)]))
    b.append(task(495, K, 104, 56, "Notificar\ncomercial", "service"))
    b.append(flow([(420, K), (443, K)], label="Sim", lx=431, ly=K - 10))
    b.append(gateway(590, K, "x"))
    b.append(flow([(547, K), (565, K)]))
    b.append(flow([(395, K - 25), (395, K - 50), (590, K - 50), (590, K - 25)], label="Não", lx=410, ly=K - 60, anchor="start"))
    # comercial recebe notificação
    b.append(event(495, C, "start", "msg", "Nova conversa", "below", interrupting=False))
    b.append(flow([(495, K + 28), (495, C - 17)], "msg"))
    b.append(task(615, C, 140, 60, "Acompanha a conversa;\npode assumir\n(Subprocesso B)", "user", size=10.5))
    b.append(flow([(512, C), (545, C)]))
    b.append(event(730, C, "end", None))
    b.append(flow([(685, C), (713, C)]))
    # agente saúda
    b.append(task(655, R1, 120, 56, "Saudar e iniciar\natendimento", "send"))
    b.append(flow([(615, K), (655, K), (655, R1 + 28)]))
    b.append(flow([(655, R1 - 28), (655, 116)], "msg", "Boas-vindas", 661, 135, anchor="start"))
    b.append(gateway(760, R1, "event"))
    b.append(flow([(715, R1), (735, R1)]))
    b.append(event(760, 375, "inter", "timer", "30 min sem\nresposta", "right"))
    b.append(flow([(760, R1 + 25), (760, 358)]))
    # cadência
    b.append(task(640, R2 + 50, 150, 58, "Cadência de\nfollow-up (Sub. C)", "agent", call=True))
    b.append(flow([(760, 392), (760, R2 + 40), (715, R2 + 40)]))
    b.append(event(790, R2 + 62, "inter", "link", "B", "right"))
    b.append(flow([(773, R2 + 62), (715, R2 + 62)]))
    b.append(gateway(500, R2 + 50, "x", "Lead\nrespondeu?", "below"))
    b.append(flow([(565, R2 + 50), (525, R2 + 50)]))
    b.append(event(500, 375, "throw", "link", "A", "left"))
    b.append(flow([(500, R2 + 25), (500, 392)], label="Sim", lx=508, ly=R2 + 8, anchor="start"))
    b.append(event(395, R2 + 50, "end", None, "Perdido", "below"))
    b.append(flow([(475, R2 + 50), (412, R2 + 50)], label="Não", lx=444, ly=R2 + 40))

    # ---------------- Coluna Em atendimento
    b.append(event(850, R1, "inter", "msg", "Lead\nrespondeu", "above"))
    b.append(flow([(785, R1), (833, R1)]))
    b.append(flow([(850, 116), (850, R1 - 17)], "msg"))
    b.append(gateway(925, R1, "x"))
    b.append(flow([(867, R1), (900, R1)]))
    b.append(event(925, R0 - 10, "inter", "link", "A", "right"))
    b.append(flow([(925, R0 + 7), (925, R1 - 25)]))
    b.append(task(925, K, 124, 56, "Mover para\nEm atendimento", "service"))
    b.append(flow([(925, R1 + 25), (925, K - 28)]))
    b.append(task(1060, R1, 124, 56, "Tirar dúvidas e\nqualificar", "agent"))
    b.append(flow([(987, K), (1060, K), (1060, R1 + 28)]))
    b.append(event(1100, R1 + 28, "inter", "timer", r=13))
    b.append(event(1100, 380, "throw", "link", "B", "right"))
    b.append(flow([(1100, R1 + 41), (1100, 363)], label="sem resposta", lx=1106, ly=346, anchor="start"))
    b.append(task(1218, R1, 148, 72, "Oferecer 3 opções:\n1 visita ao showroom\n2 ligação com vendas\n3 humano imediato", "send", size=11))
    b.append(flow([(1122, R1), (1144, R1)]))
    b.append(flow([(1215, R1 - 36), (1215, 116)], "msg", "Opções", 1221, 135, anchor="start"))
    b.append(gateway(1325, R1, "event"))
    b.append(flow([(1292, R1), (1300, R1)]))
    b.append(event(1405, R1, "inter", "msg", "Lead\nescolhe", "above"))
    b.append(flow([(1350, R1), (1388, R1)]))
    b.append(flow([(1405, 116), (1405, R1 - 17)], "msg"))
    b.append(event(1325, 375, "inter", "timer", "sem\nresposta", "left"))
    b.append(flow([(1325, R1 + 25), (1325, 358)]))
    b.append(event(1325, 450, "throw", "link", "B", "left"))
    b.append(flow([(1325, 392), (1325, 433)]))
    b.append(gateway(1485, R1, "x", "Opção?", "right"))
    b.append(flow([(1422, R1), (1460, R1)]))
    b.append(task(1485, R0 - 15, 158, 50, "Atendimento imediato\n(Subprocesso A)", "user", call=True, size=11.5))
    b.append(flow([(1485, R1 - 25), (1485, R0 + 10)], label="3", lx=1493, ly=R1 - 40, anchor="start"))
    b.append(task(1485, R2 + 30, 128, 56, "Agendar visita\nou ligação", "agent"))
    b.append(flow([(1485, R1 + 25), (1485, R2 + 2)], label="1 ou 2", lx=1493, ly=R1 + 45, anchor="start"))

    # ---------------- Coluna Alinhamento de projeto
    b.append(task(1660, K, 150, 56, "Mover para\nAlinhamento de projeto", "service", size=11.5))
    b.append(flow([(1549, R2 + 30), (1610, R2 + 30), (1610, K - 28)]))
    b.append(flow([(1564, R0 - 15), (1655, R0 - 15), (1655, K - 28)], label="visita/ligação agendada\npelo humano", lx=1572, ly=R0 - 42, anchor="start", lsize=10.5))
    b.append(task(1700, R1 + 40, 130, 64, "Alinhar projeto\ne confirmar\nagendamento*", "agent", size=11.5))
    b.append(flow([(1735, K), (1752, K), (1752, R1 + 72)]))

    # ---------------- Coluna Aguardando atendimento humano
    b.append(task(1915, K, 178, 66, "Mover para Aguardando\natendimento humano\n+ notificar comercial", "service", size=11.5))
    b.append(flow([(1765, R1 + 40), (1915, R1 + 40), (1915, K - 33)]))
    b.append(task(1915, C, 160, 56, "Assumir atendimento\n(horário comercial)", "user"))
    b.append(flow([(1915, K + 33), (1915, C - 28)]))
    b.append(event(2035, C, "end", None, "Lead com o\ncomercial", "below"))
    b.append(flow([(1995, C), (2018, C)]))

    # ---------------- Subprocessos de evento (recolhidos)
    SY = PY + 680 + 20
    def evsub(x, y, w, h, title, body, interrupting=True):
        d = '' if interrupting else ''
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#fff" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>'
                + event(x + 30, y + 30, "start", "msg", interrupting=interrupting, r=15)
                + text(x + 56, y + 30, title, anchor="start", size=13, weight=700)
                + text(x + 18, y + 80, body, anchor="start", size=11.5, color=INK)
                + f'<rect x="{x+w/2-6}" y="{y+h-16}" width="12" height="12" fill="#fff" stroke="{INK}" stroke-width="1.2"/>'
                + f'<path d="M{x+w/2-3.5},{y+h-10} h7 M{x+w/2},{y+h-13.5} v7" stroke="{INK}" stroke-width="1.4"/>')
    b.append(evsub(170, SY, 470, 140, "A · Lead pede atendimento humano",
                   "Pode acontecer em qualquer etapa (ou na opção 3).\nDentro do horário: notifica comercial, SLA 15–30 min;\nse ninguém assumir, o robô retoma e renotifica.\nFora do horário: transfere e informa o horário. → pág. 2"))
    b.append(evsub(665, SY, 450, 140, "B · Comercial assume a conversa",
                   "Em horário comercial, o comercial é notificado de\ncada conversa nova e pode substituir o robô a\nqualquer momento. O robô pausa para esse lead.\n→ pág. 2"))

    # legenda
    LX, LY = 1150, SY
    b.append(f'<rect x="{LX}" y="{LY}" width="{W-20-LX+POOLX}" height="150" rx="8" fill="#fafbfc" stroke="#c5ced8"/>')
    b.append(text(LX + 14, LY + 18, "Legenda (BPMN 2.0)", anchor="start", size=12, weight=700))
    lg = []
    cx, cy = LX + 30, LY + 44
    lg.append(event(cx, cy, "start", "msg", r=12) + text(cx + 20, cy, "Início por mensagem", anchor="start", size=11))
    lg.append(event(cx, cy + 34, "inter", "timer", r=12) + text(cx + 20, cy + 34, "Espera / prazo", anchor="start", size=11))
    lg.append(event(cx, cy + 68, "inter", "link", r=12) + text(cx + 20, cy + 68, "Conector (A, B)", anchor="start", size=11))
    cx2 = LX + 210
    lg.append(gateway(cx2, cy, "x", d=13) + text(cx2 + 20, cy, "Decisão (um caminho)", anchor="start", size=11))
    lg.append(gateway(cx2, cy + 34, "event", d=13) + text(cx2 + 20, cy + 34, "Espera o que vier primeiro", anchor="start", size=11))
    lg.append(event(cx2, cy + 68, "end", None, r=12) + text(cx2 + 20, cy + 68, "Fim", anchor="start", size=11))
    cx3 = LX + 420
    lg.append(f'<rect x="{cx3-14}" y="{cy-10}" width="28" height="20" rx="4" fill="{FILL["agent"]}" stroke="{INK}"/>' + text(cx3 + 22, cy, "Tarefa do agente de IA", anchor="start", size=11))
    lg.append(f'<rect x="{cx3-14}" y="{cy+24}" width="28" height="20" rx="4" fill="{FILL["service"]}" stroke="{INK}"/>' + text(cx3 + 22, cy + 34, "Automação do Kommo", anchor="start", size=11))
    lg.append(f'<rect x="{cx3-14}" y="{cy+58}" width="28" height="20" rx="4" fill="{FILL["user"]}" stroke="{INK}"/>' + text(cx3 + 22, cy + 68, "Tarefa humana", anchor="start", size=11))
    cx4 = LX + 620
    lg.append(f'<rect x="{cx4-14}" y="{cy-10}" width="28" height="20" rx="4" fill="#fff" stroke="{INK}" stroke-width="3"/>' + text(cx4 + 22, cy, "Subprocesso (detalhado à parte)", anchor="start", size=11))
    lg.append(flow([(cx4 - 16, cy + 34), (cx4 + 14, cy + 34)], "msg") + text(cx4 + 22, cy + 34, "Mensagem com o lead", anchor="start", size=11))
    lg.append(flow([(cx4 - 16, cy + 68), (cx4 + 14, cy + 68)]) + text(cx4 + 22, cy + 68, "Fluxo de sequência", anchor="start", size=11))
    b.extend(lg)
    b.append(text(LX + 14, LY + 138, "* conteúdo da etapa Alinhamento de projeto ainda a definir (ver pág. 3)", anchor="start", size=10.5, color=MUTED, italic=True))

    return svg(W, H, b)


# ---------------------------------------------------------------- página 2: subprocessos

def sub_a():
    W, H = 1020, 470
    b = []
    lane_defs = [("Agente de IA", 150), ("Kommo CRM", 140), ("Equipe\ncomercial", 150)]
    b.append(lanes(0, 10, W - 2, lane_defs, "A · Atendimento imediato", label_w=96))
    A, K, C = 85, 230, 375
    b.append(event(195, A, "start", "msg", "Lead pede humano\n(ou escolhe opção 3)", "below"))
    b.append(gateway(275, A, "x", "Horário\ncomercial?", "above"))
    b.append(flow([(212, A), (250, A)]))
    # Sim
    b.append(task(410, A, 150, 56, "Avisar: um especialista\nfala com você em\naté 30 min", "send", size=10.5))
    b.append(flow([(300, A), (335, A)], label="Sim", lx=316, ly=A - 10))
    b.append(task(435, K, 150, 64, "Pausar robô, mover p/\nAtendimento imediato\n+ notificar comercial", "service", size=10.5))
    b.append(flow([(410, A + 28), (410, K - 32)]))
    b.append(gateway(575, K, "event"))
    b.append(flow([(510, K), (550, K)]))
    b.append(event(575, A, "inter", "timer", "30 min sem\nhumano", "left"))
    b.append(flow([(575, K - 25), (575, A + 17)]))
    b.append(task(715, A, 160, 56, "Robô retoma: “posso\najudar com mais\nalguma coisa?”", "send", size=11))
    b.append(flow([(592, A), (635, A)]))
    b.append(task(870, K, 160, 56, "Criar tarefa +\nnova notificação\nao comercial", "service", size=11))
    b.append(flow([(795, A), (870, A), (870, K - 28)]))
    b.append(flow([(790, K), (600, K)], label="volta a aguardar", lx=695, ly=K - 10))
    b.append(event(575, C, "inter", "msg", "Comercial\nassumiu", "left"))
    b.append(flow([(575, K + 25), (575, C - 17)]))
    b.append(task(720, C, 160, 56, "Atender o lead e\nagendar visita/ligação", "user", size=11.5))
    b.append(flow([(592, C), (640, C)]))
    b.append(event(870, C, "end", None, "Segue p/ Alinhamento\nde projeto", "right"))
    b.append(flow([(800, C), (853, C)]))
    # Não
    b.append(task(275, K, 140, 64, "Enviar msg “atendemos\ndas Xh às Yh” + criar\ntarefa p/ abertura", "service", size=10))
    b.append(flow([(275, A + 25), (275, K - 32)], label="Não", lx=283, ly=A + 45, anchor="start"))
    b.append(task(275, C, 150, 56, "Atender no próximo\nhorário comercial", "user", size=11))
    b.append(flow([(275, K + 32), (275, C - 28)]))
    b.append(event(410, C, "end", None))
    b.append(flow([(350, C), (393, C)]))
    return svg(W, H, b)


def sub_b():
    W, H = 840, 300
    b = []
    lane_defs = [("Equipe\ncomercial", 140), ("Kommo CRM", 140)]
    b.append(lanes(0, 10, W - 2, lane_defs, "B · Comercial assume", label_w=96))
    C, K = 80, 220
    b.append(event(185, C, "start", "msg", "Comercial decide\nassumir a conversa", "below"))
    b.append(task(330, K, 150, 56, "Pausar o robô\npara este lead", "service"))
    b.append(flow([(202, C), (240, C), (240, K), (255, K)]))
    b.append(task(500, C, 160, 56, "Conduzir o\natendimento", "user"))
    b.append(flow([(405, K), (500, K), (500, C + 28)]))
    b.append(event(680, C, "end", None, "Comercial move a\netapa manualmente", "below"))
    b.append(flow([(580, C), (663, C)]))
    return svg(W, H, b)


def sub_c():
    W, H = 2080, 470
    b = []
    lane_defs = [("Agente de IA", 160), ("Kommo CRM", 130), ("Equipe\ncomercial", 160)]
    b.append(lanes(0, 10, W - 2, lane_defs, "C · Cadência de follow-up", label_w=96))
    A, A2, K, C, C2 = 70, 135, 235, 340, 410
    b.append(event(175, A, "start", None, "Lead sem\nresposta", "below"))
    b.append(event(250, A, "inter", "timer", "30 min*", "below"))
    b.append(flow([(192, A), (233, A)]))
    b.append(task(370, A, 150, 56, "Relance rápido*\n(dentro da janela)", "send", size=11.5))
    b.append(flow([(267, A), (295, A)]))

    def eg_resp(x, y, yr):
        return (gateway(x, y, "event")
                + event(x, yr, "inter", "msg", r=14)
                + flow([(x, y + 25), (x, yr - 14)])
                + event(x + 52, yr, "throw", "link", "A · respondeu:\nvolta ao atendimento" if x < 600 else "A", "right", r=14, lsize=10.5)
                + flow([(x + 14, yr), (x + 38, yr)]))

    b.append(eg_resp(500, A, A2))
    b.append(flow([(445, A), (475, A)]))
    b.append(event(640, A, "inter", "timer", "D+1", "above"))
    b.append(flow([(525, A), (623, A)]))
    b.append(task(790, A, 210, 62, "D+1 · Mensagem personalizada\n(enviar até 23h após a última\nmsg do lead: janela de 24h)", "send", size=10.5))
    b.append(flow([(657, A), (685, A)]))
    b.append(eg_resp(945, A, A2))
    b.append(flow([(895, A), (920, A)]))
    b.append(event(1040, A, "inter", "timer", "D+3", "above"))
    b.append(flow([(970, A), (1023, A)]))
    b.append(task(1190, A, 210, 62, "D+3 · Template pago (fora da\njanela 24h) + material\ntentador — só WhatsApp API**", "send", size=10.5))
    b.append(flow([(1057, A), (1085, A)]))
    b.append(eg_resp(1345, A, A2))
    b.append(flow([(1295, A), (1320, A)]))
    b.append(event(1440, A, "inter", "timer", "D+5", "above"))
    b.append(flow([(1370, A), (1423, A)]))
    b.append(task(1440, K, 150, 56, "Criar tarefa de\nfollow-up p/ comercial", "service", size=11))
    b.append(flow([(1440, A + 17), (1440, K - 28)]))
    b.append(task(1440, C, 170, 56, "D+5 · Follow-up humano\n(msg personalizada)**", "user", size=10.5))
    b.append(flow([(1440, K + 28), (1440, C - 28)]))
    b.append(eg_resp(1600, C, C2))
    b.append(flow([(1525, C), (1575, C)]))
    b.append(event(1690, C, "inter", "timer", "D+7", "above"))
    b.append(flow([(1625, C), (1673, C)]))
    b.append(task(1800, C, 150, 56, "D+7 · Follow-up\nhumano (último)**", "user", size=11))
    b.append(flow([(1707, C), (1725, C)]))
    b.append(eg_resp(1940, C, C2) if False else gateway(1940, C, "event"))
    b.append(flow([(1875, C), (1915, C)]))
    b.append(event(1940, C2 + 5, "inter", "msg", r=14))
    b.append(flow([(1940, C + 25), (1940, C2 - 9)]))
    b.append(event(1990, C2 + 5, "throw", "link", "A", "right", r=14))
    b.append(flow([(1954, C2 + 5), (1976, C2 + 5)]))
    b.append(event(1940, K, "inter", "timer", "prazo final\n(a definir)", "left"))
    b.append(flow([(1940, C - 25), (1940, K + 17)]))
    b.append(task(1940, A, 150, 56, "Mover para\nPerdido", "service"))
    b.append(flow([(1940, K - 17), (1940, A + 28)]))
    b.append(event(2045, A, "end", None, "Perdido", "below"))
    b.append(flow([(2015, A), (2028, A)]))
    return svg(W, H, b)


# ---------------------------------------------------------------- HTML

CSS = """
@page { size: A3 landscape; margin: 9mm; }
* { box-sizing: border-box; }
:root { --ink:#1f2933; --muted:#52606d; --line:#c5ced8; --bg:#ffffff; }
html, body { margin:0; background:var(--bg); color:var(--ink); font-family: Inter, Helvetica, Arial, sans-serif; }
.page { page-break-after: always; break-after: page; padding: 0; }
.page:last-child { page-break-after: auto; break-after: auto; }
header.doc { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid var(--ink); padding-bottom:6px; margin-bottom:10px; }
header.doc h1 { font-size:20px; margin:0; letter-spacing:-0.01em; }
header.doc .meta { font-size:11px; color:var(--muted); text-align:right; line-height:1.4; }
h2 { font-size:15px; margin:14px 0 6px; }
.row { display:flex; gap:18px; align-items:flex-start; }
.note { font-size:11.5px; color:var(--muted); line-height:1.45; }
.box { border:1px solid var(--line); border-radius:8px; padding:10px 14px; background:#fafbfc; }
table { border-collapse:collapse; width:100%; font-size:11.5px; }
th, td { border:1px solid var(--line); padding:5px 8px; text-align:left; vertical-align:top; }
th { background:#eef2f6; }
ol, ul { margin:4px 0; padding-left:20px; font-size:12px; line-height:1.5; }
li { margin-bottom:3px; }
a { color:#1d4f91; }
.cols { display:grid; grid-template-columns: 1.15fr 1fr; gap:22px; }
"""


def header(sub):
    return (f'<header class="doc"><h1>SmartYou · Processo de atendimento do agente de IA — {sub}</h1>'
            f'<div class="meta">Notação BPMN 2.0 · Versão 0.1 (rascunho para validação)<br>12/11/2026</div></header>')


def pagina3():
    return """
<div class="cols">
<div>
<h2>Etapas do funil no Kommo (proposta)</h2>
<table>
<tr><th>Etapa</th><th>Entra quando</th><th>Sai quando</th><th>Responsável</th></tr>
<tr><td>Prospect</td><td>Chega a 1ª mensagem (Instagram, Facebook ou WhatsApp)</td><td>Lead responde à saudação → Em atendimento · Cadência esgota → Perdido</td><td>Agente de IA</td></tr>
<tr><td>Em atendimento (IA)</td><td>Lead respondeu</td><td>Visita ou ligação agendada → Alinhamento de projeto · Pediu humano → Atendimento imediato</td><td>Agente de IA (o comercial pode assumir)</td></tr>
<tr><td>Atendimento imediato</td><td>Lead pede humano ou escolhe a opção 3</td><td>O humano agenda a visita ou ligação → Alinhamento de projeto</td><td>Comercial</td></tr>
<tr><td>Alinhamento de projeto</td><td>Visita ou ligação agendada</td><td>Alinhamento concluído → Aguardando atendimento humano</td><td>Agente de IA*</td></tr>
<tr><td>Aguardando atendimento humano</td><td>Alinhamento concluído; comercial notificado</td><td>O comercial assume (fora do escopo do robô)</td><td>Comercial</td></tr>
<tr><td>Perdido (fechado)</td><td>Sem resposta depois do follow-up D+7 e do prazo final</td><td>—</td><td>Kommo (automático)</td></tr>
</table>

<h2>Decisões em aberto (a validar)</h2>
<ol>
<li><b>Relance de 30 min e o “2x”.</b> Interpretei o rascunho assim: relance rápido aos 30 min → D+1 e D+3 pelo robô (os “2x”) → D+5 e D+7 pelo humano → Perdido. O relance de 30 min conta como um dos 2?</li>
<li><b>Alinhamento de projeto*</b>: o que o robô faz nessa etapa (confirmar o agendamento? coletar o briefing do projeto?) e por que ela é separada de “Aguardando atendimento humano”?</li>
<li><b>Subprocesso A, repetições</b>: quantas vezes o robô retoma e renotifica antes de escalar (por exemplo, para o gestor)?</li>
<li><b>Fora do horário</b>: depois de transferir para humano, o robô continua tirando dúvidas ou fica em silêncio até a abertura?</li>
<li><b>Prazo final</b> entre o D+7 e a mudança para Perdido.</li>
<li><b>Horário comercial</b>: dias e horas (sábado entra?). Isso define o gateway “Horário comercial?”.</li>
<li><b>Lead que chega fora do horário</b>: a equipe recebe a notificação na abertura do dia seguinte?</li>
<li><b>Subprocesso B</b>: o comercial pode devolver a conversa ao robô?</li>
<li><b>Material tentador</b>: ainda a definir.</li>
<li><b>Critérios de qualificação</b>: ficam para depois, como combinado.</li>
</ol>
</div>
<div>
<h2>** Restrições por canal que afetam a cadência</h2>
<div class="box">
<ul>
<li><b>WhatsApp Business Platform (API oficial):</b> mensagem livre só vale até 24h depois da última mensagem do cliente, e o prazo reinicia a cada nova mensagem dele. Fora dessa janela, só é possível enviar <i>templates</i> aprovados, que são cobrados. Por isso o D+1 precisa sair antes de fechar 24h, e o D+3 precisa ser template. Fonte: <a href="https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing">Meta — WhatsApp Business Platform pricing</a>.</li>
<li><b>Instagram e Facebook Messenger:</b> a janela padrão também é de 24h. Fora dela não existe template pago equivalente: só valem as <i>message tags</i> aprovadas. A tag <code>HUMAN_AGENT</code> deixa <u>um humano</u> responder manualmente por até 7 dias, com conteúdo não promocional. Fonte: <a href="https://developers.facebook.com/docs/messenger-platform/policy/policy-overview">Meta — Messenger Platform &amp; IG Messaging API Policy</a>.</li>
</ul>
<p class="note"><b>Consequências para o processo:</b> (a) no Instagram e no Facebook o robô <u>não consegue</u> fazer o D+3; (b) o D+5 e o D+7 humanos cabem na janela de 7 dias da <code>HUMAN_AGENT</code> (o D+7 fica no limite), mas “material tentador” provavelmente é promocional e pode violar a política; (c) falta confirmar como o <b>WhatsApp Lite</b> do Kommo (conexão pelo app, não pela API) lida com janela e templates. Ainda não verifiquei isso.</p>
<p class="note">Atenção: há mudanças recentes na cobrança do WhatsApp (outubro/2026) que as fontes descrevem de formas diferentes. Antes de calcular custo, confira a página oficial da Meta e a do Kommo.</p>
</div>

<h2>Regras que valem em qualquer etapa</h2>
<ul>
<li>Em horário comercial, cada conversa nova notifica a equipe comercial (raia Kommo, pág. 1).</li>
<li>O lead pode pedir humano a qualquer momento → Subprocesso A.</li>
<li>O comercial pode assumir a qualquer momento, e o robô pausa → Subprocesso B.</li>
<li>A cadência (Subprocesso C) é reiniciada pela última resposta do lead (contagem de dias desde a última resposta).</li>
</ul>
</div>
</div>
"""


def build():
    p1 = pagina1()
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Processo Atendimento IA</title>
<style>{CSS}</style></head><body>
<section class="page">{header("Visão geral")}{p1}</section>
<section class="page">{header("Subprocessos")}
<div class="row"><div style="flex:1.2">{sub_a()}</div><div style="flex:1">{sub_b()}
<p class="note" style="margin-top:8px">A: o “Sim” do gateway usa o horário comercial definido na pág. 3. O ciclo “robô retoma + renotifica” se repete a cada 30 min; o limite de repetições é uma decisão em aberto.<br>
B: evento interruptivo. Quando o humano assume, o robô para de responder esse lead.</p></div></div>
<div style="margin-top:14px">{sub_c()}</div>
<p class="note">* Relance de 30 min vem do rascunho (etapa Prospect); confirmar se faz parte dos “2x”. ** Ver restrições por canal na pág. 3. Os dias contam a partir da última resposta do lead; qualquer resposta encerra a cadência e devolve o lead ao atendimento (conector A).</p>
</section>
<section class="page">{header("Etapas, decisões em aberto e restrições")}{pagina3()}</section>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print("ok", OUT)


if __name__ == "__main__":
    build()
