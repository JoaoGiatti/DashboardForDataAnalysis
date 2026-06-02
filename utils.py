import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc

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
df_chart   = df[df[col_chart] == True]  if col_chart else pd.DataFrame()
df_nochart = df[df[col_chart] == False] if col_chart else pd.DataFrame()
df_streams = df[df[col_streams] > 0]   if col_streams else pd.DataFrame()

pop_chart_val = f"{df_chart[col_pop].mean():.1f}"   if len(df_chart)   > 0 and col_pop in df.columns else "—"
pop_noch_val  = f"{df_nochart[col_pop].mean():.1f}" if len(df_nochart) > 0 and col_pop in df.columns else "—"

exp_sim   = df_streams[df_streams[col_explicito]==True][col_streams].median()/1e3   if col_explicito and len(df_streams)>0 else 0
exp_nao   = df_streams[df_streams[col_explicito]==False][col_streams].median()/1e3  if col_explicito and len(df_streams)>0 else 0
humor_top = df_streams.groupby(col_humor)[col_streams].median().idxmax()            if col_humor and len(df_streams)>0 else "—"

top_stream_gen = (df.groupby(col_genero)[col_streams].sum().idxmax()
                  if col_genero and col_streams and col_streams in df.columns else "—")

corr_de     = df[col_dance].corr(df[col_energia]) if col_dance in df.columns and col_energia in df.columns else 0
acust_media = df[col_acustica].mean()              if col_acustica in df.columns else 0

# ── Features de áudio ─────────────────────────────────────
features_audio = [c for c in [col_dance, col_energia, col_valencia, col_fala,
                               col_acustica, col_instr, col_aovivo, col_bpm]
                  if c and c in df.columns]

nomes_audio = {
    col_dance:   "Dança",
    col_energia: "Energia",
    col_valencia:"Valência",
    col_fala:    "Fala",
    col_acustica:"Acústica",
    col_instr:   "Instr.",
    col_aovivo:  "Ao Vivo",
    col_bpm:     "BPM",
}

# ── Opções para dropdowns ─────────────────────────────────
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
    opcoes_humor += [{"label":h,"value":h} for h in sorted(df[col_humor].dropna().unique())]

opcoes_chart = [
    {"label":"Todas as faixas","value":"Todos"},
    {"label":"✅ Chegou ao chart","value":"sim"},
    {"label":"❌ Não chegou","value":"nao"},
]

# ── Helpers de layout ─────────────────────────────────────
dropdown_style = {"fontSize":"13px","background":CINZA_MD}

def card(children, style_extra=None):
    s = {"background":CARD_BG,"borderRadius":"12px","padding":"20px","border":f"1px solid {BORDA}"}
    if style_extra:
        s.update(style_extra)
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

def label_filtro(texto):
    return html.Label(texto, style={"fontSize":"10px","color":"#666","fontWeight":"700",
                                     "textTransform":"uppercase","letterSpacing":"0.08em",
                                     "marginBottom":"6px","display":"block"})

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

def empty_fig():
    f = go.Figure()
    f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False), yaxis=dict(visible=False))
    return f

# ── PRÉ-COMPUTA FIGURAS ───────────────────────────────────

# [A] Donut — faixa de streams
if col_fstreams and col_fstreams in df.columns:
    ord_streams = ["Sem chart","< 10M","10M–100M","100M–1B","> 1B"]
    fs = df[col_fstreams].value_counts().reindex(ord_streams).dropna()
    fig_donut = go.Figure(go.Pie(
        labels=fs.index, values=fs.values, hole=0.65,
        marker_colors=[CINZA_MD, AZUL, VERDE, LARANJA, ROSA],
        textinfo="percent", textfont=dict(size=12, color=BRANCO),
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
        textposition="outside", textfont=dict(color=CINZA_CLR, size=10),
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
    exp_grp      = df_streams.groupby(col_explicito)[col_streams].median()/1e3
    exp_contagem = df.groupby(col_explicito)[col_streams].count()
    labels_exp   = {True:"Explícito ✓", False:"Não Explícito"}
    rotulos_exp  = {True:"explícitas", False:"não explícitas"}
    fig_exp = go.Figure(go.Bar(
        x=[labels_exp.get(i,str(i)) for i in exp_grp.index],
        y=exp_grp.values,
        marker_color=[ROSA, AZUL],
        text=[f"{v:.0f}K" for v in exp_grp.values],
        textposition="outside", textfont=dict(color=CINZA_CLR),
        customdata=[[exp_contagem[i], rotulos_exp[i]] for i in exp_grp.index],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Streams medianos: %{y:.0f}K<br>"
            "%{customdata[0]:,} músicas são %{customdata[1]}"
            "<extra></extra>"
        ),
    ))
    base_fig(fig_exp, "Streams Medianos: Explícito vs Não Explícito (K)")
    fig_exp.update_layout(showlegend=False, yaxis_title="Streams (K)")
else:
    fig_exp = go.Figure()

# [E] Barras — humor × streams medianos
if col_humor and col_streams and col_streams in df.columns:
    hum_med      = df_streams.groupby(col_humor)[col_streams].median()/1e3
    hum_contagem = df.groupby(col_humor)[col_streams].count()
    cores_hum    = {"Melancólico": AZUL, "Neutro": LARANJA, "Alegre": VERDE}
    fig_humor = go.Figure(go.Bar(
        x=hum_med.index, y=hum_med.values,
        marker_color=[cores_hum.get(h, VERDE) for h in hum_med.index],
        text=[f"{v:.0f}K" for v in hum_med.values],
        textposition="outside", textfont=dict(color=CINZA_CLR),
        customdata=[[hum_contagem[h]] for h in hum_med.index],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Streams medianos: %{y:.0f}K<br>"
            "%{customdata[0]:,} músicas classificadas como %{x}"
            "<extra></extra>"
        ),
    ))
    base_fig(fig_humor, "Streams Medianos por Humor da Faixa (K)")
    fig_humor.update_layout(showlegend=False, yaxis_title="Streams (K)")
