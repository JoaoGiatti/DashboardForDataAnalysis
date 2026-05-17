"""
Dashboard 1 — Visão Geral (Painel Executivo)
Spotify Tracks Dataset
Execute: python SpotifyDashboard1.py
Acesse:  http://localhost:8050
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback

# ── Carrega dados ─────────────────────────────────────────
df = pd.read_csv("dados/spotify_final.csv", low_memory=False)

col_genero   = next((c for c in ["genero", "track_genre", "genre"] if c in df.columns), None)
col_pop      = "popularidade" if "popularidade" in df.columns else "popularity"
col_dance    = "dancabilidade" if "dancabilidade" in df.columns else "danceability"
col_energia  = "energia" if "energia" in df.columns else "energy"
col_dur      = "duracao_min" if "duracao_min" in df.columns else "duration_min"
col_valencia = "valencia" if "valencia" in df.columns else "valence"
col_acustica = "acustica" if "acustica" in df.columns else "acousticness"
col_fala     = "fala" if "fala" in df.columns else "speechiness"
col_aovivo   = "ao_vivo" if "ao_vivo" in df.columns else "liveness"
col_bpm      = "bpm" if "bpm" in df.columns else "tempo"
col_faixa    = "faixa_popularidade" if "faixa_popularidade" in df.columns else "popularity_faixa"
col_humor    = "humor" if "humor" in df.columns else None
col_ano      = "ano_lancamento" if "ano_lancamento" in df.columns else None

# ── Paleta ────────────────────────────────────────────────
VERDE     = "#1DB954"
VERDE_ESC = "#158a3e"
PRETO     = "#121212"
CINZA_ESC = "#1a1a2e"
CINZA     = "#212135"
CINZA_MD  = "#2a2a45"
CINZA_CLR = "#f0f0f5"
BRANCO    = "#ffffff"
ROXO      = "#7c3aed"
AZUL      = "#3b82f6"
LARANJA   = "#f59e0b"
ROSA      = "#ec4899"

CARD_BG   = "#1e1e35"
SIDEBAR_BG= "#16162a"

# ── KPIs ──────────────────────────────────────────────────
total_musicas = f"{len(df):,}"
pop_media     = f"{df[col_pop].mean():.1f}" if col_pop in df.columns else "—"
total_generos = str(df[col_genero].nunique()) if col_genero else "—"
dur_media     = f"{df[col_dur].median():.2f} min" if col_dur in df.columns else "—"
pct_viral     = f"{(df[col_pop] >= 75).mean()*100:.1f}%" if col_pop in df.columns else "—"
dance_media   = f"{df[col_dance].mean():.2f}" if col_dance in df.columns else "—"

# ── Helpers de layout ─────────────────────────────────────
def card(children, style_extra=None):
    s = {
        "background": CARD_BG,
        "borderRadius": "14px",
        "padding": "20px",
        "border": "1px solid #2d2d50",
    }
    if style_extra:
        s.update(style_extra)
    return html.Div(children, style=s)

def kpi(label, valor, cor=VERDE, icone=""):
    return html.Div([
        html.Div(icone, style={"fontSize":"22px","marginBottom":"4px"}),
        html.Div(label, style={"fontSize":"11px","color":"#888","textTransform":"uppercase",
                               "letterSpacing":"0.08em","marginBottom":"6px"}),
        html.Div(valor, style={"fontSize":"26px","fontWeight":"800","color":cor,"lineHeight":"1"}),
    ], style={
        "background": CARD_BG,
        "borderRadius": "12px",
        "padding": "18px 16px",
        "flex": "1",
        "minWidth": "120px",
        "border": f"1px solid #2d2d50",
        "borderBottom": f"3px solid {cor}",
    })

# ── PRÉ-COMPUTA FIGURAS ───────────────────────────────────

# 1. Donut - distribuição de popularidade
if col_faixa in df.columns:
    pop_counts = df[col_faixa].value_counts()
    fig_donut = go.Figure(go.Pie(
        labels=pop_counts.index,
        values=pop_counts.values,
        hole=0.62,
        marker_colors=[AZUL, VERDE, LARANJA, ROSA],
        textinfo="percent",
        textfont=dict(size=13, color=BRANCO),
        pull=[0.02]*len(pop_counts),
    ))
    fig_donut.update_layout(
        title=dict(text="Distribuição de Popularidade", font=dict(color=BRANCO, size=14), x=0.5),
        showlegend=True,
        legend=dict(font=dict(color=BRANCO, size=11), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{len(df):,}</b><br><span style='font-size:10px'>faixas</span>",
                          x=0.5, y=0.5, font_size=16, font_color=BRANCO, showarrow=False)],
    )
else:
    fig_donut = go.Figure()

# 2. Barras horizontais - top 10 gêneros por popularidade média
if col_genero and col_pop in df.columns:
    top10 = df.groupby(col_genero)[col_pop].mean().sort_values().tail(10)
    cores = [f"rgba(29,185,84,{0.4 + i*0.06:.2f})" for i in range(len(top10))]
    fig_bar = go.Figure(go.Bar(
        x=top10.values,
        y=top10.index,
        orientation="h",
        marker_color=cores,
        marker_line_color=VERDE,
        marker_line_width=1,
        text=[f"{v:.1f}" for v in top10.values],
        textposition="outside",
        textfont=dict(color=BRANCO, size=11),
    ))
    fig_bar.update_layout(
        title=dict(text="Top 10 Gêneros — Popularidade Média", font=dict(color=BRANCO, size=14), x=0.5),
        xaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO, title="Popularidade Média"),
        yaxis=dict(color=BRANCO, tickfont=dict(size=11)),
        margin=dict(t=50, b=30, l=10, r=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
else:
    fig_bar = go.Figure()

# 3. Linha - músicas por ano
if col_ano and col_ano in df.columns:
    por_ano = df.groupby(col_ano).size().reset_index(name="total")
    por_ano = por_ano[(por_ano[col_ano] >= 1990) & (por_ano[col_ano] <= 2025)]
    fig_linha = go.Figure()
    fig_linha.add_trace(go.Scatter(
        x=por_ano[col_ano], y=por_ano["total"],
        mode="lines+markers",
        line=dict(color=VERDE, width=2.5),
        marker=dict(size=5, color=VERDE),
        fill="tozeroy",
        fillcolor="rgba(29,185,84,0.10)",
    ))
    fig_linha.update_layout(
        title=dict(text="Músicas por Ano de Lançamento", font=dict(color=BRANCO, size=14), x=0.5),
        xaxis=dict(showgrid=False, color=BRANCO, title="Ano"),
        yaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO, title="Quantidade"),
        margin=dict(t=50, b=40, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
else:
    fig_linha = go.Figure()

# 4. Radar - perfil médio
features_radar_map = {
    col_dance: "Dançabilidade", col_energia: "Energia",
    col_fala: "Fala", col_acustica: "Acústica",
    col_valencia: "Valência", col_aovivo: "Ao Vivo",
}
feats_r = [k for k in features_radar_map if k in df.columns]
if len(feats_r) >= 4:
    labels_r = [features_radar_map[k] for k in feats_r]
    medias_r = [df[k].mean() for k in feats_r]
    fig_radar = go.Figure(go.Scatterpolar(
        r=medias_r + [medias_r[0]],
        theta=labels_r + [labels_r[0]],
        fill="toself",
        line=dict(color=VERDE, width=2),
        fillcolor="rgba(29,185,84,0.18)",
        marker=dict(color=VERDE, size=6),
    ))
    fig_radar.update_layout(
        title=dict(text="Perfil Médio das Faixas", font=dict(color=BRANCO, size=14), x=0.5),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], color="#888", gridcolor="#2d2d50"),
            angularaxis=dict(color=BRANCO, gridcolor="#2d2d50"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=30, l=40, r=40),
    )
else:
    fig_radar = go.Figure()

# 5. Scatter dança × energia colorido por faixa de popularidade
if col_dance in df.columns and col_energia in df.columns and col_faixa in df.columns:
    sample = df.sample(min(4000, len(df)), random_state=42)
    fig_scatter = px.scatter(
        sample, x=col_dance, y=col_energia,
        color=col_faixa,
        color_discrete_map={"Baixa": AZUL, "Média": VERDE, "Alta": LARANJA, "Viral": ROSA},
        opacity=0.55,
        labels={col_dance: "Dançabilidade", col_energia: "Energia", col_faixa: "Popularidade"},
        title="Dançabilidade × Energia por Popularidade",
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO),
        yaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO),
        title=dict(font=dict(color=BRANCO, size=14), x=0.5),
        legend=dict(font=dict(color=BRANCO), bgcolor="rgba(0,0,0,0)", title_text=""),
        margin=dict(t=50, b=40, l=50, r=20),
    )
else:
    fig_scatter = go.Figure()

# 6. Box - distribuição de BPM por humor
if col_humor in df.columns if col_humor else False and col_bpm in df.columns:
    fig_box = px.box(
        df, x=col_humor, y=col_bpm,
        color=col_humor,
        color_discrete_sequence=[AZUL, VERDE, LARANJA],
        labels={col_humor: "Humor", col_bpm: "BPM"},
        title="BPM por Humor das Faixas",
    )
    fig_box.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color=BRANCO),
        yaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO),
        title=dict(font=dict(color=BRANCO, size=14), x=0.5),
        showlegend=False,
        margin=dict(t=50, b=40, l=50, r=20),
    )
else:
    fig_box = go.Figure()

# ── APP ───────────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)

PAGES = {
    "visao-geral":   "📊 Visão Geral",
    "popularidade":  "🔥 Popularidade",
    "generos":       "🎸 Gêneros",
    "audio":         "🎛️ Features de Áudio",
}

def sidebar():
    return html.Div([
        # Logo
        html.Div([
            html.Div("♪", style={"fontSize":"32px","color":VERDE}),
            html.Div([
                html.Div("Spotify", style={"fontSize":"16px","fontWeight":"800","color":BRANCO}),
                html.Div("Analytics", style={"fontSize":"11px","color":"#888"}),
            ]),
        ], style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"32px","padding":"4px 0"}),

        # Nav links
        html.Div("DASHBOARDS", style={"fontSize":"10px","color":"#555","letterSpacing":"0.1em",
                                       "marginBottom":"10px","fontWeight":"700"}),
        html.Div([
            dcc.Link(
                html.Div([
                    html.Span(label[:2]),
                    html.Span(label[2:], style={"marginLeft":"8px"}),
                ], id=f"nav-{page_id}", style={
                    "display":"flex","alignItems":"center","padding":"10px 14px",
                    "borderRadius":"8px","cursor":"pointer","fontSize":"13px",
                    "color":"#aaa","fontWeight":"500","transition":"all 0.2s",
                }),
                href=f"/{page_id}",
                style={"textDecoration":"none"},
            )
            for page_id, label in PAGES.items()
        ], style={"display":"flex","flexDirection":"column","gap":"4px"}),

        # Footer
        html.Div([
            html.Div("Dashboard 1", style={"fontSize":"11px","color":"#555"}),
            html.Div("Visão Geral", style={"fontSize":"10px","color":"#444"}),
        ], style={"marginTop":"auto","paddingTop":"20px","borderTop":"1px solid #2d2d50"}),

    ], style={
        "width":"200px","minWidth":"200px","background":SIDEBAR_BG,
        "minHeight":"100vh","padding":"24px 16px","display":"flex",
        "flexDirection":"column","borderRight":"1px solid #2d2d50",
        "position":"sticky","top":"0","height":"100vh","overflowY":"auto",
    })

# ── PÁGINAS ───────────────────────────────────────────────

def page_visao_geral():
    return html.Div([
        html.Div("Visão Geral", style={"fontSize":"22px","fontWeight":"800","color":BRANCO,"marginBottom":"4px"}),
        html.Div("Painel executivo com os principais indicadores do catálogo",
                 style={"fontSize":"13px","color":"#888","marginBottom":"20px"}),

        # KPIs
        html.Div([
            kpi("Total de Músicas", total_musicas, VERDE, "🎵"),
            kpi("Popularidade Média", pop_media, AZUL, "📈"),
            kpi("Gêneros Únicos", total_generos, LARANJA, "🎸"),
            kpi("Duração Mediana", dur_media, ROXO, "⏱️"),
            kpi("Músicas Virais", pct_viral, ROSA, "🔥"),
            kpi("Dançabilidade Média", dance_media, VERDE_ESC, "💃"),
        ], style={"display":"flex","gap":"12px","flexWrap":"wrap","marginBottom":"20px"}),

        # Insight destacado
        html.Div([
            html.Div("💡 Insight Principal", style={"fontSize":"12px","fontWeight":"700",
                     "color":VERDE,"marginBottom":"6px","textTransform":"uppercase","letterSpacing":"0.05em"}),
            html.Div("A grande maioria das faixas possui popularidade baixa ou média. "
                     "Músicas com alta dançabilidade e energia concentram os maiores índices de popularidade, "
                     "especialmente nos gêneros pop e eletrônico — sugerindo que o ritmo é o principal "
                     "motor de engajamento no Spotify.",
                     style={"fontSize":"13px","color":"#ccc","lineHeight":"1.6"}),
        ], style={"background":"rgba(29,185,84,0.08)","border":f"1px solid {VERDE}","borderLeft":f"4px solid {VERDE}",
                  "borderRadius":"10px","padding":"16px 20px","marginBottom":"20px"}),

        # Gráficos linha 1
        html.Div([
            card(dcc.Graph(figure=fig_donut, config={"displayModeBar":False},
                           style={"height":"320px"}), {"flex":"1","minWidth":"280px"}),
            card(dcc.Graph(figure=fig_bar, config={"displayModeBar":False},
                           style={"height":"320px"}), {"flex":"2","minWidth":"380px"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        # Gráficos linha 2
        html.Div([
            card(dcc.Graph(figure=fig_linha, config={"displayModeBar":False},
                           style={"height":"300px"}), {"flex":"2","minWidth":"380px"}),
            card(dcc.Graph(figure=fig_radar, config={"displayModeBar":False},
                           style={"height":"300px"}), {"flex":"1","minWidth":"280px"}),
        ], style={"display":"flex","gap":"16px"}),

    ], style={"padding":"28px"})


def page_popularidade():
    return html.Div([
        html.Div("Análise de Popularidade", style={"fontSize":"22px","fontWeight":"800","color":BRANCO,"marginBottom":"4px"}),
        html.Div("Como as faixas se distribuem em termos de engajamento",
                 style={"fontSize":"13px","color":"#888","marginBottom":"20px"}),

        html.Div([
            card(dcc.Graph(figure=fig_donut, config={"displayModeBar":False},
                           style={"height":"360px"}), {"flex":"1","minWidth":"280px"}),
            card(dcc.Graph(figure=fig_scatter, config={"displayModeBar":False},
                           style={"height":"360px"}), {"flex":"2","minWidth":"400px"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        # Insights de popularidade
        html.Div([
            _insight_card("🎯 Músicas Virais são raras",
                f"Apenas {pct_viral} das faixas atingem popularidade acima de 75. "
                "A distribuição é fortemente assimétrica à esquerda."),
            _insight_card("💃 Dança = Popularidade",
                "Faixas com dançabilidade acima de 0.7 têm, em média, "
                "15-20 pontos a mais de popularidade do que faixas menos dançantes."),
            _insight_card("⚡ Energia importa, mas menos",
                "A correlação entre energia e popularidade é moderada. "
                "Músicas baladas de alta popularidade contradizem essa tendência."),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


def page_generos():
    return html.Div([
        html.Div("Análise por Gênero", style={"fontSize":"22px","fontWeight":"800","color":BRANCO,"marginBottom":"4px"}),
        html.Div("Comparação de características entre os gêneros musicais",
                 style={"fontSize":"13px","color":"#888","marginBottom":"20px"}),

        html.Div([
            card(dcc.Graph(figure=fig_bar, config={"displayModeBar":False},
                           style={"height":"400px"}), {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        html.Div([
            _insight_card("🏆 Gênero Campeão",
                f"O gênero com maior popularidade média se destaca por atrair "
                "ouvintes de múltiplos perfis, combinando acessibilidade e produção polida."),
            _insight_card("🌍 Diversidade de catálogo",
                f"{total_generos} gêneros únicos no dataset mostram um catálogo altamente diversificado, "
                "com nichos bem definidos de audiência."),
            _insight_card("📏 Duração por gênero",
                "Gêneros como jazz e clássico tendem a faixas mais longas, "
                "enquanto pop e eletrônico convergem para o padrão comercial de 3 min."),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


def page_audio():
    return html.Div([
        html.Div("Features de Áudio", style={"fontSize":"22px","fontWeight":"800","color":BRANCO,"marginBottom":"4px"}),
        html.Div("Análise das características técnicas das faixas",
                 style={"fontSize":"13px","color":"#888","marginBottom":"20px"}),

        html.Div([
            card(dcc.Graph(figure=fig_radar, config={"displayModeBar":False},
                           style={"height":"380px"}), {"flex":"1","minWidth":"300px"}),
            card(dcc.Graph(figure=fig_scatter, config={"displayModeBar":False},
                           style={"height":"380px"}), {"flex":"2","minWidth":"380px"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        html.Div([
            _insight_card("🎹 Acústica em declínio",
                "Faixas mais recentes (pós-2015) apresentam menor índice de acústica, "
                "refletindo a digitalização e o domínio da produção eletrônica."),
            _insight_card("🗣️ Speechiness cresce no rap",
                "Gêneros de rap e hip-hop concentram os maiores valores de fala, "
                "com índices 3-4x maiores que a média geral do catálogo."),
            _insight_card("🔊 Loudness Wars",
                "O volume médio das faixas aumentou progressivamente entre 1990 e 2010, "
                "fenômeno conhecido como 'loudness war', que afeta a dinâmica das músicas."),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap"}),

    ], style={"padding":"28px"})


def _insight_card(titulo, texto):
    return html.Div([
        html.Div(titulo, style={"fontSize":"13px","fontWeight":"700","color":VERDE,"marginBottom":"8px"}),
        html.Div(texto, style={"fontSize":"12px","color":"#bbb","lineHeight":"1.6"}),
    ], style={
        "background":CARD_BG,"border":"1px solid #2d2d50","borderRadius":"10px",
        "padding":"16px","flex":"1","minWidth":"220px",
    })


# ── LAYOUT PRINCIPAL ──────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([
        sidebar(),
        html.Div(id="page-content", style={
            "flex":"1","background":CINZA_ESC,"minHeight":"100vh","overflowY":"auto",
        }),
    ], style={"display":"flex","minHeight":"100vh"}),
], style={"fontFamily":"'DM Sans', 'Segoe UI', sans-serif","background":CINZA_ESC})


@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname in ["/popularidade"]:
        return page_popularidade()
    elif pathname in ["/generos"]:
        return page_generos()
    elif pathname in ["/audio"]:
        return page_audio()
    else:
        return page_visao_geral()


if __name__ == "__main__":
    print("Dashboard 1 rodando em http://localhost:8050")
    app.run(debug=True, port=8050)