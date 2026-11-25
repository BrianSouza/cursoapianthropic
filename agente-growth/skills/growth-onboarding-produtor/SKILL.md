---
name: growth-onboarding-produtor
description: Analisa e melhora o onboarding e a ativação de produtores (infoprodutores que passam a oferecer boleto/Pix parcelado) com abordagem product-led. Mapeia o funil cadastro → documentos → integração → 1ª venda → repasse → recorrência, mede o time-to-first-sale, encontra o "aha moment" com dados, aponta onde os produtores travam e define quem segue no self-serve e quem merece acompanhamento humano. Use sempre que alguém falar em onboarding, ativação, implantação, produtor novo que não vende, tempo até a primeira venda, integração com checkout, churn de produtor no início, product-led, self-serve, ou pedir para entender por que cadastros não viram produtores ativos, mesmo sem usar esses termos.
---

# Onboarding e ativação do produtor (product-led)

O produtor só vê valor quando **vende parcelado e recebe o repasse**. Tudo antes disso (cadastro, documentos, integração) é custo para ele. Product-led onboarding significa fazer o próprio produto levar o produtor a esse momento **o mais rápido possível e com o mínimo de ajuda humana**, deixando o time comercial e de CS para quem tem mais potencial ou está travado.

Esta skill responde quatro perguntas:
1. **Onde os produtores param** entre o cadastro e a primeira venda?
2. **Quanto tempo** levam até vender (time-to-first-sale) e o que acelera isso?
3. **Qual é o "aha moment"**, ou seja, o comportamento inicial que melhor prevê que o produtor vai continuar vendendo?
4. **Quem deve receber atenção humana** e quem segue no self-serve?

## Funil de referência

```
Cadastro → Documentos/KYC → Integração com checkout → Parcelamento ativo no checkout
        → 1ª venda aprovada → 1º repasse recebido → Vendas recorrentes (retido) → Expansão
```

Use as etapas reais da empresa se estiverem nos arquivos do Projeto (questionário de onboarding, glossário). Se os dados tiverem nomes de eventos diferentes, mapeie e diga como mapeou.

## Passo a passo

### 1. Dados necessários
- **Produtores:** `produtor_id, data_cadastro` + segmentos úteis (porte/faturamento estimado, nicho, plataforma de checkout, origem: indicação, comercial, orgânico).
- **Eventos:** `produtor_id, evento, data`. Uma linha por ação: documentos enviados, integração concluída, acesso ao painel, venda aprovada, repasse recebido, chamado de suporte...
- Se só houver uma tabela por produtor com datas de cada etapa, converta para eventos (uma linha por etapa atingida).
- Defina com a pessoa o que é **produtor retido** (padrão do script: ≥ 1 venda aprovada entre os dias 61 e 90 após o cadastro). Use a definição do glossário do Projeto, se houver.

### 2. Rodar a análise
```bash
python scripts/aha_moment.py --produtores produtores.csv --eventos eventos.csv \
  --etapas cadastro,documentos_enviados,integracao_concluida,venda_aprovada,repasse_recebido \
  --evento-venda venda_aprovada --segmento porte --saida resultados/

# Rodada 2: aha moment só entre quem já integrou (ver "Armadilha" abaixo)
python scripts/aha_moment.py ... --condicionar-em integracao_concluida --janelas 14,30,45,60
```
O script entrega: funil com conversão e mediana de dias por etapa, time-to-first-sale por mês de cadastro e segmento, e um ranking de regras candidatas a aha moment ("fez E pelo menos K vezes nos primeiros D dias") com cobertura, retenção de quem fez × quem não fez, lift, precisão, recall e F1.

