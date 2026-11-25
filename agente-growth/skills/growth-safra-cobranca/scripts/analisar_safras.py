#!/usr/bin/env python3
"""Análise de safras (cohorts) de crédito a partir de uma base de parcelas.

Entrada: CSV ou XLSX com UMA LINHA POR PARCELA. Colunas mínimas (os nomes podem ser
mapeados por parâmetro):
  contrato_id      identificador do contrato
  data_originacao  data em que o contrato foi originado
  numero_parcela   1, 2, 3...
  data_vencimento  vencimento da parcela
  data_pagamento   data do pagamento (vazio se não pago)
  valor            valor da parcela
Colunas extras (produtor, nicho, faixa de ticket...) podem ser usadas com --segmento.

Saídas (markdown no terminal + CSVs opcionais em --saida):
  1. Resumo por safra: contratos, valor, FPD (1ª parcela não paga até venc + N dias)
  2. Matriz Over X por mês de vida (MOB): % de contratos com parcela vencida há > X dias
  3. (opcional) FPD e Over X por segmento

Exemplo:
  python analisar_safras.py parcelas.csv --data-ref 2026-11-01 --over 30 --segmento nicho --saida resultados/
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

COLS = ["contrato_id", "data_originacao", "numero_parcela", "data_vencimento", "data_pagamento", "valor"]


def para_data(s: pd.Series) -> pd.Series:
    """Aceita ISO (2026-03-15) ou formato brasileiro (15/03/2026)."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    txt = s.dropna().astype(str).str.strip()
    if txt.empty:
        return pd.to_datetime(s, errors="coerce")
    if txt.str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.5:
        return pd.to_datetime(s, errors="coerce", format="ISO8601")
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def carregar(caminho: str, mapa: dict) -> pd.DataFrame:
    p = Path(caminho)
    df = pd.read_excel(p) if p.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(p, sep=None, engine="python")
    df = df.rename(columns={v: k for k, v in mapa.items() if v})
    faltando = [c for c in COLS if c not in df.columns]
    if faltando:
        sys.exit(f"Colunas ausentes: {faltando}. Colunas encontradas: {list(df.columns)}. "
                 f"Use --col-<nome> para mapear.")
    for c in ("data_originacao", "data_vencimento", "data_pagamento"):
        df[c] = para_data(df[c])
    if df["valor"].dtype == object:
        df["valor"] = (df["valor"].astype(str).str.replace("R$", "", regex=False)
                       .str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.strip())
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["numero_parcela"] = pd.to_numeric(df["numero_parcela"], errors="coerce")
    df["safra"] = df["data_originacao"].dt.to_period("M")
    return df


def resumo_fpd(df: pd.DataFrame, data_ref: pd.Timestamp, dias_fpd: int, grupo: list) -> pd.DataFrame:
    contratos = df.groupby("contrato_id").agg(
        safra=("safra", "first"), valor_total=("valor", "sum"),
        **{g: (g, "first") for g in grupo if g != "safra"})
    p1 = df[df["numero_parcela"] == 1].set_index("contrato_id")
    limite = p1["data_vencimento"] + pd.Timedelta(days=dias_fpd)
    maduro = limite <= data_ref
    nao_pago = p1["data_pagamento"].isna() | (p1["data_pagamento"] > limite)
    contratos["fpd_maduro"] = maduro.reindex(contratos.index).fillna(False)
    contratos["fpd"] = (nao_pago & maduro).reindex(contratos.index).fillna(False)
    g = contratos.groupby(grupo)
    out = pd.DataFrame({
        "contratos": g.size(),
        "valor_originado": g["valor_total"].sum().round(2),
        "contratos_maduros_fpd": g["fpd_maduro"].sum(),
        "fpd_qtd": g["fpd"].sum(),
    })
    out["fpd_%"] = (100 * out["fpd_qtd"] / out["contratos_maduros_fpd"].where(out["contratos_maduros_fpd"] > 0)).round(1)
    return out


def matriz_over(df: pd.DataFrame, data_ref: pd.Timestamp, over: int, max_mob: int, grupo: str = "safra") -> pd.DataFrame:
    """% de contratos da safra com alguma parcela vencida há > `over` dias no fim de cada MOB."""
    linhas = []
    for safra, dfs in df.groupby("safra"):
        inicio = safra.to_timestamp()
        n_contratos = dfs["contrato_id"].nunique()
        for mob in range(1, max_mob + 1):
            corte = (inicio + pd.DateOffset(months=mob)) - pd.Timedelta(days=1)
            if corte > data_ref:
                break
            vencida = (dfs["data_vencimento"] <= corte - pd.Timedelta(days=over)) & (
                dfs["data_pagamento"].isna() | (dfs["data_pagamento"] > corte))
            atrasados = dfs.loc[vencida, "contrato_id"].nunique()
            linhas.append({"safra": str(safra), "mob": mob, "pct": round(100 * atrasados / n_contratos, 1)})
    if not linhas:
        return pd.DataFrame()
    m = pd.DataFrame(linhas).pivot(index="safra", columns="mob", values="pct")
    m.columns = [f"M{c}" for c in m.columns]
    return m


