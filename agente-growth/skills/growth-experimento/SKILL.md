---
name: growth-experimento
description: Estrutura, prioriza, dimensiona e analisa experimentos de Growth (testes A/B, pilotos, mudanças de régua de cobrança, checkout, aprovação, ativação de produtores) para uma fintech de boleto/Pix parcelado. Transforma ideias soltas em hipóteses testáveis, prioriza um backlog com ICE, calcula tamanho de amostra e duração, define métrica primária e guardrails, lê o resultado e registra o aprendizado. Use sempre que alguém disser "quero testar", "vale a pena fazer X?", "como saber se funcionou", "priorize essas ideias", "o teste deu resultado?", ou trouxer uma lista de ideias de melhoria, mesmo sem usar as palavras experimento ou A/B.
---

# Experimento de Growth

Um bom experimento responde uma pergunta de negócio com o menor custo possível e deixa um aprendizado registrado, mesmo quando "falha". Esta skill cobre o ciclo inteiro: **ideia → hipótese → priorização → desenho → análise → registro**.

Identifique em qual momento a pessoa está e comece dali. Não force o ciclo inteiro se ela só quer priorizar uma lista ou ler um resultado.

## 1. Da ideia à hipótese

Reescreva cada ideia neste formato:

> **Se** [mudança específica], **então** [métrica] vai [subir/cair ~X%] **para** [público/segmento], **porque** [mecanismo/insight].

Uma hipótese boa tem:
- Mudança concreta (dá para implementar amanhã)
- Uma **métrica primária** (só uma: é ela que decide o teste)
- **Guardrails**: métricas que não podem piorar. Nesta empresa quase sempre entram **FPD/inadimplência, contestações/reclamações e opt-out**, porque é fácil "ganhar" conversão comprando risco.
- Um "porquê" que vem de dado, pesquisa ou reclamação, e não só de intuição. Se for intuição, a Confiança no ICE fica baixa.

## 2. Priorizar com ICE

Dê notas de 1 a 10 e multiplique (I × C × E):

| Critério | Pergunta | Como calibrar |
|---|---|---|
| **Impacto** | Quanto move a North Star se der certo? | Use volume afetado × efeito esperado × ticket. Estime em R$/mês quando der. |
| **Confiança** | Quão provável é dar certo? | 8–10: já funcionou aqui ou há dado forte. 5–7: funcionou no mercado/há indício. 1–4: palpite. Consulte o registro de experimentos do Projeto. |
| **Facilidade** | Quanto custa rodar? | 8–10: configuração/texto, dias. 4–7: precisa de dev, semanas. 1–3: projeto grande, regulatório ou depende de terceiros. |

Mostre a tabela ordenada e comente os 3 primeiros: por que estão no topo e o que pode dar errado. Sinalize ideias que mexem em política de crédito: além do ICE, elas precisam de aprovação de risco.

## 3. Desenhar o teste

### Tipo de teste
- **A/B aleatorizado:** padrão-ouro. Use quando dá para sortear compradores/contratos (ex.: texto do lembrete, horário de envio, layout da simulação).
- **Teste por produtor (cluster):** quando a mudança é no checkout do produtor. Sorteie produtores, não compradores, e lembre que a amostra efetiva é bem menor.
- **Antes × depois / piloto:** quando não dá para sortear. É mais fraco: controle sazonalidade e mudanças paralelas, e prefira ter um grupo de comparação (diff-in-diff).
- **Holdout de cobrança:** para medir o efeito real de um passo da régua, mantenha um pequeno grupo sem aquele contato, **se for ético e permitido**. Nunca deixe um grupo sem o aviso de vencimento obrigatório.

### Tamanho de amostra e duração
Use o script incluído (só usa a biblioteca padrão do Python):

```bash
python scripts/tamanho_amostra.py --base 0.12 --mde 0.10 --relativo
# base = taxa atual da métrica (ex.: FPD de 12%)
# mde  = menor efeito que vale detectar (10% relativo → 12% vira 10,8%)
# opções: --alpha 0.05 --poder 0.8 --volume-diario 400 (estima duração em dias)
```

Explique o resultado em português simples: "Precisamos de ~N contratos por grupo; com ~V por dia, o teste leva ~D dias".

Regras práticas:
- Rode por **semanas completas** (mínimo 1–2), para cobrir o efeito do dia da semana.
- Métricas de pagamento precisam **maturar**: um teste sobre FPD só pode ser lido 30+ dias depois do vencimento da 1ª parcela do último contrato incluído. Deixe isso explícito no cronograma.
- Se a amostra necessária for inviável, sugira: aumentar o MDE (testar mudanças mais ousadas), usar uma métrica mais próxima (ex.: "boleto aberto" em vez de "parcela paga") como sinal inicial, ou um piloto qualitativo.
- Defina **antes** de começar: duração, critério de decisão e quando parar. Não espie o resultado todo dia para decidir.

### Documento do experimento
Entregue neste formato, pronto para colar no registro:

```
### EXP-[nº] · [Nome curto]
- Status: priorizado
- Hipótese: Se ..., então ... porque ...
- Público/segmento: [ ]
- Tipo: A/B | cluster por produtor | piloto
- Variantes: Controle = [ ] · Tratamento = [ ]
- Métrica primária: [ ] (base atual: [ ])
- Guardrails: [ ] (limite aceitável: [ ])
- Amostra: [N] por grupo · Duração: [D] dias + [M] dias de maturação
- Critério de decisão: escalar se [ ]; descartar se [ ]
- ICE: I [ ] · C [ ] · E [ ] = [ ]
- Riscos e aprovações necessárias: [ ]
```

## 4. Analisar o resultado

1. **Confira a integridade:** os grupos têm tamanho próximo do planejado? Os perfis (ticket, nicho, score) estão balanceados? Se não, o sorteio pode ter falhado (SRM), e isso invalida a leitura.
2. **Métrica primária:** efeito absoluto e relativo, intervalo de confiança e p-valor. O script também calcula:
   ```bash
   python scripts/tamanho_amostra.py --analisar --conv-a 120 --n-a 1000 --conv-b 98 --n-b 1000
   ```
3. **Guardrails:** algum piorou além do limite? Se sim, não escale, mesmo com a primária positiva.
4. **Segmentos:** olhe, mas trate achados em segmentos como **novas hipóteses**, não como conclusão (com muitos cortes, algum sempre "dá significativo" por acaso).
5. **Tradução em dinheiro:** efeito × volume mensal × ticket × (1 − perda esperada) = R$/mês estimado se escalar.
6. **Decisão:** escalar, iterar ou descartar, com o aprendizado em uma frase.

Resultado neutro também é resultado: registre como aprendizado ("lembrete no D-2 não muda o FPD, então o problema não é esquecimento").

## Cuidados
- Não proponha experimentos com práticas de cobrança abusivas ou que escondam o custo do crédito do comprador. Além de antiético, é risco regulatório (CDC).
- Experimentos que alteram critérios de aprovação precisam da área de risco/crédito no desenho.
- Se não houver dados suficientes para estimar a base da métrica, peça o número ou use uma faixa e mostre a sensibilidade.
