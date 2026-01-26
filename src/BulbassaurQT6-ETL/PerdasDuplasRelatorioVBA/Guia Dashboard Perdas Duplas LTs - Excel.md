Guia: Criando Dashboard de Contingências (Sem VBA)

Este guia ensina como transformar sua lista bruta de "Contingências Duplas" em gráficos profissionais na aba "Gráficos", similar ao que você faria com pandas e matplotlib, mas usando ferramentas nativas do Excel.

🛠️ Passo 0: Preparar os Dados (O "DataFrame")

Para o Excel entender "X e Y" corretamente, seus dados precisam estar formatados como Tabela.

Vá na aba Contingências Duplas.

Selecione todos os dados (do cabeçalho até a última linha).

Pressione Ctrl + T (ou vá em Inserir > Tabela).

Confirme que "Minha tabela tem cabeçalhos".

Dica: Dê um nome para essa tabela (ex: TabContingencias) na aba Design da Tabela lá no topo.

📊 Gráfico 1: Quantidade por Área (Gráfico de Barras)

Equivalente Python: df['Area'].value_counts().plot(kind='bar')

Criar a Agregação:

Clique em qualquer célula da sua tabela de dados.

Vá em Inserir > Tabela Dinâmica.

Escolha Nova Planilha. (Renomeie essa nova aba para Graficos).

Configurar X e Y:

No painel lateral "Campos da Tabela Dinâmica":

Arraste Área Geoelétrica para Linhas (Eixo X).

Arraste Área Geoelétrica (de novo) para Valores (Eixo Y).

Verifique se está aparecendo "Contagem de Área...".

Gerar o Gráfico:

Clique na Tabela Dinâmica criada.

Vá em Inserir > Gráfico Dinâmico (ou Gráfico de Colunas).

Escolha Colunas Agrupadas ou Barras.

Limpeza Visual (Estilo Python/Seaborn):

Clique nos botões cinzas do gráfico -> Botão direito -> Ocultar todos os botões.

Delete as Linhas de Grade (clique nas linhas horizontais e aperte Delete).

Delete a Legenda (se for cor única).

Título: "Ocorrências por Área".

🥧 Gráfico 2: Distribuição por Horizonte (Gráfico de Rosca/Pizza)

Equivalente Python: df['Horizonte'].value_counts().plot(kind='pie')

Criar a Agregação:

Copie a Tabela Dinâmica que você fez no Passo 1 e cole ao lado (na mesma aba Graficos).

Limpe os campos antigos.

Configurar X e Y:

Arraste Horizonte para Linhas (Categorias).

Arraste Horizonte para Valores (Contagem).

Gerar o Gráfico:

Vá em Inserir > Gráfico de Pizza -> Rosca.

Formatação:

Clique na rosca -> Formatar Série de Dados -> Tamanho do Orifício (aumente para 60-70% para ficar moderno).

Adicione Rótulos de Dados (Clique com botão direito na fatia -> Adicionar Rótulos).

📈 Gráfico 3: Evolução ou Outra Categoria (Linha ou Coluna)

Se você tiver uma coluna de Data ou quiser ver por Tipo de Contingência.

Criar a Agregação:

Copie e cole a Tabela Dinâmica novamente.

Configurar X e Y:

Arraste Data (se tiver) ou Volume para Linhas.

Arraste Contingência para Valores (Contagem).

Gerar o Gráfico:

Inserir > Gráfico de Linha (com marcadores) ou Coluna.

Dica de Design:

Coloque as cores oficiais do ONS (Azul e Laranja) clicando nas barras/linhas e alterando o "Preenchimento".

💾 Dica Final: Atualização Automática

Como criamos Tabelas Dinâmicas baseadas na Tabela de Dados (TabContingencias), quando você rodar sua Macro VBA e novos dados entrarem:

Vá na aba Graficos.

Vá em Dados > Atualizar Tudo (ou clique com botão direito na tabela dinâmica > Atualizar).

Todos os gráficos se ajustarão sozinhos!