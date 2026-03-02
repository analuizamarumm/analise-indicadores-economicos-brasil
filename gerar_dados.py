"""
Geração de dados sintéticos realistas dos indicadores econômicos brasileiros.
Fonte de referência: BCB (Banco Central do Brasil), IBGE.
Em um cenário real, você usaria a API do BCB ou bibliotecas como python-bcb.

Este script gera dados que simulam os indicadores reais para fins de portfólio.
"""

import pandas as pd
import numpy as np
from datetime import datetime

np.random.seed(42)


def gerar_dados_economicos():
    """Gera dataset mensal de indicadores econômicos do Brasil (2015-2024)."""

    datas = pd.date_range(start="2015-01-01", end="2024-12-01", freq="MS")
    n = len(datas)

    # --- IPCA (Inflação mensal, %) ---
    # Média histórica ~0.4% ao mês, com picos em 2015-2016 e 2021-2022
    ipca_base = np.random.normal(0.40, 0.15, n)
    for i, d in enumerate(datas):
        if d.year in [2015, 2016]:
            ipca_base[i] += np.random.uniform(0.15, 0.40)
        elif d.year in [2021, 2022]:
            ipca_base[i] += np.random.uniform(0.20, 0.50)
        elif d.year in [2023, 2024]:
            ipca_base[i] -= np.random.uniform(0.05, 0.15)
    ipca_mensal = np.clip(ipca_base, -0.30, 1.60)

    # IPCA acumulado 12 meses
    ipca_12m = []
    for i in range(n):
        if i < 12:
            acum = ((1 + ipca_mensal[:i+1] / 100).prod() - 1) * 100
        else:
            acum = ((1 + ipca_mensal[i-11:i+1] / 100).prod() - 1) * 100
        ipca_12m.append(round(acum, 2))

    # --- Taxa Selic (% ao ano) ---
    selic_valores = {
        2015: 13.75, 2016: 14.25, 2017: 10.00, 2018: 6.50,
        2019: 4.50, 2020: 2.00, 2021: 9.25, 2022: 13.75,
        2023: 12.25, 2024: 10.50
    }
    selic = []
    for d in datas:
        base = selic_valores[d.year]
        variacao = np.random.uniform(-0.25, 0.25)
        # Simula transições graduais entre anos
        if d.month <= 3:
            peso_anterior = (4 - d.month) / 6
            ano_anterior = d.year - 1 if d.year > 2015 else 2015
            base = base * (1 - peso_anterior) + selic_valores[ano_anterior] * peso_anterior
        selic.append(round(base + variacao, 2))

    # --- Câmbio USD/BRL ---
    cambio_base = {
        2015: 3.35, 2016: 3.50, 2017: 3.20, 2018: 3.65,
        2019: 4.00, 2020: 5.20, 2021: 5.40, 2022: 5.15,
        2023: 4.95, 2024: 5.05
    }
    cambio = []
    for i, d in enumerate(datas):
        base = cambio_base[d.year]
        tendencia = np.sin(d.month * np.pi / 12) * 0.15
        ruido = np.random.normal(0, 0.10)
        cambio.append(round(base + tendencia + ruido, 4))

    # --- Taxa de Desemprego (%) ---
    desemp_base = {
        2015: 8.5, 2016: 11.5, 2017: 12.7, 2018: 12.3,
        2019: 11.9, 2020: 13.5, 2021: 14.2, 2022: 9.8,
        2023: 8.0, 2024: 7.0
    }
    desemprego = []
    for d in datas:
        base = desemp_base[d.year]
        sazonalidade = np.sin((d.month - 3) * np.pi / 6) * 0.8
        ruido = np.random.normal(0, 0.3)
        desemprego.append(round(max(base + sazonalidade + ruido, 4.0), 1))

    # --- PIB Trimestral (variação % em relação ao trimestre anterior) ---
    pib_trimestral = []
    for d in datas:
        if d.year == 2015:
            base_pib = -0.8
        elif d.year == 2016:
            base_pib = -0.5
        elif d.year in [2017, 2018, 2019]:
            base_pib = 0.3
        elif d.year == 2020:
            base_pib = -1.5 if d.month <= 6 else 1.8
        elif d.year == 2021:
            base_pib = 1.0
        elif d.year in [2022, 2023]:
            base_pib = 0.5
        else:
            base_pib = 0.6
        ruido = np.random.normal(0, 0.3)
        pib_trimestral.append(round(base_pib + ruido, 2))

    # --- Montar DataFrame ---
    df = pd.DataFrame({
        "data": datas,
        "ipca_mensal_pct": np.round(ipca_mensal, 2),
        "ipca_acumulado_12m_pct": ipca_12m,
        "selic_aa_pct": selic,
        "cambio_usd_brl": cambio,
        "taxa_desemprego_pct": desemprego,
        "pib_variacao_trimestral_pct": pib_trimestral
    })

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["trimestre"] = df["data"].dt.quarter

    return df


if __name__ == "__main__":
    df = gerar_dados_economicos()
    df.to_csv("data/indicadores_economicos_brasil_2015_2024.csv", index=False)
    print(f"✅ Dataset gerado com {len(df)} registros")
    print(f"📅 Período: {df['data'].min().strftime('%Y-%m')} a {df['data'].max().strftime('%Y-%m')}")
    print(f"\nPrimeiras linhas:")
    print(df.head().to_string())
    print(f"\nEstatísticas descritivas:")
    print(df.describe().round(2).to_string())
