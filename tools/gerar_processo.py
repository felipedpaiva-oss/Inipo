#!/usr/bin/env python3
"""Gera processos/atendimento-agente-ia-smartyou.drawio (abrir em app.diagrams.net).

O arquivo .drawio é a fonte de verdade depois de gerado: edite no draw.io.
Rode este script de novo só se quiser recriar tudo do zero (sobrescreve edições).
"""
from xml.sax.saxutils import quoteattr
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "processos" / "atendimento-agente-ia-smartyou.drawio"

# ---------------------------------------------------------------- estilos
EV_PTS = "points=[[0.145,0.145,0],[0.5,0,0],[0.855,0.145,0],[1,0.5,0],[0.855,0.855,0],[0.5,1,0],[0.145,0.855,0],[0,0.5,0]];"
GW_PTS = "points=[[0.25,0.25,0],[0.5,0,0],[0.75,0.25,0],[1,0.5,0],[0.75,0.75,0],[0.5,1,0],[0.25,0.75,0],[0,0.5,0]];"
TK_PTS = "points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"

LANE_COLORS = {
    "lead": ("#f5f5f5", "#666666"),
    "agente": ("#dae8fc", "#6c8ebf"),
    "crm": ("#ffe6cc", "#d79b00"),
    "humano": ("#d5e8d4", "#82b366"),
}

LABEL_BELOW = "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
LABEL_RIGHT = "labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;spacingLeft=4;"
LABEL_LEFT = "labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;spacingRight=4;"
LABEL_ABOVE = "verticalLabelPosition=top;verticalAlign=bottom;align=center;"


def ev(outline, symbol, lp="below", fill="#ffffff"):
    pos = {"below": LABEL_BELOW, "right": LABEL_RIGHT, "left": LABEL_LEFT, "above": LABEL_ABOVE}[lp]
    sw = "strokeWidth=1;"
    return (f"{EV_PTS}shape=mxgraph.bpmn.event;html=1;whiteSpace=wrap;labelBackgroundColor=none;"
            f"perimeter=ellipsePerimeter;outlineConnect=0;aspect=fixed;outline={outline};symbol={symbol};"
            f"fillColor={fill};{sw}{pos}fontSize=11;")


def gw(kind, lp="above"):
    sym = {"x": "outline=none;symbol=exclusiveGw;", "+": "outline=none;symbol=parallelGw;",
           "evt": "outline=catching;symbol=multiple;"}[kind]
    pos = {"below": LABEL_BELOW, "right": LABEL_RIGHT, "left": LABEL_LEFT, "above": LABEL_ABOVE}[lp]
    return (f"{GW_PTS}shape=mxgraph.bpmn.gateway2;html=1;whiteSpace=wrap;labelBackgroundColor=none;"
            f"perimeter=rhombusPerimeter;outlineConnect=0;{sym}{pos}fontSize=11;fillColor=#ffffff;")


def task(lane, marker="abstract", call=False):
    fill, stroke = LANE_COLORS[lane]
    extra = "bpmnShapeType=call;" if call else f"taskMarker={marker};"
    return (f"{TK_PTS}shape=mxgraph.bpmn.task2;whiteSpace=wrap;rectStyle=rounded;size=10;html=1;"
            f"expand=0;collapsible=0;{extra}fillColor={fill};strokeColor={stroke};fontSize=11;")


NOTE = ("shape=note;whiteSpace=wrap;html=1;size=12;align=left;verticalAlign=top;spacing=6;"
        "fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;")
OPEN = ("shape=note;whiteSpace=wrap;html=1;size=12;align=left;verticalAlign=top;spacing=6;"
        "fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;")
ANNOT = ("html=1;shape=mxgraph.flowchart.annotation_1;align=left;verticalAlign=middle;pointerEvents=1;"
         "whiteSpace=wrap;spacingLeft=6;fontSize=10;fontColor=#333333;")
FLOW = ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;"
        "endFill=1;labelBackgroundColor=#ffffff;fontSize=10;")
ASSOC = "endArrow=none;dashed=1;dashPattern=2 3;html=1;strokeColor=#999999;"


