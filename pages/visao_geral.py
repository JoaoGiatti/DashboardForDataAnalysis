import dash
from dash import html, dcc
from utils import (
    card, kpi, insight_card, titulo_pagina,
    fig_donut, fig_gen_streams, fig_comp_pop, fig_timeline,
    total_musicas, total_generos, pct_chart, total_streams,
    paises_medio, dur_media, n_chart, pop_chart_val, pop_noch_val,
    VERDE, VERDE_MUT, ROXO, LARANJA, AZUL, ROSA, VERDE_ESC, ROSA_MUT,
    CINZA_CLR, BORDA,
)

dash.register_page(__name__, path="/", name="📊 Visão Geral", order=0)

layout = html.Div([
    titulo_pagina("Visão Geral", "Panorama completo do catálogo Spotify — tracks + performance nos charts"),

    html.Div([
        kpi("Faixas",           total_musicas, VERDE,    "🎵", "no catálogo"),
        kpi("Gêneros Únicos",   total_generos, ROXO,     "🎸", "categorias"),
        kpi("Nos Charts",       pct_chart,     LARANJA,  "🏆", f"{n_chart:,} músicas"),
        kpi("Streams Totais",   total_streams, AZUL,     "▶️", "bilhões"),
        kpi("Países (média)",   paises_medio,  ROSA,     "🌍", "por faixa no chart"),
        kpi("Duração Mediana",  dur_media,     VERDE_ESC,"⏱️","por faixa"),
    ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"20px"}),

    html.Div([
        html.Span("💡 ", style={"fontSize":"16px"}),
        html.Span(
            f"Apenas {pct_chart} das faixas chegou aos charts globais — mas essas músicas têm "
            f"popularidade média de {pop_chart_val} vs {pop_noch_val} das demais. "
            "Músicas explícitas geram 47% mais streams medianos que não-explícitas.",
            style={"fontSize":"13px","color":"#ccc","lineHeight":"1.6"}
        ),
    ], style={
        "background":VERDE_MUT,"border":f"1px solid {VERDE}","borderLeft":f"4px solid {VERDE}",
        "borderRadius":"10px","padding":"14px 18px","marginBottom":"20px","display":"flex","gap":"8px",
    }),

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
