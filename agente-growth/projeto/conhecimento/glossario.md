# Glossário de Growth e Operações

> Arquivo de conhecimento do Projeto. **Revisar e ajustar** as definições para que fiquem iguais às usadas internamente. O agente vai seguir exatamente o que estiver aqui.

## Funil do comprador

| Termo | Definição |
|---|---|
| **Checkout iniciado** | Comprador chegou à etapa de pagamento e selecionou boleto/Pix parcelado. |
| **Solicitação de crédito** | Comprador enviou os dados para análise de crédito. |
| **Taxa de aprovação** | Solicitações aprovadas ÷ solicitações analisadas (excluir duplicadas do mesmo CPF no mesmo dia). |
| **Conversão pós-aprovação** | Aprovados que concluíram a compra (assinatura/emissão) ÷ aprovados. |
| **Ativação do comprador** | 1ª parcela paga até o vencimento + [N] dias. |
| **FPD (First Payment Default)** | % de contratos cuja 1ª parcela não foi paga até D+[30]. Forte sinal de fraude ou de aprovação ruim. |
| **Quitação** | Contrato com todas as parcelas pagas. |

## Crédito e cobrança

| Termo | Definição |
|---|---|
| **Safra (cohort)** | Conjunto de contratos originados no mesmo período (normalmente mês de originação). |
| **Over X (ex.: Over 30, Over 90)** | % do saldo (ou dos contratos, especificar) com parcela vencida há mais de X dias, medido em um ponto da vida da safra (ex.: Over 30 no 3º mês, "Over30@M3"). |
| **Inadimplência por valor** | Saldo vencido > X dias ÷ saldo total da carteira. Definir sempre se é por valor ou por quantidade. |
| **Roll rate** | % de contratos que passam de uma faixa de atraso para a seguinte (ex.: de 1–30 para 31–60 dias) de um mês para o outro. |
| **Taxa de recuperação** | Valor recebido de parcelas vencidas ÷ valor vencido no início do período. |
| **Régua de cobrança** | Sequência de contatos antes e depois do vencimento (ex.: D-3 lembrete, D0, D+1, D+3, D+7, D+15...), com canal e mensagem de cada passo. |
| **Contestação** | Comprador questiona a cobrança (chargeback, reclamação formal, Reclame Aqui, Procon). |
| **Perda esperada** | Probabilidade de inadimplência × exposição × (1 − recuperação). |

## Lado do produtor

| Termo | Definição |
|---|---|
| **Produtor ativo** | Produtor com ≥ 1 venda parcelada aprovada nos últimos [30] dias. |
| **TPV** | Total Payment Volume: valor total das vendas parceladas originadas no período. |
| **Ativação do produtor** | 1ª venda parcelada aprovada em até [N] dias após o cadastro. |
| **Take rate** | Receita da empresa ÷ TPV. |
| **Risco do produtor** | Indicador composto de inadimplência, FPD e contestação das vendas daquele produtor. |

## Growth

| Termo | Definição |
|---|---|
| **North Star Metric** | Métrica única que representa o valor entregue (ver `north-star-e-metricas.md`). |
| **AARRR** | Aquisição, Ativação, Retenção, Receita, Indicação. |
| **ICE** | Priorização por Impacto × Confiança × Facilidade (notas de 1 a 10). |
| **MDE** | Minimum Detectable Effect: menor efeito que o teste consegue detectar com a amostra disponível. |
| **Guardrail** | Métrica que não pode piorar durante um experimento (ex.: FPD, contestação). |
