# Entrega final — Pulso Macro

**Projeto:** Analytics Financeiro com BACEN / SGS

**Linha temática:** 3 — Macroeconomia, Taxas de Juros & Indicadores Econômicos

**Período:** janeiro de 2019 a dezembro de 2023

**Conta responsável no GitHub:** `evelynkleinenf-cloud`

## Links para a entrega

| Material | Link | Acesso |
|---|---|---|
| Dashboard em produção | [Abrir Pulso Macro](https://pulso-macro-bacen.streamlit.app/) | Público, sem login |
| Código e histórico Git | [Repositório pulso-macro-bacen](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen) | Público, sem login ou convite |
| Instruções e metodologia | [README](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/blob/master/README.md) | Mesmo acesso do repositório |
| Análise exploratória | [Notebook executado](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/blob/master/notebooks/eda_exploratoria.ipynb) | Mesmo acesso do repositório |
| Dados consolidados | [CSV mensal](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/blob/master/data/macro_mensal.csv) | Mesmo acesso do repositório; também disponível no painel |
| Testes automatizados | [GitHub Actions](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen/actions) | Mesmo acesso do repositório |
| Conferência de requisitos | [Checklist](checklist_avaliacao.md) | Incluído nos documentos do projeto |
| Apresentação | [Roteiro de demonstração](roteiro_apresentacao.md) | Incluído nos documentos do projeto |

## Texto pronto para colar no ambiente de entrega

> Apresento o Pulso Macro, projeto da Linha 3 de Analytics Financeiro, desenvolvido em Python e Streamlit para analisar juros, inflação, câmbio e atividade econômica do Brasil entre 2019 e 2023.
>
> Dashboard: https://pulso-macro-bacen.streamlit.app/
>
> Repositório: https://github.com/evelynkleinenf-cloud/pulso-macro-bacen
>
> O projeto utiliza as séries SGS 432, 433, 13522, 1 e 24364 do Banco Central, consolidadas em 60 competências mensais. Inclui ETL reproduzível, banco PostgreSQL no Supabase, contingência automática em CSV, cache, filtros com reset, quatro KPIs com deltas, seis gráficos Plotly Express e exportação da base filtrada. O notebook, a metodologia e os testes estão no repositório.
>
> O dashboard e o repositório são públicos e podem ser consultados sem login ou convite.

## Acesso do avaliador — concluído

O repositório foi tornado público em **30/10/2026**, por solicitação da autora. A visibilidade pública e a resposta HTTP 200 foram confirmadas na API do GitHub sem autenticação. Não é necessário informar uma conta de avaliador nem enviar convite para consultar o material.

O avaliador pode abrir o repositório, README, notebook, base e histórico Git pelos links acima. A publicação não inclui o arquivo real de Secrets, ambiente virtual ou credenciais. O dashboard também permanece público.

Se a instituição permitir entrega por arquivo, o pacote ZIP sem credenciais pode ser anexado como complemento. Ele não contém a pasta `.git`; consulte o histórico pelo GitHub.

## Antes de enviar

- [ ] Preencher nome, turma, disciplina e demais campos exigidos no ambiente da instituição.
- [ ] Comparar a entrega com o enunciado oficial; a conferência atual usa o prompt fornecido.
- [x] Confirmar acesso público ao GitHub, sem login ou convite.
- [ ] Abrir o dashboard e conferir a indicação da fonte dos dados.
- [ ] Anexar o pacote sem credenciais, se o ambiente aceitar ou exigir arquivos.
- [ ] Conferir prazo, formato e eventual duração da apresentação no enunciado.

Não incluir senha, arquivo real de Secrets, chaves de API ou acesso administrativo do Supabase no material enviado.
