# North Star e árvore de métricas

> Arquivo de conhecimento do Projeto. Os valores entre `[ ]` são para a empresa preencher. Os números de referência ajudam o agente a dizer se algo está "bom" ou "ruim". Sem eles, ele só consegue comparar períodos entre si.

## North Star Metric (proposta)

**Valor de parcelas pagas no mês (R$)**

Por que essa e não "TPV" ou "vendas aprovadas":
- Ela só cresce quando a venda é aprovada **e** o comprador paga, então já embute a qualidade do crédito.
- Alinha os dois lados: o produtor recebe, o comprador cumpre e a empresa gera receita.
- O que não cresce junto com ela é vaidade (ex.: aprovar mais e receber menos).

> Alternativa, se a empresa preferir uma métrica de "originação saudável": **TPV aprovado com 1ª parcela paga**.

## Árvore de métricas (inputs da North Star)

```
Parcelas pagas (R$)
├── Originação
│   ├── Produtores ativos × vendas por produtor × ticket médio
│   ├── Taxa de aprovação
│   └── Conversão pós-aprovação
└── Performance da carteira
    ├── Ativação do comprador (1ª parcela paga)  ← inverso do FPD
    ├── Pagamento em dia das parcelas seguintes
    └── Recuperação de parcelas vencidas
```

## Números de referência

| Métrica | Valor atual | Meta | Alerta se |
|---|---|---|---|
| Taxa de aprovação | [ % ] | [ % ] | variação > [3 p.p.] semana a semana |
| Conversão pós-aprovação | [ % ] | [ % ] | < [ % ] |
| FPD (D+30) | [ % ] | [ % ] | > [ % ] |
| Over30@M3 | [ % ] | [ % ] | > [ % ] |
| Taxa de recuperação (vencidos 1–30) | [ % ] | [ % ] | < [ % ] |
| Produtores ativos | [ n ] | [ n ] | queda > [10%] mês a mês |
| Ticket médio | [ R$ ] | n/a | variação > [15%] |
| Nº médio de parcelas | [ n ] | n/a | n/a |
| Reclamações / 1.000 contratos | [ n ] | [ n ] | > [ n ] |

## Segmentações padrão

Sempre que fizer sentido, quebrar as análises por:
- Produtor (top 20 por TPV + "demais")
- Nicho do infoproduto: [listar: finanças, saúde, marketing digital, idiomas, concursos...]
- Faixa de ticket: [até R$ 500 / 500–1.500 / 1.500–3.000 / > 3.000]
- Número de parcelas: [até 6 / 7–12 / > 12]
- Canal de origem do comprador, quando disponível
- Safra (mês de originação)

## Fontes de dados

| Dado | Onde está | Atualização | Responsável |
|---|---|---|---|
| Funil de checkout | [ ] | [ ] | [ ] |
| Base de contratos e parcelas | [ ] | [ ] | [ ] |
| Régua de cobrança (envios e respostas) | [ ] | [ ] | [ ] |
| Cadastro de produtores | [ ] | [ ] | [ ] |
| Reclamações | [ ] | [ ] | [ ] |