### 3. Ler o funil e o tempo
- **Maior queda absoluta:** onde se perde mais produtor. Normalmente é na integração.
- **Maior tempo mediano** entre etapas: onde está a espera. Uma etapa com boa conversão mas 15 dias de mediana é atrito escondido.
- **Por segmento:** plataforma de checkout (uma integração pode ser muito pior que outra), porte e origem. Produtores vindos do comercial ativam mais? Isso indica onde o humano faz diferença.
- **Meses recentes** ainda não maturaram: sinalize.

### 4. Escolher o aha moment
Um bom aha moment é:
- **Preditivo:** quem cumpre retém bem mais (lift alto, grande diferença entre "fez" e "não fez").
- **Frequente o bastante:** cobertura razoável (algo como 20% a 70%). Uma regra que só 3% cumprem não serve de meta.
- **Cedo e acionável:** acontece nos primeiros dias/semanas e o time consegue empurrar o produtor para ele.
- **Simples de comunicar:** "3 vendas aprovadas nos primeiros 30 dias".

**Armadilha principal:** etapas obrigatórias (integrar, acessar o painel) sempre parecem ótimas, porque todo retido passou por elas, mas não dizem nada novo. Por isso rode também com `--condicionar-em` na etapa anterior à venda e escolha entre as regras que aparecem **depois** do pré-requisito.

Correlação não é causalidade: produtores com lançamento grande vendem cedo **e** retêm, e isso não prova que empurrar vendas cedo cause retenção. Proponha confirmar com um experimento (skill `growth-experimento`), por exemplo uma ação que acelere a 1ª venda num grupo sorteado.

### 5. Self-serve × acompanhamento humano
Monte uma regra simples de priorização, explicitando as premissas:

| Faixa | Critério sugerido (ajustar) | Tratamento |
|---|---|---|
| **High-touch** | Potencial alto (faturamento estimado/porte grande, lançamento previsto) | Gerente/CS dedicado, ajuda na integração, acompanhamento até o aha moment |
| **Tech-touch com alerta** | Potencial médio, ou qualquer produtor **travado** há > [N] dias numa etapa | Self-serve + contato humano disparado pelo travamento |
| **Self-serve** | Demais | Checklist no painel, conteúdos, mensagens automáticas por comportamento |

O valor do humano deve ser medido: compare ativação e time-to-first-sale de quem recebeu acompanhamento × perfil similar que não recebeu.

### 6. Recomendar
Consulte `references/taticas-onboarding.md` para o catálogo de táticas product-led por etapa. Recomende no máximo 3 a 5 ações, cada uma ligada a um gargalo encontrado nos dados, com a métrica que deve mexer (ex.: "% que integra em 7 dias").

## Formato do relatório

```
# Onboarding de produtores: [período]

## Resumo
[3–5 linhas: maior gargalo, time-to-first-sale, aha moment proposto, principal recomendação]

## Funil de onboarding
[tabela: etapa, produtores, conversão, mediana de dias]

## Time-to-first-sale
[mediana/p75 por mês e pelos segmentos relevantes]

## Aha moment proposto
- Regra: [ ]
- Evidência: retenção [X%] se cumpre × [Y%] se não cumpre; cobertura [Z%]
- Alternativas consideradas e por que não
- Como validar: [experimento]

## Self-serve × high-touch
[regra proposta + estimativa de quantos produtores em cada faixa]

## Recomendações
| Ação | Gargalo que ataca | Métrica | Esforço |

## Ressalvas
[maturação, definição de retenção, eventos faltantes, correlação ≠ causalidade]
```

## Cuidados
- Produtor ativo que vende muito mas gera alto FPD/contestação **não** é um onboarding bem-sucedido. Cruze com a skill `growth-safra-cobranca` quando houver dados de carteira por produtor.
- Não proponha afrouxar KYC ou validação cadastral para acelerar o onboarding sem envolver Risco/Compliance: é atrito com função (prevenção a fraude e lavagem).
- Se não houver dados de eventos, ainda dá para ajudar: desenhe o funil ideal, liste os eventos que deveriam ser registrados e use o questionário de onboarding do Projeto para levantar hipóteses.
