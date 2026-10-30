# Entrega final — Pulso Macro

**Projeto:** Analytics Financeiro com BACEN / SGS  
**Linha temática:** 3 — Macroeconomia, Taxas de Juros & Indicadores Econômicos  
**Período:** janeiro de 2019 a dezembro de 2023  
**Conta responsável no GitHub:** `evelynkleinenf-cloud`

## Links para a entrega

| Material | Link | Acesso |
|---|---|---|
| Dashboard em produção | [Abrir Pulso Macro](https://pulso-macro-bacen.streamlit.app/) | Público, sem login |
| Código e histórico Git | [Repositório pulso-macro-bacen](https://github.com/evelynkleinenf-cloud/pulso-macro-bacen) | Privado; avaliador precisa de convite aceito |
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
> O repositório é privado. O acesso do avaliador deve ser confirmado antes da submissão.

Após a aceitação e a conferência do convite, substitua a última frase por: **“O acesso ao repositório foi liberado para a conta GitHub indicada pelo avaliador.”** Não declare essa etapa concluída antes da confirmação.

## Acesso do avaliador — etapa pendente

O dashboard já está público. Para o código, falta o usuário GitHub ou e-mail indicado pelo avaliador. Não é possível verificar acesso sem identificar a conta.

Na conferência de 30/10/2026, somente a proprietária `evelynkleinenf-cloud` constava na lista de colaboradores; não havia convites pendentes.

O repositório pertence a uma conta pessoal. A [documentação do GitHub sobre permissões](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository) informa que colaboradores de repositórios pessoais privados recebem leitura e escrita. Há relatos de diferenças entre a API e essa documentação; por isso, o nível oferecido deve ser conferido na conta antes do convite. Não se deve prometer acesso somente de leitura nem conceder escrita inadvertidamente.

Depois de informar a conta:

1. Verificar se ela já tem acesso ou convite pendente.
2. Conferir o nível de acesso disponível. Se houver somente colaboração com escrita, confirmar essa permissão com a autora antes de conceder acesso.
3. Enviar o convite autorizado e registrar seu estado como **enviado**, até a aceitação.
4. Após a aceitação, conferir o acesso da conta ao repositório. O avaliador também deve abrir README, notebook e histórico com a própria conta.

Se a instituição permitir entrega por arquivo, o pacote ZIP sem credenciais pode ser anexado como complemento. Ele não substitui o histórico Git ou o acesso ao GitHub quando esses forem exigidos na rubrica.

## Antes de enviar

- [ ] Preencher nome, turma, disciplina e demais campos exigidos no ambiente da instituição.
- [ ] Comparar a entrega com o enunciado oficial; a conferência atual usa o prompt fornecido.
- [ ] Confirmar convite aceito e acesso do avaliador ao GitHub.
- [ ] Abrir o dashboard e conferir a indicação da fonte dos dados.
- [ ] Anexar o pacote sem credenciais, se o ambiente aceitar ou exigir arquivos.
- [ ] Conferir prazo, formato e eventual duração da apresentação no enunciado.

Não incluir senha, arquivo real de Secrets, chaves de API ou acesso administrativo do Supabase no material enviado.
