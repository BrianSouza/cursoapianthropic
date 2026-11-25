---
name: growth-safra-cobranca
description: Analisa a carteira de boleto/Pix parcelado por safra (cohort de originação), com FPD, curvas Over 30/60/90 por mês de vida, roll rate, recuperação e desempenho da régua de cobrança, quebrando por produtor, nicho, ticket e nº de parcelas para achar onde o risco está concentrado e o que fazer. Use sempre que alguém falar em inadimplência, atraso, FPD, safra, cohort, carteira, cobrança, régua, recuperação, "produtores problemáticos", ou mandar uma base de contratos/parcelas pedindo leitura, mesmo que não use esses termos técnicos.
---

# Análise de safra e cobrança

Num negócio de crédito parcelado, crescer aprovando mais só é bom se as safras novas pagarem tão bem quanto as antigas. Esta skill responde três perguntas:

1. **As safras estão melhorando ou piorando?** (FPD e curvas Over X por mês de vida)
2. **Onde o risco está concentrado?** (produtor, nicho, ticket, nº de parcelas, canal)
3. **A cobrança está funcionando?** (recuperação, roll rate, efeito de cada passo da régua)

## Por que olhar por safra (e não só a inadimplência da carteira)
A inadimplência da carteira inteira mistura contratos novos (que ainda nem tiveram chance de atrasar) com antigos. Se a empresa está crescendo rápido, a carteira fica cheia de contratos novos e a inadimplência *parece* cair, mesmo que o crédito esteja piorando. A comparação justa é **safra contra safra, na mesma idade** (ex.: Over30 no 3º mês de vida, "Over30@M3").

## Passo a passo

### 1. Preparar os dados
O formato ideal é **uma linha por parcela**: `contrato_id, data_originacao, numero_parcela, data_vencimento, data_pagamento (vazio se não pago), valor` + colunas de segmento (produtor, nicho, ticket, canal).

- Se vier em outro formato (uma linha por contrato, com status agregado), explique o que dá e o que não dá para calcular e, se possível, reconstrua.
- Se a base tiver CPF, nome ou contatos, **não os exiba**. Trabalhe com o ID do contrato e recomende anonimizar nas próximas extrações.
- Defina a **data de referência** (data de corte da extração). Tudo que não teve tempo de vencer + maturar é excluído das taxas.

### 2. Rodar a análise base
Use o script incluído, que funciona com CSV ou XLSX, datas ISO ou brasileiras e nomes de coluna mapeáveis:

```bash
python scripts/analisar_safras.py parcelas.csv --data-ref 2026-11-01 --over 30 --segmento nicho --saida resultados/
# se as colunas tiverem outros nomes: --col-contrato-id id_contrato --col-data-pagamento dt_pgto ...
# outros cortes: --over 60 | --dias-fpd 15 | --mob-segmento 6 | --segmento produtor
```

Ele entrega: resumo por safra com FPD, matriz Over X × mês de vida (MOB) e, opcionalmente, FPD e Over X por segmento. Rode de novo com outros segmentos conforme a pergunta. Para análises que o script não cobre (roll rate, recuperação, régua), calcule com pandas seguindo as definições do glossário do Projeto.

### 3. Ler as safras
- **Tendência:** compare as safras na mesma coluna (mesmo MOB). Piora consistente nas safras recentes é o principal alerta.
- **Quebra:** uma safra específica muito pior que as vizinhas? Cruze com o que mudou naquele mês: política de crédito, produtor novo grande, campanha, nicho novo.
- **FPD alto + Over que estabiliza:** típico de fraude ou de venda problemática (comprador nunca quis pagar). Olhe por produtor.
- **FPD normal + Over que cresce ao longo dos meses:** perda de engajamento ou de valor percebido no meio do contrato. Olhe nº de parcelas e tipo de produto.
- **Sinalize a imaturidade:** safras recentes têm poucas colunas preenchidas e poucos contratos maduros.

### 4. Concentração de risco
- Monte o ranking de **produtores** por perda (volume × taxa), não só por taxa. Um produtor pequeno com 30% de FPD pesa menos que um grande com 12%.
- Para cada segmento problemático, estime o impacto: "se o produtor X tivesse o FPD médio, teríamos R$ Y a menos de perda por mês".
- Compare a taxa de **reclamações/contestações** dos produtores com mais inadimplência: muitas vezes o problema é o produto ou a entrega, não o comprador. Isso afeta reputação e é tema jurídico (CDC).

### 5. Cobrança e régua
Quando houver dados de régua (envios, canal, aberturas, pagamentos após contato):
- **Roll rate** entre faixas (em dia → 1–30 → 31–60 → 61–90 → 90+): onde a "escada" acelera?
- **Recuperação por faixa e por canal** (WhatsApp, e-mail, SMS, ligação).
- **Curva de pagamento após o vencimento:** em que dia (D+1, D+3, D+7...) os pagamentos se concentram? Passos da régua sem pico depois deles podem estar sobrando, e lacunas sem contato antes de um pico podem ser oportunidade.
- Atribuir pagamento a um contato **não** prova causalidade (a pessoa talvez pagasse de qualquer jeito). Para medir o efeito real de um passo, proponha um experimento com a skill `growth-experimento`.

## Formato do relatório

```
# Safras e cobrança: data de referência [ ]

## Resumo
[3–5 linhas: tendência das safras, onde está o risco, o que fazer]

## Safras
[tabela resumo FPD + matriz Over X, destacando a tendência]

## Concentração de risco
[top produtores/segmentos por perda estimada, com R$]

## Cobrança
[roll rate, recuperação, achados da régua, se houver dados]

## Recomendações
| Ação | Área (crédito / cobrança / produtor / produto) | Impacto estimado | Precisa de aprovação de? |

## Ressalvas
[maturação, definições usadas, dados faltantes]
```

## Cuidados
- **Cobrança responsável:** recomende apenas práticas compatíveis com o CDC: sem constrangimento, sem contato excessivo, sem expor o devedor a terceiros, respeitando horários e opt-out. Sugestões de régua devem melhorar a experiência (lembrar antes, facilitar 2ª via e renegociação), não só aumentar a pressão.
- **Decisões de crédito** (cortar produtor, mudar limites e score) são recomendações para a área de risco, não decisões do agente.
- Diga sempre se a taxa é **por quantidade de contratos ou por valor**: os resultados podem divergir bastante.
- Veja `references/leitura-de-curvas.md` para padrões de curva e o que costumam indicar.