else:
    fig_humor = go.Figure()

# [F] Barras agrupadas — perfil de áudio hits vs não-hits
feats_comparar = {
    col_dance:   "Dançabilidade",
    col_energia: "Energia",
    col_acustica:"Acústica",
    col_valencia:"Valência",
    col_fala:    "Fala",
    col_aovivo:  "Ao Vivo",
}
feats_c = [k for k in feats_comparar if k and k in df.columns and col_chart in df.columns]
if len(feats_c) >= 3:
    medias_hit   = [df[df[col_chart]==True][f].mean()  for f in feats_c]
    medias_nohit = [df[df[col_chart]==False][f].mean() for f in feats_c]
    labels_c     = [feats_comparar[f] for f in feats_c]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Bar(
        name="No chart (hit)", x=labels_c, y=medias_hit,
        marker_color=VERDE, opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Hits: %{y:.3f}<extra></extra>",
    ))
    fig_radar.add_trace(go.Bar(
        name="Sem chart", x=labels_c, y=medias_nohit,
        marker_color=AZUL, opacity=0.75,
        hovertemplate="<b>%{x}</b><br>Sem chart: %{y:.3f}<extra></extra>",
    ))
    fig_radar.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color=CINZA_CLR, tickfont=dict(size=11), gridcolor=BORDA),
        yaxis=dict(color=CINZA_CLR, gridcolor=BORDA, range=[0,1], title="Valor médio (0–1)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=CINZA_CLR, size=11)),
        margin=dict(t=10, b=40, l=55, r=20),
        font=dict(color=BRANCO),
    )
else:
    fig_radar = go.Figure()

# [G] Scatter — streams vs popularidade
if col_streams and col_pop in df.columns and len(df_streams) > 0:
    samp = df_streams.sample(min(3000, len(df_streams)), random_state=42)
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
feats_heat = [c for c in [col_dance,col_energia,col_valencia,col_acustica,col_fala]
              if c and c in df.columns]
if len(feats_heat) >= 3:
    labels_h = [nomes_audio.get(f,f) for f in feats_heat]
    corr = df[feats_heat].corr().round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values, x=labels_h, y=labels_h,
        colorscale="RdYlGn", zmid=0,
        text=corr.values, texttemplate="%{text:.2f}",
        textfont=dict(size=12, color=BRANCO), showscale=True,
        colorbar=dict(thickness=12, tickfont=dict(color=CINZA_CLR, size=10)),
        hovertemplate="<b>%{x} × %{y}</b><br>Correlação: %{z:.2f}<extra></extra>",
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=60, l=80, r=20),
        xaxis=dict(tickangle=0, color=CINZA_CLR, tickfont=dict(size=12)),
        yaxis=dict(color=CINZA_CLR, tickfont=dict(size=12)),
        font=dict(color=BRANCO),
    )
else:
    fig_heat = go.Figure()

# [H2] Boxplot — dançabilidade por humor
if col_humor and col_dance and col_dance in df.columns:
    fig_box_humor = px.box(
        df, x=col_humor, y=col_dance, color=col_humor,
        color_discrete_map={"Melancólico":AZUL,"Neutro":LARANJA,"Alegre":VERDE},
        labels={col_humor:"Humor", col_dance:"Dançabilidade"},
        category_orders={col_humor:["Melancólico","Neutro","Alegre"]},
    )
    fig_box_humor.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color=CINZA_CLR, tickfont=dict(size=12), gridcolor=BORDA),
        yaxis=dict(color=CINZA_CLR, gridcolor=BORDA, title="Dançabilidade (0–1)"),
        margin=dict(t=10, b=40, l=55, r=20),
        font=dict(color=BRANCO),
        showlegend=False,
    )
    fig_box_humor.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Mediana: %{median:.2f}<br>"
            "50% das músicas: entre %{q1:.2f} e %{q3:.2f}<br>"
            "Mínimo: %{lowerfence:.2f} | Máximo: %{upperfence:.2f}"
            "<extra></extra>"
        )
    )
else:
    fig_box_humor = go.Figure()

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
        marker=dict(size=7, color=VERDE, line=dict(color=BRANCO, width=1.5)),
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