# ---------------------------------------------------------------- modelo
class Page:
    def __init__(self, pid, name, w=2400, h=1500):
        self.pid, self.name, self.w, self.h = pid, name, w, h
        self.cells = []
        self.lanes = {}  # key -> (id, x, y)
        self.n = 0

    def nid(self, p="c"):
        self.n += 1
        return f"{self.pid}-{p}{self.n}"

    def raw(self, xml):
        self.cells.append(xml)

    def vertex(self, label, style, x, y, w, h, parent="1", id=None, link=None, tooltip=None):
        id = id or self.nid()
        geo = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        if link or tooltip:
            attrs = f' label={quoteattr(label)}'
            if link:
                attrs += f' link={quoteattr(link)}'
            if tooltip:
                attrs += f' tooltip={quoteattr(tooltip)}'
            self.raw(f'<UserObject id="{id}"{attrs}><mxCell style={quoteattr(style)} vertex="1" '
                     f'parent="{parent}">{geo}</mxCell></UserObject>')
        else:
            self.raw(f'<mxCell id="{id}" value={quoteattr(label)} style={quoteattr(style)} vertex="1" '
                     f'parent="{parent}">{geo}</mxCell>')
        return id

    def pool(self, title, x, y, width, lanes):
        """lanes: list of (key, label, height)"""
        self.vertex(f"<b>{title}</b>", "text;html=1;align=left;verticalAlign=middle;fontSize=18;",
                    x, y - 46, width, 36)
        cy = y
        for key, label, h in lanes:
            fill, stroke = LANE_COLORS[key]
            lid = f"{self.pid}-lane-{key}"
            st = (f"swimlane;horizontal=0;html=1;startSize=36;fillColor={fill};strokeColor={stroke};"
                  f"swimlaneFillColor=#ffffff;fontStyle=1;fontSize=13;collapsible=0;")
            self.vertex(label, st, x, cy, width, h, id=lid)
            self.lanes[key] = (lid, x, cy)
            cy += h
        return cy

    def at(self, lane, x, y):
        """converte coord. relativa da raia em absoluta (para waypoints)"""
        _, lx, ly = self.lanes[lane]
        return (lx + x, ly + y)

    def node(self, lane, label, style, x, y, w, h, **kw):
        return self.vertex(label, style, x, y, w, h, parent=self.lanes[lane][0], **kw)

    def edge(self, src, tgt, label="", style=FLOW, pts=None, exit=None, entry=None, id=None):
        id = id or self.nid("e")
        st = style
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        geo = '<mxGeometry relative="1" as="geometry">'
        if pts:
            geo += '<Array as="points">' + "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts) + "</Array>"
        geo += "</mxGeometry>"
        self.raw(f'<mxCell id="{id}" value={quoteattr(label)} style={quoteattr(st)} edge="1" parent="1" '
                 f'source="{src}" target="{tgt}">{geo}</mxCell>')
        return id

    def xml(self):
        body = "".join(self.cells)
        return (f'<diagram id="{self.pid}" name={quoteattr(self.name)}>'
                f'<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" '
                f'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root>'
                f'</mxGraphModel></diagram>')


def pagelink(pid):
    return f"data:page/id,{pid}"


FONTE_META = ("Fonte: Meta for Developers — WhatsApp Business Platform, &quot;Customer service windows&quot; "
              "e Messenger/Instagram Platform, &quot;Human Agent tag&quot;.")

CRITERIOS = ("<b>Critérios de qualificação</b> (o agente identifica durante a conversa)<br>"
             "• Tipo: obra nova, reforma ou casa pronta<br>"
             "• Bairro / cidade<br>"
             "• Ambientes<br>"
             "• Soluções desejadas<br>"
             "• Prioridade: conforto, segurança, praticidade ou entretenimento<br>"
             "• Estágio da obra e prazo<br>"
             "• Faixa de investimento (quando apropriado)<br>"
             "• Responsáveis pela decisão")

