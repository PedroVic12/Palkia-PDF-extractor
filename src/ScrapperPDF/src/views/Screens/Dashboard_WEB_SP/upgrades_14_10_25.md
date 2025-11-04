# O que há de novo na nova versão MUST Gestão Desktop + Dashboard HTML V4.0.0:
--- 

## Atualizações - 14/10/2025


### Autocomplete no Notepad++

Régua: O atalho padrão é Ctrl + Espaço. Ele mostra uma lista de sugestões. Não é possível, por padrão, usar Ctrl + * para isso. O Ctrl + * no Notepad++ serve para outra coisa (selecionar tudo no modo coluna).

Ele completa palavras-chave ou funções, não linhas inteiras. Por exemplo, se você digitar DE e pressionar Ctrl + Espaço, ele pode sugerir DEMT.

- Dois arquivos de configuração:

    - Organon_Script_Plugin.udl.xml: Define a sua "linguagem". É aqui que você diz ao Notepad++ que palavras são comandos, quais são comentários, etc. O nome da linguagem (ex: "Organon Script") é definido aqui.

    - Organon_AutoComplete.xml: Contém a lista de palavras que o autocomplete deve sugerir para a linguagem que você criou no outro arquivo. O nome da linguagem nos dois arquivos XML deve ser idêntico!



Possui um script .bat ou .exe que abre no terminal e faz a configuração do plugin antes de abrir o Notepad++

### Busca com automação o Excel de controle de MUST operado por Alexandre

- Pega o excel do SharePoint mais atualizado e atualiza a tela de pendencias do dashboard em HTML

### Banco de dados interno ONS - MUST com SQL Server e Microsoft Access

- Busca dos dados direto do Servidor da ONS
- FIltragem dos dados para atividades SP
- Extração de PDF e Geração de Deck da análise do SIN
- Geração de Docx (word) template para preenchimento das análises


### Agenda Kanban Interativa:

A "Agenda de Prioridades" foi transformada em um painel Kanban com colunas "Atrasadas", "Para Hoje", "Próximos 7 Dias" e "Próximos 30 Dias".

Agora você pode arrastar e soltar as atividades entre as colunas "Para Hoje", "7 Dias" e "30 Dias" para reorganizar suas prioridades.

Ao mover um card, a nova data de previsão é calculada e salva automaticamente no localStorage, garantindo que suas mudanças persistam.

### Ferramentas de Análise Customizáveis:

No menu "Ferramentas de Análise", as matrizes (Eisenhower e Forças/Fraquezas) agora são painéis interativos com uma lista de "Atividades Não Classificadas" ao lado.

Você pode arrastar as atividades da lista e soltá-las diretamente nos quadrantes desejados. Sua classificação é salva no localStorage.

### Atualização Inteligente de Dados:

Ao carregar um novo arquivo Excel, o sistema agora preserva os dados de abas que não existem mais no novo arquivo, mantendo seu histórico e suas análises salvas.

### Exportação para Excel (.xlsx):

No menu lateral, o botão "Exportar Dados Atualizados" agora está funcional.

Ele gera um novo arquivo Excel contendo todas as suas abas com os dados atualizados (incluindo as novas datas do Kanban) e duas novas abas com os resultados das suas análises nas matrizes.