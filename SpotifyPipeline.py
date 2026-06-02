"""
ETAPAS:
  1. Aquisição via Kaggle API
  2. Integração (merge por título + artista)
  3. Limpeza e tratamento
  4. Transformação e novas variáveis
  5. Análise exploratória + insights
=============================================================
"""
import os, warnings
import kaggle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")


# ------------------------------------------------------------
# 1. aquisição
# ------------------------------------------------------------

os.makedirs("dados/dataset1", exist_ok=True)
os.makedirs("dados/dataset2", exist_ok=True)

kaggle.api.dataset_download_files(
    "maharshipandya/-spotify-tracks-dataset",
    path="dados/dataset1", unzip=True
)
kaggle.api.dataset_download_files(
    "dhruvildave/spotify-charts",
    path="dados/dataset2", unzip=True
)

def ler_csvs(pasta, label):
    arquivos = [f for f in os.listdir(pasta) if f.endswith(".csv")]
    dfs = []
    for arq in sorted(arquivos):
        df = pd.read_csv(os.path.join(pasta, arq), low_memory=False)
        df["arquivo_origem"] = arq
        print(f"  {label} / {arq}: {len(df):,} linhas")
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

df_tracks = ler_csvs("dados/dataset1", "tracks")
df_charts = ler_csvs("dados/dataset2", "charts")

print(f"tracks: {len(df_tracks):,} | charts: {len(df_charts):,}")


# ------------------------------------------------------------
# 2. merge
# ------------------------------------------------------------

df_tracks.columns = df_tracks.columns.str.strip().str.lower().str.replace(" ", "_")
df_charts.columns = df_charts.columns.str.strip().str.lower().str.replace(" ", "_")

