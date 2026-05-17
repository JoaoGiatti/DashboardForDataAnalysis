"""
=============================================================
  Pipeline de Ciência de Dados — Spotify Tracks
  Datasets: thedevastator/spotify-tracks-genre-dataset
            maharshipandya/-spotify-tracks-dataset
=============================================================
Etapas:
  1. Aquisição via Kaggle API
  2. Integração (merge + consolidação)
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

print("Baixando Dataset 1 (Genre Dataset)...")
kaggle.api.dataset_download_files(
    "thedevastator/spotify-tracks-genre-dataset",
    path="dados/dataset1", unzip=True
)

print("Baixando Dataset 2 (Tracks Dataset)...")
kaggle.api.dataset_download_files(
    "maharshipandya/-spotify-tracks-dataset",
    path="dados/dataset2", unzip=True
)

def ler_csvs(pasta, label):
    arquivos = [f for f in os.listdir(pasta) if f.endswith(".csv")]
    dfs = []
    for arq in arquivos:
        df = pd.read_csv(os.path.join(pasta, arq))
        df["arquivo_origem"] = arq
        print(f"  {label} / {arq}: {len(df):,} registros | {df.shape[1]} colunas")
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

df1 = ler_csvs("dados/dataset1", "DS1")
df2 = ler_csvs("dados/dataset2", "DS2")

print(f"\nTotal DS1: {len(df1):,} | Total DS2: {len(df2):,}")

# ─────────────────────────────────────────────────────────
# 2. INTEGRAÇÃO DE DADOS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 2 — Integração de dados")
print("=" * 60)

df1.columns = df1.columns.str.strip().str.lower().str.replace(" ", "_")
df2.columns = df2.columns.str.strip().str.lower().str.replace(" ", "_")

if "track_id" in df1.columns and "track_id" in df2.columns:
    print("Merge por track_id (outer)...")
    df = pd.merge(df1, df2, on="track_id", how="outer", suffixes=("_ds1", "_ds2"))
    print(f"Após merge: {len(df):,} registros | {df.shape[1]} colunas")

    # Consolida colunas duplicadas (_ds1 / _ds2)
    colunas_base = list(dict.fromkeys(
        c.replace("_ds1", "").replace("_ds2", "")
        for c in df.columns if "_ds1" in c or "_ds2" in c
    ))
    for col in colunas_base:
        c1, c2 = f"{col}_ds1", f"{col}_ds2"
        if c1 in df.columns and c2 in df.columns:
            df[col] = df[c1].combine_first(df[c2])
            df.drop(columns=[c1, c2], inplace=True)
        elif c1 in df.columns:
            df.rename(columns={c1: col}, inplace=True)
        elif c2 in df.columns:
            df.rename(columns={c2: col}, inplace=True)
    print("Colunas consolidadas com sucesso.")
else:
    df1["fonte"] = "genre_dataset"
    df2["fonte"] = "tracks_dataset"
    df = pd.concat([df1, df2], ignore_index=True)
    print(f"Concat realizado: {len(df):,} registros")

# ─────────────────────────────────────────────────────────
# 3. LIMPEZA E TRATAMENTO
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 3 — Limpeza e tratamento")
print("=" * 60)

# Remove colunas inúteis
colunas_remover = [c for c in df.columns if c.startswith("unnamed") or c == "arquivo_origem"]
df.drop(columns=colunas_remover, inplace=True, errors="ignore")
print(f"Colunas removidas: {colunas_remover}")

# Nulos
for col in df.select_dtypes(include=[np.number]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].median(), inplace=True)

for col in df.select_dtypes(include=["object"]).columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna("Desconhecido", inplace=True)

# Duplicatas
antes = len(df)
df.drop_duplicates(inplace=True)
print(f"Duplicatas removidas: {antes - len(df):,}")

# Consistência
if "duration_ms" in df.columns:
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
if "popularity" in df.columns:
    df = df[(df["popularity"] >= 0) & (df["popularity"] <= 100)]

print(f"Dataset limpo: {len(df):,} registros")

# ─────────────────────────────────────────────────────────
# 4. TRANSFORMAÇÃO + TRADUÇÃO
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 4 — Transformação e tradução")
print("=" * 60)

# Novas variáveis
if "duration_ms" in df.columns:
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)

if "popularity" in df.columns:
    df["faixa_popularidade"] = pd.cut(
        df["popularity"],
        bins=[0, 25, 50, 75, 100],
        labels=["Baixa", "Média", "Alta", "Viral"],
        include_lowest=True
    )

if "danceability" in df.columns and "energy" in df.columns:
    df["score_danca_energia"] = (df["danceability"] * df["energy"]).round(4)

if "valence" in df.columns:
    df["humor"] = pd.cut(
        df["valence"],
        bins=[0, 0.33, 0.66, 1.0],
        labels=["Melancólico", "Neutro", "Alegre"],
        include_lowest=True
    )

# Coluna de ano (se existir data)
col_data = next((c for c in ["track_album_release_date", "release_year", "year"] if c in df.columns), None)
if col_data:
    df["ano_lancamento"] = pd.to_datetime(df[col_data], errors="coerce").dt.year
    df["decada"] = (df["ano_lancamento"] // 10 * 10).astype("Int64").astype(str) + "s"

# Z-score das features de áudio
features_audio = [c for c in ["danceability","energy","loudness","speechiness",
                               "acousticness","instrumentalness","liveness","valence","tempo"]
                  if c in df.columns]
for feat in features_audio:
    std = df[feat].std()
    if std > 0:
        df[f"{feat}_z"] = ((df[feat] - df[feat].mean()) / std).round(4)

# ── TRADUÇÃO DAS COLUNAS ──────────────────────────────────
traducao = {
    "track_id":           "id_musica",
    "track_name":         "nome_musica",
    "artists":            "artistas",
    "album_name":         "album",
    "track_genre":        "genero",
    "genre":              "genero",
    "playlist_genre":     "genero",
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
    "faixa_popularidade": "faixa_popularidade",
    "score_danca_energia":"score_danca_energia",
    "humor":              "humor",
    "ano_lancamento":     "ano_lancamento",
    "decada":             "decada",
}

# Aplica só as que existem
df.rename(columns={k: v for k, v in traducao.items() if k in df.columns}, inplace=True)

# Remove colunas _z (auxiliares) e outras residuais sem uso
colunas_z = [c for c in df.columns if c.endswith("_z")]
df.drop(columns=colunas_z, inplace=True, errors="ignore")

print("Colunas finais:", df.columns.tolist())

# Agregação por gênero (salva auxiliar)
col_genero = "genero" if "genero" in df.columns else None
if col_genero:
    agg = df.groupby(col_genero).agg(
        total_musicas=(col_genero, "count"),
        popularidade_media=("popularidade", "mean") if "popularidade" in df.columns else (col_genero, "count"),
        dancabilidade_media=("dancabilidade", "mean") if "dancabilidade" in df.columns else (col_genero, "count"),
        energia_media=("energia", "mean") if "energia" in df.columns else (col_genero, "count"),
    ).dropna(axis=1).round(3).sort_values("total_musicas", ascending=False)
    agg.to_csv("dados/agg_por_genero.csv")
    print("Salvo: dados/agg_por_genero.csv")

# ─────────────────────────────────────────────────────────
# 5. ANÁLISE EXPLORATÓRIA + INSIGHTS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ETAPA 5 — Análise Exploratória")
print("=" * 60)

features_pt = [c for c in ["dancabilidade","energia","volume","fala",
                             "acustica","instrumental","ao_vivo","valencia","bpm"]
               if c in df.columns]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Análise Exploratória — Spotify Tracks", fontsize=16, fontweight="bold")

if "popularidade" in df.columns:
    df["popularidade"].hist(bins=30, ax=axes[0,0], color="#1DB954", edgecolor="white")
    axes[0,0].set_title("Distribuição de Popularidade")

if "faixa_popularidade" in df.columns:
    df["faixa_popularidade"].value_counts().plot(kind="bar", ax=axes[0,1],
        color=["#cfe2f3","#6fa8dc","#1c6ea4","#0b3d91"], edgecolor="white")
    axes[0,1].set_title("Músicas por Faixa de Popularidade")
    axes[0,1].tick_params(axis="x", rotation=0)

if "dancabilidade" in df.columns and "energia" in df.columns:
    s = df.sample(min(3000, len(df)), random_state=42)
    axes[0,2].scatter(s["dancabilidade"], s["energia"], alpha=0.3, s=10, color="#1DB954")
    axes[0,2].set_title("Dançabilidade × Energia")

if col_genero:
    df[col_genero].value_counts().head(10).plot(kind="barh", ax=axes[1,0], color="#1DB954")
    axes[1,0].set_title("Top 10 Gêneros por Quantidade")
    axes[1,0].invert_yaxis()

if col_genero and "duracao_min" in df.columns:
    df.groupby(col_genero)["duracao_min"].mean().sort_values(ascending=False).head(8).plot(
        kind="bar", ax=axes[1,1], color="#0b3d91", edgecolor="white")
    axes[1,1].set_title("Duração Média por Gênero (min)")
    axes[1,1].tick_params(axis="x", rotation=45)

if len(features_pt) >= 3:
    corr = df[features_pt].corr()
    sns.heatmap(corr, ax=axes[1,2], cmap="RdYlGn", center=0,
                annot=True, fmt=".1f", annot_kws={"size": 7}, linewidths=0.5, cbar=False)
    axes[1,2].set_title("Correlação entre Features de Áudio")
    axes[1,2].tick_params(axis="x", rotation=45, labelsize=8)
    axes[1,2].tick_params(axis="y", labelsize=8)

plt.tight_layout()
plt.savefig("dados/analise_exploratoria.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico salvo: dados/analise_exploratoria.png")

# Insights
print("\n" + "=" * 60)
print("INSIGHTS")
print("=" * 60)

if "popularidade" in df.columns:
    pop_media = df["popularidade"].mean()
    pop_viral = (df["faixa_popularidade"] == "Viral").sum() if "faixa_popularidade" in df.columns else 0
    print(f"[1] Popularidade média: {pop_media:.1f}/100")
    print(f"    Músicas virais: {pop_viral:,} ({pop_viral/len(df)*100:.1f}%)")

if "dancabilidade" in df.columns and "energia" in df.columns:
    corr_de = df["dancabilidade"].corr(df["energia"])
    print(f"[2] Correlação Dançabilidade × Energia: {corr_de:.3f}")

if col_genero and "popularidade" in df.columns:
    top = df.groupby(col_genero)["popularidade"].mean().idxmax()
    print(f"[3] Gênero mais popular: {top}")

if "duracao_min" in df.columns:
    print(f"[4] Duração mediana: {df['duracao_min'].median():.2f} min")

if "humor" in df.columns:
    humor_dist = df["humor"].value_counts(normalize=True).round(3) * 100
    print(f"[5] Distribuição de humor:\n{humor_dist.to_string()}")

# Salva
df.to_csv("dados/spotify_final.csv", index=False)
print(f"\nDataset final: dados/spotify_final.csv ({len(df):,} registros)")
print("Pipeline concluído!")