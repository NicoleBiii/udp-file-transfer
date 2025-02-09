import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from common.common import FileRequest, FileResponse


UDP_IP = "127.0.0.1"
UDP_PORT = 9991
FILE_BLOCK_SIZE = 1024
CONCURRENCY = 50


def send_request(file_req: FileRequest) -> FileResponse:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(file_req.to_json().encode('utf-8'), (UDP_IP, UDP_PORT))
    data, _ = sock.recvfrom(4096)
    return FileResponse.from_json(data.decode('utf-8'))


def get_file_size() -> int:
    logging.info("Requesting file size")
    file_req = FileRequest(start=float('inf'), end=float('inf'))
    file_resp = send_request(file_req)
    return file_resp.start


def request_file_block(start: int, end: int) -> bytes:
    file_req = FileRequest(start=start, end=end)
    file_resp = send_request(file_req)
    return file_resp.content


def save_file(save_path: str):
    file_size = get_file_size()
    total_blocks = (file_size + FILE_BLOCK_SIZE - 1) // FILE_BLOCK_SIZE

    with open(save_path, "wb") as file:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
            futures = []
            for block_id in range(total_blocks):
                start = block_id * FILE_BLOCK_SIZE
                end = min(start + FILE_BLOCK_SIZE, file_size)
                futures.append(executor.submit(request_file_block, start, end))

            for future in futures:
                content = future.result()
                file.write(content)
                logging.info(f"Saved block: {len(content)} bytes")

    logging.info(f"File saved to {save_path}")


if __name__ == "__main__":
    save_file("output.txt")
