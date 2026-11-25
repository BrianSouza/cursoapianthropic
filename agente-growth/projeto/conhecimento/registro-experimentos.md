# Registro de experimentos

> Arquivo de conhecimento do Projeto. Mantenha atualizado: é a memória do time. O agente consulta este registro para não repetir testes e para calibrar a "Confiança" do ICE com base no que já funcionou.
>
> Quando a lista crescer, vale mover para uma planilha ou Notion e conectar ao Projeto.

## Como registrar

Um bloco por experimento, do mais recente para o mais antigo:

```
### EXP-000 · [Nome curto]
- Status: ideia | priorizado | rodando | concluído | cancelado
- Período: AAAA-MM-DD a AAAA-MM-DD
- Área do funil: aquisição produtor | aprovação | conversão | 1ª parcela | cobrança | retenção produtor
- Hipótese: Se [mudança], então [métrica] vai [subir/cair X%], porque [motivo].
- Métrica primária: [ ]
- Guardrails: [ ]
- ICE: I [ ] · C [ ] · E [ ] = [ ]
- Resultado: [efeito medido, intervalo/significância, amostra]
- Decisão: escalar | iterar | descartar
- Aprendizado: [o que sabemos agora que não sabíamos antes]
```

## Experimentos

### EXP-001 · Exemplo: lembrete por WhatsApp no D-2 da 1ª parcela
- Status: ideia
- Período: n/a
- Área do funil: 1ª parcela
- Hipótese: Se enviarmos um lembrete por WhatsApp 2 dias antes do vencimento da 1ª parcela, o FPD vai cair 10% (relativo), porque parte do não pagamento é esquecimento ou falta do boleto em mãos.
- Métrica primária: FPD (D+30)
- Guardrails: taxa de opt-out do WhatsApp; reclamações
- ICE: I 7 · C 6 · E 8 = 336
- Resultado: n/a
- Decisão: n/a
- Aprendizado: n/a

> Este é um exemplo ilustrativo. Apague ao começar a registrar os reais.
