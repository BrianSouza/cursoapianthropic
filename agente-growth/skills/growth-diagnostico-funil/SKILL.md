---
name: growth-diagnostico-funil
description: Diagnostica o funil de uma fintech de boleto/Pix parcelado (checkout → solicitação → aprovação → conversão → 1ª parcela paga → quitação, e o funil de produtores), encontra o maior gargalo, segmenta para achar a causa e propõe hipóteses priorizadas. Use sempre que alguém perguntar por que vendas, aprovação, conversão ou TPV caíram ou subiram, onde o funil está perdendo gente, qual etapa atacar primeiro, ou mandar uma planilha/exportação de checkout, aprovações ou contratos pedindo uma leitura, mesmo sem usar a palavra "funil".
---

# Diagnóstico de funil

Objetivo: sair de "os números mudaram" para **"o gargalo é a etapa X, no segmento Y, provavelmente por causa de Z, e aqui está o que testar"**, sempre com os números que sustentam a conclusão.

O funil desta empresa tem uma particularidade: o fim não é a venda, é a **parcela paga**. Uma etapa que melhora a conversão mas piora o FPD pode estar destruindo valor. Por isso o diagnóstico sempre olha o funil até a 1ª parcela.

## Funis de referência

**Comprador:**
1. Checkout iniciado (boleto/Pix parcelado selecionado)
2. Solicitação de crédito enviada
3. Aprovado
4. Compra concluída (assinatura/emissão)
5. 1ª parcela paga (ativação)
6. Parcelas em dia / quitação

**Produtor:**
1. Lead/cadastro → 2. Integração concluída → 3. 1ª venda parcelada (ativação) → 4. Ativo recorrente → 5. Expansão (mais produtos, mais TPV)

Use as definições do glossário do Projeto. Se os dados recebidos tiverem etapas diferentes, mapeie para estas e diga como mapeou.

## Passo a passo

### 1. Entender os dados antes de calcular
- Liste as colunas, o período coberto e o nível de detalhe (evento, contrato, agregado diário).
- Verifique: duplicidades (mesmo CPF várias tentativas), períodos incompletos (a última semana costuma estar "imatura" para 1ª parcela), mudanças de definição.
- Se faltar uma etapa, diga qual e siga com o que há. Não trave a análise por isso.

### 2. Montar o funil geral
Para cada etapa: volume absoluto, conversão da etapa (vs. anterior) e conversão acumulada (vs. topo). Compare com o período anterior equivalente (semana vs. semana, mês vs. mês) e, se houver, com a meta em `north-star-e-metricas.md`.

### 3. Achar o gargalo
O gargalo **não** é necessariamente a etapa com menor conversão. É onde há **mais valor recuperável**:

> Valor potencial da etapa ≈ (conversão de referência − conversão atual) × volume que entra na etapa × ticket médio × (1 − FPD esperado)

A conversão de referência pode ser a meta, o melhor período recente ou o melhor segmento comparável. Ordene as etapas por valor potencial.

### 4. Segmentar a etapa gargalo
Quebre a etapa pelos segmentos padrão (produtor, nicho, faixa de ticket, nº de parcelas, canal, dia da semana/horário se houver). Procure:
- **Concentração:** a queda vem de 1–2 produtores ou nichos? (Muito comum: um lançamento grande distorce a média.)
- **Mix:** a conversão de cada segmento ficou igual, mas o peso dos segmentos mudou? Isso é efeito mix, não piora real. Separe sempre "efeito taxa" de "efeito mix".
- **Quebra temporal:** a mudança começou num dia específico? Cruze com mudanças conhecidas (política de crédito, deploy no checkout, nova régua, instabilidade de provedor de boleto/Pix).

### 5. Formular hipóteses
Para o gargalo, gere de 3 a 5 hipóteses no formato:

> **Se** [causa], **então** veríamos [evidência nos dados]. **Evidência atual:** [confirma / contradiz / não dá para saber].

Consulte `references/hipoteses-por-etapa.md` para o catálogo de causas comuns em cada etapa. Ele serve de ponto de partida e não substitui os dados.

### 6. Recomendar
- Ações imediatas (correção de bug, falar com produtor específico)
- Experimentos sugeridos (se a pessoa quiser estruturar, use a skill `growth-experimento`)
- Dados que faltam para confirmar as hipóteses

## Formato do relatório

```
# Diagnóstico de funil: [período]

## Resumo
[3–5 linhas: o que mudou, onde está o gargalo, causa mais provável, ação recomendada]

## Funil
| Etapa | Volume | Conv. etapa | Conv. acumulada | Δ vs. anterior |

## Gargalo: [etapa]
- Valor potencial estimado: R$ [ ] / mês (premissas: ...)
- Segmentação: [tabela ou bullets com onde está concentrado]
- Efeito taxa vs. efeito mix: [ ]

## Hipóteses
1. [hipótese], evidência: [ ]
...

## Recomendações
| Ação | Tipo (correção/experimento/investigação) | Responsável sugerido | Métrica para acompanhar |

## Ressalvas
[dados imaturos, amostra pequena, sazonalidade, etc.]
```

## Cuidados
- **Maturação:** contratos recentes ainda não tiveram tempo de pagar a 1ª parcela. Exclua da conta de ativação os que ainda não venceram, ou sinalize.
- **Aprovação × risco:** se recomendar algo que aumente a aprovação, estime o impacto no FPD e lembre que mudança de política de crédito exige aprovação humana.
- **Amostras pequenas:** segmentos com < ~100 eventos na etapa geram variações enganosas. Agrupe ou sinalize.
