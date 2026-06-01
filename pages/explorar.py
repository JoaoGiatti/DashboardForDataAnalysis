import dash
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
from utils import (
    df, card, label_filtro, dropdown_style,
    opcoes_genero, opcoes_pop, opcoes_humor, opcoes_chart, opcoes_features,
    features_audio, nomes_audio,
    col_genero, col_pop, col_humor, col_chart, col_faixa, col_streams,
    VERDE, AZUL, LARANJA, ROSA, CINZA_CLR, BORDA, BRANCO, CINZA_MD, SIDEBAR_BG,
)

dash.register_page(__name__, path="/explorar", name="🔍 Exploração", order=4)

def empty_fig():
    f = go.Figure()
    f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False), yaxis=dict(visible=False))
    return f

def bl(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color=BRANCO, size=12), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=BORDA, color=CINZA_CLR, tickfont=dict(size=10)),
        margin=dict(t=40, b=40, l=50, r=20),
        font=dict(color=BRANCO),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=CINZA_CLR, size=10)),
    )
    return fig

layout = html.Div([
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

    html.Div([
        html.Div([
            html.Div("Exploração Interativa",
                     style={"fontSize":"20px","fontWeight":"800","color":BRANCO}),
            html.Div("Filtre e cruze as variáveis para descobrir padrões",
                     style={"fontSize":"12px","color":CINZA_CLR}),
        ], style={"padding":"20px 24px 14px","borderTop":f"1px solid {BORDA}"}),

        html.Div([
            html.Div([
                html.Div(card(dcc.Graph(id="g-scatter", config={"displayModeBar":False}, style={"height":"320px"})),
                         style={"flex":"3","minWidth":"340px"}),
                html.Div(card(dcc.Graph(id="g-hist",    config={"displayModeBar":False}, style={"height":"320px"})),
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


@callback(
    Output("contagem", "children"),
    Output("g-scatter", "figure"),
    Output("g-hist",    "figure"),
    Output("g-box",     "figure"),
    Output("g-bar2",    "figure"),
    Output("g-heat2",   "figure"),
    Input("f-genero",   "value"),
    Input("f-pop",      "value"),
    Input("f-humor",    "value"),
    Input("f-chart",    "value"),
    Input("slider-pop", "value"),
    Input("f-feat-x",   "value"),
    Input("f-feat-y",   "value"),
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

    # Scatter
    if feat_x and feat_y and feat_x in dff.columns and feat_y in dff.columns and n > 0:
        samp = dff.sample(min(3000, n), random_state=42)
        cor_col2 = col_humor if col_humor and col_humor in samp.columns else None
        cores_h  = {"Melancólico":AZUL,"Neutro":LARANJA,"Alegre":VERDE}
        nome_x = next((o["label"] for o in opcoes_features if o["value"]==feat_x), feat_x)
        nome_y = next((o["label"] for o in opcoes_features if o["value"]==feat_y), feat_y)
        fig_sc = px.scatter(samp, x=feat_x, y=feat_y, color=cor_col2,
                            color_discrete_map=cores_h if cor_col2 else None,
                            color_discrete_sequence=[VERDE], opacity=0.5,
                            labels={feat_x:nome_x, feat_y:nome_y})
        bl(fig_sc, f"{nome_x} × {nome_y}")
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
        top8  = dff[col_genero].value_counts().head(8).index
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
        fig_br.update_layout(yaxis=dict(autorange="reversed", color=CINZA_CLR),
                              coloraxis_showscale=False)
    else:
        fig_br = empty_fig()

    # Heatmap
    feats_d = [f for f in features_audio if f in dff.columns]
    if len(feats_d) >= 3 and n > 0:
        labs   = [nomes_audio.get(f,f) for f in feats_d]
        corr2  = dff[feats_d].corr().round(2)
        fig_ht = go.Figure(go.Heatmap(
            z=corr2.values, x=labs, y=labs,
            colorscale="RdYlGn", zmid=0,
            text=corr2.values, texttemplate="%{text:.2f}",
            textfont=dict(size=8, color=BRANCO), showscale=False,
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
