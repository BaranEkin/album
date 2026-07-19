from PyQt5.QtCore import QEventLoop, QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox


class ProcessThread(QThread):
    current_operation = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    process_finished = pyqtSignal()

    def __init__(self, operation, operation_args=None, message=""):
        super().__init__()
        self._is_running = True
        self.operation = operation
        self.operation_args = operation_args or ()
        self.message = message

    def run(self):
        try:
            if not self._is_running:
                return

            self.current_operation.emit(self.message)
            try:
                # Run the operation with provided arguments
                self.operation(*self.operation_args)

            except Exception as e:
                self.error_occurred.emit(str(e))
                return

            self.process_finished.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False


class ResultThread(QThread):
    finished_ok = pyqtSignal(object)
    finished_error = pyqtSignal(str)

    def __init__(self, operation, operation_args=None):
        super().__init__()
        self.operation = operation
        self.operation_args = operation_args or ()

    def run(self):
        try:
            result = self.operation(*self.operation_args)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.finished_error.emit(str(exc))


def _make_wait_dialog(parent, message, title):
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setWindowIcon(
        QIcon("res/icons/Chat-Bubble-Square-Warning--Streamline-Core.png")
    )
    dialog.setWindowFlags(
        dialog.windowFlags()
        & ~Qt.WindowCloseButtonHint
        & ~Qt.WindowContextHelpButtonHint
    )
    dialog.setFixedSize(400, 100)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel(message))
    dialog.setModal(True)
    return dialog


def run_with_delayed_wait(
    parent,
    operation,
    operation_args=None,
    message="",
    title="",
    delay_ms=2000,
):
    """
    Run operation in a worker thread. If it still runs after delay_ms,
    show a non-closable wait dialog. Returns the operation result.
    """
    operation_args = operation_args or ()
    loop = QEventLoop(parent)
    state = {"result": None, "error": None, "dialog": None, "finished": False}

    thread = ResultThread(operation=operation, operation_args=operation_args)

    def finish_ok(value):
        state["result"] = value
        state["finished"] = True
        timer.stop()
        if state["dialog"] is not None:
            state["dialog"].accept()
        loop.quit()

    def finish_error(error_message):
        state["error"] = error_message
        state["finished"] = True
        timer.stop()
        if state["dialog"] is not None:
            state["dialog"].reject()
        loop.quit()

    def show_wait_dialog():
        if state["finished"] or state["dialog"] is not None:
            return
        state["dialog"] = _make_wait_dialog(parent, message, title)
        state["dialog"].show()

    thread.finished_ok.connect(finish_ok)
    thread.finished_error.connect(finish_error)

    timer = QTimer(parent)
    timer.setSingleShot(True)
    timer.timeout.connect(show_wait_dialog)

    thread.start()
    timer.start(delay_ms)
    loop.exec_()
    thread.wait()

    if state["dialog"] is not None:
        state["dialog"].deleteLater()

    if state["error"] is not None:
        raise RuntimeError(state["error"])
    return state["result"]


class DialogProcess(QDialog):
    def __init__(self, operation, operation_args=None, message="", title=""):
        super().__init__()
        self.operation = operation
        self.operation_args = operation_args or ()
        self.message = message
        self.setWindowTitle(title)
        self.setWindowIcon(
            QIcon("res/icons/Chat-Bubble-Square-Warning--Streamline-Core.png")
        )
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowCloseButtonHint
            & ~Qt.WindowContextHelpButtonHint
        )
        self.setFixedSize(400, 100)

        self.layout = QVBoxLayout(self)

        self.label = QLabel(self.message)
        self.layout.addWidget(self.label)

        self.retry = False

        self.start_process()

    def start_process(self):
        self.thread = ProcessThread(
            operation=self.operation,
            operation_args=self.operation_args,
            message=self.message,
        )
        self.thread.current_operation.connect(self.label.setText)
        self.thread.error_occurred.connect(self.show_error_dialog)
        self.thread.process_finished.connect(self.process_complete)
        self.thread.start()

    def process_complete(self):
        self.accept()

    def show_error_dialog(self, error_message):
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(f"An error occurred: {error_message}")
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        error_dialog.setDefaultButton(QMessageBox.Retry)

        result = error_dialog.exec_()
        if result == QMessageBox.Retry:
            self.retry = True
            self.thread.stop()  # Stop the current thread if it's still running
            self.thread.wait()  # Wait for the thread to properly stop
            self.start_process()  # Restart the process
        elif result == QMessageBox.Cancel:
            self.retry = False
            self.thread.stop()  # Ensure the thread is stopped
            self.reject()  # Close the dialog

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()  # Stop the thread if running
            self.thread.wait()  # Wait for the thread to finish
        super().closeEvent(event)
