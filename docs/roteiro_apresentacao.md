# Roteiro de apresentação — Pulso Macro

**Duração sugerida: oito minutos.** Ajustar à duração que o professor determinar. O roteiro não pressupõe um limite oficial, pois ele não foi fornecido.

## Preparação antes da apresentação

Abra o [dashboard](https://pulso-macro-bacen.streamlit.app/), o README, o notebook e o GitHub Actions. Restaure os filtros. Confirme o acesso ao código com a conta do avaliador. Para os quatro cartões ficarem legíveis, use uma janela ampla; se necessário, ajuste o zoom do navegador.

Prepare uma cópia local extraída do pacote de entrega, sem `.streamlit/secrets.toml`, para demonstrar o fallback. Instale as dependências antecipadamente e rode `python -m streamlit run app.py --server.port 8502` na raiz dessa cópia, com o ambiente virtual ativado. Ela deve indicar **CSV local · BACEN/SGS**. Não altere o banco nem os Secrets da hospedagem durante a apresentação.

## 0:00–0:45 — Problema e objetivo

**Mostrar:** título, intervalo e fonte no dashboard.

**Fala sugerida:** “O Pulso Macro reúne juros, inflação, câmbio e atividade econômica para explorar como esses indicadores se comportaram entre 2019 e 2023. A pergunta central é: como evoluíram os ciclos de juros e inflação, e quais associações aparecem com o câmbio e a atividade? A análise é descritiva, sem afirmar causalidade.”

## 0:45–1:45 — Dados e ETL

**Mostrar:** catálogo na aba Metodologia; depois a estrutura `src/`, `data/` e o notebook.

**Fala sugerida:** “A origem é o Banco Central, com as séries 432, 433, 13522, 1 e 24364. O ETL consulta a API com timeout e novas tentativas, converte datas e números e consolida frequências distintas em 60 competências mensais. Selic e PTAX usam o fechamento do mês; a PTAX também tem média das observações mensais. IPCA e IBC-Br preservam suas competências. Os JSON originais e o hash do CSV permitem reproduzir e conferir o snapshot.”

Explique que a Selic tem histórico auxiliar desde dezembro/2017 para calcular a janela retrospectiva de 12 meses em 2019. A base final entregue permanece em 2019–2023. O fim do mês identifica a competência, não a data da divulgação.

## 1:45–2:45 — Supabase, contingência e arquitetura

**Mostrar:** “Fonte em uso: PostgreSQL” no painel online; depois a cópia local com indicação de CSV.

**Fala sugerida:** “O PostgreSQL do Supabase é a primeira fonte consultada. A conexão usa `st.connection` e os segredos ficam em `st.secrets`. Se a consulta falhar ou retornar uma base inválida, o aplicativo usa automaticamente o CSV local, validado pelo mesmo contrato. Os dados e as transformações de maior custo usam cache de uma hora.”

Apresente as responsabilidades: `etl.py` extrai e consolida; `database.py` conecta e aplica a contingência; `analytics.py` valida, filtra e calcula; `charts.py` cria as figuras; `app.py` compõe a interface. Não abra Secrets nem mostre credenciais.

## 2:45–3:45 — KPIs e filtros

**Mostrar:** quatro cartões e seleção de anos.

Com o recorte completo, os valores de dezembro/2023 são **Selic 11,75%**, **IPCA 12m 4,62%**, **juro real proxy 8,29%** e **PTAX R$ 4,84**. Os deltas comparam a última observação do recorte à anterior; taxas usam pontos percentuais e câmbio usa reais por dólar.

Selecione apenas **2020**: a tabela deve ter 12 competências e a Selic terminal deve mudar para **2,00%**. Clique em **Restaurar filtros** e confirme o retorno aos 60 meses. Explique o uso de estado de sessão para preservar as escolhas e restaurar o estado original.

**Fala sobre o juro real:** “Esta é uma proxy ex-post: capitalizo a meta Selic diária na janela anterior de 12 meses e aplico Fisher com o IPCA de 12 meses. Não é simplesmente subtrair a inflação da taxa terminal, e também não representa o retorno efetivo da Selic overnight.”

## 3:45–5:30 — Seis gráficos e interpretações

| Aba / gráfico | Demonstração e interpretação |
|---|---|
| Panorama — Selic, inflação e juro real | Compare dezembro/2020, com Selic de 2,00%, a dezembro/2022, com 13,75%. Mostre a mudança do ciclo e explique os horizontes distintos da meta terminal e do juro real retrospectivo. |
| Panorama — PTAX | Diferencie fechamento, média mensal e média móvel. Troque a janela de três para 12 meses e mostre a suavização; no início da janela completa, a média ainda não existe. |
| Preços & atividade — IBC-Br | Identifique o mínimo do snapshot em abril/2020. Ative o rebaseamento em 100 e explique que muda a escala, não a trajetória. O indicador de atividade não substitui o PIB. |
| Preços & atividade — IPCA mensal | Diferencie meses de inflação e deflação pelas barras; não confunda taxa mensal com acumulado em 12 meses. |
| Relações — dispersão PTAX × IPCA mensal | Mostre que cada ponto corresponde a uma competência e que as cores identificam anos. A nuvem de pontos não prova transmissão causal do câmbio para os preços. |
| Relações — correlação | Alterne variações e níveis. Explique a escala de -1 a 1 e o risco de tendências comuns em níveis; defasagens e variáveis omitidas não são controladas. |

Evite narrar choques econômicos específicos como causa dos movimentos sem uma análise adicional. A base demonstra as trajetórias e associações observadas.

## 5:30–6:15 — Exportação e casos de borda

**Mostrar:** aba Base de dados.

Selecione somente 2020, baixe o CSV e confira **12 linhas de dados**, além do cabeçalho. Explique o separador `;`, a vírgula decimal e UTF-8 BOM. Restaure os filtros.

Se houver tempo, reduza o período a uma competência: os deltas deixam de existir e o mapa de correlação informa a insuficiência de dados. Depois restaure novamente.

## 6:15–7:15 — Qualidade, notebook e Git

**Mostrar:** notebook executado, testes, workflow e histórico Git.

**Fala sugerida:** “O notebook registra a análise exploratória e a metodologia. Os 26 testes cobrem qualidade dos dados, fórmulas, exportação, prioridade do banco, fallback e interação do Streamlit. O CI executa testes, lint e formatação em Python 3.11 e 3.14. O `.gitignore` protege Secrets e ambientes locais. O histórico contém os commits reais do desenvolvimento, implantação e documentação, sem datas ou etapas artificiais.”

Abra o run aprovado, não apenas o arquivo YAML. Diferencie testes locais isolados de integração real com o Supabase e da verificação online do dashboard.

## 7:15–8:00 — Conclusão e limites

**Fala sugerida:** “O projeto transforma cinco séries com frequências diferentes em uma base mensal validada e numa aplicação interativa, com resiliência e exportação. A meta Selic termina 2020 em 2,00% e 2022 em 13,75%; o IPCA em 12 meses passa de 10,06% no fim de 2021 para 4,62% no fim de 2023. O painel permite explorar esses movimentos junto com câmbio e atividade, preservando os limites da análise.”

Encerre com os links do dashboard e do GitHub. Reforce: as séries são revisáveis, o snapshot foi extraído em 2026, o juro real é uma proxy e correlação não demonstra causalidade.

## Respostas curtas para perguntas prováveis

- **Por que consolidar mensalmente?** As séries têm frequências distintas; a competência mensal torna os indicadores comparáveis, com regras explícitas por série.
- **O que acontece se o banco cair?** O erro fica contido na camada de dados e o CSV validado é usado; a interface informa a fonte ativa.
- **Por que não usar só CSV?** O PostgreSQL atende à persistência e consulta centralizada; o arquivo mantém a demonstração disponível sem a infraestrutura remota.
- **O que o delta representa?** A diferença entre as duas últimas observações selecionadas. Para taxas é uma diferença em pontos percentuais, não uma variação percentual.
- **Por que o juro real é uma proxy?** A série 432 é a meta Selic, não a taxa overnight realizada. A capitalização da meta aproxima o histórico nominal antes da deflação por Fisher.
- **Como evitar erros de cache?** O cache tem TTL de 3600 segundos e a versão do CSV participa da chave. Falhas do banco não tornam o fallback uma escolha permanente em cache.
- **A aplicação reproduz o que se sabia em 2020?** Não. Ela usa um snapshot de séries históricas revisáveis; backtesting exigiria dados por data de publicação e por versão.
- **O gráfico prova que o câmbio causa inflação?** Não. Ele mostra associação contemporânea; uma afirmação causal exigiria outra estratégia analítica.