# ================================================================ PÁGINA 1
def pagina_mapa():
    p = Page("p1", "1. Fontes → Canais → Atendentes", 1900, 1150)
    p.vertex("<b>SmartYou · Atendimento de leads: fontes → canais → atendentes</b>",
             "text;html=1;align=left;fontSize=20;", 40, 20, 1200, 34)
    p.vertex("<b>Como associar:</b> passe o mouse sobre uma caixa, arraste uma das setas azuis até a caixa de destino "
             "e solte. Para apagar uma associação, clique na linha e tecle Delete. Cada coluna é um contêiner: "
             "arraste o título para mover a coluna inteira.<br><b>Legenda:</b> borda tracejada = a confirmar (\"?\") · "
             "borda vermelha = com bug · cinza = não utilizado.",
             NOTE, 40, 60, 1120, 70)

    colw, itemh, gap, top = 300, 46, 16, 160
    cols = [
        ("FONTES DE LEADS", "#e1d5e7", "#9673a6", [
            ("Facebook Ads", ""), ("Instagram Ads", ""), ("Orgânico Instagram", ""),
            ("Botões de WhatsApp no site", ""), ("Google Ads", ""), ("Indicação", ""), ("Arquitetos", ""),
        ]),
        ("CANAIS DE ATENDIMENTO", "#dae8fc", "#6c8ebf", [
            ("Instagram Messenger", ""), ("Facebook Messenger", ""),
            ("WhatsApp Lite<br>+55 31 9455-9999", ""),
            ("WhatsApp Business<br>(4 números, nenhum em uso)", "off"),
            ("WhatsApp pessoal do Lucas?", "q"), ("WhatsApp pessoal do Daniel?", "q"),
            ("Formulário no site ⚠ bug", "bug"),
            ("Botão \"Entre em contato e peça um orçamento! / Falar com atendente\" ⚠ bug", "bug"),
            ("Chatbot do site", ""), ("Ligação para o fixo?", "q"), ("TikTok Messenger?", "q"),
        ]),
        ("ATENDENTES", "#ffe6cc", "#d79b00", [
            ("<b>Agente IA Genérico</b>", "gen"), ("Agente IA Específico 1", ""), ("Agente IA Específico 2", ""),
            ("Agente IA Específico 3<br>(ou mudar para botão de WhatsApp)", "q"),
            ("Lucas", ""), ("Daniel", ""), ("Atendente humano", ""), ("Não usa", "off"),
        ]),
    ]
    xs = [40, 480, 920]
    gen_id = None
    for (title, fill, stroke, items), x in zip(cols, xs):
        h = 50 + len(items) * (itemh + gap) + 10
        cid = p.vertex(title, f"swimlane;html=1;startSize=40;fillColor={fill};strokeColor={stroke};"
                              f"swimlaneFillColor=#fbfbfb;fontStyle=1;fontSize=13;rounded=1;arcSize=4;collapsible=0;",
                       x, top, colw, h)
        for i, (label, kind) in enumerate(items):
            st = "rounded=1;whiteSpace=wrap;html=1;fontSize=12;arcSize=12;"
            if kind == "q":
                st += f"fillColor=#ffffff;strokeColor={stroke};dashed=1;"
            elif kind == "bug":
                st += "fillColor=#ffffff;strokeColor=#b85450;strokeWidth=2;fontColor=#b85450;"
            elif kind == "off":
                st += "fillColor=#eeeeee;strokeColor=#999999;fontColor=#777777;dashed=1;"
            elif kind == "gen":
                st += f"fillColor={fill};strokeColor={stroke};strokeWidth=3;"
            else:
                st += f"fillColor=#ffffff;strokeColor={stroke};"
            vid = p.vertex(label, st, 20, 50 + i * (itemh + gap), colw - 40, itemh, parent=cid)
            if kind == "gen":
                gen_id = vid

    # saída do Agente Genérico para os dois cenários
    g = p.vertex("Lead chegou em<br>horário comercial?<br>(seg–sex, 9h–18h)", gw("x", "below"), 1340, 205, 50, 50)
    p.edge(gen_id, g, exit=(1, 0.5), entry=(0, 0.5))
    a = p.vertex("Atendimento em horário comercial<br><i>(clique para abrir a pág. 2)</i>", task("agente", call=True),
                 1470, 80, 200, 80, link=pagelink("p2"))
    b = p.vertex("Atendimento fora do horário<br><i>(clique para abrir a pág. 3)</i>", task("agente", call=True),
                 1470, 190, 200, 80, link=pagelink("p3"))
    p.edge(g, a, "Sim", exit=(0.5, 0), entry=(0, 0.5))
    p.edge(g, b, "Não", exit=(1, 0.5), entry=(0, 0.5))
    p.vertex("Daqui em diante o documento detalha <b>apenas o Agente IA Genérico</b>. "
             "Os demais atendentes só aparecem neste mapa.", NOTE, 1340, 370, 330, 70)
    return p


