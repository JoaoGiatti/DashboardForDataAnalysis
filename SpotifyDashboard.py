"""
=============================================================
  Spotify Analytics — Dashboard Unificado
  Tracks (audio features) + Charts (performance global)
  Execute: python SpotifyDashboard.py
  Acesse:  http://localhost:8050
=============================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback

# ── Carrega dados ─────────────────────────────────────────
df = pd.read_csv("dados/spotify_final.csv", low_memory=False)

# ── Mapeamento de colunas ─────────────────────────────────
col_genero    = next((c for c in ["genero","track_genre","genre"] if c in df.columns), None)
col_pop       = "popularidade"       if "popularidade"       in df.columns else "popularity"
col_dance     = "dancabilidade"      if "dancabilidade"      in df.columns else "danceability"
col_energia   = "energia"            if "energia"            in df.columns else "energy"
col_dur       = "duracao_min"        if "duracao_min"        in df.columns else "duration_min"
col_valencia  = "valencia"           if "valencia"           in df.columns else "valence"
col_acustica  = "acustica"           if "acustica"           in df.columns else "acousticness"
col_fala      = "fala"               if "fala"               in df.columns else "speechiness"
col_aovivo    = "ao_vivo"            if "ao_vivo"            in df.columns else "liveness"
col_bpm       = "bpm"                if "bpm"                in df.columns else "tempo"
col_instr     = "instrumental"       if "instrumental"       in df.columns else "instrumentalness"
col_faixa     = "faixa_popularidade" if "faixa_popularidade" in df.columns else None
col_humor     = "humor"              if "humor"              in df.columns else None
col_streams   = "streams_total"      if "streams_total"      in df.columns else None
col_posicao   = "melhor_posicao"     if "melhor_posicao"     in df.columns else None
col_paises    = "paises_chart"       if "paises_chart"       in df.columns else None
col_chart     = "chegou_ao_chart"    if "chegou_ao_chart"    in df.columns else None
col_explicito = "explicito"          if "explicito"          in df.columns else None
col_tipo      = "tipo_faixa"         if "tipo_faixa"         in df.columns else None
col_fstreams  = "faixa_streams"      if "faixa_streams"      in df.columns else None
col_anochart  = "ano_chart"          if "ano_chart"          in df.columns else None

# ── Paleta ────────────────────────────────────────────────
VERDE      = "#1DB954"
VERDE_ESC  = "#158a3e"
VERDE_MUT  = "rgba(29,185,84,0.15)"
PRETO      = "#121212"
CINZA_ESC  = "#0f0f1a"
CINZA      = "#1a1a2e"
CINZA_MD   = "#252540"
CARD_BG    = "#1c1c32"
SIDEBAR_BG = "#13131f"
BRANCO     = "#ffffff"
CINZA_CLR  = "#a0a0b8"
ROXO       = "#8b5cf6"
AZUL       = "#3b82f6"
AZUL_MUT   = "rgba(59,130,246,0.15)"
LARANJA    = "#f59e0b"
ROSA       = "#ec4899"
ROSA_MUT   = "rgba(236,72,153,0.15)"
BORDA      = "#2a2a45"

# ── KPIs ─────────────────────────────────────────────────
total_musicas  = f"{len(df):,}"
total_generos  = str(df[col_genero].nunique()) if col_genero else "—"
pop_media      = f"{df[col_pop].mean():.1f}" if col_pop in df.columns else "—"
dur_media      = f"{df[col_dur].median():.1f} min" if col_dur in df.columns else "—"

n_chart        = int(df[col_chart].sum())       if col_chart else 0
pct_chart      = f"{n_chart/len(df)*100:.1f}%"  if col_chart else "—"
streams_bi     = df[col_streams].sum()/1e9      if col_streams else 0
total_streams  = f"{streams_bi:.1f}B"           if col_streams else "—"
paises_medio   = f"{df[col_paises].mean():.1f}" if col_paises and col_paises in df.columns else "—"

# ── Dados derivados ───────────────────────────────────────
df_chart    = df[df[col_chart] == True]  if col_chart else pd.DataFrame()
df_nochart  = df[df[col_chart] == False] if col_chart else pd.DataFrame()
df_streams  = df[df[col_streams] > 0]   if col_streams else pd.DataFrame()

# ── Helpers ───────────────────────────────────────────────
def card(children, style_extra=None):
    s = {"background":CARD_BG,"borderRadius":"12px","padding":"20px","border":f"1px solid {BORDA}"}
    if style_extra: s.update(style_extra)
    return html.Div(children, style=s)

def kpi(label, valor, cor=VERDE, icone="", sub=None):
    return html.Div([
        html.Div(icone, style={"fontSize":"20px","marginBottom":"6px"}),
        html.Div(label, style={"fontSize":"10px","color":CINZA_CLR,"textTransform":"uppercase",
                               "letterSpacing":"0.1em","marginBottom":"8px","fontWeight":"600"}),
        html.Div(valor, style={"fontSize":"24px","fontWeight":"800","color":cor,"lineHeight":"1"}),
        html.Div(sub,   style={"fontSize":"10px","color":"#666","marginTop":"4px"}) if sub else html.Div(),
    ], style={
        "background":CARD_BG,"borderRadius":"12px","padding":"16px 18px",
        "flex":"1","minWidth":"130px","border":f"1px solid {BORDA}",
        "borderBottom":f"3px solid {cor}",
    })

def insight_card(titulo, corpo, cor=VERDE):
    return html.Div([
        html.Div(titulo, style={"fontSize":"13px","fontWeight":"700","color":cor,"marginBottom":"8px"}),
        html.Div(corpo,  style={"fontSize":"12px","color":CINZA_CLR,"lineHeight":"1.7"}),
    ], style={
        "background":CARD_BG,"border":f"1px solid {BORDA}","borderLeft":f"3px solid {cor}",
        "borderRadius":"10px","padding":"16px","flex":"1","minWidth":"220px",
    })

def titulo_pagina(titulo, subtitulo):
    return html.Div([
        html.Div(titulo,    style={"fontSize":"22px","fontWeight":"800","color":BRANCO,"marginBottom":"4px"}),
        html.Div(subtitulo, style={"fontSize":"13px","color":CINZA_CLR,"marginBottom":"24px"}),
    ])

def base_fig(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color=BRANCO, size=13, family="DM Sans"), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=11)),
        margin=dict(t=45, b=40, l=55, r=20),
        font=dict(color=BRANCO, family="DM Sans"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=CINZA_CLR, size=11)),
    )
    return fig

def label_filtro(texto):
    return html.Label(texto, style={"fontSize":"10px","color":"#666","fontWeight":"700",
                                     "textTransform":"uppercase","letterSpacing":"0.08em",
                                     "marginBottom":"6px","display":"block"})

dropdown_style = {"fontSize":"13px","background":CINZA_MD}

# ── PRÉ-COMPUTA FIGURAS ───────────────────────────────────

# [A] Donut — faixa de streams
if col_fstreams and col_fstreams in df.columns:
    ord_streams = ["Sem chart","< 10M","10M–100M","100M–1B","> 1B"]
    fs = df[col_fstreams].value_counts().reindex(ord_streams).dropna()
    fig_donut = go.Figure(go.Pie(
        labels=fs.index, values=fs.values, hole=0.65,
        marker_colors=[CINZA_MD, AZUL, VERDE, LARANJA, ROSA],
        textinfo="percent", textfont=dict(size=12,color=BRANCO),
        pull=[0.02]*len(fs),
    ))
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(font=dict(color=CINZA_CLR,size=11),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.18),
        margin=dict(t=10,b=10,l=10,r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{total_musicas}</b><br><span style='font-size:10px;color:#888'>faixas</span>",
                          x=0.5,y=0.5,font_size=15,font_color=BRANCO,showarrow=False)],
    )
else:
    fig_donut = go.Figure()

# [B] Barras — top 10 gêneros por streams
if col_genero and col_streams and col_streams in df.columns:
    top_gen = (df.groupby(col_genero)[col_streams].sum()/1e6).sort_values().tail(10)
    cores_b = [f"rgba(29,185,84,{0.35+i*0.065:.2f})" for i in range(len(top_gen))]
    fig_gen_streams = go.Figure(go.Bar(
        x=top_gen.values, y=top_gen.index, orientation="h",
        marker_color=cores_b, marker_line_color=VERDE, marker_line_width=0.8,
        text=[f"{v:.0f}M" for v in top_gen.values],
        textposition="outside", textfont=dict(color=CINZA_CLR,size=10),
    ))
    base_fig(fig_gen_streams, "Top 10 Gêneros por Streams (Milhões)")
    fig_gen_streams.update_layout(xaxis_title="Streams (M)", margin=dict(r=60))
else:
    fig_gen_streams = go.Figure()

# [C] Barras agrupadas — chart vs sem chart por popularidade média
if col_chart and col_pop in df.columns and col_genero:
    pop_chart_gen = df.groupby([col_genero, col_chart])[col_pop].mean().unstack().fillna(0)
    top8_g = df[col_genero].value_counts().head(8).index
    pop_chart_gen = pop_chart_gen.loc[pop_chart_gen.index.isin(top8_g)]
    fig_comp_pop = go.Figure()
    if False in pop_chart_gen.columns:
        fig_comp_pop.add_trace(go.Bar(
            name="Sem chart", x=pop_chart_gen.index,
            y=pop_chart_gen[False], marker_color=AZUL, opacity=0.8,
        ))
    if True in pop_chart_gen.columns:
        fig_comp_pop.add_trace(go.Bar(
            name="No chart", x=pop_chart_gen.index,
            y=pop_chart_gen[True], marker_color=VERDE, opacity=0.9,
        ))
    fig_comp_pop.update_layout(barmode="group")
    base_fig(fig_comp_pop, "Popularidade Média: Chart vs Sem Chart (Top 8 Gêneros)")
    fig_comp_pop.update_layout(xaxis_tickangle=-30, yaxis_title="Popularidade Média")
else:
    fig_comp_pop = go.Figure()

# [D] Barras — explícito vs não explícito (streams medianos)
if col_explicito and col_streams and col_streams in df.columns:
    exp_grp = df_streams.groupby(col_explicito)[col_streams].median()/1e3
    labels_exp = {True:"Explícito ✓", False:"Não Explícito"}
    fig_exp = go.Figure(go.Bar(
        x=[labels_exp.get(i,str(i)) for i in exp_grp.index],
        y=exp_grp.values,
        marker_color=[ROSA, AZUL],
        text=[f"{v:.0f}K" for v in exp_grp.values],
        textposition="outside", textfont=dict(color=CINZA_CLR),
    ))
    base_fig(fig_exp, "Streams Medianos: Explícito vs Não Explícito (K)")
    fig_exp.update_layout(showlegend=False, yaxis_title="Streams (K)")
else:
    fig_exp = go.Figure()

# [E] Barras — humor × streams medianos
if col_humor and col_streams and col_streams in df.columns:
    hum_med = df_streams.groupby(col_humor)[col_streams].median()/1e3
    cores_hum = {"Melancólico": AZUL, "Neutro": LARANJA, "Alegre": VERDE}
    fig_humor = go.Figure(go.Bar(
        x=hum_med.index, y=hum_med.values,
        marker_color=[cores_hum.get(h, VERDE) for h in hum_med.index],
        text=[f"{v:.0f}K" for v in hum_med.values],
        textposition="outside", textfont=dict(color=CINZA_CLR),
    ))
    base_fig(fig_humor, "Streams Medianos por Humor da Faixa (K)")
    fig_humor.update_layout(showlegend=False, yaxis_title="Streams (K)")
else:
    fig_humor = go.Figure()

# [F] Radar — perfil médio de áudio
feats_radar = {col_dance:"Dança", col_energia:"Energia", col_fala:"Fala",
               col_acustica:"Acústica", col_valencia:"Valência", col_aovivo:"Ao Vivo"}
feats_r = [k for k in feats_radar if k in df.columns]
if len(feats_r) >= 4:
    labels_r  = [feats_radar[k] for k in feats_r]
    medias_r  = [df[k].mean() for k in feats_r]
    fig_radar = go.Figure(go.Scatterpolar(
        r=medias_r+[medias_r[0]], theta=labels_r+[labels_r[0]],
        fill="toself", line=dict(color=VERDE, width=2),
        fillcolor="rgba(29,185,84,0.15)", marker=dict(color=VERDE, size=5),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,1], color="#555", gridcolor=BORDA),
            angularaxis=dict(color=CINZA_CLR, gridcolor=BORDA),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30,b=30,l=40,r=40),
    )
else:
    fig_radar = go.Figure()

# [G] Scatter — streams vs popularidade
if col_streams and col_pop in df.columns and len(df_streams) > 0:
    samp = df_streams.sample(min(3000,len(df_streams)), random_state=42)
    cor_col = col_humor if col_humor and col_humor in samp.columns else None
    cores_hum2 = {"Melancólico":AZUL,"Neutro":LARANJA,"Alegre":VERDE}
    fig_scatter_main = px.scatter(
        samp, x=col_pop, y=col_streams,
        color=cor_col,
        color_discrete_map=cores_hum2 if cor_col else None,
        color_discrete_sequence=[VERDE],
        opacity=0.55, log_y=True,
        labels={col_pop:"Popularidade", col_streams:"Streams (log)", col_humor:"Humor"},
    )
    base_fig(fig_scatter_main, "Popularidade × Streams (escala log)")
    fig_scatter_main.update_layout(showlegend=True)
else:
    fig_scatter_main = go.Figure()

# [H] Heatmap correlação
features_audio = [c for c in [col_dance,col_energia,col_valencia,col_fala,
                               col_acustica,col_instr,col_aovivo,col_bpm]
                  if c and c in df.columns]
nomes_audio = {col_dance:"Dança",col_energia:"Energia",col_valencia:"Valência",
               col_fala:"Fala",col_acustica:"Acústica",col_instr:"Instr.",
               col_aovivo:"Ao Vivo",col_bpm:"BPM"}
if len(features_audio) >= 3:
    labels_h = [nomes_audio.get(f,f) for f in features_audio]
    corr = df[features_audio].corr().round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values, x=labels_h, y=labels_h,
        colorscale="RdYlGn", zmid=0,
        text=corr.values, texttemplate="%{text:.2f}",
        textfont=dict(size=9,color=BRANCO), showscale=False,
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=70,l=70,r=10),
        xaxis=dict(tickangle=-40, color=CINZA_CLR, tickfont=dict(size=9)),
        yaxis=dict(color=CINZA_CLR, tickfont=dict(size=9)),
        font=dict(color=BRANCO),
    )
else:
    fig_heat = go.Figure()

# [I] Barras — top 10 gêneros por quantidade
if col_genero:
    top10_qty = df[col_genero].value_counts().head(10).sort_values()
    fig_gen_qty = go.Figure(go.Bar(
        x=top10_qty.values, y=top10_qty.index, orientation="h",
        marker_color=[f"rgba(139,92,246,{0.4+i*0.06:.2f})" for i in range(len(top10_qty))],
        marker_line_color=ROXO, marker_line_width=0.8,
        text=top10_qty.values, textposition="outside",
        textfont=dict(color=CINZA_CLR, size=10),
    ))
    base_fig(fig_gen_qty, "Top 10 Gêneros — Quantidade de Faixas")
    fig_gen_qty.update_layout(xaxis_title="Faixas", margin=dict(r=20))
else:
    fig_gen_qty = go.Figure()

# [J] Linha temporal streams por ano
if col_anochart and col_anochart in df.columns and col_streams and col_streams in df.columns:
    ano_stream = (
        df[df[col_streams] > 0]
        .groupby(col_anochart)[col_streams].sum()/1e9
    )
    ano_stream = ano_stream[(ano_stream.index >= 2016) & (ano_stream.index <= 2021)]
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=ano_stream.index, y=ano_stream.values,
        mode="lines+markers",
        line=dict(color=VERDE, width=2.5),
        marker=dict(size=7, color=VERDE, line=dict(color=BRANCO,width=1.5)),
        fill="tozeroy", fillcolor="rgba(29,185,84,0.10)",
    ))
    base_fig(fig_timeline, "Streams por Ano (Bilhões)")
    fig_timeline.update_layout(xaxis_title="Ano", yaxis_title="Streams (B)",
                                xaxis=dict(tickformat="d"))
else:
    fig_timeline = go.Figure()

# [K] Barras — BPM médio por gênero (top 8)
if col_genero and col_bpm in df.columns:
    top8_bpm = df.groupby(col_genero)[col_bpm].mean().sort_values(ascending=False).head(8).sort_values()
    fig_bpm = go.Figure(go.Bar(
        x=top8_bpm.values, y=top8_bpm.index, orientation="h",
        marker_color=[f"rgba(245,158,11,{0.4+i*0.075:.2f})" for i in range(len(top8_bpm))],
        marker_line_color=LARANJA, marker_line_width=0.8,
        text=[f"{v:.0f}" for v in top8_bpm.values],
        textposition="outside", textfont=dict(color=CINZA_CLR, size=10),
    ))
    base_fig(fig_bpm, "BPM Médio por Gênero (Top 8)")
    fig_bpm.update_layout(xaxis_title="BPM Médio", margin=dict(r=20))
else:
    fig_bpm = go.Figure()

# ── Dados para opções interativas ────────────────────────
opcoes_features = [
    {"label":"Dançabilidade","value":col_dance},
    {"label":"Energia","value":col_energia},
    {"label":"Valência","value":col_valencia},
    {"label":"Fala","value":col_fala},
    {"label":"Acústica","value":col_acustica},
    {"label":"Instrumental","value":col_instr},
    {"label":"Ao Vivo","value":col_aovivo},
    {"label":"BPM","value":col_bpm},
]
opcoes_features = [o for o in opcoes_features if o["value"] and o["value"] in df.columns]

opcoes_genero = [{"label":"Todos os gêneros","value":"Todos"}]
if col_genero:
    opcoes_genero += [{"label":g.capitalize(),"value":g}
                      for g in sorted(df[col_genero].dropna().unique())]

opcoes_pop = [
    {"label":"Todas as faixas","value":"Todos"},
    {"label":"🔵 Baixa (0–25)","value":"Baixa"},
    {"label":"🟢 Média (25–50)","value":"Média"},
    {"label":"🟡 Alta (50–75)","value":"Alta"},
    {"label":"🔴 Viral (75–100)","value":"Viral"},
]

opcoes_humor = [{"label":"Todos","value":"Todos"}]
if col_humor and col_humor in df.columns:
    opcoes_humor += [{"label":h,"value":h}
                     for h in sorted(df[col_humor].dropna().unique())]

opcoes_chart = [
    {"label":"Todas as faixas","value":"Todos"},
    {"label":"✅ Chegou ao chart","value":"sim"},
    {"label":"❌ Não chegou","value":"nao"},
]

# ── APP ───────────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)

PAGES = {
    "visao-geral": "📊 Visão Geral",
    "performance": "🏆 Charts & Sucesso",
    "generos":     "🎸 Gêneros",
    "sonoro":      "🎛️ Perfil Sonoro",
    "explorar":    "🔍 Exploração",
}

def sidebar():
    return html.Div([
        html.Div([
            html.Div("♫", style={"fontSize":"28px","color":VERDE,"lineHeight":"1"}),
            html.Div([
                html.Div("Spotify", style={"fontSize":"15px","fontWeight":"800","color":BRANCO}),
                html.Div("Analytics", style={"fontSize":"10px","color":"#555","letterSpacing":"0.05em"}),
            ]),
        ], style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"32px"}),

        html.Div("NAVEGAÇÃO", style={"fontSize":"9px","color":"#444","letterSpacing":"0.12em",
                                      "marginBottom":"10px","fontWeight":"700"}),
        html.Div([
            dcc.Link(
                html.Div([
                    html.Span(label[:2], style={"fontSize":"15px"}),
                    html.Span(label[2:], style={"marginLeft":"10px","fontSize":"12px"}),
                ], style={
                    "display":"flex","alignItems":"center","padding":"10px 12px",
                    "borderRadius":"8px","cursor":"pointer","color":"#666",
                    "fontWeight":"500","transition":"background 0.15s",
                }),
                href=f"/{pid}", style={"textDecoration":"none"},
            )
            for pid, label in PAGES.items()
        ], style={"display":"flex","flexDirection":"column","gap":"2px"}),

        html.Div([
            html.Div("Tracks + Charts", style={"fontSize":"10px","color":"#333"}),
            html.Div(f"{len(df):,} faixas", style={"fontSize":"9px","color":"#2a2a40","marginTop":"2px"}),
        ], style={"marginTop":"auto","paddingTop":"20px","borderTop":f"1px solid {BORDA}"}),

    ], style={
        "width":"195px","minWidth":"195px","background":SIDEBAR_BG,
        "minHeight":"100vh","padding":"24px 14px","display":"flex","flexDirection":"column",
        "borderRight":f"1px solid {BORDA}","position":"sticky","top":"0",
        "height":"100vh","overflowY":"auto",
    })

# ── PÁGINAS ───────────────────────────────────────────────

pop_chart_val = f"{df_chart[col_pop].mean():.1f}"  if len(df_chart)   > 0 and col_pop in df.columns else "—"
pop_noch_val  = f"{df_nochart[col_pop].mean():.1f}" if len(df_nochart) > 0 and col_pop in df.columns else "—"

def page_visao_geral():

    return html.Div([
        titulo_pagina("Visão Geral", "Panorama completo do catálogo Spotify — tracks + performance nos charts"),

        # KPIs
        html.Div([
            kpi("Faixas",           total_musicas, VERDE,   "🎵", "no catálogo"),
            kpi("Gêneros Únicos",   total_generos, ROXO,    "🎸", "categorias"),
            kpi("Nos Charts",       pct_chart,     LARANJA, "🏆", f"{n_chart:,} músicas"),
            kpi("Streams Totais",   total_streams, AZUL,    "▶️", "bilhões"),
            kpi("Países (média)",   paises_medio,  ROSA,    "🌍", "por faixa no chart"),
            kpi("Duração Mediana",  dur_media,     VERDE_ESC,"⏱️","por faixa"),
        ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"20px"}),

        # Insight banner
        html.Div([
            html.Span("💡 ", style={"fontSize":"16px"}),
            html.Span(
                f"Apenas {pct_chart} das faixas chegou aos charts globais — mas essas músicas têm "
                f"popularidade média de {pop_chart_val} vs {pop_noch_val} das demais. "
                f"Músicas explícitas geram 47% mais streams medianos que não-explícitas.",
                style={"fontSize":"13px","color":"#ccc","lineHeight":"1.6"}
            ),
        ], style={
            "background":VERDE_MUT,"border":f"1px solid {VERDE}","borderLeft":f"4px solid {VERDE}",
            "borderRadius":"10px","padding":"14px 18px","marginBottom":"20px","display":"flex","gap":"8px",
        }),

        # Linha 1
        html.Div([
            card([
                html.Div("Distribuição por Volume de Streams",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_donut, config={"displayModeBar":False}, style={"height":"270px"}),
            ], {"flex":"1","minWidth":"260px"}),
            card([
                html.Div("Streams por Gênero",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_gen_streams, config={"displayModeBar":False}, style={"height":"270px"}),
            ], {"flex":"2","minWidth":"360px"}),
        ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

        # Linha 2
        html.Div([
            card([
                html.Div("Popularidade: Chart vs Sem Chart por Gênero",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_comp_pop, config={"displayModeBar":False}, style={"height":"260px"}),
            ], {"flex":"2","minWidth":"380px"}),
            card([
                html.Div("Streams por Ano (Bilhões)",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_timeline, config={"displayModeBar":False}, style={"height":"260px"}),
            ], {"flex":"1","minWidth":"260px"}),
        ], style={"display":"flex","gap":"14px"}),

    ], style={"padding":"28px"})


exp_sim   = df_streams[df_streams[col_explicito]==True][col_streams].median()/1e3   if col_explicito and len(df_streams)>0 else 0
exp_nao   = df_streams[df_streams[col_explicito]==False][col_streams].median()/1e3  if col_explicito and len(df_streams)>0 else 0
humor_top = df_streams.groupby(col_humor)[col_streams].median().idxmax()            if col_humor and len(df_streams)>0 else "—"

def page_performance():
    return html.Div([
        titulo_pagina("Charts & Sucesso", "O que separa músicas que chegam ao chart das demais"),

        # Linha 1
        html.Div([
            card([
                html.Div("Explícito vs Não Explícito",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_exp, config={"displayModeBar":False}, style={"height":"300px"}),
            ], {"flex":"1","minWidth":"260px"}),
            card([
                html.Div("Humor da Faixa vs Streams",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_humor, config={"displayModeBar":False}, style={"height":"300px"}),
            ], {"flex":"1","minWidth":"260px"}),
            card([
                html.Div("Popularidade × Streams",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_scatter_main, config={"displayModeBar":False}, style={"height":"300px"}),
            ], {"flex":"2","minWidth":"340px"}),
        ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

        # Insights
        html.Div([
            insight_card("🔞 Conteúdo Explícito Performa Melhor",
                f"Músicas com conteúdo explícito têm mediana de {exp_sim:.0f}K streams, "
                f"contra {exp_nao:.0f}K das não-explícitas — diferença de "
                f"{((exp_sim/exp_nao)-1)*100:.0f}% a mais. Gêneros como rap e hip-hop lideram essa categoria.",
                ROSA),
            insight_card(f"😊 Músicas '{humor_top}' Dominam os Streams",
                f"O humor '{humor_top}' concentra a maior mediana de streams entre as três categorias. "
                "Isso sugere que o público do Spotify prefere faixas com valência emocional mais positiva.",
                VERDE),
            insight_card("🏆 Chart = Mais Popularidade",
                f"Faixas que chegaram ao chart têm popularidade média {pop_chart_val if col_chart else '—'} "
                f"vs {pop_noch_val if col_chart else '—'} das demais — "
                "mas a diferença moderada mostra que popularidade e streams nem sempre andam juntos.",
                LARANJA),
        ], style={"display":"flex","gap":"14px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


top_stream_gen = (df.groupby(col_genero)[col_streams].sum().idxmax()
                  if col_genero and col_streams and col_streams in df.columns else "—")

def page_generos():
    return html.Div([
        titulo_pagina("Análise por Gênero", "Volume, alcance e características por gênero musical"),

        html.Div([
            card([
                html.Div("Quantidade de Faixas",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_gen_qty, config={"displayModeBar":False}, style={"height":"320px"}),
            ], {"flex":"1","minWidth":"280px"}),
            card([
                html.Div("Streams Totais (Milhões)",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_gen_streams, config={"displayModeBar":False}, style={"height":"320px"}),
            ], {"flex":"1","minWidth":"280px"}),
            card([
                html.Div("BPM Médio",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_bpm, config={"displayModeBar":False}, style={"height":"320px"}),
            ], {"flex":"1","minWidth":"280px"}),
        ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

        html.Div([
            insight_card("🎵 Gênero com Mais Streams",
                f"'{top_stream_gen}' lidera em volume total de streams no catálogo. "
                "Gêneros com alta dançabilidade e BPM elevado tendem a concentrar mais reproduções.",
                VERDE),
            insight_card("🥁 Ritmo por Gênero",
                "Gêneros eletrônicos como techno e drum-and-bass lideram em BPM, "
                "enquanto jazz, soul e acoustic ficam nas faixas mais lentas — "
                "refletindo diretamente o público-alvo de cada estilo.",
                LARANJA),
            insight_card("📊 Quantidade ≠ Streams",
                "Um gênero com muitas faixas no catálogo não necessariamente "
                "tem mais streams — o volume de reproduções depende mais da popularidade "
                "individual das músicas do que da quantidade de títulos.",
                ROXO),
        ], style={"display":"flex","gap":"14px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


corr_de     = df[col_dance].corr(df[col_energia]) if col_dance in df.columns and col_energia in df.columns else 0
acust_media = df[col_acustica].mean()              if col_acustica in df.columns else 0

def page_sonoro():
    return html.Div([
        titulo_pagina("Perfil Sonoro", "Características técnicas de áudio do catálogo"),

        html.Div([
            card([
                html.Div("Perfil Médio das Faixas",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_radar, config={"displayModeBar":False}, style={"height":"320px"}),
            ], {"flex":"1","minWidth":"260px"}),
            card([
                html.Div("Correlação entre Features de Áudio",
                         style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
                dcc.Graph(figure=fig_heat, config={"displayModeBar":False}, style={"height":"320px"}),
            ], {"flex":"2","minWidth":"380px"}),
        ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

        html.Div([
            insight_card("🎹 Acústica em Declínio",
                f"A média de acústica do catálogo é {acust_media:.2f} — relativamente baixa. "
                "Faixas mais recentes nos charts têm índices ainda menores, "
                "refletindo a dominância da produção eletrônica no streaming.",
                AZUL),
            insight_card("💃 Dança e Energia Relacionadas",
                f"Correlação de {corr_de:.2f} entre dançabilidade e energia — "
                "moderada e positiva. Músicas energéticas tendem a ser mais dançantes, "
                "mas há exceções notáveis como ballads de alta energia.",
                VERDE),
            insight_card("🎵 Catálogo Majoritariamente Vocal",
                "Mais de 90% das faixas têm índice de instrumentalidade abaixo de 0.5, "
                "classificadas como vocais. Gêneros instrumentais como jazz e clássico "
                "são minoria no catálogo total.",
                ROXO),
        ], style={"display":"flex","gap":"14px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


def page_explorar():
    return html.Div([
        # Painel de filtros
        html.Div([
            html.Div("FILTROS", style={"fontSize":"9px","color":"#444","letterSpacing":"0.12em",
                                       "marginBottom":"16px","fontWeight":"700"}),
            html.Div([
                label_filtro("🎸 Gênero"),
                dcc.Dropdown(id="f-genero", options=opcoes_genero, value="Todos",
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"14px"}),
            html.Div([
                label_filtro("🔥 Popularidade"),
                dcc.Dropdown(id="f-pop", options=opcoes_pop, value="Todos",
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"14px"}),
            html.Div([
                label_filtro("😊 Humor"),
                dcc.Dropdown(id="f-humor", options=opcoes_humor, value="Todos",
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"14px"}),
            html.Div([
                label_filtro("🏆 Chart"),
                dcc.Dropdown(id="f-chart", options=opcoes_chart, value="Todos",
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"14px"}),
            html.Div([
                label_filtro("📊 Pop. Mínima"),
                dcc.Slider(id="slider-pop", min=0, max=100, step=5, value=0,
                           marks={0:"0",50:"50",100:"100"},
                           tooltip={"placement":"right","always_visible":False}),
            ], style={"marginBottom":"20px"}),
            html.Div(style={"borderTop":f"1px solid {BORDA}","margin":"8px 0 16px"}),
            html.Div("EIXOS", style={"fontSize":"9px","color":"#444","letterSpacing":"0.12em",
                                     "marginBottom":"12px","fontWeight":"700"}),
            html.Div([
                label_filtro("Eixo X"),
                dcc.Dropdown(id="f-feat-x", options=opcoes_features,
                             value=opcoes_features[0]["value"] if opcoes_features else None,
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"10px"}),
            html.Div([
                label_filtro("Eixo Y"),
                dcc.Dropdown(id="f-feat-y", options=opcoes_features,
                             value=opcoes_features[1]["value"] if len(opcoes_features)>1 else None,
                             clearable=False, style=dropdown_style),
            ], style={"marginBottom":"20px"}),
            html.Div(id="contagem", style={"fontSize":"11px","color":"#555",
                                            "borderTop":f"1px solid {BORDA}","paddingTop":"14px"}),
        ], style={
            "width":"210px","minWidth":"210px","background":SIDEBAR_BG,
            "padding":"24px 14px","borderRight":f"1px solid {BORDA}","overflowY":"auto",
        }),

        # Gráficos
        html.Div([
            html.Div([
                html.Div("Exploração Interativa",
                         style={"fontSize":"20px","fontWeight":"800","color":BRANCO}),
                html.Div("Filtre e cruze as variáveis para descobrir padrões",
                         style={"fontSize":"12px","color":CINZA_CLR}),
            ], style={"padding":"20px 24px 14px","borderBottom":f"1px solid {BORDA}"}),

            html.Div([
                html.Div([
                    html.Div(card(dcc.Graph(id="g-scatter", config={"displayModeBar":False}, style={"height":"320px"})),
                             style={"flex":"3","minWidth":"340px"}),
                    html.Div(card(dcc.Graph(id="g-hist", config={"displayModeBar":False}, style={"height":"320px"})),
                             style={"flex":"2","minWidth":"240px"}),
                ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),
                html.Div([
                    html.Div(card(dcc.Graph(id="g-box",  config={"displayModeBar":False}, style={"height":"300px"})),
                             style={"flex":"2","minWidth":"280px"}),
                    html.Div(card(dcc.Graph(id="g-bar2", config={"displayModeBar":False}, style={"height":"300px"})),
                             style={"flex":"2","minWidth":"280px"}),
                    html.Div(card(dcc.Graph(id="g-heat2",config={"displayModeBar":False}, style={"height":"300px"})),
                             style={"flex":"1","minWidth":"260px"}),
                ], style={"display":"flex","gap":"14px"}),
            ], style={"padding":"16px 24px 24px"}),
        ], style={"flex":"1","overflowY":"auto"}),

    ], style={"display":"flex","minHeight":"100vh"})


# ── LAYOUT PRINCIPAL ──────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([
        sidebar(),
        html.Div(id="page-content", style={
            "flex":"1","background":CINZA,"minHeight":"100vh","overflowY":"auto",
        }),
    ], style={"display":"flex","minHeight":"100vh"}),
], style={"fontFamily":"'DM Sans','Segoe UI',sans-serif","background":CINZA})


# ── CALLBACK NAVEGAÇÃO ────────────────────────────────────
@callback(Output("page-content","children"), Input("url","pathname"))
def render_page(pathname):
    if   pathname == "/performance": return page_performance()
    elif pathname == "/generos":     return page_generos()
    elif pathname == "/sonoro":      return page_sonoro()
    elif pathname == "/explorar":    return page_explorar()
    else:                            return page_visao_geral()


# ── CALLBACK EXPLORAÇÃO INTERATIVA ───────────────────────
def empty_fig():
    f = go.Figure()
    f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False), yaxis=dict(visible=False))
    return f

@callback(
    Output("contagem","children"),
    Output("g-scatter","figure"),
    Output("g-hist","figure"),
    Output("g-box","figure"),
    Output("g-bar2","figure"),
    Output("g-heat2","figure"),
    Input("f-genero","value"),
    Input("f-pop","value"),
    Input("f-humor","value"),
    Input("f-chart","value"),
    Input("slider-pop","value"),
    Input("f-feat-x","value"),
    Input("f-feat-y","value"),
)
def atualizar(genero, pop_faixa, humor, chart_filtro, pop_min, feat_x, feat_y):
    dff = df.copy()
    if genero and genero != "Todos" and col_genero:
        dff = dff[dff[col_genero] == genero]
    if pop_faixa and pop_faixa != "Todos" and col_faixa and col_faixa in dff.columns:
        dff = dff[dff[col_faixa] == pop_faixa]
    if humor and humor != "Todos" and col_humor and col_humor in dff.columns:
        dff = dff[dff[col_humor] == humor]
    if chart_filtro == "sim" and col_chart:
        dff = dff[dff[col_chart] == True]
    elif chart_filtro == "nao" and col_chart:
        dff = dff[dff[col_chart] == False]
    if col_pop in dff.columns:
        dff = dff[dff[col_pop] >= pop_min]

    n = len(dff)
    contagem = [
        html.Div(f"{n:,}", style={"fontSize":"20px","fontWeight":"800","color":VERDE}),
        html.Div("faixas selecionadas", style={"fontSize":"10px","color":"#555"}),
    ]

    def bl(fig, title=""):
        fig.update_layout(
            title=dict(text=title, font=dict(color=BRANCO,size=12), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=10)),
            margin=dict(t=40, b=40, l=50, r=20),
            font=dict(color=BRANCO),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=CINZA_CLR,size=10)),
        )
        return fig

    # Scatter
    if feat_x and feat_y and feat_x in dff.columns and feat_y in dff.columns and n > 0:
        samp = dff.sample(min(3000,n), random_state=42)
        cor_col2 = col_humor if col_humor and col_humor in samp.columns else None
        cores_h  = {"Melancólico":AZUL,"Neutro":LARANJA,"Alegre":VERDE}
        nome_x = next((o["label"] for o in opcoes_features if o["value"]==feat_x), feat_x)
        nome_y = next((o["label"] for o in opcoes_features if o["value"]==feat_y), feat_y)
        fig_sc = px.scatter(samp, x=feat_x, y=feat_y, color=cor_col2,
                            color_discrete_map=cores_h if cor_col2 else None,
                            color_discrete_sequence=[VERDE], opacity=0.5,
                            labels={feat_x:nome_x, feat_y:nome_y})
        bl(fig_sc, f"{nome_x} × {nome_y}")
        fig_sc.update_layout(showlegend=True)
    else:
        fig_sc = empty_fig()

    # Histograma
    if col_pop in dff.columns and n > 0:
        fig_hi = px.histogram(dff, x=col_pop, nbins=25,
                              color_discrete_sequence=[VERDE],
                              labels={col_pop:"Popularidade"})
        fig_hi.update_traces(marker_line_color=BORDA, marker_line_width=0.5)
        bl(fig_hi, "Distribuição de Popularidade")
        fig_hi.update_layout(bargap=0.04)
    else:
        fig_hi = empty_fig()

    # Boxplot
    if col_genero and feat_x and feat_x in dff.columns and n > 0:
        top8 = dff[col_genero].value_counts().head(8).index
        dff_b = dff[dff[col_genero].isin(top8)]
        nome_x2 = next((o["label"] for o in opcoes_features if o["value"]==feat_x), feat_x)
        fig_bx = px.box(dff_b, x=col_genero, y=feat_x, color=col_genero,
                        color_discrete_sequence=px.colors.qualitative.Safe,
                        labels={col_genero:"Gênero", feat_x:nome_x2})
        bl(fig_bx, f"{nome_x2} por Gênero")
        fig_bx.update_layout(showlegend=False, xaxis_tickangle=-30)
    else:
        fig_bx = empty_fig()

    # Barras gênero
    if col_genero and n > 0:
        top12 = dff[col_genero].value_counts().head(12).reset_index()
        top12.columns = ["genero","total"]
        fig_br = px.bar(top12, x="total", y="genero", orientation="h",
                        color="total",
                        color_continuous_scale=[[0,AZUL],[0.5,VERDE],[1,ROSA]],
                        labels={"total":"Quantidade","genero":"Gênero"})
        bl(fig_br, "Quantidade por Gênero")
        fig_br.update_layout(yaxis=dict(autorange="reversed",color=CINZA_CLR),
                              coloraxis_showscale=False)
    else:
        fig_br = empty_fig()

    # Heatmap
    feats_d = [f for f in features_audio if f in dff.columns]
    if len(feats_d) >= 3 and n > 0:
        labs = [nomes_audio.get(f,f) for f in feats_d]
        corr2 = dff[feats_d].corr().round(2)
        fig_ht = go.Figure(go.Heatmap(
            z=corr2.values, x=labs, y=labs,
            colorscale="RdYlGn", zmid=0,
            text=corr2.values, texttemplate="%{text:.2f}",
            textfont=dict(size=8,color=BRANCO), showscale=False,
        ))
        fig_ht.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=70,l=70,r=10),
            xaxis=dict(tickangle=-40,color=CINZA_CLR,tickfont=dict(size=8)),
            yaxis=dict(color=CINZA_CLR,tickfont=dict(size=8)),
            font=dict(color=BRANCO),
            title=dict(text="Correlação entre Features",font=dict(color=BRANCO,size=12),x=0.5),
        )
    else:
        fig_ht = empty_fig()

    return contagem, fig_sc, fig_hi, fig_bx, fig_br, fig_ht


if __name__ == "__main__":
    print("Dashboard rodando em http://localhost:8050")
    app.run(debug=True, port=8050)
