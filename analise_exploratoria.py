"""
Análise Exploratória dos Indicadores Econômicos do Brasil (2015-2024)
=====================================================================
Projeto de portfólio para análise de dados.
Autor: Ana Luiza Marum
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import warnings

warnings.filterwarnings("ignore")

# Configurações de estilo
plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#fafafa",
    "text.color": "#fafafa",
    "xtick.color": "#cccccc",
    "ytick.color": "#cccccc",
    "grid.color": "#1e2530",
    "font.family": "sans-serif",
    "font.size": 11,
})

# Paleta de cores
CORES = {
    "azul": "#4fc3f7",
    "vermelho": "#ef5350",
    "verde": "#66bb6a",
    "amarelo": "#ffd54f",
    "roxo": "#ab47bc",
    "laranja": "#ffa726",
    "cinza": "#90a4ae",
}


def carregar_dados(caminho: str = "data/indicadores_economicos_brasil_2015_2024.csv") -> pd.DataFrame:
    """Carrega e prepara o dataset."""
    df = pd.read_csv(caminho, parse_dates=["data"])
    df = df.sort_values("data").reset_index(drop=True)
    return df


def analise_estatistica(df: pd.DataFrame) -> None:
    """Imprime resumo estatístico dos indicadores."""
    indicadores = {
        "IPCA Mensal (%)": "ipca_mensal_pct",
        "IPCA Acum. 12m (%)": "ipca_acumulado_12m_pct",
        "Selic (% a.a.)": "selic_aa_pct",
        "Câmbio USD/BRL": "cambio_usd_brl",
        "Desemprego (%)": "taxa_desemprego_pct",
        "PIB Trim. (%)": "pib_variacao_trimestral_pct",
    }

    print("=" * 70)
    print("  RESUMO ESTATÍSTICO DOS INDICADORES ECONÔMICOS (2015-2024)")
    print("=" * 70)

    for nome, coluna in indicadores.items():
        serie = df[coluna]
        print(f"\n📊 {nome}")
        print(f"   Média: {serie.mean():.2f} | Mediana: {serie.median():.2f}")
        print(f"   Mín: {serie.min():.2f} | Máx: {serie.max():.2f}")
        print(f"   Desvio Padrão: {serie.std():.2f}")
        print(f"   Assimetria: {serie.skew():.2f} | Curtose: {serie.kurtosis():.2f}")


def analise_correlacao(df: pd.DataFrame) -> None:
    """Calcula e exibe a matriz de correlação."""
    colunas = [
        "ipca_mensal_pct", "selic_aa_pct", "cambio_usd_brl",
        "taxa_desemprego_pct", "pib_variacao_trimestral_pct"
    ]
    labels = ["IPCA", "Selic", "Câmbio", "Desemprego", "PIB"]

    corr = df[colunas].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(labels, fontsize=10)

    # Anotar valores
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr.values[i, j]
            color = "white" if abs(val) > 0.5 else "#cccccc"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color=color, fontsize=11, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.tick_params(colors="#cccccc")

    ax.set_title("Matriz de Correlação dos Indicadores", fontsize=14, pad=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig("visualizacoes/01_matriz_correlacao.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico salvo: visualizacoes/01_matriz_correlacao.png")


def grafico_painel_indicadores(df: pd.DataFrame) -> None:
    """Cria painel com a evolução temporal de todos os indicadores."""
    fig = plt.figure(figsize=(16, 14))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)

    configs = [
        ("IPCA Acumulado 12 Meses (%)", "ipca_acumulado_12m_pct", CORES["vermelho"], gs[0, 0]),
        ("Taxa Selic (% a.a.)", "selic_aa_pct", CORES["azul"], gs[0, 1]),
        ("Câmbio USD/BRL", "cambio_usd_brl", CORES["verde"], gs[1, 0]),
        ("Taxa de Desemprego (%)", "taxa_desemprego_pct", CORES["laranja"], gs[1, 1]),
        ("PIB - Variação Trimestral (%)", "pib_variacao_trimestral_pct", CORES["roxo"], gs[2, 0]),
        ("IPCA Mensal (%)", "ipca_mensal_pct", CORES["amarelo"], gs[2, 1]),
    ]

    for titulo, coluna, cor, pos in configs:
        ax = fig.add_subplot(pos)
        ax.plot(df["data"], df[coluna], color=cor, linewidth=1.5, alpha=0.9)
        ax.fill_between(df["data"], df[coluna], alpha=0.1, color=cor)
        ax.set_title(titulo, fontsize=12, fontweight="bold", pad=10)
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(True, alpha=0.3)

        # Linha de referência para PIB
        if "pib" in coluna:
            ax.axhline(y=0, color="#666666", linestyle="--", linewidth=0.8)

    fig.suptitle(
        "Painel de Indicadores Econômicos do Brasil (2015-2024)",
        fontsize=16, fontweight="bold", y=0.98
    )
    plt.savefig("visualizacoes/02_painel_indicadores.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico salvo: visualizacoes/02_painel_indicadores.png")


def grafico_inflacao_vs_selic(df: pd.DataFrame) -> None:
    """Analisa a relação entre IPCA e Selic ao longo do tempo."""
    fig, ax1 = plt.subplots(figsize=(14, 6))

    cor_ipca = CORES["vermelho"]
    cor_selic = CORES["azul"]

    ax1.plot(df["data"], df["ipca_acumulado_12m_pct"], color=cor_ipca,
             linewidth=2, label="IPCA 12m", zorder=3)
    ax1.fill_between(df["data"], df["ipca_acumulado_12m_pct"], alpha=0.1, color=cor_ipca)
    ax1.set_ylabel("IPCA Acumulado 12m (%)", color=cor_ipca, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=cor_ipca)

    ax2 = ax1.twinx()
    ax2.plot(df["data"], df["selic_aa_pct"], color=cor_selic,
             linewidth=2, label="Selic", linestyle="--", zorder=3)
    ax2.set_ylabel("Taxa Selic (% a.a.)", color=cor_selic, fontsize=12)
    ax2.tick_params(axis="y", labelcolor=cor_selic)

    # Meta de inflação (4.5% até 2018, depois 3.75%, 3.5%, 3.25%, 3.0%)
    ax1.axhline(y=4.5, color=CORES["amarelo"], linestyle=":", linewidth=1, alpha=0.7)
    ax1.text(df["data"].iloc[5], 4.8, "Meta ~4.5%", color=CORES["amarelo"], fontsize=9)

    # Destaque: período COVID
    covid_inicio = pd.Timestamp("2020-03-01")
    covid_fim = pd.Timestamp("2020-12-01")
    ax1.axvspan(covid_inicio, covid_fim, alpha=0.08, color="white", label="Período COVID-19")

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.grid(True, alpha=0.2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
               framealpha=0.3, edgecolor="#444444")

    ax1.set_title("Inflação (IPCA) vs Taxa Selic — Política Monetária Brasileira",
                   fontsize=14, fontweight="bold", pad=15)

    plt.savefig("visualizacoes/03_ipca_vs_selic.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico salvo: visualizacoes/03_ipca_vs_selic.png")


def grafico_analise_anual(df: pd.DataFrame) -> None:
    """Compara indicadores médios por ano."""
    resumo_anual = df.groupby("ano").agg({
        "ipca_mensal_pct": "sum",
        "selic_aa_pct": "mean",
        "cambio_usd_brl": "mean",
        "taxa_desemprego_pct": "mean",
    }).round(2)

    resumo_anual.columns = ["IPCA Anual (%)", "Selic Média (%)", "Câmbio Médio", "Desemprego Médio (%)"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # IPCA Anual
    cores_ipca = [CORES["vermelho"] if v > 6 else CORES["amarelo"] if v > 4.5 else CORES["verde"]
                  for v in resumo_anual["IPCA Anual (%)"]]
    axes[0, 0].bar(resumo_anual.index, resumo_anual["IPCA Anual (%)"], color=cores_ipca, alpha=0.85)
    axes[0, 0].axhline(y=4.5, color=CORES["amarelo"], linestyle="--", linewidth=1, alpha=0.7)
    axes[0, 0].set_title("IPCA Acumulado Anual", fontweight="bold")
    for i, v in enumerate(resumo_anual["IPCA Anual (%)"]):
        axes[0, 0].text(resumo_anual.index[i], v + 0.2, f"{v:.1f}%", ha="center", fontsize=8, color="#cccccc")

    # Selic Média
    axes[0, 1].bar(resumo_anual.index, resumo_anual["Selic Média (%)"], color=CORES["azul"], alpha=0.85)
    axes[0, 1].set_title("Selic Média Anual", fontweight="bold")
    for i, v in enumerate(resumo_anual["Selic Média (%)"]):
        axes[0, 1].text(resumo_anual.index[i], v + 0.15, f"{v:.1f}%", ha="center", fontsize=8, color="#cccccc")

    # Câmbio Médio
    axes[1, 0].bar(resumo_anual.index, resumo_anual["Câmbio Médio"], color=CORES["verde"], alpha=0.85)
    axes[1, 0].set_title("Câmbio Médio Anual (USD/BRL)", fontweight="bold")
    for i, v in enumerate(resumo_anual["Câmbio Médio"]):
        axes[1, 0].text(resumo_anual.index[i], v + 0.05, f"R${v:.2f}", ha="center", fontsize=8, color="#cccccc")

    # Desemprego Médio
    axes[1, 1].bar(resumo_anual.index, resumo_anual["Desemprego Médio (%)"], color=CORES["laranja"], alpha=0.85)
    axes[1, 1].set_title("Desemprego Médio Anual", fontweight="bold")
    for i, v in enumerate(resumo_anual["Desemprego Médio (%)"]):
        axes[1, 1].text(resumo_anual.index[i], v + 0.1, f"{v:.1f}%", ha="center", fontsize=8, color="#cccccc")

    for ax in axes.flat:
        ax.grid(True, alpha=0.2, axis="y")
        ax.set_xticks(resumo_anual.index)
        ax.set_xticklabels(resumo_anual.index, rotation=45, fontsize=9)

    fig.suptitle("Comparativo Anual dos Indicadores Econômicos", fontsize=14, fontweight="bold", y=1.0)
    plt.tight_layout()
    plt.savefig("visualizacoes/04_analise_anual.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico salvo: visualizacoes/04_analise_anual.png")


def grafico_volatilidade(df: pd.DataFrame) -> None:
    """Analisa a volatilidade do câmbio com média móvel."""
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["data"], df["cambio_usd_brl"], color=CORES["cinza"], alpha=0.5, linewidth=1, label="Câmbio diário")

    # Médias móveis
    df["mm_3m"] = df["cambio_usd_brl"].rolling(window=3).mean()
    df["mm_6m"] = df["cambio_usd_brl"].rolling(window=6).mean()
    df["mm_12m"] = df["cambio_usd_brl"].rolling(window=12).mean()

    ax.plot(df["data"], df["mm_3m"], color=CORES["azul"], linewidth=1.5, label="MM 3 meses")
    ax.plot(df["data"], df["mm_6m"], color=CORES["amarelo"], linewidth=1.5, label="MM 6 meses")
    ax.plot(df["data"], df["mm_12m"], color=CORES["vermelho"], linewidth=2, label="MM 12 meses")

    # Bandas de Bollinger (20 períodos)
    mm20 = df["cambio_usd_brl"].rolling(window=6).mean()
    std20 = df["cambio_usd_brl"].rolling(window=6).std()
    ax.fill_between(df["data"], mm20 - 2 * std20, mm20 + 2 * std20,
                    alpha=0.08, color=CORES["azul"], label="Banda ±2σ")

    ax.legend(loc="upper left", framealpha=0.3, edgecolor="#444444")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.2)
    ax.set_title("Câmbio USD/BRL — Análise de Tendência e Volatilidade",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("R$ / US$", fontsize=12)

    plt.savefig("visualizacoes/05_volatilidade_cambio.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico salvo: visualizacoes/05_volatilidade_cambio.png")


# ============================================================
#  EXECUÇÃO PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("\n🇧🇷 ANÁLISE DE INDICADORES ECONÔMICOS DO BRASIL (2015-2024)")
    print("=" * 60)

    df = carregar_dados()
    print(f"\n📂 Dataset carregado: {len(df)} registros | {df['data'].min():%Y-%m} a {df['data'].max():%Y-%m}\n")

    # 1. Análise estatística
    analise_estatistica(df)

    # 2. Gráficos
    print("\n\n📈 GERANDO VISUALIZAÇÕES...")
    print("-" * 40)
    analise_correlacao(df)
    grafico_painel_indicadores(df)
    grafico_inflacao_vs_selic(df)
    grafico_analise_anual(df)
    grafico_volatilidade(df)

    print("\n✅ Análise concluída! Verifique a pasta 'visualizacoes/'.")
