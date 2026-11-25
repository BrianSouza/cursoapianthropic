# Catálogo de hipóteses por etapa do funil

Ponto de partida para gerar hipóteses. Para cada causa, a "evidência esperada" diz o que procurar nos dados para confirmar ou descartar.

## Checkout → Solicitação de crédito

| Causa possível | Evidência esperada |
|---|---|
| Formulário longo ou confuso (muitos campos, validação ruim) | Abandono concentrado em um campo; pior no mobile |
| Opção de parcelamento pouco visível no checkout do produtor | Baixa seleção da opção em produtores específicos; varia por plataforma de checkout |
| Simulação de parcelas pouco clara (valor total, juros) | Muitos acessos à simulação sem envio |
| Problema técnico (integração, instabilidade) | Queda abrupta em data/hora específica; erros nos logs |
| Tráfego de menor intenção (campanha nova do produtor) | Volume no topo sobe e conversão cai; concentrado em 1 produtor ou origem |

## Solicitação → Aprovação

| Causa possível | Evidência esperada |
|---|---|
| Mudança na política/modelo de crédito | Quebra na data da mudança; afeta todos os produtores |
| Mudança no perfil do público (nicho ou campanha nova) | Queda concentrada em produtor/nicho; score médio menor |
| Fonte de dados de crédito (bureau) instável | Aumento de "sem decisão"/erros; queda em horários específicos |
| Ticket ou nº de parcelas acima do apetite | Reprovação maior em tickets altos / muitas parcelas |
| Tentativas repetidas do mesmo CPF inflando a base | Muitas solicitações por CPF; aprovação "real" por CPF estável |

## Aprovação → Compra concluída

| Causa possível | Evidência esperada |
|---|---|
| Condição aprovada pior que a esperada (entrada, parcelas, valor) | Conversão menor quando a condição aprovada difere da solicitada |
| Passo de assinatura/confirmação com atrito (OTP, contrato longo) | Abandono no passo; tempo alto entre aprovação e conclusão |
| Comprador comparando com outra opção | Conversão menor em tickets altos; abandono após ver valor total |
| Falha na emissão do boleto / geração do Pix | Erros técnicos; reclamações de "não recebi o boleto" |

## Compra → 1ª parcela paga (FPD)

| Causa possível | Evidência esperada |
|---|---|
| Esquecimento / boleto não chegou | FPD menor quando houve lembrete; reclamações de não recebimento |
| Arrependimento / produto não entregue | FPD concentrado em produtores específicos; reclamações sobre o produto |
| Fraude | FPD muito alto em safra/produtor específico; padrões de dados (e-mails, dispositivos) |
| Vencimento da 1ª parcela mal posicionado (longe do dia de pagamento do salário) | FPD varia por dia de vencimento |
| Aprovação frouxa em um segmento | FPD alto em faixa de score/ticket recém-liberada |

## Parcelas seguintes / quitação

| Causa possível | Evidência esperada |
|---|---|
| Régua de cobrança fraca no meio do contrato | Atraso cresce a partir da 3ª–4ª parcela |
| Perda de valor percebido do curso | Atraso maior em produtos de entrega curta com parcelamento longo |
| Choque de renda sazonal | Piora generalizada em meses específicos (jan, pós-festas) |

## Funil do produtor

| Etapa | Causas comuns |
|---|---|
| Cadastro → integração | Integração técnica difícil; falta de suporte; documentação |
| Integração → 1ª venda | Opção escondida no checkout; produtor sem lançamento próximo; desconhece o benefício |
| 1ª venda → ativo recorrente | Taxa de aprovação baixa frustra o produtor; repasse demorado; atendimento |
| Ativo → expansão | Sem incentivo para mais produtos; produtor migra para concorrente |
