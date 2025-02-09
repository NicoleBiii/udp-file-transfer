import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class FileRequest:
    start: int
    end: int

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str: str) -> 'FileRequest':
        data = json.loads(json_str)
        return FileRequest(start=data['start'], end=data['end'])


@dataclass
class FileResponse:
    content: Optional[bytes]
    start: int
    end: int
    md5_hash: str

    def to_json(self) -> str:
        return json.dumps({
            'content': self.content.decode('latin1') if self.content else None,
            'start': self.start,
            'end': self.end,
            'md5_hash': self.md5_hash,
        })

    @staticmethod
    def from_json(json_str: str) -> 'FileResponse':
        data = json.loads(json_str)
        return FileResponse(
            content=data['content'].encode('latin1') if data['content'] else None,
            start=data['start'],
            end=data['end'],
            md5_hash=data['md5_hash'],
        )
