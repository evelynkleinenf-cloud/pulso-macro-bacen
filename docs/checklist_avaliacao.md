# Conferência de requisitos — Pulso Macro

Conferência em **30/10/2026**. Base: requisitos do prompt inicial da autora. O enunciado oficial e os documentos indicados por `[cite: ...]` não foram fornecidos; portanto, esta conferência não certifica aderência a critérios adicionais, pesos ou nota final.

## Requisitos técnicos

| Requisito recebido | Resultado | Evidência no projeto |
|---|---|---|
| Linha 3 e séries 432, 433, 13522, 1 e 24364 | Atendido | `src/config.py`, catálogo em `app.py` e metadados da base |
| Período de janeiro/2019 a dezembro/2023 | Atendido | CSV com 60 competências; datas mensais no último dia de cada mês |
| ETL real BACEN/SGS, sem dados simulados | Atendido | `src/etl.py`, cinco JSON em `data/raw/`, notebook e testes de reprocessamento |
| Tratamento e qualidade da base | Atendido | Conversão de datas/valores, duplicatas, contrato mensal, derivados e validação em `src/analytics.py` |
| Caminhos relativos | Atendido no código revisado | `Path("data")` em `src/config.py`; notebook aceita execução na raiz ou em `notebooks/` |
| Credenciais via `st.secrets` | Atendido | `get_database_settings()` em `src/database.py` |
| Exemplo de Secrets e proteção no Git | Atendido | `.streamlit/secrets.toml.example` e `.gitignore`; arquivo real fora dos arquivos versionados |
| PostgreSQL/Supabase prioritário | Atendido | `st.connection("postgresql", type="sql")`; painel online indicou PostgreSQL |
| Fallback CSV com `try/except` | Atendido | `load_dataset()`; testes isolados simulam indisponibilidade do banco |
| Cache de leitura e tratamento pesado, TTL 3600 | Atendido | Extração, parsing, consolidação, validação, leitura, filtros, correlação e exportação cacheados |
| Filtros reativos na barra lateral | Atendido | Anos, competências, curvas, média móvel, rebaseamento e modo de correlação |
| `st.session_state` e reset funcional | Atendido | `reset_filters()` e testes de restauração, inclusive seleção vazia |
| Abas com `st.tabs` | Atendido | Cinco abas: Panorama, Preços & atividade, Relações, Base de dados e Metodologia |
| Exportação da base filtrada | Atendido | `st.download_button`; download online de 2020–2023 conferido com 48 linhas e dez colunas |
| Quatro KPIs com deltas | Atendido | Selic, IPCA 12m, juro real ex-post proxy e PTAX; deltas omitidos corretamente em recorte de um mês |
| Pelo menos cinco gráficos em Plotly Express | Atendido | Seis gráficos em `src/charts.py`, incluindo todos os cinco recomendados |
| Arquitetura modular e estrutura solicitada | Atendido | `app.py`, `src/etl.py`, `src/database.py`, dados, notebook, configuração e dependências; módulos e testes adicionais |
| Git e documentação de execução | Implementado; avaliação qualitativa depende da rubrica | Histórico real, README, `.gitignore`, `.gitattributes` e GitHub Actions |
| Dashboard hospedado | Atendido | [Aplicação pública](https://pulso-macro-bacen.streamlit.app/) com Supabase e contingência local |
| Acesso do avaliador ao código privado | Pendente | É necessário informar a conta GitHub do avaliador e confirmar o nível de acesso efetivamente disponível |

## Evidências verificadas

- CSV: **60 linhas e dez colunas**, de 31/01/2019 a 31/12/2023, sem datas duplicadas. A data identifica a competência; o recorte temático começa em 01/01/2019.
- SHA-256 do CSV coincide com `data/metadata.json`: `0d6ea74c2e118296af8009c882804115f99f3de1fe4eb52fe501e0c010199641`.
- Notebook válido: **nove células de código executadas**, sem outputs de erro salvos.
- Código da aplicação e módulos revisados sem caminhos pessoais absolutos.
- Validação automatizada do código: **26 testes aprovados**, lint e formatação. [CI do commit de implantação `69d8ccc`](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/actions/runs/41112273251), com jobs aprovados em Python 3.11 e 3.14.
- Validação online: fonte PostgreSQL, quatro KPIs, seis gráficos, filtro, reset e download. [Captura](dashboard-online.png).
- Aplicativo público; código GitHub privado. São permissões independentes.

## Pontos para a avaliação

1. Comparar esta matriz ao enunciado oficial quando ele estiver disponível. Não foram fornecidos pesos, prazo, formato da apresentação ou exigência de quantidade de commits.
2. O histórico existente contém dois commits de implementação/implantação antes dos documentos de entrega. Ele deve ser apresentado como realmente ocorreu; não há garantia de pontuação máxima em evolução Git.
3. O juro real é uma **proxy retrospectiva pela meta Selic capitalizada**, não o retorno efetivo da Selic overnight. A metodologia está explícita no painel e no README.
4. A base contém séries históricas revisáveis extraídas em 2026. Não representa o conjunto de informações disponível em tempo real em 2019–2023.
5. Concluir e confirmar o acesso do avaliador ao repositório antes de enviar o trabalho. O link privado, isoladamente, não concede acesso.

## Resultado da conferência

Os requisitos técnicos explícitos do prompt estão implementados. A entrega depende da identificação do avaliador para acesso ao GitHub e da comparação com a rubrica oficial, caso ela contenha exigências adicionais. Esta análise não atribui uma nota nem substitui a avaliação docente.
