import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from py_xsr import PyXStepRecorder, RecorderConfig


class LogSignalEmitter(QObject):
    """Isolated helper QObject dedicated solely to thread-safe signaling."""

    log_signal = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    """
    Pure Python logging handler. By avoiding multiple inheritance with QObject,
    it prevents C++ lifecycle teardown collisions when the application exits.
    """

    def __init__(self):
        super().__init__()
        self.emitter = LogSignalEmitter()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.log_signal.emit(msg)


class RecorderWorker(QThread):
    """Background worker thread executing the core recording loop."""

    finished_signal = pyqtSignal()

    def __init__(self, config: RecorderConfig):
        super().__init__()
        self.config = config
        self.recorder = None

    def run(self):
        self.recorder = PyXStepRecorder(cfg=self.config)
        self.recorder.start()
        self.finished_signal.emit()

    def stop_recording(self):
        if self.recorder:
            self.recorder._trigger_stop()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if hasattr(sys, "_MEIPASS"):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent

        uic.loadUi(str(base_path / "main_window.ui"), self)

        self.txt_output.setText(
            str(Path.home() / "Documents" / "steps_recorded" / "Steps_Recorded.html")
        )
        self.spin_quality.setValue(100)
        self.spin_quality.setRange(1, 100)
        self.toggle_cursor_inputs(False)

        self.txt_console.setPlaceholderText("System status logs will appear here...")
        self.txt_console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-size: 11px;
                border: 1px solid #333333;
                border-radius: 6px;
            }
        """)

        self.setup_logging()

        self.btn_browse_html.clicked.connect(self.browse_html_location)
        self.btn_browse_cursor.clicked.connect(self.browse_cursor_location)
        self.chk_custom_cursor.toggled.connect(self.toggle_cursor_inputs)
        self.btn_toggle.clicked.connect(self.handle_toggle_clicked)

        self.worker = None
        self.is_recording_active = False

    def setup_logging(self):
        """Attaches the thread-safe GUI handler directly to the core logging pipelines."""
        formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")

        self.qt_handler = QtLogHandler()
        self.qt_handler.setFormatter(formatter)
        self.qt_handler.emitter.log_signal.connect(self.append_log_message)

        self.submodule_logger = logging.getLogger("py_xsr")
        self.submodule_logger.setLevel(logging.INFO)
        self.submodule_logger.addHandler(self.qt_handler)

        self.app_logger = logging.getLogger("PyXSR_App")
        self.app_logger.setLevel(logging.INFO)
        self.app_logger.addHandler(self.qt_handler)

    def append_log_message(self, message: str):
        """Appends streaming logging data directly onto the console view panel."""
        self.txt_console.appendPlainText(message)

    def browse_html_location(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select HTML Report Destination",
            self.txt_output.text(),
            "HTML Files (*.html)",
        )
        if file_path:
            self.txt_output.setText(file_path)

    def browse_cursor_location(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Custom Cursor Image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg)",
        )
        if file_path:
            self.txt_cursor_path.setText(file_path)

    def toggle_cursor_inputs(self, checked: bool):
        self.txt_cursor_path.setEnabled(checked)
        self.btn_browse_cursor.setEnabled(checked)

    def handle_toggle_clicked(self):
        if not self.is_recording_active:
            self.start_recording_workflow()
        else:
            self.stop_recording_workflow()

    def start_recording_workflow(self):
        cursor_file = None
        if self.chk_custom_cursor.isChecked() and self.txt_cursor_path.text():
            cursor_file = Path(self.txt_cursor_path.text())

        config = RecorderConfig(
            outfile=Path(self.txt_output.text()),
            cursor_path=cursor_file,
            image_ext="jpg",
            quality=self.spin_quality.value(),
        )

        self.is_recording_active = True
        self.btn_toggle.setText("Stop Recording")
        self.set_inputs_enabled(False)
        self.txt_console.clear()

        self.app_logger.info("Initializing recorder interface workflow engine...")

        self.worker = RecorderWorker(config)
        self.worker.finished_signal.connect(self.on_recording_complete)
        self.worker.start()

    def stop_recording_workflow(self):
        self.btn_toggle.setEnabled(False)
        self.btn_toggle.setText("Compiling Report...")
        if self.worker:
            self.worker.stop_recording()

    def on_recording_complete(self):
        self.is_recording_active = False
        self.btn_toggle.setEnabled(True)
        self.btn_toggle.setText("Start Recording")
        self.set_inputs_enabled(True)

    def set_inputs_enabled(self, enabled: bool):
        self.txt_output.setEnabled(enabled)
        self.btn_browse_html.setEnabled(enabled)
        self.spin_quality.setEnabled(enabled)
        self.chk_custom_cursor.setEnabled(enabled)

        if enabled:
            self.toggle_cursor_inputs(self.chk_custom_cursor.isChecked())
        else:
            self.toggle_cursor_inputs(False)

    def closeEvent(self, event):
        """Safely detaches logging hooks from active channels upon system window close."""
        if hasattr(self, "submodule_logger") and hasattr(self, "qt_handler"):
            self.submodule_logger.removeHandler(self.qt_handler)

        if hasattr(self, "app_logger") and hasattr(self, "qt_handler"):
            self.app_logger.removeHandler(self.qt_handler)

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