# ================================================================ PÁGINA 2
def pagina_horario():
    p = Page("p2", "2. IA Genérico – Horário comercial", 2200, 1300)
    W = 1960
    p.pool("Agente IA Genérico · Em horário comercial (seg–sex, 9h–18h)", 40, 90, W, [
        ("lead", "Lead", 170), ("agente", "Agente IA Genérico", 430),
        ("crm", "CRM / Funis", 140), ("humano", "Atendente humano", 330)])

    # Lead
    s = p.node("lead", "Lead envia a 1ª mensagem<br>(qualquer canal)", ev("standard", "message", "right"), 130, 60, 50, 50)
    p.node("lead", "Humano pode assumir a conversa a qualquer momento (o agente é interrompível).",
           ANNOT, 470, 20, 300, 40)
    p.node("lead", "O lead pode pedir um humano a qualquer momento: isso dispara o evento <b>\"Lead pede humano\"</b> "
                   "e o leva direto ao ponto <b>A</b>.", ANNOT, 830, 20, 360, 50)

    # Agente
    gp = p.node("agente", "", gw("+", "above"), 130, 80, 50, 50)
    tq = p.node("agente", "Responder dúvidas do lead e fazer a qualificação", task("agente", "service"), 230, 60, 200, 90)
    bi = p.node("agente", "Inatividade", ev("boundNonint", "timer", "left"), 250, 130, 40, 40)
    bh = p.node("agente", "Lead pede<br>humano", ev("boundInt", "message", "right"), 360, 130, 40, 40)
    la = p.node("agente", "Vai para <b>A</b>", ev("throwing", "link", "right"), 360, 205, 40, 40)
    ci = p.node("agente", "Regras de inatividade<br><i>(pág. 4)</i>", task("agente", call=True), 185, 250, 170, 70,
                link=pagelink("p4"))
    gq = p.node("agente", "Lead<br>qualificado?", gw("x", "above"), 500, 80, 50, 50)
    ts = p.node("agente", "Sinalizar o lead para avaliação humana <i>(o agente segue a conversa)</i>", task("agente", "send"), 450, 255, 150, 80)
    to = p.node("agente", "Personalizar a proposta e oferecer as 3 opções", task("agente", "service"), 610, 65, 180, 80)
    go = p.node("agente", "Opção<br>escolhida", gw("x", "above"), 860, 80, 50, 50)
    tv = p.node("agente", "1) Agendar visita ao showroom", task("agente", "service"), 990, 10, 180, 60)
    tl = p.node("agente", "2) Agendar ligação com a equipe de vendas", task("agente", "service"), 990, 75, 180, 60)
    te = p.node("agente", "3) Avisar o lead: espera estimada de 15–30 min", task("agente", "send"), 990, 165, 180, 70)
    lai = p.node("agente", "<b>A</b>", ev("catching", "link", "left"), 1060, 290, 40, 40)
    ec = p.node("agente", "Processo<br>Comercial", ev("end", "general", "right"), 1240, 52, 40, 40)
    tn = p.node("agente", "Notificar humano: pedido de atendimento imediato", task("agente", "send"), 1230, 165, 180, 70)
    ge = p.node("agente", "", gw("evt", "above"), 1470, 175, 50, 50)
    t30 = p.node("agente", "30 min sem<br>humano assumir", ev("catching", "timer", "below"), 1580, 180, 40, 40)
    tm = p.node("agente", "Enviar ao lead: \"ainda estamos localizando um atendente; fico à disposição para dúvidas\" "
                          "+ <b>2ª notificação ao humano</b>", task("agente", "send"), 1670, 155, 230, 90)
    hw = p.node("agente", "Aguarda o humano<br>(sem novos lembretes)", ev("catching", "message", "right"), 1765, 300, 40, 40)

    # CRM
    ep = p.node("crm", "Funil: Perdidos<br>por inatividade", ev("end", "terminate", "right"), 250, 50, 40, 40)
    ed = p.node("crm", "Funil:<br>Desqualificados", ev("end", "terminate", "right"), 820, 50, 40, 40)

    # Humano
    hn = p.node("humano", "Recebe notificação: novo lead", task("humano", "receive"), 100, 180, 150, 70)
    ga = p.node("humano", "Assumir a<br>conversa?", gw("x", "above"), 300, 190, 50, 50)
    en = p.node("humano", "Não: o agente<br>conduz", ev("end", "general", "right"), 310, 280, 30, 30)
    ha = p.node("humano", "Assumir a conversa (o agente pausa)", task("humano", "user"), 420, 180, 170, 70)
    eh = p.node("humano", "Processo<br>Comercial", ev("end", "general", "right"), 485, 275, 40, 40)
    hv = p.node("humano", "Avaliar o lead<br><i>(critérios: ver nota)</i>", task("humano", "user"), 450, 30, 150, 70)
    gd = p.node("humano", "Decisão", gw("x", "above"), 650, 40, 50, 50)
    h3 = p.node("humano", "Assumir o chat", task("humano", "user"), 1420, 40, 150, 70)
    e3 = p.node("humano", "Processo<br>Comercial", ev("end", "general", "right"), 1475, 160, 40, 40)

    # Fluxos
    p.edge(s, gp, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(gp, tq, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gp, hn, exit=(0.5, 1), entry=(0.367, 0))
    p.edge(bi, ci, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ci, ep, "24h sem<br>mensagem do lead", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(bh, la, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(tq, gq, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gq, to, "Sim", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gq, ts, "Não / em dúvida", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ts, hv, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(hv, gd, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gd, to, "Seguir com o agente", exit=(0.5, 0), entry=(0.361, 1))
    p.edge(gd, ed, "Desqualificar", exit=(1, 0.5), entry=(0.5, 1))
    p.edge(gd, ha, "Assumir", exit=(0.5, 1), entry=(1, 0.5))
    p.edge(to, go, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(go, tv, "1", exit=(0.5, 0), entry=(0, 0.5))
    p.edge(go, tl, "2", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(go, te, "3", exit=(0.5, 1), entry=(0, 0.5))
    p.edge(tv, ec, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(tl, ec, exit=(1, 0.5), entry=(0.5, 1))
    p.edge(lai, te, exit=(0.5, 0), entry=(0.389, 1))
    p.edge(te, tn, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(tn, ge, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ge, t30, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(t30, tm, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(tm, hw, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(hw, h3, "Humano assume", exit=(0.5, 1), entry=(1, 0.5))
    p.edge(ge, h3, "Humano assume", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(h3, e3, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(hn, ga, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ga, ha, "Sim", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ga, en, "Não", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ha, eh, exit=(0.5, 1), entry=(0.5, 0))

    # Notas e pendências (fora da pool, à direita/abaixo)
    oy = 90 + 170 + 430 + 140 + 330 + 30
    p.vertex(CRITERIOS, NOTE, 40, oy, 470, 170)
    p.vertex("<b>Regras desta página</b><br>"
             "• Na 1ª mensagem o humano é notificado <i>em paralelo</i> ao início do atendimento pelo agente.<br>"
             "• \"Lead pede humano\" interrompe a qualificação e cai na opção 3 (ponto A).<br>"
             "• Lead em dúvida: o humano avalia enquanto o agente segue a conversa.<br>"
             "• Opção 3: depois da 2ª notificação o agente não insiste mais; aguarda o humano.<br>"
             "• Feriados não são horário comercial (seguem a pág. 3).<br>"
             "• Inatividade: ver pág. 4 (15 min ×2, 23h, 24h → perdido).<br>"
             "• Do agendamento em diante, a responsabilidade é do <b>Processo Comercial</b>.",
             NOTE, 530, oy, 640, 170)
    p.vertex("<b>⚠ Em aberto (horário comercial)</b><br>"
             "1. Quem recebe as notificações (Lucas, Daniel, um grupo) e por qual canal (WhatsApp, e-mail, CRM)?",
             OPEN, 1190, oy, 420, 80)
    return p


# ================================================================ PÁGINA 3
def pagina_fora():
    p = Page("p3", "3. IA Genérico – Fora do horário", 2450, 1350)
    W = 2320
    p.pool("Agente IA Genérico · Fora do horário comercial (noites, fins de semana e feriados)", 40, 90, W, [
        ("lead", "Lead", 170), ("agente", "Agente IA Genérico", 430),
        ("crm", "CRM / Funis", 140), ("humano", "Atendente humano", 360)])

    s = p.node("lead", "Lead envia a 1ª mensagem<br>(qualquer canal)", ev("standard", "message", "right"), 185, 60, 50, 50)
    p.node("lead", "Fora do horário (inclusive feriados) só o agente atende: <b>não</b> há notificação ao humano na 1ª mensagem.", ANNOT, 430, 20, 360, 50)
    p.node("lead", "O lead pode pedir um humano a qualquer momento. Ele é avisado do horário "
                   "(seg–sex, 9h–18h) e pode deixar o pedido na fila.", ANNOT, 830, 20, 380, 50)

    tq = p.node("agente", "Responder dúvidas do lead e fazer a qualificação", task("agente", "service"), 100, 60, 220, 90)
    bi = p.node("agente", "Inatividade", ev("boundNonint", "timer", "left"), 130, 130, 40, 40)
    bh = p.node("agente", "Lead pede<br>humano", ev("boundNonint", "message", "right"), 260, 130, 40, 40)
    ci = p.node("agente", "Regras de inatividade<br><i>(pág. 4)</i>", task("agente", call=True), 65, 250, 170, 70,
                link=pagelink("p4"))
    ti = p.node("agente", "Informar o horário humano (seg–sex, 9h–18h) e oferecer: deixar pedido para o humano ou seguir com o agente",
                task("agente", "send"), 250, 240, 200, 90)
    gpf = p.node("agente", "Lead<br>prefere", gw("x", "above"), 490, 260, 50, 50)
    es = p.node("agente", "Conversa segue<br>com o agente", ev("end", "general", "right"), 500, 360, 30, 30)
    lb = p.node("agente", "Vai para <b>B</b>", ev("throwing", "link", "above"), 600, 265, 40, 40)
    gq = p.node("agente", "Lead<br>qualificado?", gw("x", "above"), 700, 80, 50, 50)
    ts = p.node("agente", "Sinalizar o lead para avaliação humana no próximo dia útil <i>(o agente segue a conversa)</i>", task("agente", "send"), 650, 245, 150, 90)
    to = p.node("agente", "Personalizar a proposta e oferecer as 3 opções", task("agente", "service"), 810, 65, 180, 80)
    go = p.node("agente", "Opção<br>escolhida", gw("x", "above"), 1060, 80, 50, 50)
    tv = p.node("agente", "1) Agendar visita ao showroom", task("agente", "service"), 1190, 10, 180, 60)
    tl = p.node("agente", "2) Agendar ligação com a equipe de vendas", task("agente", "service"), 1190, 75, 180, 60)
    tf = p.node("agente", "3) Avisar o horário humano (seg–sex, 9h–18h) e registrar o pedido na fila",
                task("agente", "send"), 1190, 165, 180, 80)
    lbi = p.node("agente", "<b>B</b>", ev("catching", "link", "left"), 1260, 300, 40, 40)
    ec = p.node("agente", "Processo<br>Comercial", ev("end", "general", "right"), 1440, 52, 40, 40)

    ep = p.node("crm", "Funil: Perdidos<br>por inatividade", ev("end", "terminate", "right"), 130, 50, 40, 40)
    ed = p.node("crm", "Funil:<br>Desqualificados", ev("end", "terminate", "right"), 1000, 50, 40, 40)
    cf = p.node("crm", "Marcar lead como <b>\"Aguardando humano\"</b> (não vira perdido por inatividade)",
                task("crm", "service"), 1440, 30, 220, 80)

    hv = p.node("humano", "Avaliar o lead no próximo dia útil<br><i>(critérios: ver nota)</i>", task("humano", "user"),
                650, 30, 150, 80)
    gd = p.node("humano", "Decisão", gw("x", "above"), 850, 45, 50, 50)
    ha = p.node("humano", "Assumir a conversa<br><i>(aplicar regra da janela, ponto B)</i>", task("humano", "user"),
                800, 170, 150, 70)
    eh = p.node("humano", "Processo<br>Comercial", ev("end", "general", "right"), 855, 280, 40, 40)
    td = p.node("humano", "Próximo dia<br>útil, 9h", ev("catching", "timer", "below"), 1530, 40, 40, 40)
    gj = p.node("humano", "Janela de 24h<br>ainda aberta?", gw("x", "above"), 1640, 35, 50, 50)
    hr = p.node("humano", "Retomar a conversa no chat (mensagem livre)", task("humano", "user"), 1760, 25, 180, 70)
    gc = p.node("humano", "Canal", gw("x", "left"), 1640, 145, 50, 50)
    ht = p.node("humano", "Enviar <b>template aprovado</b> pela Meta (mensagem paga) para reabrir a conversa",
                task("humano", "send"), 1760, 130, 180, 80)
    hg = p.node("humano", "Responder com a tag <b>HUMAN_AGENT</b> (permitido até 7 dias após a última mensagem do lead)",
                task("humano", "send"), 1760, 240, 180, 90)
    hat = p.node("humano", "Atendimento humano", task("humano", "user"), 2000, 140, 150, 70)
    eh2 = p.node("humano", "Processo<br>Comercial", ev("end", "general"), 2195, 155, 40, 40)

    p.edge(s, tq, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(bi, ci, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ci, ep, "24h sem msg do lead<br>e fora da fila", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(bh, ti, exit=(0.5, 1), entry=(0.05, 0))
    p.edge(ti, gpf, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gpf, es, "Seguir com<br>o agente", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(gpf, lb, "Deixar pedido", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(tq, gq, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gq, to, "Sim", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gq, ts, "Não / em dúvida", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ts, hv, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(hv, gd, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gd, to, "Seguir com o agente", exit=(0.5, 0), entry=(0.361, 1))
    p.edge(gd, ed, "Desqualificar", exit=(1, 0.5), entry=(0.5, 1))
    p.edge(gd, ha, "Assumir", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(ha, eh, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(to, go, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(go, tv, "1", exit=(0.5, 0), entry=(0, 0.5))
    p.edge(go, tl, "2", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(go, tf, "3", exit=(0.5, 1), entry=(0, 0.5))
    p.edge(tv, ec, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(tl, ec, exit=(1, 0.5), entry=(0.5, 1))
    p.edge(lbi, tf, exit=(0.5, 0), entry=(0.389, 1))
    p.edge(tf, cf, exit=(1, 0.5), entry=(0.5, 0))
    p.edge(cf, td, exit=(0.5, 1), entry=(0.5, 0))
    p.edge(td, gj, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gj, hr, "Sim", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gj, gc, "Não", exit=(0.5, 1), entry=(0.5, 0))
    p.edge(gc, ht, "WhatsApp", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gc, hg, "Instagram /<br>Facebook", exit=(0.5, 1), entry=(0, 0.5))
    p.edge(hr, hat, exit=(1, 0.5), entry=(0.5, 0))
    p.edge(ht, hat, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(hg, hat, exit=(1, 0.5), entry=(0.5, 1))
    p.edge(hat, eh2, exit=(1, 0.5), entry=(0, 0.5))

    oy = 90 + 170 + 430 + 140 + 360 + 30
    p.vertex(CRITERIOS, NOTE, 40, oy, 470, 170)
    p.vertex("<b>⚠ Em aberto (fora do horário)</b><br>"
             "1. No dia útil seguinte o humano envia o template (WhatsApp) ou a mensagem com a tag (Instagram/Facebook) "
             "e o lead <b>não responde</b>: tenta de novo? Quantas vezes? Depois de quanto tempo o lead vai para Perdidos?<br>"
             "2. Quem trabalha a fila \"Aguardando humano\" às 9h? Em que ordem (chegada, score)?<br>"
             "3. Templates: textos e categoria (utilidade × marketing) a aprovar na Meta antes de ir para produção.<br>"
             "<i>Implementação: o agente precisa de um calendário de feriados para saber que está fora do horário.</i>",
             OPEN, 530, oy, 560, 170)
    p.vertex("<b>Por que o ponto B se divide por canal</b><br>"
             "• <b>WhatsApp</b>: a janela de atendimento de 24h abre e <i>reinicia só quando o lead escreve</i>. Fora dela, "
             "só é permitido enviar template aprovado.<br>"
             "• <b>Instagram/Facebook</b>: a tag HUMAN_AGENT permite que um <i>humano</i> responda até 7 dias depois. "
             "Não pode ser usada em mensagem automática e exige permissão aprovada no app da Meta.<br>"
             f"<i>{FONTE_META}</i>",
             NOTE, 1110, oy, 760, 170)
    return p


# ================================================================ PÁGINA 4
def pagina_inatividade():
    p = Page("p4", "4. Subprocesso – Inatividade", 1500, 1000)
    W = 1300
    p.pool("Subprocesso · Regras de inatividade (chamado pelas págs. 2 e 3)", 40, 90, W, [
        ("agente", "Agente IA Genérico", 470), ("crm", "CRM / Funis", 140)])

    s = p.node("agente", "Lead parou<br>de responder", ev("standard", "general", "below"), 70, 215, 40, 40)
    gm = p.node("agente", "", gw("x", "above"), 150, 210, 50, 50)
    ge = p.node("agente", "", gw("evt", "below"), 240, 210, 50, 50)
    mr = p.node("agente", "Lead<br>respondeu", ev("catching", "message", "below"), 340, 60, 40, 40)
    eb = p.node("agente", "Volta ao ponto da conversa<br>(zera os contadores)", ev("end", "general", "right"), 440, 60, 40, 40)
    t15 = p.node("agente", "15 min sem<br>resposta", ev("catching", "timer", "below"), 340, 160, 40, 40)
    gc = p.node("agente", "Atingiu o limite de<br>reativações de 15 min?<br>(comercial: 2 · fora: 1)", gw("x", "below"), 450, 155, 50, 50)
    r15 = p.node("agente", "Enviar mensagem de reativação (15 min)", task("agente", "send"), 560, 145, 180, 70)
    t23 = p.node("agente", "23h desde a última<br>mensagem <b>do lead</b>", ev("catching", "timer", "below"), 340, 270, 40, 40)
    r23 = p.node("agente", "Enviar última reativação (ainda dentro da janela de 24h)", task("agente", "send"), 560, 255, 180, 70)
    t24 = p.node("agente", "24h desde a última<br>mensagem <b>do lead</b>", ev("catching", "timer", "below"), 340, 375, 40, 40)
    gf = p.node("agente", "Lead está na fila<br>\"Aguardando humano\"?", gw("x", "above"), 470, 370, 50, 50)
    ef = p.node("agente", "Não vira perdido: o humano retoma no<br>próximo dia útil (pág. 3, ponto B)",
                ev("end", "general", "right"), 640, 375, 40, 40)
    ep = p.node("crm", "Mover para o funil<br>Perdidos por inatividade", ev("end", "terminate", "right"), 475, 50, 40, 40)

    p.edge(s, gm, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gm, ge, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ge, mr, exit=(0.5, 0), entry=(0, 0.5))
    p.edge(mr, eb, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ge, t15, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(t15, gc, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gc, r15, "Não", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ge, t23, exit=(0.75, 0.75), entry=(0, 0.5))
    p.edge(t23, r23, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(ge, t24, exit=(0.5, 1), entry=(0, 0.5))
    p.edge(t24, gf, exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gf, ef, "Sim", exit=(1, 0.5), entry=(0, 0.5))
    p.edge(gf, ep, "Não", exit=(0.5, 1), entry=(0.5, 0))
    # laços de volta para "aguardar" (gateway de junção)
    top = p.at("agente", 0, 25)[1]
    xr = p.at("agente", 800, 0)[0]
    gmx = p.at("agente", 175, 0)[0]
    p.edge(r15, gm, "volta a aguardar", exit=(1, 0.5), entry=(0.5, 0),
           pts=[(xr, p.at("agente", 0, 180)[1]), (xr, top), (gmx, top)])
    p.edge(r23, gm, exit=(1, 0.5), entry=(0.5, 0),
           pts=[(xr, p.at("agente", 0, 290)[1]), (xr, top), (gmx, top)])
    gcx = p.at("agente", 475, 0)[0]
    p.edge(gc, gm, "Sim (só aguarda)", exit=(0.5, 0), entry=(0.5, 0),
           pts=[(gcx, p.at("agente", 0, 120)[1]), (xr, p.at("agente", 0, 120)[1]), (xr, top), (gmx, top)])

    p.vertex("<b>Regras</b><br>"
             "• 15 min sem resposta → reativação. Limite por período de silêncio: <b>2</b> em horário comercial, "
             "<b>1</b> fora do horário.<br>"
             "• 23h → última reativação. Os relógios de 23h/24h contam a partir da <b>última mensagem do lead</b>, "
             "não da última mensagem do agente: a janela de 24h da Meta só reinicia quando o usuário escreve. "
             "Uma reativação enviada pelo agente não estende o prazo.<br>"
             "• 24h → perdido, <i>exceto</i> se o lead estiver na fila \"Aguardando humano\" (pedido feito fora do horário).<br>"
             f"<i>{FONTE_META}</i>",
             NOTE, 870, 110, 450, 230)
    p.vertex("<b>⚠ Em aberto</b><br>"
             "1. A reativação única vale para todo o período fora do horário (ex.: sábado às 14h) ou só para a madrugada? "
             "Se for só madrugada, qual faixa (ex.: 22h–7h)?<br>"
             "2. Textos das mensagens de reativação.<br>"
             "3. No Instagram/Facebook a janela padrão também é de 24h: a regra vale igual em todos os canais?",
             OPEN, 870, 360, 450, 110)
    return p


# ================================================================ PÁGINA 5
def pagina_leiame():
    p = Page("p5", "Leia-me · Legenda", 1300, 900)
    p.vertex("<b>Leia-me · Notação usada (BPMN 2.0 simplificado)</b>", "text;html=1;align=left;fontSize=20;",
             40, 20, 900, 34)
    rows = [
        (ev("standard", "message", "right"), "Evento de início (mensagem do lead)", 40, 40),
        (ev("end", "general", "right"), "Evento de fim (passa para outro processo)", 40, 40),
        (ev("end", "terminate", "right"), "Fim em funil do CRM (perdido / desqualificado)", 40, 40),
        (ev("catching", "timer", "right"), "Espera por tempo (timer)", 40, 40),
        (ev("boundInt", "message", "right"), "Evento de borda que interrompe a atividade", 40, 40),
        (ev("boundNonint", "timer", "right"), "Evento de borda que não interrompe (tracejado)", 40, 40),
        (ev("throwing", "link", "right"), "Link de saída / entrada (\"Vai para A\"): evita linhas cruzadas", 40, 40),
        (gw("x", "right"), "Decisão exclusiva (só um caminho)", 50, 50),
        (gw("+", "right"), "Paralelo (os caminhos acontecem ao mesmo tempo)", 50, 50),
        (gw("evt", "right"), "Baseado em evento (segue o que acontecer primeiro)", 50, 50),
    ]
    y = 80
    for st, label, w, h in rows:
        p.vertex(label, st, 60, y, w, h)
        y += h + 18
    p.vertex("Tarefa automática do agente", task("agente", "service"), 560, 80, 180, 60)
    p.vertex("Envio de mensagem / notificação", task("agente", "send"), 560, 160, 180, 60)
    p.vertex("Tarefa humana", task("humano", "user"), 560, 240, 180, 60)
    p.vertex("Subprocesso (clique para abrir a página)", task("agente", call=True), 560, 320, 180, 60)
    p.vertex("Pendência / decisão em aberto", OPEN, 560, 400, 180, 50)
    p.vertex("<b>Raias:</b> Lead · Agente IA Genérico · CRM/Funis · Atendente humano. "
             "Cada raia mostra <i>quem</i> executa o passo.<br><br>"
             "<b>Exportar para Visio:</b> no draw.io, Arquivo → Exportar como → VSDX.<br>"
             "<b>Editar:</b> app.diagrams.net → Abrir de → Dispositivo (ou GitHub).",
             NOTE, 800, 80, 420, 170)
    return p


def main():
    pages = [pagina_mapa(), pagina_horario(), pagina_fora(), pagina_inatividade(), pagina_leiame()]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<mxfile host="app.diagrams.net" agent="gerar_processo.py" version="24.7.17">'
           + "".join(pg.xml() for pg in pages) + "</mxfile>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")
    print(f"ok: {OUT} ({len(xml)} bytes, {len(pages)} páginas)")


if __name__ == "__main__":
    main()
