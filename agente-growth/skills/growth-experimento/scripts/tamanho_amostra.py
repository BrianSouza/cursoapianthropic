#!/usr/bin/env python3
"""Tamanho de amostra e análise de teste A/B para proporções (só biblioteca padrão).

Exemplos:
  # Planejar: FPD atual de 12%, quero detectar queda de 10% relativa
  python tamanho_amostra.py --base 0.12 --mde 0.10 --relativo --volume-diario 400

  # Planejar com MDE absoluto (2 p.p.)
  python tamanho_amostra.py --base 0.12 --mde 0.02

  # Analisar resultado
  python tamanho_amostra.py --analisar --conv-a 120 --n-a 1000 --conv-b 98 --n-b 1000
"""
import argparse
import math
from statistics import NormalDist

Z = NormalDist()


def tamanho_por_grupo(p1: float, p2: float, alpha: float, poder: float) -> int:
    """Amostra por grupo, teste bicaudal de duas proporções (aproximação normal)."""
    z_a = Z.inv_cdf(1 - alpha / 2)
    z_b = Z.inv_cdf(poder)
    p_bar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * p_bar * (1 - p_bar))
           + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p1 - p2) ** 2)


def analisar(conv_a: int, n_a: int, conv_b: int, n_b: int, alpha: float) -> dict:
    pa, pb = conv_a / n_a, conv_b / n_b
    p_pool = (conv_a + conv_b) / (n_a + n_b)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (pb - pa) / se_pool if se_pool > 0 else 0.0
    p_valor = 2 * (1 - Z.cdf(abs(z)))
    se = math.sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)
    z_a = Z.inv_cdf(1 - alpha / 2)
    diff = pb - pa
    return {
        "taxa_a": pa, "taxa_b": pb, "diff_abs": diff,
        "diff_rel": diff / pa if pa else float("nan"),
        "ic_low": diff - z_a * se, "ic_high": diff + z_a * se,
        "p_valor": p_valor, "significativo": p_valor < alpha,
        "srm_alerta": abs(n_a - n_b) / max(n_a, n_b) > 0.05,
    }


def pct(x: float) -> str:
    return f"{x * 100:.2f}%".replace(".", ",")


def pp(x: float) -> str:
    return f"{x * 100:+.2f} p.p.".replace(".", ",", 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", type=float, help="taxa atual da métrica (0-1)")
    ap.add_argument("--mde", type=float, help="efeito mínimo detectável")
    ap.add_argument("--relativo", action="store_true", help="interpreta --mde como relativo (0.10 = 10%%)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--poder", type=float, default=0.8)
    ap.add_argument("--volume-diario", type=float, help="eventos elegíveis por dia (somando os grupos)")
    ap.add_argument("--grupos", type=int, default=2)
    ap.add_argument("--analisar", action="store_true")
    ap.add_argument("--conv-a", type=int); ap.add_argument("--n-a", type=int)
    ap.add_argument("--conv-b", type=int); ap.add_argument("--n-b", type=int)
    a = ap.parse_args()

    if a.analisar:
        if None in (a.conv_a, a.n_a, a.conv_b, a.n_b):
            ap.error("--analisar exige --conv-a --n-a --conv-b --n-b")
        r = analisar(a.conv_a, a.n_a, a.conv_b, a.n_b, a.alpha)
        print(f"Controle (A):    {pct(r['taxa_a'])}  (n={a.n_a})")
        print(f"Tratamento (B):  {pct(r['taxa_b'])}  (n={a.n_b})")
        print(f"Diferença:       {pp(r['diff_abs'])} (absoluta) | {pct(r['diff_rel'])} (relativa)")
        print(f"IC {int((1 - a.alpha) * 100)}%:          [{pp(r['ic_low'])} ; {pp(r['ic_high'])}]")
        print(f"p-valor:         {r['p_valor']:.4f} -> {'SIGNIFICATIVO' if r['significativo'] else 'não significativo'} (alpha={a.alpha})")
        if r["srm_alerta"]:
            print("ALERTA: grupos com tamanhos muito diferentes (>5%). Verifique o sorteio (SRM) antes de confiar no resultado.")
        return

    if a.base is None or a.mde is None:
        ap.error("informe --base e --mde (ou use --analisar)")
    p1 = a.base
    p2 = p1 * (1 + a.mde) if a.relativo else p1 + a.mde
    if not (0 < p2 < 1) or p1 == p2:
        ap.error(f"taxa alvo inválida: {p2}")
    # também testa a direção oposta (bicaudal) e usa o maior n
    p2_neg = p1 * (1 - a.mde) if a.relativo else p1 - a.mde
    ns = [tamanho_por_grupo(p1, p2, a.alpha, a.poder)]
    if 0 < p2_neg < 1:
        ns.append(tamanho_por_grupo(p1, p2_neg, a.alpha, a.poder))
    n = max(ns)
    total = n * a.grupos
    print(f"Taxa base:        {pct(p1)}")
    print(f"Efeito detectável: {pp(abs(p2 - p1))[1:]} ({pct(abs(p2 - p1) / p1)} relativo)")
    print(f"alpha={a.alpha}  poder={a.poder}")
    print(f"Amostra:          {n:,} por grupo | {total:,} no total".replace(",", "."))
    if a.volume_diario:
        dias = math.ceil(total / a.volume_diario)
        semanas = math.ceil(dias / 7)
        print(f"Duração estimada: {dias} dias -> arredondar para {semanas} semana(s) completa(s)")
        print("Lembrete: métricas de pagamento ainda precisam de tempo de maturação após o fim da coleta.")


if __name__ == "__main__":
    main()
