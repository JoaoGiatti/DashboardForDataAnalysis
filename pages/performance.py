import dash
from dash import html, dcc
from utils import (
    card, insight_card, titulo_pagina,
    fig_exp, fig_humor, fig_scatter_main, fig_top_musicas,
    exp_sim, exp_nao, humor_top,
    pop_chart_val, pop_noch_val, col_chart,
    VERDE, LARANJA, ROSA, AZUL, CINZA_CLR,
)

dash.register_page(__name__, path="/performance", name="🏆 Charts & Sucesso", order=1)

layout = html.Div([
    titulo_pagina("Charts & Sucesso", "O que separa músicas que chegam ao chart das demais"),

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

    # top músicas
    card([
        html.Div("Top 15 Músicas por Streams",
                 style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
        dcc.Graph(figure=fig_top_musicas, config={"displayModeBar":False}, style={"height":"420px"}),
    ], {"marginBottom":"14px"}),

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