def normalizar(serie):
    return (serie.astype(str)
            .str.lower().str.strip()
            .str.replace(r"[^\w\s]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True))

df_tracks["_chave"] = normalizar(df_tracks["track_name"])
df_charts["_chave"] = normalizar(df_charts["title"])

charts_agg = df_charts.groupby("_chave").agg(
    streams_total   = ("streams", "sum"),
    streams_media   = ("streams", "mean"),
    melhor_posicao  = ("rank",    "min"),
    aparicoes_chart = ("rank",    "count"),
    paises_chart    = ("region",  "nunique"),
    primeira_data   = ("date",    "min"),
    ultima_data     = ("date",    "max"),
).reset_index()

if "chart" in df_charts.columns:
    charts_tipo = df_charts.groupby(["_chave", "chart"]).size().unstack(fill_value=0).reset_index()
    charts_tipo.columns = ["_chave"] + [f"chart_{c}" for c in charts_tipo.columns[1:]]
    charts_agg = charts_agg.merge(charts_tipo, on="_chave", how="left")

df = df_tracks.merge(charts_agg, on="_chave", how="left")
df["chegou_ao_chart"] = df["streams_total"].notna()

print(f"após merge: {len(df):,} | charted: {df['chegou_ao_chart'].mean()*100:.1f}%")

df.drop(columns=["_chave", "arquivo_origem"], inplace=True, errors="ignore")


# ------------------------------------------------------------
# 3. limpeza
# ------------------------------------------------------------

snap_antes = pd.DataFrame({
    "coluna":          df.columns,
    "tipo":            df.dtypes.values,
    "nulos_antes":     df.isnull().sum().values,
    "pct_nulos_antes": (df.isnull().mean() * 100).round(2).values,
})
resumo_antes = {
    "linhas":      len(df),
    "colunas":     df.shape[1],
    "duplicatas":  df.duplicated(subset=["track_id"]).sum() if "track_id" in df.columns else df.duplicated().sum(),
    "total_nulos": int(df.isnull().sum().sum()),
}

df.drop(columns=[c for c in df.columns if c.startswith("unnamed")], inplace=True, errors="ignore")

for col in df.select_dtypes(include=[np.number]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].median(), inplace=True)

for col in df.select_dtypes(include=["object"]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna("Desconhecido", inplace=True)

antes = len(df)
df.drop_duplicates(subset=["track_id"], inplace=True)
print(f"duplicatas removidas: {antes - len(df):,}")

if "duration_ms" in df.columns:
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
if "popularity" in df.columns:
    df = df[(df["popularity"] >= 0) & (df["popularity"] <= 100)]

resumo_depois = {
    "linhas":      len(df),
    "colunas":     df.shape[1],
    "duplicatas":  0,
    "total_nulos": int(df.isnull().sum().sum()),
}

colunas_comuns = [c for c in snap_antes["coluna"] if c in df.columns]
snap_antes_f   = snap_antes[snap_antes["coluna"].isin(colunas_comuns)].copy()
snap_depois    = pd.DataFrame({
    "coluna":              df[colunas_comuns].columns,
    "nulos_depois":        df[colunas_comuns].isnull().sum().values,
    "pct_nulos_depois":    (df[colunas_comuns].isnull().mean() * 100).round(2).values,
})

relatorio = snap_antes_f.merge(snap_depois, on="coluna")
relatorio["nulos_removidos"] = relatorio["nulos_antes"] - relatorio["nulos_depois"]
relatorio["tratamento"] = relatorio.apply(
    lambda r: "mediana" if r["nulos_antes"] > 0 and pd.api.types.is_numeric_dtype(r["tipo"])
              else ("desconhecido" if r["nulos_antes"] > 0 else "ok"),
    axis=1
)
relatorio = relatorio[["coluna","tipo","nulos_antes","pct_nulos_antes",
                        "nulos_depois","pct_nulos_depois","nulos_removidos","tratamento"]]

resumo = pd.DataFrame([
    {"metrica": "Linhas",         "antes": resumo_antes["linhas"],      "depois": resumo_depois["linhas"]},
    {"metrica": "Colunas",        "antes": resumo_antes["colunas"],     "depois": resumo_depois["colunas"]},
    {"metrica": "Duplicatas",     "antes": resumo_antes["duplicatas"],  "depois": resumo_depois["duplicatas"]},
    {"metrica": "Total de Nulos", "antes": resumo_antes["total_nulos"], "depois": resumo_depois["total_nulos"]},
])

os.makedirs("dados", exist_ok=True)
with open("dados/relatorio_tratamento.csv", "w", encoding="utf-8") as f:
    f.write("resumo geral\n")
    resumo.to_csv(f, index=False)
    f.write("\ndetalhe por coluna\n")
    relatorio.to_csv(f, index=False)

print(resumo.to_string(index=False))
tratadas = relatorio[relatorio["nulos_antes"] > 0][["coluna","nulos_antes","nulos_depois","tratamento"]]
print(tratadas.to_string(index=False) if len(tratadas) > 0 else "nenhum nulo")


# ------------------------------------------------------------
# 4. feature engineering
# ------------------------------------------------------------

if "duration_ms" in df.columns:
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)

if "popularity" in df.columns:
    df["faixa_popularidade"] = pd.cut(
        df["popularity"],
        bins=[0, 25, 50, 75, 100],
        labels=["Baixa","Média","Alta","Viral"],
        include_lowest=True
    )

if "valence" in df.columns:
    df["humor"] = pd.cut(
        df["valence"],
        bins=[0, 0.33, 0.66, 1.0],
        labels=["Melancólico","Neutro","Alegre"],
        include_lowest=True
    )

if "streams_total" in df.columns:
    df["streams_total"] = pd.to_numeric(df["streams_total"], errors="coerce").fillna(0)
    df["faixa_streams"] = pd.cut(
        df["streams_total"],
        bins=[-1, 0, 1e7, 1e8, 1e9, float("inf")],
        labels=["Sem chart","< 10M","10M–100M","100M–1B","> 1B"]
    )

if "instrumentalness" in df.columns:
    df["tipo_faixa"] = np.where(df["instrumentalness"] >= 0.5, "Instrumental", "Vocal")

if "primeira_data" in df.columns:
    df["ano_chart"] = pd.to_datetime(df["primeira_data"], errors="coerce").dt.year

if "danceability" in df.columns and "energy" in df.columns:
    df["score_danca_energia"] = (df["danceability"] * df["energy"]).round(4)

traducao = {
    "track_id": "id_musica", "track_name": "nome_musica", "artists": "artistas",
    "album_name": "album", "track_genre": "genero", "popularity": "popularidade",
    "duration_ms": "duracao_ms", "duration_min": "duracao_min", "explicit": "explicito",
    "danceability": "dancabilidade", "energy": "energia", "key": "tom",
    "loudness": "volume", "mode": "modo", "speechiness": "fala",
    "acousticness": "acustica", "instrumentalness": "instrumental",
    "liveness": "ao_vivo", "valence": "valencia", "tempo": "bpm",
    "time_signature": "compasso", "streams_total": "streams_total",
    "streams_media": "streams_media", "melhor_posicao": "melhor_posicao",
    "aparicoes_chart": "aparicoes_chart", "paises_chart": "paises_chart",
    "chegou_ao_chart": "chegou_ao_chart", "faixa_popularidade": "faixa_popularidade",
    "faixa_streams": "faixa_streams", "score_danca_energia": "score_danca_energia",
    "tipo_faixa": "tipo_faixa", "humor": "humor", "ano_chart": "ano_chart",
}
df.rename(columns={k: v for k, v in traducao.items() if k in df.columns}, inplace=True)

col_genero = "genero" if "genero" in df.columns else None
if col_genero:
    agg_cols = {"total_musicas": (col_genero, "count")}
    if "popularidade"  in df.columns: agg_cols["popularidade_media"]  = ("popularidade",  "mean")
    if "dancabilidade" in df.columns: agg_cols["dancabilidade_media"] = ("dancabilidade", "mean")
    if "energia"       in df.columns: agg_cols["energia_media"]       = ("energia",       "mean")
    if "streams_total" in df.columns: agg_cols["streams_total"]       = ("streams_total", "sum")
    if "melhor_posicao" in df.columns: agg_cols["melhor_posicao"]     = ("melhor_posicao","min")
    if "paises_chart"  in df.columns: agg_cols["paises_chart_media"]  = ("paises_chart",  "mean")

    agg = df.groupby(col_genero).agg(**agg_cols).round(3).sort_values("total_musicas", ascending=False)
    agg.to_csv("dados/agg_por_genero.csv")


# ------------------------------------------------------------
# 5. eda
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Spotify Tracks + Charts — EDA", fontsize=16, fontweight="bold")

if "popularidade" in df.columns:
    df["popularidade"].hist(bins=30, ax=axes[0,0], color="#1DB954", edgecolor="white")
    axes[0,0].set_title("distribuição de popularidade")

if "chegou_ao_chart" in df.columns:
    df["chegou_ao_chart"].value_counts().rename({True:"no chart", False:"sem chart"}).plot(
        kind="bar", ax=axes[0,1], color=["#1DB954","#444"], edgecolor="white")
    axes[0,1].set_title("faixas nos charts vs fora")
    axes[0,1].tick_params(axis="x", rotation=0)

if col_genero and "streams_total" in df.columns:
    top_streams = df.groupby(col_genero)["streams_total"].sum().sort_values(ascending=False).head(10)
    top_streams.plot(kind="barh", ax=axes[0,2], color="#1DB954")
    axes[0,2].set_title("top 10 gêneros por streams")
    axes[0,2].invert_yaxis()

if "chegou_ao_chart" in df.columns and "popularidade" in df.columns:
    df.boxplot(column="popularidade", by="chegou_ao_chart", ax=axes[1,0],
               patch_artist=True, boxprops=dict(facecolor="#1DB954", alpha=0.7))
    axes[1,0].set_xlabel("")
    plt.sca(axes[1,0])
    plt.title("popularidade: chart vs sem chart")

if "humor" in df.columns and "streams_total" in df.columns:
    humor_streams = df[df["streams_total"] > 0].groupby("humor")["streams_total"].median()
    humor_streams.plot(kind="bar", ax=axes[1,1], color=["#6fa8dc","#6aa84f","#f59e0b"], edgecolor="white")
    axes[1,1].set_title("streams medianos por humor")
    axes[1,1].tick_params(axis="x", rotation=0)

features_pt = [c for c in ["dancabilidade","energia","volume","fala",
                             "acustica","instrumental","ao_vivo","valencia","bpm"]
               if c in df.columns]
if len(features_pt) >= 3:
    corr = df[features_pt].corr()
    sns.heatmap(corr, ax=axes[1,2], cmap="RdYlGn", center=0,
                annot=True, fmt=".1f", annot_kws={"size": 7},
                linewidths=0.5, cbar=False)
    axes[1,2].set_title("correlação entre features de áudio")
    axes[1,2].tick_params(axis="x", rotation=45, labelsize=8)
    axes[1,2].tick_params(axis="y", labelsize=8)

plt.tight_layout()
plt.savefig("dados/analise_exploratoria.png", dpi=150, bbox_inches="tight")
plt.close()

# insights rápidos
if "popularidade" in df.columns:
    print(f"popularidade média: {df['popularidade'].mean():.1f}/100")

if "chegou_ao_chart" in df.columns:
    n = df["chegou_ao_chart"].sum()
    print(f"músicas nos charts: {n:,} ({n/len(df)*100:.1f}%)")

    if "popularidade" in df.columns:
        pc  = df[df["chegou_ao_chart"]]["popularidade"].mean()
        psc = df[~df["chegou_ao_chart"]]["popularidade"].mean()
        print(f"popularidade — chart: {pc:.1f} | sem chart: {psc:.1f}")

if col_genero and "streams_total" in df.columns:
    print(f"gênero top streams: {df.groupby(col_genero)['streams_total'].sum().idxmax()}")

if "humor" in df.columns and "streams_total" in df.columns:
    print(f"humor top streams: {df[df['streams_total']>0].groupby('humor')['streams_total'].median().idxmax()}")

if "tipo_faixa" in df.columns and "streams_total" in df.columns:
    voc  = df[(df["tipo_faixa"]=="Vocal")        & (df["streams_total"]>0)]["streams_total"].median()
    inst = df[(df["tipo_faixa"]=="Instrumental") & (df["streams_total"]>0)]["streams_total"].median()
    print(f"streams medianos — vocal: {voc:,.0f} | instrumental: {inst:,.0f}")

if "explicito" in df.columns and "streams_total" in df.columns:
    exp    = df[(df["explicito"]==True)  & (df["streams_total"]>0)]["streams_total"].median()
    nexp   = df[(df["explicito"]==False) & (df["streams_total"]>0)]["streams_total"].median()
    print(f"streams medianos — explícito: {exp:,.0f} | não explícito: {nexp:,.0f}")

if "paises_chart" in df.columns:
    print(f"média de países por música: {df['paises_chart'].mean():.1f}")

df.to_csv("dados/spotify_final.csv", index=False)
print(f"dataset final: dados/spotify_final.csv ({len(df):,} linhas)")