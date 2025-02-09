import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QProgressBar
from PyQt5.QtCore import Qt
from common.common import FileRequest, FileResponse

# UDP settings
UDP_IP = "127.0.0.1"
UDP_PORT = 9991
FILE_BLOCK_SIZE = 1024
CONCURRENCY = 50

class FileTransferApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Transfer Client")

        # Layout
        self.layout = QVBoxLayout()

        # File path label and input field
        self.file_label = QLabel("File Path:", self)
        self.layout.addWidget(self.file_label)
        
        self.file_input = QLineEdit(self)
        self.file_input.setText("output.txt")
        self.layout.addWidget(self.file_input)

        # Progress bar
        self.progress_label = QLabel("Download Progress:", self)
        self.layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setOrientation(Qt.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        # Start button
        self.start_button = QPushButton("Start Download", self)
        self.start_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.start_button)

        # Status label
        self.status_label = QLabel("", self)
        self.layout.addWidget(self.status_label)

        # Set layout for the main window
        self.setLayout(self.layout)
        
        self.show()

    def send_request(self, file_req: FileRequest) -> FileResponse:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(file_req.to_json().encode('utf-8'), (UDP_IP, UDP_PORT))
        data, _ = sock.recvfrom(4096)
        return FileResponse.from_json(data.decode('utf-8'))

    def get_file_size(self) -> int:
        self.status_label.setText("Requesting file size...")
        file_req = FileRequest(start=float('inf'), end=float('inf'))
        file_resp = self.send_request(file_req)
        return file_resp.start

    def request_file_block(self, start: int, end: int) -> bytes:
        file_req = FileRequest(start=start, end=end)
        file_resp = self.send_request(file_req)
        return file_resp.content

    def save_file(self, save_path: str):
        file_size = self.get_file_size()
        total_blocks = (file_size + FILE_BLOCK_SIZE - 1) // FILE_BLOCK_SIZE

        with open(save_path, "wb") as file:
            with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
                futures = []
                for block_id in range(total_blocks):
                    start = block_id * FILE_BLOCK_SIZE
                    end = min(start + FILE_BLOCK_SIZE, file_size)
                    futures.append(executor.submit(self.request_file_block, start, end))

                for future in futures:
                    content = future.result()
                    file.write(content)
                    progress = int((futures.index(future) + 1) / total_blocks * 100)
                    self.progress_bar.setValue(progress)

                    # Process GUI updates
                    QApplication.processEvents()
                    logging.info(f"Saved block: {len(content)} bytes")

        logging.info(f"File saved to {save_path}")
        self.status_label.setText("Download Complete!")

    def start_download(self):
        save_path = self.file_input.text()
        self.status_label.setText("Starting download...")
        self.progress_bar.setValue(0)
        self.save_file(save_path)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    window = FileTransferApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
