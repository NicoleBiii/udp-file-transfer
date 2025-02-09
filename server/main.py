
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import hashlib
from common.common import FileRequest, FileResponse
import socket


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


UDP_IP = "0.0.0.0"
UDP_PORT = 9991
FILE_PATH = "bible.txt"


def calculate_md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def handle_request(file_req: FileRequest, file) -> FileResponse:
    file.seek(file_req.start)
    content = file.read(file_req.end - file_req.start)
    md5_hash = calculate_md5(content)
    return FileResponse(content=content, start=file_req.start, end=file_req.end, md5_hash=md5_hash)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    logging.info(f"Server started on {UDP_IP}:{UDP_PORT}")

    with open(FILE_PATH, "rb") as file:
        file_size = file.seek(0, 2)
        logging.info(f"File size: {file_size} bytes")

        while True:
            data, addr = sock.recvfrom(4096)
            logging.info(f"Received request from {addr}")

            try:
                file_req = FileRequest.from_json(data.decode('utf-8'))
                logging.info(f"Request: start={file_req.start}, end={file_req.end}")

                if file_req.start == file_req.end == float('inf'):
                    file_resp = FileResponse(content=None, start=file_size, end=file_size, md5_hash="file_size")
                else:
                    file_resp = handle_request(file_req, file)

                sock.sendto(file_resp.to_json().encode('utf-8'), addr)
                logging.info(f"Sent response to {addr}")
            except Exception as e:
                logging.error(f"Error handling request: {e}")


if __name__ == "__main__":
    main()
