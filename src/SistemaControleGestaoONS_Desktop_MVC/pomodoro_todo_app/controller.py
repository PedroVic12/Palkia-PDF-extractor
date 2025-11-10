from PySide6.QtCore import QObject, Signal, QTimer, Slot

class PomodoroController(QObject):
    def __init__(self, model, view):
        super().__init__()
        self._model = model
        self._view = view
        self._timer = QTimer()
        self._time_left = 25 * 60

        self._connect_signals()

        self.refresh_tasks()

    def _connect_signals(self):
        self._view.add_task_requested.connect(self.add_task)
        self._view.delete_task_requested.connect(self.delete_task)
        self._view.toggle_task_status_requested.connect(self.toggle_task_status)
        self._model.tasks_changed.connect(self.refresh_tasks)

        self._view.start_pomodoro_requested.connect(self.start_pomodoro)
        self._view.start_short_break_requested.connect(self.start_short_break)
        self._view.start_long_break_requested.connect(self.start_long_break)
        
        self._timer.timeout.connect(self.update_timer)

    @Slot(str)
    def add_task(self, description):
        self._model.add_task(description)

    @Slot(int)
    def delete_task(self, task_id):
        self._model.delete_task(task_id)

    @Slot(int, bool)
    def toggle_task_status(self, task_id, completed):
        self._model.update_task_status(task_id, completed)

    @Slot()
    def refresh_tasks(self):
        tasks = self._model.get_tasks()
        self._view.render_tasks(tasks)

    @Slot()
    def start_pomodoro(self):
        self.start_timer(25 * 60)

    @Slot()
    def start_short_break(self):
        self.start_timer(5 * 60)

    @Slot()
    def start_long_break(self):
        self.start_timer(15 * 60)

    def start_timer(self, duration):
        self._time_left = duration
        self._timer.start(1000)
        self.update_display()

    @Slot()
    def update_timer(self):
        if self._time_left > 0:
            self._time_left -= 1
            self.update_display()
        else:
            self._timer.stop()
            # Here you can add notification logic
            self._view.update_timer_display("00:00")
            
            # If it was a pomodoro cycle, increment the counter for the selected task
            if self._timer.interval() == 1000 and self._time_left == 0:
                current_item = self._view.task_list.currentItem()
                if current_item:
                    task_id = current_item.data(Qt.UserRole)
                    self._model.increment_pomodoro_cycle(task_id)


    def update_display(self):
        minutes = self._time_left // 60
        seconds = self._time_left % 60
        self._view.update_timer_display(f"{minutes:02d}:{seconds:02d}")
