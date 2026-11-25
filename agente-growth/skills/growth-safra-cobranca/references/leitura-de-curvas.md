# Leitura de curvas de safra: padrões comuns

Use como guia de interpretação. Confirme sempre com segmentação; o padrão sugere a causa, não prova.

## Matriz Over X × MOB

```
          M1   M2   M3   M4   M5   M6
2026-01  0.0  1.0  5.0  7.0  8.5  9.0    ← safra "normal": sobe e estabiliza
2026-02  0.0  1.2  5.3  7.4  8.8  9.4
2026-03  0.0  2.5  9.8 12.0 13.1        ← quebra: algo mudou na originação de março
2026-04  0.0  1.1  5.1  7.2
```

Leia **por coluna** (mesma idade) para comparar safras e **por linha** para ver a evolução de uma safra.

## Padrões e o que costumam indicar

| Padrão | Causa provável | O que checar |
|---|---|---|
| FPD alto, curva estabiliza logo | Fraude, venda forçada, comprador sem intenção de pagar | FPD por produtor; padrões de cadastro; reclamações "não reconheço a compra" |
| FPD normal, Over cresce mês a mês | Perda de valor percebido; parcelamento longo demais para o produto | Over por nº de parcelas e tipo de produto; pausa de conteúdo do produtor |
| Todas as safras pioram no mesmo mês-calendário (diagonal) | Choque externo: sazonalidade (janeiro), falha na régua, problema na emissão de boletos | Olhe a matriz por mês-calendário, não por MOB; logs da régua |
| Safra isolada muito pior | Mudança pontual: política de crédito, produtor grande novo, campanha agressiva | Composição da safra por produtor/nicho vs. vizinhas |
| Safras recentes melhores, mas TPV caiu | Política de crédito mais restritiva (troca de volume por qualidade) | Taxa de aprovação no mesmo período |
| Melhora após mudança na régua | Efeito da régua (ou coincidência) | Ideal: experimento com grupo de controle |

## Efeito mix
Se a inadimplência total mudou mas a de cada segmento ficou estável, a causa é **mudança de composição** (ex.: mais vendas em nicho de maior risco). Mostre as duas leituras:
- *Efeito taxa*: quanto mudou porque os segmentos pioraram/melhoraram
- *Efeito mix*: quanto mudou porque o peso dos segmentos mudou

## Pontos de referência de maturação
- **FPD (D+30):** legível ~2 meses após a originação (1º vencimento ~30 dias + 30 de tolerância).
- **Over30@M3:** legível após o 3º mês completo.
- **Perda final:** só para safras com contratos já encerrados (vencimento da última parcela + 90 dias).
