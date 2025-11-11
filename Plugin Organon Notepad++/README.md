# Guia de Instalação e Uso do Plugin Organon para Notepad++

Este guia completo explica como instalar e utilizar o conjunto de ferramentas para a linguagem Organon no Notepad++, que inclui coloração de sintaxe, autocompletar e snippets de código (templates).

## Tarefas até o Deploy (04/11/2025)

- Colocar todos os comandos do anaRede (.PWF) e .spt(Organon)
- Testar versão final com .exe do script.bat rodando tudo 



## Como Utilizar o Plugin
(UPDATE: 22/10/2025)
- Esta sendo usado uma versão portatil do Notepad++ para instalar o Plugin com script.bat sem senha de administrador.

- Para o deploy do projeto o script.bat tem que rodar como administrador e pedir para o 767 liberar a senha da ONS para cada usuário para atualizar o notepad++ "global" da maquina do usuário.

- O plugin utiliza os principais comandos do Organon e AnaREDE de acordo com o arquivo "tutorial_script.pdf"

- Esta sendo criada uma pasta de exemplos de estudos do SEP com o SIN para PLC para uso do notepad++ em conjunto.


--- 

## Componentes do Plugin e como fazer um:
Cada arquivo tem uma função específica para integrar a linguagem Organon ao Notepad++:

- Organon_Script_Plugin.udl.xml: Define as regras de coloração de sintaxe (syntax highlighting), fazendo com que palavras-chave como DEMT, DLIN e comentários fiquem coloridas.

- Organon_AutoComplete.xml: Contém a lista de palavras que o Notepad++ sugere ao pressionar CTRL + Espaço, facilitando a escrita de comandos.

- organon.fts: Arquivo de snippets para o plugin FingerText. Define os templates de código, como a régua do DLIN, que são expandidos ao digitar uma palavra-chave e pressionar a tecla TAB.

- instalar_plugin.bat: Um script que automatiza todo o processo, copiando os arquivos de configuração para as pastas corretas do Notepad++ no seu perfil de usuário (%APPDATA%).

---

## Passo 1: Instalar o Plugin "FingerText" (Apenas uma vez)

Este plugin é essencial para os snippets (réguas) funcionarem.

1.  Abra o Notepad++.
2.  Vá para o menu **Plugins > Plugins Admin...**.
3.  Na aba **"Available"**, procure por **`FingerText`**.
4.  Marque a caixa de seleção ao lado dele e clique no botão **Install**.
5.  O Notepad++ irá reiniciar.

---

## Passo 2: Executar o Instalador

O script `instalar_plugin.bat` fará todo o trabalho de copiar os arquivos de configuração para os lugares certos.

1.  Certifique-se de que os arquivos `Organon_Script_Plugin.udl.xml`, `Organon_AutoComplete.xml` e `organon.fts` estão na mesma pasta que o `instalar_plugin.bat`.
2.  Dê um duplo-clique em **`instalar_plugin.bat`**.
3.  Siga as instruções na tela. O script fechará o Notepad++, copiará os arquivos e o abrirá novamente.

---

## Passo 3:  Como Usar e Testar as Ferramentas
Após a instalação, verifique se tudo está funcionando corretamente.

Teste 1: Coloração de Sintaxe
Abra um novo arquivo e digite os seguintes comandos. Eles devem aparecer coloridos:

DEMT

DLIN

BARRA

! Este é um comentário (a linha inteira deve mudar para a cor de comentário).

Teste 2: Autocompletar Palavras
Digite DGB e pressione a combinação de teclas CTRL + Espaço. Uma pequena janela deve aparecer sugerindo a palavra DGBT.

Teste 3: Snippets (Templates de Código)
Este é o recurso mais poderoso, ativado pelo FingerText.

Em uma nova linha, digite DLIN.

Pressione a tecla TAB.

A palavra DLIN será automaticamente substituída pela régua completa:



## Uso de Plugins de Snippets


1) FingerText: https://github.com/erinata/FingerText?tab=readme-ov-file
Como funciona? É baseado em gatilho + tecla de atalho. Você digita uma palavra-chave (o "gatilho", como DLIN) e pressiona uma tecla (geralmente TAB). O plugin então substitui o gatilho pelo snippet correspondente.

Vantagens: Muito rápido e eficiente para quem já sabe os gatilhos de cor. Não polui a interface, pois não há painéis visíveis. Os snippets são armazenados em arquivos de texto simples (.fts), o que os torna fáceis de editar e compartilhar.

Ideal para: Uso repetitivo de templates conhecidos.


### para gerar um .exe a partir do .bat (Opcional)

https://supertutoriais.com.br/pc/como-converter-arquivos-bat-exe-windows/

Criando o .exe com Iexpress
Este é o passo final para criar o seu instalador "tudo-em-um".

Abra o Iexpress: Pressione Win + R, digite iexpress e tecle Enter.

Novo Projeto: "Create new Self Extraction Directive file" -> Avançar.

Tipo de Pacote: "Extract files and run an installation command" -> Avançar.

Título: Instalador Organon para Notepad++ -> Avançar.

Confirmação/Licença: "No prompt" -> Avançar. "Do not display a license" -> Avançar.

Adicione os Arquivos: Clique em "Add" e adicione TODOS os arquivos e pastas da sua pasta de projeto, EXCETO o próprio .exe que você está criando. Isso inclui:

instalar_plugin.bat

organon_GLOBAL_MESTRE.sqlite (o seu arquivo mestre!)

Organon_Script_Plugin.udl.xml

Organon_AutoComplete.xml

A pasta FingerText - 0.5.60

A pasta npp_portable_V8

-> Avançar.

Comando de Instalação: No campo "Install Program", digite: instalar_plugin.bat. -> Avançar.

Janela: "Default (recommended)" -> Avançar.

Mensagem Final: "No message" -> Avançar.

Salvar o .exe: Escolha o nome e local para salvar seu Setup_Organon.exe. Marque a opção "Hide File Extracting Progress Animation". -> Avançar.

Reiniciar e Salvar: "No restart" -> Avançar. Salve o arquivo .sed para futuras edições. -> Avançar.

Criar Pacote: Clique em "Avançar" para compilar e em "Finish" para terminar.