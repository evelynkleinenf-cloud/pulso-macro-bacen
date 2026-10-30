# Pitch individual — Pulso Macro (3 a 5 minutos)

**Autora:** Evelyn Klein dos Santos. **Meta de gravação:** 4min30s a 4min55s, validada por ensaio com cronômetro. O limite oficial é cinco minutos; este roteiro substitui o anterior de oito minutos.

## Antes de gravar

- Abra o dashboard em produção: https://pulso-macro-bacen.streamlit.app/ . Restaure os filtros e confira fonte/competência.
- Deixe README, notebook, Trello e um CI aprovado em abas prontas. Feche páginas com Secrets, credenciais, notificações e dados privados.
- Grave tela e sua própria apresentação/voz com linguagem profissional. Não é necessário mostrar uma criação de conta ou instalar dependências durante o vídeo.
- Faça um ensaio. Use apenas as falas abaixo e as ações indicadas; os parágrafos de preparação não fazem parte da narração.

## 0:00–0:45 — Identidade, contexto e problema

**Na tela:** título, quatro KPIs e intervalo.

> Olá, sou Evelyn Klein dos Santos e apresento o Pulso Macro, projeto da Linha 3 de Analytics Financeiro. O painel analisa juros, inflação, dólar e atividade econômica do Brasil entre 2019 e 2023. A pergunta é como esses ciclos se relacionam e quais sensibilidades uma equipe financeira deve observar ao planejar custos, receitas e demanda. A aplicação organiza cinco séries oficiais em uma base mensal e permite explorar os resultados sem tratar correlação como causalidade.

## 0:45–1:30 — Dados e engenharia

**Na tela:** catálogo/Metodologia; mostrar rapidamente a estrutura src e o notebook, já abertos.

> Os dados vêm da API SGS do Banco Central: meta Selic, IPCA mensal, IPCA de 12 meses, PTAX de venda e IBC-Br com ajuste sazonal. O ETL em Python converte datas e números, rejeita duplicatas e valida 60 competências. O PostgreSQL no Supabase é a fonte prioritária. Se ele falhar, o app usa o CSV validado e informa a contingência. O código separa extração, banco, cálculos e visualizações. As credenciais ficam fora do GitHub e as leituras e tratamentos principais têm cache de uma hora.

## 1:30–3:45 — Aplicação ao vivo

**Ação 1:** mostrar os KPIs; selecionar somente 2020 e restaurar. **Ação 2:** navegar por Panorama e Relações. **Ação 3:** abrir Respostas de negócio e Base de dados.

> Os quatro KPIs mostram Selic, inflação acumulada, juro real aproximado e dólar, com diferenças contra a observação anterior. Ao selecionar 2020, o recorte passa para 12 meses e a Selic terminal muda para 2%. O botão Restaurar filtros recupera os cinco anos.
>
> No Panorama, Selic e IPCA estão em linhas, com juro real em barras. A PTAX tem uma referência histórica fixa de R$ 4,9434, além das médias mensal e móvel. Na dispersão, o eixo vertical é o IPCA de 12 meses, a cor indica o ano e o tamanho indica a Selic. O mapa térmico mostra Pearson em níveis ou variações.
>
> A aba Respostas de negócio explicita as cinco perguntas: o maior juro real proxy foi 10,22% em junho de 2023; o dólar ficou acima da referência em 38 meses. Também há correlações com inflação posterior, comparação de ciclos com a atividade e ranking de pares. A base filtrada pode ser baixada em CSV.

**Se houver atraso:** apenas aponte a tabela de defasagens; não leia cada linha. Mostre o botão de download e uma interação Plotly, sem abrir vários arquivos durante a gravação.

## 3:45–4:55 — Conclusão, limites e links

**Na tela:** Respostas de negócio/Metodologia; encerrar com README e links.

> Um gestor pode usar esse histórico para priorizar testes de sensibilidade de juros, exposição cambial e demanda. O painel não prevê preços nem isola efeitos causais. A Selic utilizada é a meta, então o juro real é uma proxy pela capitalização retrospectiva e pela fórmula de Fisher. As séries são revisáveis, e o snapshot não reproduz exatamente as informações disponíveis em cada data histórica. O projeto inclui testes automatizados, integração por branches e um Trello individual com o planejamento das adequações. O código, o notebook e os links estão no GitHub, e o dashboard está público no Streamlit.

## Publicação e entrega

1. Grave e confira se o vídeo tem entre três e cinco minutos, áudio compreensível, textos legíveis e demonstração do app em produção.
2. Hospede no YouTube não listado, Drive público ou LinkedIn. A gravação não está concluída até existir um arquivo real conferido e uma URL acessível ao avaliador.
3. Envie a URL para completar README e texto de entrega. Não inventar endereço de vídeo.
4. Submeta GitHub, Streamlit e vídeo no AVA até 03/11/2026 às 22h, conforme o enunciado; depois mantenha o repositório sem alterações até a nota.

LinkedIn é uma alternativa de divulgação. Se publicar por lá, o PDF determina marcar Professor Savio Ricardo Garcia, LAB365, SENAI Santa Catarina e Sistema FIESC. Consulte os perfis indicados no enunciado.
