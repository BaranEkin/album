from PyQt5.QtCore import QThread, pyqtSignal, Qt
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


class DialogProcess(QDialog):
    def __init__(self, operation, operation_args=None, message="", title=""):
        super().__init__()
        self.operation = operation
        self.operation_args = operation_args or ()
        self.message = message
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("res/icons/Chat-Bubble-Square-Warning--Streamline-Core.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowContextHelpButtonHint)
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
            message=self.message
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
