from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox
from media_loader import MediaLoader


class DownloadThread(QThread):
    current_operation = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    download_finished = pyqtSignal()

    def __init__(self, media_loader: MediaLoader, media_key):
        super().__init__()
        self._is_running = True
        self.media_loader = media_loader
        self.media_key = media_key

    def run(self):
        try:
            if not self._is_running:
                return

            self.current_operation.emit(f"İndirme işlemi devam ediyor...")
            try:
                self.media_loader.play_video_audio_from_cloud(self.media_key)
                
            except Exception as e:
                self.error_occurred.emit(str(e))
                return

            self.download_finished.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False


class DialogDownload(QDialog):
    def __init__(self, media_loader: MediaLoader, media_key):
        super().__init__()
        self.media_loader = media_loader
        self.media_key = media_key
        self.thread = None

        self.setWindowTitle("Medya İndirme İşlemi")
        self.setFixedSize(400, 100)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("İndirme başlatılıyor...")
        self.layout.addWidget(self.label)

        self.retry = False

        self.start_download()

    def start_download(self):
        self.thread = DownloadThread(self.media_loader, self.media_key)
        self.thread.current_operation.connect(self.label.setText)
        self.thread.error_occurred.connect(self.show_error_dialog)
        self.thread.download_finished.connect(self.download_complete)
        self.thread.start()

    def download_complete(self):
        self.accept()  # Close the dialog and return Accepted when the download finishes

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
            self.start_download()  # Restart the download process
        elif result == QMessageBox.Cancel:
            self.retry = False
            self.thread.stop()  # Ensure the thread is stopped
            self.reject()  # Close the dialog

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()  # Stop the thread if running
            self.thread.wait()  # Wait for the thread to finish
        super().closeEvent(event)
