import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QProgressBar, QLabel, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

from config.config import Config
from data.data_manager import DataManager
from ops import cloud_ops


class UploadThread(QThread):
    progress = pyqtSignal(int)
    current_operation = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    upload_finished = pyqtSignal()

    def __init__(self, media_paths, media_list, data_manager: DataManager):
        super().__init__()
        self.media_paths = media_paths
        self.media_list = media_list
        self.data_manager = data_manager
        self._is_running = True

    def run(self):
        try:
            for i, media_path in enumerate(self.media_paths):
                if not self._is_running:
                    break

                media = self.media_list[i]
                thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, media.thumbnail_key)

                self.current_operation.emit(f"Medya bulut sistemine yükleniyor:\n\n{media_path}")
                try:
                    cloud_ops.upload_to_s3_bucket(path=media_path, key=media.media_key, prefix="media/")
                    cloud_ops.upload_to_s3_bucket(path=thumbnail_path, key=media.thumbnail_key, prefix="thumbnails/")

                except Exception as e:
                    self.error_occurred.emit(str(e))
                    return
                self.progress.emit((i + 1) * 80 // len(self.media_paths))

            try:
                self.current_operation.emit(f"Veri tabanı güncelleniyor...")
                success = self.data_manager.update_local_db()
                if not success:
                    raise ValueError("Bulut sistemine bağlantı sağlanamadı.")
                self.data_manager.insert_media_list_to_local(self.media_list)
                self.progress.emit(90)

                self.current_operation.emit(f"Veri tabanı yükleniyor...")
                cloud_ops.upload_to_s3_bucket(path=f"{Config.DATABASE_DIR}/album.db", key="album_cloud.db")

            except Exception as e:
                self.error_occurred.emit(str(e))
                return

            self.progress.emit(100)
            self.upload_finished.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False


class DialogUpload(QDialog):
    def __init__(self, media_paths, media_list, data_manager):
        super().__init__()
        self.media_paths = media_paths
        self.media_list = media_list
        self.data_manager = data_manager
        self.thread = None

        self.setWindowTitle("Medya Yükleme İlerlemesi")
        self.setFixedSize(400, 150)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Yükleme başlatılıyor...")
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.retry = False

        self.start_upload()

    def start_upload(self):
        self.progress_bar.setValue(0)
        self.thread = UploadThread(self.media_paths, self.media_list, self.data_manager)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.current_operation.connect(self.label.setText)
        self.thread.error_occurred.connect(self.show_error_dialog)
        self.thread.upload_finished.connect(self.upload_complete)
        self.thread.start()

    def upload_complete(self):
        self.accept()  # Close the dialog and return Accepted when upload finishes

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
            self.start_upload()  # Restart the upload process
        elif result == QMessageBox.Cancel:
            self.retry = False
            self.thread.stop()  # Ensure the thread is stopped
            self.reject()  # Close the dialog

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()  # Stop the thread if running
            self.thread.wait()  # Wait for the thread to finish
        super().closeEvent(event)
