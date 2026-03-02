-- ============================================================
-- CONSULTAS SQL — Indicadores Econômicos do Brasil (2015-2024)
-- ============================================================
-- Estas queries podem ser executadas em SQLite, PostgreSQL ou MySQL
-- após importar o CSV para uma tabela chamada 'indicadores'.
--
-- Para testar localmente com SQLite:
-- sqlite3 economia.db
-- .mode csv
-- .import data/indicadores_economicos_brasil_2015_2024.csv indicadores


-- ============================================================
-- 1. VISÃO GERAL: Resumo estatístico por ano
-- ============================================================
SELECT
    ano,
    ROUND(SUM(ipca_mensal_pct), 2)          AS ipca_anual_pct,
    ROUND(AVG(selic_aa_pct), 2)             AS selic_media,
    ROUND(AVG(cambio_usd_brl), 2)          AS cambio_medio,
    ROUND(MIN(cambio_usd_brl), 2)          AS cambio_minimo,
    ROUND(MAX(cambio_usd_brl), 2)          AS cambio_maximo,
    ROUND(AVG(taxa_desemprego_pct), 1)      AS desemprego_medio
FROM indicadores
GROUP BY ano
ORDER BY ano;


-- ============================================================
-- 2. RANKING: Anos com maior inflação acumulada
-- ============================================================
SELECT
    ano,
    ROUND(SUM(ipca_mensal_pct), 2) AS ipca_anual,
    CASE
        WHEN SUM(ipca_mensal_pct) > 6 THEN '🔴 Acima da meta'
        WHEN SUM(ipca_mensal_pct) > 4.5 THEN '🟡 No limite'
        ELSE '🟢 Dentro da meta'
    END AS status_meta
FROM indicadores
GROUP BY ano
ORDER BY ipca_anual DESC;


-- ============================================================
-- 3. ANÁLISE TRIMESTRAL: Desempenho do PIB
-- ============================================================
SELECT
    ano,
    trimestre,
    ROUND(AVG(pib_variacao_trimestral_pct), 2) AS pib_medio_trim,
    CASE
        WHEN AVG(pib_variacao_trimestral_pct) > 0 THEN 'Crescimento'
        ELSE 'Retração'
    END AS situacao
FROM indicadores
GROUP BY ano, trimestre
ORDER BY ano, trimestre;


-- ============================================================
-- 4. CORRELAÇÃO PRÁTICA: Meses onde Selic subiu e IPCA caiu
-- ============================================================
WITH mensal AS (
    SELECT
        data,
        ano,
        mes,
        selic_aa_pct,
        ipca_mensal_pct,
        LAG(selic_aa_pct) OVER (ORDER BY data) AS selic_anterior,
        LAG(ipca_mensal_pct) OVER (ORDER BY data) AS ipca_anterior
    FROM indicadores
)
SELECT
    data,
    ROUND(selic_aa_pct, 2)    AS selic_atual,
    ROUND(selic_anterior, 2)   AS selic_anterior,
    ROUND(ipca_mensal_pct, 2)  AS ipca_atual,
    ROUND(ipca_anterior, 2)    AS ipca_anterior
FROM mensal
WHERE selic_aa_pct > selic_anterior
  AND ipca_mensal_pct < ipca_anterior
ORDER BY data;


-- ============================================================
-- 5. VOLATILIDADE: Desvio padrão do câmbio por semestre
-- ============================================================
SELECT
    ano,
    CASE WHEN mes <= 6 THEN '1º Semestre' ELSE '2º Semestre' END AS semestre,
    ROUND(AVG(cambio_usd_brl), 4)                                AS cambio_medio,
    ROUND(MIN(cambio_usd_brl), 4)                                AS cambio_min,
    ROUND(MAX(cambio_usd_brl), 4)                                AS cambio_max,
    ROUND(MAX(cambio_usd_brl) - MIN(cambio_usd_brl), 4)          AS amplitude
FROM indicadores
GROUP BY ano, CASE WHEN mes <= 6 THEN '1º Semestre' ELSE '2º Semestre' END
ORDER BY ano, semestre;


-- ============================================================
-- 6. CENÁRIOS ECONÔMICOS: Classificação dos períodos
-- ============================================================
SELECT
    ano,
    ROUND(SUM(ipca_mensal_pct), 2) AS inflacao_anual,
    ROUND(AVG(taxa_desemprego_pct), 1) AS desemprego_medio,
    ROUND(AVG(pib_variacao_trimestral_pct), 2) AS pib_medio,
    CASE
        WHEN AVG(pib_variacao_trimestral_pct) < 0 AND SUM(ipca_mensal_pct) > 6
            THEN '⚠️  Estagflação'
        WHEN AVG(pib_variacao_trimestral_pct) < 0
            THEN '📉 Recessão'
        WHEN SUM(ipca_mensal_pct) > 6
            THEN '🔥 Crescimento inflacionário'
        WHEN AVG(pib_variacao_trimestral_pct) > 0 AND SUM(ipca_mensal_pct) < 4.5
            THEN '✅ Equilíbrio'
        ELSE '📊 Transição'
    END AS cenario_economico
FROM indicadores
GROUP BY ano
ORDER BY ano;


-- ============================================================
-- 7. MOVING AVERAGE: Média móvel de 3 meses do IPCA
-- ============================================================
SELECT
    data,
    ipca_mensal_pct,
    ROUND(AVG(ipca_mensal_pct) OVER (
        ORDER BY data
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS media_movel_3m,
    ROUND(AVG(ipca_mensal_pct) OVER (
        ORDER BY data
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ), 2) AS media_movel_6m
FROM indicadores
ORDER BY data;
