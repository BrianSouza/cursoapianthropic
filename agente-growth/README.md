# Agente de Growth: Operações (fintech de boleto/Pix parcelado)

Kit para montar um **agente de Growth dentro do app do Claude** (claude.ai, desktop e mobile), sem código: um **Projeto** com instruções e base de conhecimento, mais **3 Skills** que ensinam o agente a executar análises do mesmo jeito sempre.

```
agente-growth/
├── projeto/
│   ├── instrucoes-projeto.md          → colar nas instruções do Projeto
│   └── conhecimento/                  → subir como arquivos do Projeto
│       ├── glossario.md
│       ├── north-star-e-metricas.md
│       └── registro-experimentos.md
├── skills/                            → subir em Configurações › Capacidades › Skills
│   ├── growth-diagnostico-funil/
│   ├── growth-experimento/            (inclui script de tamanho de amostra e teste A/B)
│   └── growth-safra-cobranca/         (inclui script de matriz de safras / FPD / Over X)
├── dist/                              → skills empacotadas (.skill / .zip) prontas para upload
└── exemplos/parcelas-ficticias.csv    → base 100% fictícia para testar a skill de safras
```

## Instalação (≈ 20 minutos)

### 1. Preencher os campos `[ ]`
Antes de subir, preencha nos arquivos de `projeto/`:
- nome da empresa e da gestora em `instrucoes-projeto.md`
- definições que diferem das internas em `glossario.md` (ex.: FPD em D+30 ou D+15?)
- **números de referência e metas** em `north-star-e-metricas.md`. Sem eles, o agente só compara períodos entre si.

### 2. Criar o Projeto
1. No Claude, abra **Projetos → Criar projeto**, com o nome "Growth".
2. Em **Instruções**, cole o conteúdo de `projeto/instrucoes-projeto.md` (a partir da linha "Você é o Analista de Growth...").
3. Em **Arquivos/Conhecimento**, suba os 3 arquivos de `projeto/conhecimento/`.

### 3. Instalar as Skills
1. Confirme que **Execução de código / criação de arquivos** está ativada (Configurações › Capacidades). As skills usam Python para os cálculos.
2. Em **Configurações › Capacidades › Skills**, faça upload de cada arquivo de `dist/` (um por skill).
3. Ative as três.

> Em planos Team/Enterprise, um admin pode precisar liberar skills customizadas, ou pode publicá-las para a organização toda.

### 4. Conectores (opcional, recomendado)
Em **Configurações › Conectores**, conecte o que o time usa:
- **Google Drive**: planilhas de funil e bases de parcelas
- **Slack**: para o agente resumir ou postar análises
- **Notion/Confluence**: para manter o registro de experimentos fora do Projeto

Banco de dados ou data warehouse (BigQuery, Postgres...) exige um conector MCP. Use **credencial somente leitura** e, de preferência, views com dados agregados ou anonimizados.

## Como testar (primeira semana)

Dentro do Projeto, experimente:

| Pedido | Skill que deve entrar |
|---|---|
| "Segue a exportação do checkout de outubro. Onde estamos perdendo mais venda?" | diagnóstico de funil |
| "Tenho essas 8 ideias para reduzir FPD, prioriza pra mim" | experimento |
| "Quero testar lembrete de WhatsApp no D-2. Quantos contratos preciso e quanto tempo leva?" | experimento |
| "Anexei a base de parcelas. As safras estão piorando? Algum produtor preocupa?" | safra e cobrança |
| "A inadimplência caiu esse mês, é real?" | safra e cobrança (efeito mix/maturação) |

**Dica:** para os primeiros testes, use uma base **anonimizada**, só com ID do contrato e sem CPF, nome ou contato.

## Privacidade e governança
- Dados de crédito e de devedores são dados pessoais (LGPD). Valide com o jurídico/DPO o que pode ser enviado ao Claude conforme o plano contratado.
- O agente **recomenda**. Mudanças em política de crédito, régua de cobrança e comunicação com devedores seguem aprovação humana.
- As instruções já proíbem o agente de sugerir práticas abusivas de cobrança e de repetir dados pessoais nas respostas.

## Próximas evoluções
- Tarefa agendada semanal: "resumo de segunda-feira" com funil, FPD das safras e alertas
- Skill de análise de reclamações (Reclame Aqui/atendimento) × produtores
- Skill de growth do lado do produtor (ativação, indicação, expansão de TPV)
- Conector direto ao data warehouse
