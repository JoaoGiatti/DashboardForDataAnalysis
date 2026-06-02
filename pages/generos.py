import dash
from dash import html, dcc
from utils import (
    card, insight_card, titulo_pagina,
    fig_pop_genero, fig_gen_streams, fig_bpm,
    top_stream_gen,
    VERDE, LARANJA, ROXO, CINZA_CLR,
)

dash.register_page(__name__, path="/generos", name="🎸 Gêneros", order=2)

layout = html.Div([
    titulo_pagina("Análise por Gênero", "Volume, alcance e características por gênero musical"),

    html.Div([
        card([
            html.Div("Popularidade Média",
                     style={"fontSize":"12px","color":CINZA_CLR,"marginBottom":"12px","fontWeight":"600"}),
            dcc.Graph(figure=fig_pop_genero, config={"displayModeBar":False}, style={"height":"320px"}),
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
        insight_card("⭐ Popularidade ≠ Volume",
            "Um gênero pode ter popularidade média alta sem liderar em streams totais — "
            "o que indica faixas individualmente bem avaliadas, mas sem o alcance massivo "
            "de gêneros como pop e hip-hop.",
            ROXO),
    ], style={"display":"flex","gap":"14px","flexWrap":"wrap"}),

], style={"padding":"28px"})