def matriz_over_segmento(df: pd.DataFrame, data_ref: pd.Timestamp, over: int, mob: int, seg: str) -> pd.DataFrame:
    """Over X no MOB fixo, por segmento (só safras que já atingiram aquele MOB)."""
    linhas = []
    for (safra, s), d in df.groupby(["safra", seg]):
        corte = (safra.to_timestamp() + pd.DateOffset(months=mob)) - pd.Timedelta(days=1)
        if corte > data_ref:
            continue
        vencida = (d["data_vencimento"] <= corte - pd.Timedelta(days=over)) & (
            d["data_pagamento"].isna() | (d["data_pagamento"] > corte))
        linhas.append({seg: s, "contratos": d["contrato_id"].nunique(),
                       "atrasados": d.loc[vencida, "contrato_id"].nunique()})
    if not linhas:
        return pd.DataFrame()
    t = pd.DataFrame(linhas).groupby(seg)[["contratos", "atrasados"]].sum()
    t[f"over{over}@M{mob}_%"] = (100 * t["atrasados"] / t["contratos"]).round(1)
    return t.sort_values(f"over{over}@M{mob}_%", ascending=False)


def md(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown()
    except ImportError:  # tabulate não instalado
        return df.to_string()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo")
    ap.add_argument("--data-ref", help="data de corte da base (padrão: maior data de pagamento/vencimento)")
    ap.add_argument("--dias-fpd", type=int, default=30)
    ap.add_argument("--over", type=int, default=30, help="dias de atraso para Over X")
    ap.add_argument("--max-mob", type=int, default=12)
    ap.add_argument("--mob-segmento", type=int, default=3, help="MOB usado na comparação por segmento")
    ap.add_argument("--segmento", help="coluna para quebrar FPD e Over X (ex.: nicho, produtor)")
    ap.add_argument("--saida", help="pasta para salvar CSVs")
    for c in COLS:
        ap.add_argument(f"--col-{c.replace('_', '-')}", dest=f"col_{c}", help=f"nome da coluna de {c} no arquivo")
    a = ap.parse_args()

    mapa = {c: getattr(a, f"col_{c}") for c in COLS}
    df = carregar(a.arquivo, mapa)
    if a.segmento and a.segmento not in df.columns:
        sys.exit(f"Coluna de segmento '{a.segmento}' não encontrada.")
    data_ref = pd.Timestamp(a.data_ref) if a.data_ref else max(df["data_pagamento"].max(), df["data_originacao"].max())

    print(f"# Análise de safras · data de referência {data_ref.date()}\n")
    n_c = f"{df['contrato_id'].nunique():,}".replace(",", ".")
    n_p = f"{len(df):,}".replace(",", ".")
    print(f"Base: {n_c} contratos | {n_p} parcelas | safras {df['safra'].min()} a {df['safra'].max()}\n")
    invalidas = df[COLS].isna().drop(columns=["data_pagamento"]).any(axis=1).sum()
    if invalidas:
        print(f"> Atenção: {invalidas} linhas com campos obrigatórios vazios ou inválidos.\n")

    r = resumo_fpd(df, data_ref, a.dias_fpd, ["safra"])
    print(f"## Resumo por safra (FPD = 1ª parcela não paga até vencimento + {a.dias_fpd} dias)\n")
    print(md(r) + "\n")
    print("> Safras com poucos contratos maduros ainda não têm FPD confiável.\n")

    m = matriz_over(df, data_ref, a.over, a.max_mob)
    print(f"## Over{a.over} por mês de vida (% de contratos com parcela vencida há > {a.over} dias)\n")
    print((md(m) if not m.empty else "Sem safras maduras o suficiente.") + "\n")

    seg_fpd = seg_over = None
    if a.segmento:
        seg_fpd = resumo_fpd(df, data_ref, a.dias_fpd, [a.segmento]).sort_values("fpd_%", ascending=False)
        print(f"## FPD por {a.segmento}\n\n{md(seg_fpd)}\n")
        seg_over = matriz_over_segmento(df, data_ref, a.over, a.mob_segmento, a.segmento)
        if not seg_over.empty:
            print(f"## Over{a.over}@M{a.mob_segmento} por {a.segmento}\n\n{md(seg_over)}\n")

    if a.saida:
        out = Path(a.saida); out.mkdir(parents=True, exist_ok=True)
        r.to_csv(out / "resumo_safras.csv")
        if not m.empty:
            m.to_csv(out / f"matriz_over{a.over}.csv")
        if seg_fpd is not None:
            seg_fpd.to_csv(out / f"fpd_por_{a.segmento}.csv")
        if seg_over is not None and not seg_over.empty:
            seg_over.to_csv(out / f"over{a.over}_por_{a.segmento}.csv")
        print(f"CSVs salvos em {out.resolve()}")


if __name__ == "__main__":
    main()
