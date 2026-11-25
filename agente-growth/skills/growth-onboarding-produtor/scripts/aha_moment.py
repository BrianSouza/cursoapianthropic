#!/usr/bin/env python3
"""Onboarding de produtores: funil de ativação, time-to-first-sale e candidatos a "aha moment".

Entradas:
  --produtores  CSV/XLSX, uma linha por produtor: produtor_id, data_cadastro [, colunas de segmento]
  --eventos     CSV/XLSX, uma linha por evento:   produtor_id, evento, data
                (evento = nome da ação: "documentos_enviados", "integracao_concluida",
                 "venda_aprovada", "repasse_recebido", "acesso_painel"...)

Definição de retenção (ajustável): o produtor está RETIDO se tiver pelo menos 1 evento
--evento-retencao entre os dias --ret-inicio e --ret-fim após o cadastro. Só entram na
análise de retenção os produtores "maduros" (cadastrados há mais de --ret-fim dias).

Saídas (markdown + CSVs opcionais em --saida):
  1. Funil de onboarding (etapas em --etapas): % que chegou e mediana de dias até chegar
  2. Time-to-first-sale por mês de cadastro (e por segmento, se --segmento)
  3. Candidatos a aha moment: "fez o evento E pelo menos K vezes nos primeiros D dias",
     com cobertura, retenção de quem fez × quem não fez, precisão e recall

Exemplo:
  python aha_moment.py --produtores produtores.csv --eventos eventos.csv \
      --etapas cadastro,documentos_enviados,integracao_concluida,venda_aprovada,repasse_recebido \
      --evento-venda venda_aprovada --segmento porte --saida resultados/
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def ler(caminho: str) -> pd.DataFrame:
    p = Path(caminho)
    if p.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(p)
    return pd.read_csv(p, sep=None, engine="python")


def para_data(s: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    txt = s.dropna().astype(str).str.strip()
    if not txt.empty and txt.str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.5:
        return pd.to_datetime(s, errors="coerce", format="ISO8601")
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def exigir(df: pd.DataFrame, cols: list, nome: str) -> None:
    falta = [c for c in cols if c not in df.columns]
    if falta:
        sys.exit(f"{nome}: colunas ausentes {falta}. Encontradas: {list(df.columns)}")


def md(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown()
    except ImportError:
        return df.to_string()


def funil(prod: pd.DataFrame, ev: pd.DataFrame, etapas: list, data_ref: pd.Timestamp, janela: int) -> pd.DataFrame:
    """% que chegou em cada etapa (alguma vez e dentro de `janela` dias) e mediana de dias."""
    primeiro = ev.groupby(["produtor_id", "evento"])["dias"].min().unstack()
    base = prod.set_index("produtor_id")
    maduros_janela = base["data_cadastro"] <= data_ref - pd.Timedelta(days=janela)
    linhas = []
    for etapa in etapas:
        if etapa == "cadastro":
            dias = pd.Series(0, index=base.index)
        elif etapa in primeiro.columns:
            dias = primeiro[etapa].reindex(base.index)
        else:
            print(f"> Aviso: etapa '{etapa}' não encontrada nos eventos.\n")
            continue
        chegou = dias.notna()
        chegou_jan = (dias <= janela) & maduros_janela
        linhas.append({
            "etapa": etapa,
            "produtores": int(chegou.sum()),
            "%_do_total": round(100 * chegou.mean(), 1),
            f"%_em_{janela}d (maduros)": round(100 * chegou_jan.sum() / max(maduros_janela.sum(), 1), 1),
            "mediana_dias": dias[chegou].median(),
        })
    out = pd.DataFrame(linhas).set_index("etapa")
    out["conv_vs_etapa_anterior_%"] = (100 * out["produtores"] / out["produtores"].shift(1)).round(1)
    return out


def time_to_first_sale(prod: pd.DataFrame, ev: pd.DataFrame, evento_venda: str, grupo: str) -> pd.DataFrame:
    vendas = ev[ev["evento"] == evento_venda].groupby("produtor_id")["dias"].min()
    p = prod.set_index("produtor_id").copy()
    p["ttfs"] = vendas.reindex(p.index)
    g = p.groupby(grupo)
    return pd.DataFrame({
        "produtores": g.size(),
        "com_1a_venda_%": (100 * g["ttfs"].apply(lambda s: s.notna().mean())).round(1),
        "mediana_dias": g["ttfs"].median(),
        "p75_dias": g["ttfs"].quantile(0.75),
    })


def candidatos_aha(prod: pd.DataFrame, ev: pd.DataFrame, data_ref: pd.Timestamp, evento_ret: str,
                   ret_ini: int, ret_fim: int, janelas: list, limiares: list, cobertura_min: float,
                   condicionar_em: str = None) -> tuple:
    base = prod.set_index("produtor_id")
    maduros = base.index[base["data_cadastro"] <= data_ref - pd.Timedelta(days=ret_fim)]
    if condicionar_em:
        # analisa só quem atingiu a etapa antes do início da janela de retenção
        ok = ev[(ev["evento"] == condicionar_em) & (ev["dias"] < ret_ini)]["produtor_id"].unique()
        maduros = maduros[maduros.isin(ok)]
    if len(maduros) == 0:
        return pd.DataFrame(), 0, float("nan")
    evm = ev[ev["produtor_id"].isin(maduros)]
    ret = evm[(evm["evento"] == evento_ret) & evm["dias"].between(ret_ini, ret_fim)]
    retido = pd.Series(False, index=maduros)
    retido[ret["produtor_id"].unique()] = True
    taxa_base = retido.mean()

    linhas = []
    for d in janelas:
        cedo = evm[evm["dias"] <= d]
        contagem = cedo.groupby(["produtor_id", "evento"]).size().unstack(fill_value=0).reindex(maduros, fill_value=0)
        for e in contagem.columns:
            if e == condicionar_em:
                continue
            for k in limiares:
                fez = contagem[e] >= k
                cob = fez.mean()
                if cob < cobertura_min or cob > 0.98:
                    continue
                r_fez = retido[fez].mean()
                r_nao = retido[~fez].mean() if (~fez).any() else float("nan")
                recall = (fez & retido).sum() / max(retido.sum(), 1)
                linhas.append({
                    "regra": f"{e} >= {k} em {d}d",
                    "cobertura_%": round(100 * cob, 1),
                    "retencao_se_fez_%": round(100 * r_fez, 1),
                    "retencao_se_nao_fez_%": round(100 * r_nao, 1),
                    "lift": round(r_fez / taxa_base, 2) if taxa_base else float("nan"),
                    "precisao_%": round(100 * r_fez, 1),
                    "recall_%": round(100 * recall, 1),
                    "f1": round(2 * r_fez * recall / (r_fez + recall), 3) if (r_fez + recall) else 0.0,
                })
    if not linhas:
        return pd.DataFrame(), len(maduros), taxa_base
    t = pd.DataFrame(linhas).set_index("regra").sort_values(["f1", "lift"], ascending=False)
    return t, len(maduros), taxa_base


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--produtores", required=True)
    ap.add_argument("--eventos", required=True)
    ap.add_argument("--etapas", default="cadastro,integracao_concluida,venda_aprovada",
                    help="etapas do funil em ordem, separadas por vírgula ('cadastro' = data_cadastro)")
    ap.add_argument("--evento-venda", default="venda_aprovada")
    ap.add_argument("--evento-retencao", help="padrão: igual a --evento-venda")
    ap.add_argument("--ret-inicio", type=int, default=61)
    ap.add_argument("--ret-fim", type=int, default=90)
    ap.add_argument("--janela-funil", type=int, default=30)
    ap.add_argument("--janelas", default="7,14,30,45", help="janelas (dias) para candidatos a aha moment")
    ap.add_argument("--condicionar-em", help="analisa o aha moment só entre quem atingiu esta etapa (ex.: integracao_concluida)")
    ap.add_argument("--limiares", default="1,2,3,5,10")
    ap.add_argument("--cobertura-min", type=float, default=0.05, help="ignora regras que <5%% dos produtores cumprem")
    ap.add_argument("--segmento", help="coluna de produtores para quebrar o time-to-first-sale")
    ap.add_argument("--data-ref", help="data de corte (padrão: data do último evento)")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--saida")
    ap.add_argument("--col-produtor-id", default="produtor_id")
    ap.add_argument("--col-data-cadastro", default="data_cadastro")
    ap.add_argument("--col-evento", default="evento")
    ap.add_argument("--col-data", default="data")
    a = ap.parse_args()

    prod = ler(a.produtores).rename(columns={a.col_produtor_id: "produtor_id", a.col_data_cadastro: "data_cadastro"})
    ev = ler(a.eventos).rename(columns={a.col_produtor_id: "produtor_id", a.col_evento: "evento", a.col_data: "data"})
    exigir(prod, ["produtor_id", "data_cadastro"], "produtores")
    exigir(ev, ["produtor_id", "evento", "data"], "eventos")
    if a.segmento and a.segmento not in prod.columns:
        sys.exit(f"Segmento '{a.segmento}' não existe na base de produtores.")
    prod["data_cadastro"] = para_data(prod["data_cadastro"])
    ev["data"] = para_data(ev["data"])
    ev["evento"] = ev["evento"].astype(str).str.strip()
    prod = prod.dropna(subset=["data_cadastro"]).drop_duplicates("produtor_id")
    ev = ev.merge(prod[["produtor_id", "data_cadastro"]], on="produtor_id", how="inner")
    ev["dias"] = (ev["data"] - ev["data_cadastro"]).dt.days
    ev = ev[ev["dias"] >= 0]
    data_ref = pd.Timestamp(a.data_ref) if a.data_ref else ev["data"].max()
    prod["mes_cadastro"] = prod["data_cadastro"].dt.to_period("M").astype(str)
    evento_ret = a.evento_retencao or a.evento_venda

    print(f"# Onboarding de produtores · data de referência {data_ref.date()}\n")
    print(f"Base: {len(prod)} produtores | {len(ev)} eventos | tipos de evento: {sorted(ev['evento'].unique())}\n")

    etapas = [e.strip() for e in a.etapas.split(",") if e.strip()]
    f = funil(prod, ev, etapas, data_ref, a.janela_funil)
    print(f"## 1. Funil de onboarding\n\n{md(f)}\n")

    t = time_to_first_sale(prod, ev, a.evento_venda, "mes_cadastro")
    print(f"## 2. Time-to-first-sale ('{a.evento_venda}') por mês de cadastro\n\n{md(t)}\n")
    print("> Meses recentes ainda não tiveram tempo de converter: compare com cautela.\n")
    ts = None
    if a.segmento:
        ts = time_to_first_sale(prod, ev, a.evento_venda, a.segmento)
        print(f"### Por {a.segmento}\n\n{md(ts)}\n")

    janelas = [int(x) for x in a.janelas.split(",") if int(x) < a.ret_inicio]
    if len(janelas) < len(a.janelas.split(",")):
        print(f"> Janelas >= {a.ret_inicio} dias foram ignoradas: elas se sobrepõem ao período de retenção.\n")
    limiares = [int(x) for x in a.limiares.split(",")]
    c, n_mad, taxa = candidatos_aha(prod, ev, data_ref, evento_ret, a.ret_inicio, a.ret_fim,
                                    janelas, limiares, a.cobertura_min, a.condicionar_em)
    print(f"## 3. Candidatos a aha moment\n")
    print(f"Retenção = pelo menos 1 '{evento_ret}' entre os dias {a.ret_inicio} e {a.ret_fim} após o cadastro. "
          f"Produtores maduros: {n_mad} | retenção base: {round(100 * taxa, 1) if n_mad else 'n/a'}%"
          + (f" | apenas quem atingiu '{a.condicionar_em}'" if a.condicionar_em else "") + "\n")
    if c.empty:
        print("Sem produtores maduros ou regras com cobertura suficiente.\n")
    else:
        print(md(c.head(a.top)) + "\n")
        print("> Ordenado por F1 (equilíbrio entre precisão e recall). Correlação, não causalidade: "
              "confirme o candidato escolhido com um experimento.\n")

    if a.saida:
        out = Path(a.saida); out.mkdir(parents=True, exist_ok=True)
        f.to_csv(out / "funil_onboarding.csv")
        t.to_csv(out / "time_to_first_sale.csv")
        if ts is not None:
            ts.to_csv(out / f"time_to_first_sale_por_{a.segmento}.csv")
        if not c.empty:
            c.to_csv(out / "candidatos_aha.csv")
        print(f"CSVs salvos em {out.resolve()}")


if __name__ == "__main__":
    main()
