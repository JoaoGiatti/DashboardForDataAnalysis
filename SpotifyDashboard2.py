"""
Dashboard 2 — Exploração Interativa
Spotify Tracks Dataset
Execute: python SpotifyDashboard2.py
Acesse:  http://localhost:8051
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
col_instr    = "instrumental" if "instrumental" in df.columns else "instrumentalness"
col_faixa    = "faixa_popularidade" if "faixa_popularidade" in df.columns else "popularity_faixa"
col_humor    = "humor" if "humor" in df.columns else None
col_ano      = "ano_lancamento" if "ano_lancamento" in df.columns else None

# ── Paleta ────────────────────────────────────────────────
VERDE     = "#1DB954"
PRETO     = "#121212"
CINZA_ESC = "#1a1a2e"
CINZA     = "#212135"
CINZA_MD  = "#2a2a45"
CARD_BG   = "#1e1e35"
SIDEBAR_BG= "#16162a"
BRANCO    = "#ffffff"
ROXO      = "#7c3aed"
AZUL      = "#3b82f6"
LARANJA   = "#f59e0b"
ROSA      = "#ec4899"

# Features disponíveis para seleção
features_map = {
    col_dance:    "Dançabilidade",
    col_energia:  "Energia",
    col_fala:     "Fala (Speechiness)",
    col_acustica: "Acústica",
    col_instr:    "Instrumental",
    col_aovivo:   "Ao Vivo",
    col_valencia: "Valência (Humor)",
    col_bpm:      "BPM (Tempo)",
}
features_audio = [k for k in features_map if k in df.columns]
opcoes_features = [{"label": features_map[k], "value": k} for k in features_audio]

# Opções de gênero
opcoes_genero = [{"label": "Todos os gêneros", "value": "Todos"}]
if col_genero:
    generos = sorted(df[col_genero].dropna().unique())
    opcoes_genero += [{"label": g.capitalize(), "value": g} for g in generos]

opcoes_pop = [
    {"label": "Todas as faixas", "value": "Todos"},
    {"label": "🔵 Baixa (0–25)", "value": "Baixa"},
    {"label": "🟢 Média (25–50)", "value": "Média"},
    {"label": "🟡 Alta (50–75)", "value": "Alta"},
    {"label": "🔴 Viral (75–100)", "value": "Viral"},
]

opcoes_humor = [{"label": "Todos", "value": "Todos"}]
if col_humor and col_humor in df.columns:
    humores = sorted(df[col_humor].dropna().unique())
    opcoes_humor += [{"label": h, "value": h} for h in humores]

# ── Helpers ───────────────────────────────────────────────
def card(children, style_extra=None):
    s = {"background": CARD_BG,"borderRadius":"14px","padding":"16px",
         "border":"1px solid #2d2d50"}
    if style_extra: s.update(style_extra)
    return html.Div(children, style=s)

def label_filtro(texto):
    return html.Label(texto, style={"fontSize":"11px","color":"#888",
                                     "fontWeight":"700","textTransform":"uppercase",
                                     "letterSpacing":"0.06em","marginBottom":"6px","display":"block"})

dropdown_style = {"fontSize":"13px","background":CINZA_MD}

# ── APP ───────────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)

def sidebar():
    return html.Div([
        html.Div([
            html.Div("♪", style={"fontSize":"32px","color":VERDE}),
            html.Div([
                html.Div("Spotify", style={"fontSize":"16px","fontWeight":"800","color":BRANCO}),
                html.Div("Explorer", style={"fontSize":"11px","color":"#888"}),
            ]),
        ], style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"28px"}),

        html.Div("FILTROS", style={"fontSize":"10px","color":"#555","letterSpacing":"0.1em",
                                   "marginBottom":"16px","fontWeight":"700"}),

        # Gênero
        html.Div([
            label_filtro("🎸 Gênero"),
            dcc.Dropdown(id="f-genero", options=opcoes_genero, value="Todos",
                         clearable=False, style=dropdown_style),
        ], style={"marginBottom":"16px"}),

        # Popularidade
        html.Div([
            label_filtro("🔥 Popularidade"),
            dcc.Dropdown(id="f-pop", options=opcoes_pop, value="Todos",
                         clearable=False, style=dropdown_style),
        ], style={"marginBottom":"16px"}),

        # Humor
        html.Div([
            label_filtro("😊 Humor"),
            dcc.Dropdown(id="f-humor", options=opcoes_humor, value="Todos",
                         clearable=False, style=dropdown_style),
        ], style={"marginBottom":"20px"}) if col_humor and col_humor in df.columns else html.Div(id="f-humor", style={"display":"none"}),

        # Slider popularidade mínima
        html.Div([
            label_filtro("📊 Pop. Mínima"),
            dcc.Slider(id="slider-pop", min=0, max=100, step=5, value=0,
                       marks={0:"0", 50:"50", 100:"100"},
                       tooltip={"placement":"right","always_visible":False}),
        ], style={"marginBottom":"20px"}),

        # Divisor
        html.Div(style={"borderTop":"1px solid #2d2d50","margin":"8px 0 20px"}),

        html.Div("EIXOS DO SCATTER", style={"fontSize":"10px","color":"#555",
                                            "letterSpacing":"0.1em","marginBottom":"12px","fontWeight":"700"}),

        # Feature X
        html.Div([
            label_filtro("Eixo X"),
            dcc.Dropdown(id="f-feat-x", options=opcoes_features,
                         value=features_audio[0] if features_audio else None,
                         clearable=False, style=dropdown_style),
        ], style={"marginBottom":"12px"}),

        # Feature Y
        html.Div([
            label_filtro("Eixo Y"),
            dcc.Dropdown(id="f-feat-y", options=opcoes_features,
                         value=features_audio[1] if len(features_audio)>1 else None,
                         clearable=False, style=dropdown_style),
        ], style={"marginBottom":"24px"}),

        # Contagem
        html.Div(id="contagem", style={"fontSize":"11px","color":"#888",
                                        "borderTop":"1px solid #2d2d50","paddingTop":"16px"}),

        html.Div([
            html.Div("Dashboard 2", style={"fontSize":"11px","color":"#555"}),
            html.Div("Exploração Interativa", style={"fontSize":"10px","color":"#444"}),
        ], style={"marginTop":"auto","paddingTop":"16px"}),

    ], style={
        "width":"220px","minWidth":"220px","background":SIDEBAR_BG,
        "minHeight":"100vh","padding":"24px 16px","display":"flex",
        "flexDirection":"column","borderRight":"1px solid #2d2d50",
        "position":"sticky","top":"0","height":"100vh","overflowY":"auto",
    })


app.layout = html.Div([
    html.Div([
        sidebar(),

        # Área principal
        html.Div([
            # Header
            html.Div([
                html.Div("Exploração Interativa",
                         style={"fontSize":"22px","fontWeight":"800","color":BRANCO}),
                html.Div("Use os filtros na barra lateral para explorar o catálogo",
                         style={"fontSize":"13px","color":"#888"}),
            ], style={"padding":"24px 28px 16px","borderBottom":"1px solid #2d2d50"}),

            # Grid de gráficos
            html.Div([

                # Linha 1
                html.Div([
                    html.Div(card(dcc.Graph(id="g-scatter", config={"displayModeBar":False},
                                           style={"height":"340px"})),
                             style={"flex":"3","minWidth":"360px"}),
                    html.Div(card(dcc.Graph(id="g-hist", config={"displayModeBar":False},
                                           style={"height":"340px"})),
                             style={"flex":"2","minWidth":"260px"}),
                ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

                # Linha 2
                html.Div([
                    html.Div(card(dcc.Graph(id="g-box", config={"displayModeBar":False},
                                           style={"height":"340px"})),
                             style={"flex":"2","minWidth":"300px"}),
                    html.Div(card(dcc.Graph(id="g-bar", config={"displayModeBar":False},
                                           style={"height":"340px"})),
                             style={"flex":"2","minWidth":"300px"}),
                    html.Div(card(dcc.Graph(id="g-heat", config={"displayModeBar":False},
                                           style={"height":"340px"})),
                             style={"flex":"1","minWidth":"280px"}),
                ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

                # Linha 3 - gráfico extra: linha temporal (se houver ano)
                html.Div([
                    html.Div(card(dcc.Graph(id="g-linha", config={"displayModeBar":False},
                                           style={"height":"280px"})),
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"16px"}),

            ], style={"padding":"20px 28px 28px"}),

        ], style={"flex":"1","background":CINZA_ESC,"overflowY":"auto"}),

    ], style={"display":"flex","minHeight":"100vh"}),
], style={"fontFamily":"'DM Sans','Segoe UI',sans-serif","background":CINZA_ESC})


# ── CALLBACK ──────────────────────────────────────────────
@callback(
    Output("contagem", "children"),
    Output("g-scatter", "figure"),
    Output("g-hist", "figure"),
    Output("g-box", "figure"),
    Output("g-bar", "figure"),
    Output("g-heat", "figure"),
    Output("g-linha", "figure"),
    Input("f-genero", "value"),
    Input("f-pop", "value"),
    Input("f-humor", "value"),
    Input("slider-pop", "value"),
    Input("f-feat-x", "value"),
    Input("f-feat-y", "value"),
)
def atualizar(genero, pop_faixa, humor, pop_min, feat_x, feat_y):

    dff = df.copy()

    if genero and genero != "Todos" and col_genero:
        dff = dff[dff[col_genero] == genero]
    if pop_faixa and pop_faixa != "Todos" and col_faixa in dff.columns:
        dff = dff[dff[col_faixa] == pop_faixa]
    if humor and humor != "Todos" and col_humor and col_humor in dff.columns:
        dff = dff[dff[col_humor] == humor]
    if col_pop in dff.columns:
        dff = dff[dff[col_pop] >= pop_min]

    n = len(dff)
    contagem = [
        html.Div(f"{n:,}", style={"fontSize":"22px","fontWeight":"800","color":VERDE}),
        html.Div("faixas selecionadas", style={"fontSize":"11px","color":"#666"}),
    ]

    def empty():
        f = go.Figure()
        f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(visible=False), yaxis=dict(visible=False))
        return f

    def base_layout(fig, title=""):
        fig.update_layout(
            title=dict(text=title, font=dict(color=BRANCO, size=13), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO),
            yaxis=dict(showgrid=True, gridcolor="#2d2d50", color=BRANCO),
            margin=dict(t=45, b=40, l=50, r=20),
            font=dict(color=BRANCO),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=BRANCO, size=10)),
        )
        return fig

    # 1. SCATTER
    if feat_x and feat_y and feat_x in dff.columns and feat_y in dff.columns and n > 0:
        sample = dff.sample(min(4000, n), random_state=42)
        cor_col = col_faixa if col_faixa in sample.columns else None
        color_map = {"Baixa": AZUL, "Média": VERDE, "Alta": LARANJA, "Viral": ROSA}
        # Detecta colunas de nome e artista (português ou inglês)
        col_nome = next((c for c in ["nome_musica", "track_name"] if c in dff.columns), None)
        col_artista = next((c for c in ["artistas", "artists"] if c in dff.columns), None)

        hover_extra = {}
        if col_nome:    hover_extra[col_nome] = True
        if col_artista: hover_extra[col_artista] = True

        fig_scatter = px.scatter(
            sample, x=feat_x, y=feat_y,
            color=cor_col,
            color_discrete_map=color_map if cor_col else None,
            color_discrete_sequence=[VERDE],
            opacity=0.5,
            labels={feat_x: features_map.get(feat_x, feat_x),
                    feat_y: features_map.get(feat_y, feat_y),
                    col_faixa: "Popularidade"},
            hover_data=hover_extra,
        )
        fig_scatter.update_traces(
            hovertemplate=(
                f"<b>%{{customdata[0]}}</b><br>"
                f"🎤 %{{customdata[1]}}<br>"
                f"{features_map.get(feat_x, feat_x)}: %{{x:.3f}}<br>"
                f"{features_map.get(feat_y, feat_y)}: %{{y:.3f}}<extra></extra>"
            )
        )
        base_layout(fig_scatter, f"{features_map.get(feat_x,feat_x)} × {features_map.get(feat_y,feat_y)}")
        fig_scatter.update_layout(showlegend=True)
    else:
        fig_scatter = empty()

    # 2. HISTOGRAMA
    if col_pop in dff.columns and n > 0:
        fig_hist = px.histogram(dff, x=col_pop, nbins=25,
                                color_discrete_sequence=[VERDE],
                                labels={col_pop: "Popularidade"})
        fig_hist.update_traces(marker_line_color="#0b3d91", marker_line_width=0.5)
        base_layout(fig_hist, "Distribuição de Popularidade")
        fig_hist.update_layout(bargap=0.04)
    else:
        fig_hist = empty()

    # 3. BOXPLOT
    if col_genero and feat_x and feat_x in dff.columns and n > 0:
        top8 = dff[col_genero].value_counts().head(8).index
        dff_box = dff[dff[col_genero].isin(top8)]
        fig_box = px.box(
            dff_box, x=col_genero, y=feat_x,
            color=col_genero,
            color_discrete_sequence=px.colors.qualitative.Safe,
            labels={col_genero: "Gênero", feat_x: features_map.get(feat_x, feat_x)},
        )
        base_layout(fig_box, f"{features_map.get(feat_x,feat_x)} por Gênero (Top 8)")
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
    else:
        fig_box = empty()

    # 4. BARRAS - top 12 gêneros por quantidade
    if col_genero and n > 0:
        top12 = dff[col_genero].value_counts().head(12).reset_index()
        top12.columns = ["genero", "total"]
        fig_bar = px.bar(
            top12, x="total", y="genero", orientation="h",
            color="total",
            color_continuous_scale=[[0, "#0b3d91"],[0.5, VERDE],[1, ROSA]],
            labels={"total": "Quantidade", "genero": "Gênero"},
        )
        base_layout(fig_bar, "Quantidade por Gênero")
        fig_bar.update_layout(
            yaxis=dict(autorange="reversed", color=BRANCO),
            coloraxis_showscale=False,
        )
    else:
        fig_bar = empty()

    # 5. HEATMAP
    feats_disp = [f for f in features_audio if f in dff.columns]
    if len(feats_disp) >= 3 and n > 0:
        labels_disp = [features_map.get(f, f) for f in feats_disp]
        corr = dff[feats_disp].corr().round(2)
        fig_heat = go.Figure(go.Heatmap(
            z=corr.values,
            x=labels_disp,
            y=labels_disp,
            colorscale="RdYlGn",
            zmid=0,
            text=corr.values,
            texttemplate="%{text:.2f}",
            textfont=dict(size=9, color=BRANCO),
            showscale=False,
        ))
        fig_heat.update_layout(
            title=dict(text="Correlação entre Features", font=dict(color=BRANCO, size=13), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=45, b=80, l=80, r=20),
            xaxis=dict(tickangle=-40, color=BRANCO, tickfont=dict(size=9)),
            yaxis=dict(color=BRANCO, tickfont=dict(size=9)),
            font=dict(color=BRANCO),
        )
    else:
        fig_heat = empty()

    # 6. LINHA TEMPORAL
    if col_ano and col_ano in dff.columns and n > 0:
        por_ano = dff.groupby(col_ano).size().reset_index(name="total")
        por_ano = por_ano[(por_ano[col_ano] >= 1990) & (por_ano[col_ano] <= 2025)]
        fig_linha = go.Figure()
        fig_linha.add_trace(go.Scatter(
            x=por_ano[col_ano], y=por_ano["total"],
            mode="lines+markers",
            line=dict(color=VERDE, width=2),
            marker=dict(size=5, color=VERDE),
            fill="tozeroy",
            fillcolor="rgba(29,185,84,0.10)",
            name="Faixas",
        ))
        base_layout(fig_linha, "Evolução Temporal — Músicas por Ano")
        fig_linha.update_layout(
            xaxis_title="Ano", yaxis_title="Quantidade",
        )
    else:
        fig_linha = empty()

    return contagem, fig_scatter, fig_hist, fig_box, fig_bar, fig_heat, fig_linha


if __name__ == "__main__":
    print("Dashboard 2 rodando em http://localhost:8051")
    app.run(debug=True, port=8051)