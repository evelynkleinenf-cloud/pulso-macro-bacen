# Checklist com a rubrica oficial — Pulso Macro

Conferência e adequações em **30/10/2026**, com base no PDF oficial de 15 páginas fornecido pela estudante. Este documento substitui o checklist preliminar baseado somente no prompt. Não atribui nota nem substitui a avaliação do professor.

## Matriz de requisitos

| Requisito | Referência no PDF | Evidência / situação |
|---|---|---|
| Cinco séries SGS e 2019–2023 | p. 6 | 432, 433, 13522, 1 e 24364; 60 meses |
| ETL e caminhos relativos | p. 8–9 | src/etl.py, contrato compartilhado, snapshots e notebook |
| Dicionário com tipos, significado e cálculo | p. 9 e 11 | README, seção 4, dez campos |
| Conexão, fallback, Secrets e cache | p. 9 | src/database.py e decorators TTL 3600; Secrets reais fora do Git |
| Estado, filtros, reset e deploy | p. 9 | app.py; implantação pública preservada em master |
| Gráficos oficiais da Linha 3 | p. 7 e 9 | Linhas/barras, média PTAX horizontal, bolhas IPCA 12m com tamanho Selic, IBC-Br, heatmap; mais inflação mensal e defasagens |
| Quatro KPIs com deltas | p. 7 e 9 | Selic, IPCA 12m, juro real proxy e PTAX; duas linhas legíveis |
| Abas e download filtrado | p. 9 | Seis abas e CSV em UTF-8 BOM |
| Cinco respostas de negócio | p. 6–7 | src/insights.py e aba Respostas de negócio; cálculo sob filtros e limites explícitos |
| Rigor e ausência de causalidade indevida | p. 9 | README, notebook e painel; defasagens exploratórias, sem inferência causal |
| README nos 14 tópicos | p. 11 | Estruturado; falta completar URL do vídeo após gravação |
| Trello público com print | p. 11–12 | Link e docs/trello.png no README; criado nas adequações, sem histórico retroativo |
| Cards com nome/especificações e WIP 1 | p. 14 | Nome completo, descrições e movimentações reais; histórico anterior não é reconstituído |
| GitFlow | p. 12 e 14 | Feature analítica integrada por PR em develop; documentação em feature própria; conferir PRs finais para main e master |
| Vídeo individual de 3–5 minutos | p. 2–3 e 12–14 | Roteiro corrigido; **gravação e URL pendentes da autora** |
| Autoria, LinkedIn e referências | p. 11 | Nome completo e LinkedIn confirmados; fontes e assistência técnica identificadas |
| Entrega dos três links no AVA | p. 3 | **Pendente da autora**, até 03/11/2026 às 22h |
| Congelamento após submissão | p. 3 | Não atualizar o repositório após entregar, até receber a nota |

## Pesos oficiais

| Grupo | Peso máximo |
|---|---:|
| Vídeo | 1,00 |
| Trello: identificação/especificações, movimentação e WIP | 1,50 |
| GitHub: branches/commits e README | 1,50 |
| ETL | 1,50 |
| EDA / Plotly | 1,50 |
| Arquitetura / interatividade / deploy | 1,50 |
| KPIs / storytelling / conclusões | 1,50 |
| **Total** | **10,00** |

## Evidências e limites

- 32 testes locais aprovados, incluindo calendário de defasagens, filtros descontínuos, média histórica fixa e eixos/tamanhos dos gráficos oficiais.
- CI da funcionalidade analítica aprovado em Python 3.11 e 3.14: [run 41122542502](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/actions/runs/41122542502).
- CSV original preservado com seu SHA-256; as adequações não reextraíram nem alteraram o snapshot.
- O juro real continua sendo uma proxy pela meta Selic capitalizada em 12 meses, deflacionada por Fisher. O PDF não fixa uma fórmula diferente.
- O catálogo oficial informa ODbL para as fichas disponíveis 432, 1 e 24364; o README distingue o estado dos metadados de licença de 433/13522, sem presumir licença não confirmada.
- Os quatro commits iniciais diretos em master permanecem reais. O GitFlow é usado nas correções atuais; novas branches não demonstram utilização histórica anterior.
- O Trello documenta as adequações a partir da sua criação. Não garante pontuação máxima pelo processo anterior.
- CI aprovado não garante nota máxima nem substitui vídeo, Trello, submissão ou defesa individual.

## Pendências finais

1. Concluir e verificar as integrações finais e o dashboard atualizado.
2. A autora gravar e hospedar o pitch, enviar sua URL e conferir os acessos.
3. Completar o campo de vídeo no README/texto de entrega antes da submissão.
4. Submeter GitHub, Streamlit e vídeo no AVA e congelar alterações até a nota.
