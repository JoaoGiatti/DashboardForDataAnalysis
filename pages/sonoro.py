import dash
from dash import html, dcc
from utils import (
    card, insight_card, titulo_pagina,
    fig_radar, fig_heat, fig_box_humor,
    VERDE, LARANJA, ROSA, CINZA_CLR, BORDA,
)

dash.register_page(__name__, path="/sonoro", name="🎛️ Perfil Sonoro", order=3)

layout = html.Div([
    titulo_pagina("Perfil Sonoro", "O que diferencia sonoramente um hit de uma música comum?"),

    html.Div([
        card([
            html.Div("Perfil de Áudio: Hits vs Músicas Comuns",
                     style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"4px","fontWeight":"600"}),
            html.Div("Valores médios de cada característica sonora (0–1)",
                     style={"fontSize":"10px","color":"#555","marginBottom":"12px"}),
            dcc.Graph(figure=fig_radar, config={"displayModeBar":False}, style={"height":"300px"}),
        ], {"flex":"2","minWidth":"360px"}),
        card([
            html.Div("Correlação entre Features de Áudio",
                     style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"4px","fontWeight":"600"}),
            html.Div("Verde = correlação positiva | Vermelho = negativa",
                     style={"fontSize":"10px","color":"#555","marginBottom":"12px"}),
            dcc.Graph(figure=fig_heat, config={"displayModeBar":False}, style={"height":"300px"}),
        ], {"flex":"1","minWidth":"260px"}),
    ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

    html.Div([
        card([
            html.Div("Dançabilidade por Humor da Faixa",
                     style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"4px","fontWeight":"600"}),
            html.Div("Músicas alegres tendem a ser mais dançantes?",
                     style={"fontSize":"10px","color":"#555","marginBottom":"12px"}),
            dcc.Graph(figure=fig_box_humor, config={"displayModeBar":False}, style={"height":"260px"}),
        ], {"flex":"1","minWidth":"280px"}),
        html.Div([
            insight_card("🎯 Hits são mais dançantes e enérgicos",
                "Músicas que chegaram ao chart têm dançabilidade e energia médias "
                "visivelmente maiores que as que ficaram fora — confirma que ritmo "
                "e intensidade são características-chave de um hit no Spotify.",
                VERDE),
            insight_card("🔴 Energia × Acústica: opostos",
                "A correlação de -0.73 entre energia e acústica é a mais forte do catálogo. "
                "Músicas acústicas são quase sempre de baixa energia — "
                "e o heatmap deixa isso visível em vermelho.",
                ROSA),
            insight_card("😊 Alegria e dança andam juntas",
                "Faixas classificadas como 'Alegre' têm a maior mediana de dançabilidade. "
                "Músicas melancólicas apresentam maior variação — "
                "algumas são dançantes, outras não.",
                LARANJA),
        ], style={"flex":"1","minWidth":"280px","display":"flex","flexDirection":"column","gap":"12px"}),
    ], style={"display":"flex","gap":"14px"}),

], style={"padding":"28px"})
