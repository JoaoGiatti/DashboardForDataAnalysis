"""
=============================================================
  Pipeline de Ciência de Dados — Spotify
  Dataset 1: maharshipandya/-spotify-tracks-dataset
             (características de áudio das faixas)
  Dataset 2: dhruvildave/spotify-charts
             (performance nos charts globais)
=============================================================
Etapas:
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

# ─────────────────────────────────────────────────────────
# 1. AQUISIÇÃO DE DADOS
# ─────────────────────────────────────────────────────────
print("=" * 60)
print("ETAPA 1 — Aquisição de dados")
print("=" * 60)

os.makedirs("dados/dataset1", exist_ok=True)
os.makedirs("dados/dataset2", exist_ok=True)

print("Baixando Dataset 1 (Spotify Tracks — features de áudio)...")
kaggle.api.dataset_download_files(
    "maharshipandya/-spotify-tracks-dataset",
    path="dados/dataset1", unzip=True
)

print("Baixando Dataset 2 (Spotify Charts — performance global)...")
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
        print(f"  {label} / {arq}: {len(df):,} registros | {df.shape[1]} colunas")
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

df_tracks = ler_csvs("dados/dataset1", "DS1-Tracks")
df_charts = ler_csvs("dados/dataset2", "DS2-Charts")

print(f"\nTotal Tracks : {len(df_tracks):,} registros")
print(f"Total Charts : {len(df_charts):,} registros")

# ─────────────────────────────────────────────────────────
# 2. INTEGRAÇÃO DE DADOS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 2 — Integração de dados")
print("=" * 60)

# Normaliza nomes de colunas
df_tracks.columns = df_tracks.columns.str.strip().str.lower().str.replace(" ", "_")
df_charts.columns = df_charts.columns.str.strip().str.lower().str.replace(" ", "_")

print("Colunas Tracks :", df_tracks.columns.tolist())
print("Colunas Charts :", df_charts.columns.tolist())

# ── Prepara chave de merge ────────────────────────────────
# Tracks: track_name + artists
# Charts: title + artist
def normalizar_texto(serie):
    return (serie
            .astype(str)
            .str.lower()
            .str.strip()
            .str.replace(r"[^\w\s]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True))

df_tracks["_chave"] = normalizar_texto(df_tracks["track_name"])
df_charts["_chave"] = normalizar_texto(df_charts["title"])

# Agrega charts por música: streams totais, melhor posição, países, datas
print("Agregando charts por música...")
charts_agg = df_charts.groupby("_chave").agg(
    streams_total   = ("streams",  "sum"),
    streams_media   = ("streams",  "mean"),
    melhor_posicao  = ("rank",     "min"),
    aparicoes_chart = ("rank",     "count"),
    paises_chart    = ("region",   "nunique"),
    primeira_data   = ("date",     "min"),
    ultima_data     = ("date",     "max"),
).reset_index()

# Top200 vs Viral50 (se existir coluna chart)
if "chart" in df_charts.columns:
    charts_tipo = df_charts.groupby(["_chave", "chart"]).size().unstack(fill_value=0).reset_index()
    charts_tipo.columns = ["_chave"] + [f"chart_{c}" for c in charts_tipo.columns[1:]]
    charts_agg = charts_agg.merge(charts_tipo, on="_chave", how="left")

print(f"Músicas únicas nos charts: {len(charts_agg):,}")

# Merge tracks + charts agregado
df = df_tracks.merge(charts_agg, on="_chave", how="left")
print(f"Após merge: {len(df):,} registros")

# Flag: música chegou ou não aos charts
df["chegou_ao_chart"] = df["streams_total"].notna()
pct_charted = df["chegou_ao_chart"].mean() * 100
print(f"Músicas que chegaram aos charts: {pct_charted:.1f}%")

# Remove colunas auxiliares
df.drop(columns=["_chave", "arquivo_origem"], inplace=True, errors="ignore")

# ─────────────────────────────────────────────────────────
# 3. LIMPEZA E TRATAMENTO
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 3 — Limpeza e tratamento")
print("=" * 60)

# Remove colunas inúteis
colunas_remover = [c for c in df.columns if c.startswith("unnamed")]
df.drop(columns=colunas_remover, inplace=True, errors="ignore")

# Nulos numéricos — mediana
for col in df.select_dtypes(include=[np.number]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].median(), inplace=True)

# Nulos texto
for col in df.select_dtypes(include=["object"]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna("Desconhecido", inplace=True)

# Duplicatas
antes = len(df)
df.drop_duplicates(subset=["track_id"], inplace=True)
print(f"Duplicatas removidas: {antes - len(df):,}")

# Consistência
if "duration_ms" in df.columns:
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
if "popularity" in df.columns:
    df = df[(df["popularity"] >= 0) & (df["popularity"] <= 100)]

print(f"Dataset limpo: {len(df):,} registros")

# ─────────────────────────────────────────────────────────
# 4. TRANSFORMAÇÃO E NOVAS VARIÁVEIS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 4 — Transformação e novas variáveis")
print("=" * 60)

# Duração em minutos
if "duration_ms" in df.columns:
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)

# Faixa de popularidade
if "popularity" in df.columns:
    df["faixa_popularidade"] = pd.cut(
        df["popularity"],
        bins=[0, 25, 50, 75, 100],
        labels=["Baixa", "Média", "Alta", "Viral"],
        include_lowest=True
    )

# Humor pela valência
if "valence" in df.columns:
    df["humor"] = pd.cut(
        df["valence"],
        bins=[0, 0.33, 0.66, 1.0],
        labels=["Melancólico", "Neutro", "Alegre"],
        include_lowest=True
    )

# Faixa de streams
if "streams_total" in df.columns:
    df["streams_total"] = pd.to_numeric(df["streams_total"], errors="coerce").fillna(0)
    df["faixa_streams"] = pd.cut(
        df["streams_total"],
        bins=[-1, 0, 1e7, 1e8, 1e9, float("inf")],
        labels=["Sem chart", "< 10M", "10M–100M", "100M–1B", "> 1B"]
    )

# Vocal vs Instrumental
if "instrumentalness" in df.columns:
    df["tipo_faixa"] = np.where(df["instrumentalness"] >= 0.5, "Instrumental", "Vocal")

# Ano dos charts
if "primeira_data" in df.columns:
    df["ano_chart"] = pd.to_datetime(df["primeira_data"], errors="coerce").dt.year

# Score dança × energia
if "danceability" in df.columns and "energy" in df.columns:
    df["score_danca_energia"] = (df["danceability"] * df["energy"]).round(4)

# ── TRADUÇÃO DAS COLUNAS ─────────────────────────────────
traducao = {
    "track_id":           "id_musica",
    "track_name":         "nome_musica",
    "artists":            "artistas",
    "album_name":         "album",
    "track_genre":        "genero",
    "popularity":         "popularidade",
    "duration_ms":        "duracao_ms",
    "duration_min":       "duracao_min",
    "explicit":           "explicito",
    "danceability":       "dancabilidade",
    "energy":             "energia",
    "key":                "tom",
    "loudness":           "volume",
    "mode":               "modo",
    "speechiness":        "fala",
    "acousticness":       "acustica",
    "instrumentalness":   "instrumental",
    "liveness":           "ao_vivo",
    "valence":            "valencia",
    "tempo":              "bpm",
    "time_signature":     "compasso",
    "streams_total":      "streams_total",
    "streams_media":      "streams_media",
    "melhor_posicao":     "melhor_posicao",
    "aparicoes_chart":    "aparicoes_chart",
    "paises_chart":       "paises_chart",
    "chegou_ao_chart":    "chegou_ao_chart",
    "faixa_popularidade": "faixa_popularidade",
    "faixa_streams":      "faixa_streams",
    "score_danca_energia":"score_danca_energia",
    "tipo_faixa":         "tipo_faixa",
    "humor":              "humor",
    "ano_chart":          "ano_chart",
}
df.rename(columns={k: v for k, v in traducao.items() if k in df.columns}, inplace=True)

print("Colunas finais:", df.columns.tolist())

# Agregação por gênero
col_genero = "genero" if "genero" in df.columns else None
if col_genero:
    agg_cols = {"total_musicas": (col_genero, "count")}
    if "popularidade"    in df.columns: agg_cols["popularidade_media"]  = ("popularidade",    "mean")
    if "dancabilidade"   in df.columns: agg_cols["dancabilidade_media"] = ("dancabilidade",   "mean")
    if "energia"         in df.columns: agg_cols["energia_media"]       = ("energia",         "mean")
    if "streams_total"   in df.columns: agg_cols["streams_total"]       = ("streams_total",   "sum")
    if "melhor_posicao"  in df.columns: agg_cols["melhor_posicao"]      = ("melhor_posicao",  "min")
    if "paises_chart"    in df.columns: agg_cols["paises_chart_media"]  = ("paises_chart",    "mean")

    agg = df.groupby(col_genero).agg(**agg_cols).round(3).sort_values("total_musicas", ascending=False)
    agg.to_csv("dados/agg_por_genero.csv")
    print("Salvo: dados/agg_por_genero.csv")

# ─────────────────────────────────────────────────────────
# 5. ANÁLISE EXPLORATÓRIA + INSIGHTS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 5 — Análise Exploratória")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Análise Exploratória — Spotify Tracks + Charts", fontsize=16, fontweight="bold")

# 1. Distribuição de popularidade
if "popularidade" in df.columns:
    df["popularidade"].hist(bins=30, ax=axes[0,0], color="#1DB954", edgecolor="white")
    axes[0,0].set_title("Distribuição de Popularidade")

# 2. Músicas que chegaram vs não chegaram aos charts
if "chegou_ao_chart" in df.columns:
    df["chegou_ao_chart"].value_counts().rename({True:"No chart", False:"Sem chart"}).plot(
        kind="bar", ax=axes[0,1], color=["#1DB954","#444"], edgecolor="white")
    axes[0,1].set_title("Faixas nos Charts vs Fora dos Charts")
    axes[0,1].tick_params(axis="x", rotation=0)

# 3. Streams totais por gênero (top 10)
if col_genero and "streams_total" in df.columns:
    top_streams = df.groupby(col_genero)["streams_total"].sum().sort_values(ascending=False).head(10)
    top_streams.plot(kind="barh", ax=axes[0,2], color="#1DB954")
    axes[0,2].set_title("Top 10 Gêneros por Streams Totais")
    axes[0,2].invert_yaxis()

# 4. Popularidade: músicas nos charts vs fora
if "chegou_ao_chart" in df.columns and "popularidade" in df.columns:
    df.boxplot(column="popularidade", by="chegou_ao_chart", ax=axes[1,0],
               patch_artist=True, boxprops=dict(facecolor="#1DB954", alpha=0.7))
    axes[1,0].set_title("Popularidade: chart vs sem chart")
    axes[1,0].set_xlabel("")
    plt.sca(axes[1,0])
    plt.title("Popularidade: chart vs sem chart")

# 5. Humor × streams médios
if "humor" in df.columns and "streams_total" in df.columns:
    humor_streams = df[df["streams_total"] > 0].groupby("humor")["streams_total"].median()
    humor_streams.plot(kind="bar", ax=axes[1,1], color=["#6fa8dc","#6aa84f","#f59e0b"], edgecolor="white")
    axes[1,1].set_title("Streams Medianos por Humor")
    axes[1,1].tick_params(axis="x", rotation=0)

# 6. Correlação features de áudio
features_pt = [c for c in ["dancabilidade","energia","volume","fala",
                             "acustica","instrumental","ao_vivo","valencia","bpm"]
               if c in df.columns]
if len(features_pt) >= 3:
    corr = df[features_pt].corr()
    sns.heatmap(corr, ax=axes[1,2], cmap="RdYlGn", center=0,
                annot=True, fmt=".1f", annot_kws={"size":7},
                linewidths=0.5, cbar=False)
    axes[1,2].set_title("Correlação entre Features de Áudio")
    axes[1,2].tick_params(axis="x", rotation=45, labelsize=8)
    axes[1,2].tick_params(axis="y", labelsize=8)

plt.tight_layout()
plt.savefig("dados/analise_exploratoria.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico salvo: dados/analise_exploratoria.png")

# ── INSIGHTS ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("INSIGHTS")
print("=" * 60)

if "popularidade" in df.columns:
    print(f"[1] Popularidade média geral: {df['popularidade'].mean():.1f}/100")

if "chegou_ao_chart" in df.columns:
    n_chart = df["chegou_ao_chart"].sum()
    print(f"[2] Músicas nos charts: {n_chart:,} ({n_chart/len(df)*100:.1f}% do catálogo)")

if "chegou_ao_chart" in df.columns and "popularidade" in df.columns:
    pop_chart     = df[df["chegou_ao_chart"]]["popularidade"].mean()
    pop_sem_chart = df[~df["chegou_ao_chart"]]["popularidade"].mean()
    print(f"[3] Popularidade média — no chart: {pop_chart:.1f} | sem chart: {pop_sem_chart:.1f}")

if col_genero and "streams_total" in df.columns:
    top_genero = df.groupby(col_genero)["streams_total"].sum().idxmax()
    print(f"[4] Gênero com mais streams: {top_genero}")

if "humor" in df.columns and "streams_total" in df.columns:
    humor_top = df[df["streams_total"] > 0].groupby("humor")["streams_total"].median().idxmax()
    print(f"[5] Humor com maior mediana de streams: {humor_top}")

if "tipo_faixa" in df.columns and "streams_total" in df.columns:
    voc  = df[(df["tipo_faixa"] == "Vocal")        & (df["streams_total"] > 0)]["streams_total"].median()
    inst = df[(df["tipo_faixa"] == "Instrumental") & (df["streams_total"] > 0)]["streams_total"].median()
    print(f"[6] Streams medianos — Vocal: {voc:,.0f} | Instrumental: {inst:,.0f}")

if "explicito" in df.columns and "streams_total" in df.columns:
    exp     = df[(df["explicito"] == True)  & (df["streams_total"] > 0)]["streams_total"].median()
    nao_exp = df[(df["explicito"] == False) & (df["streams_total"] > 0)]["streams_total"].median()
    print(f"[7] Streams medianos — Explícito: {exp:,.0f} | Não explícito: {nao_exp:,.0f}")

if "paises_chart" in df.columns:
    print(f"[8] Média de países nos charts por música: {df['paises_chart'].mean():.1f}")

# Salva dataset final
df.to_csv("dados/spotify_final.csv", index=False)
print(f"\nDataset final salvo: dados/spotify_final.csv ({len(df):,} registros)")
print("Pipeline concluído!")
