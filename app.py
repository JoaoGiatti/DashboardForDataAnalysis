import dash
from dash import html, dcc
from utils import (
    CINZA, SIDEBAR_BG, VERDE, BRANCO, CINZA_CLR, BORDA,
    total_musicas,
)

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
)

def sidebar():
    return html.Div([
        html.Div([
            html.Div("♫", style={"fontSize":"28px","color":VERDE,"lineHeight":"1"}),
            html.Div([
                html.Div("Spotify",   style={"fontSize":"15px","fontWeight":"800","color":BRANCO}),
                html.Div("Analytics", style={"fontSize":"10px","color":"#555","letterSpacing":"0.05em"}),
            ]),
        ], style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"32px"}),

        html.Div("NAVEGAÇÃO", style={"fontSize":"9px","color":"#444","letterSpacing":"0.12em",
                                      "marginBottom":"10px","fontWeight":"700"}),
        html.Div([
            dcc.Link(
                html.Div([
                    html.Span(page["name"][:2], style={"fontSize":"15px"}),
                    html.Span(page["name"][2:], style={"marginLeft":"10px","fontSize":"12px"}),
                ], style={
                    "display":"flex","alignItems":"center","padding":"10px 12px",
                    "borderRadius":"8px","cursor":"pointer","color":"#666","fontWeight":"500",
                }),
                href=page["relative_path"],
                style={"textDecoration":"none"},
            )
            for page in dash.page_registry.values()
        ], style={"display":"flex","flexDirection":"column","gap":"2px"}),

        html.Div([
            html.Div("Tracks + Charts", style={"fontSize":"10px","color":"#333"}),
            html.Div(f"{total_musicas} faixas", style={"fontSize":"9px","color":"#2a2a40","marginTop":"2px"}),
        ], style={"marginTop":"auto","paddingTop":"20px","borderTop":f"1px solid {BORDA}"}),

    ], style={
        "width":"195px","minWidth":"195px","background":SIDEBAR_BG,
        "minHeight":"100vh","padding":"24px 14px","display":"flex","flexDirection":"column",
        "borderRight":f"1px solid {BORDA}","position":"sticky","top":"0",
        "height":"100vh","overflowY":"auto",
    })

# use_pages=True já injeta o dcc.Location internamente — não adicione outro aqui
app.layout = html.Div([
    html.Div([
        sidebar(),
        html.Div(
            dash.page_container,
            style={"flex":"1","background":CINZA,"minHeight":"100vh","overflowY":"auto"},
        ),
    ], style={"display":"flex","minHeight":"100vh"}),
], style={"fontFamily":"'DM Sans','Segoe UI',sans-serif","background":CINZA})


if __name__ == "__main__":
    print("Dashboard rodando em http://localhost:8050")
    app.run(debug=True, port=8050)