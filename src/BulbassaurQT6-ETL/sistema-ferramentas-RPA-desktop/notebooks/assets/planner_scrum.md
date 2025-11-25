# Planner Scrum - Sprint de Hoje

Este é um plano de sprint diário baseado nas suas tarefas, organizado em um formato Kanban. Cada tarefa foi dimensionada para um ciclo de foco de 50 minutos (Pomodoro).

**Foco do Dia:** Backend Python e Estudos de SEP (Sistemas Elétricos de Potência).

---

## Quadro Kanban do Dia

| Prioridade | Tarefa (Foco) | Detalhamento da Ação (Ciclo de 50 min) | Status |
| :--- | :--- | :--- | :--- |
| 🔴 **Alta** | `FLASK CRUD: Modelagem SQL` | No seu `PikachuWebServer`, defina a tabela `Client` (ou `Task_Log`) usando SQLAlchemy. Teste a criação da tabela no seu `app.db`. | `Para Fazer` |
| 🔴 **Alta** | `FLASK CRUD: Rotas API` | Crie os endpoints `POST /clients` (Criação) e `GET /clients` (Leitura) na sua Blueprint `user_bp`. | `Para Fazer` |
| 🟡 **Média** | `TEORIA: Matriz Y-Bus` | TEORIA PURA (Stevenson): Finalizar a montagem da Matriz Y-Bus 3x3 em papel (conforme sua meta de 2 equações/dia). | `Para Fazer` |
| 🟡 **Média** | `CÓDIGO: ybus_solver.py` | Iniciar o código Python. Codificar a representação da Matriz Y-Bus 3x3 em NumPy com números complexos (transformar a teoria do papel em código). | `Para Fazer` |
| 🟢 **Baixa** | `DOCUMENTAÇÃO: IEDs` | Criar o novo arquivo `.md` (ex: `ieds_log.md`) e salvar a lógica de MQTT/LED/Buzzer que você aprendeu ontem. | `Para Fazer` |

---

## Backlog de Épicos (Tarefas Maiores)

Estas são as outras tarefas importantes que você listou para hoje. Elas podem ser quebradas em ciclos de 50 minutos nos próximos dias ou quando você finalizar o sprint de hoje.

| Prioridade | Épico | Estimativa (Ciclos de 50 min) |
| :--- | :--- | :--- |
| 🔴 **Alta** | `PySide6`: Integrar menu com leitura de `INSTRUCOES.md` | ~2-3 Ciclos |
| 🟡 **Média** | `Next.js`: Criar `start.sh` + Docker-compose para o MVP | ~3-4 Ciclos |

### Como Usar:
1.  Mova uma tarefa de `Para Fazer` para `Em Andamento` quando iniciar um ciclo de 50 minutos.
2.  Ao final do ciclo, mova-a para `Concluído`.
3.  Faça uma pausa de 10 minutos antes de começar o próximo ciclo.
