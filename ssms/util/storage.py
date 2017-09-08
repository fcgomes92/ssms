import os

import re

import uuid

import io

import mimetypes


class SimpleBaseStore(object):
    _CHUNK_SIZE_BYTES = 4096
    _NAME_PATTERN = re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{2,4}$'
    )

    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        self._storage_path = storage_path
        self._uuidgen = uuidgen
        self._fopen = fopen

        # creates the storage path if doesn't exist
        os.makedirs(storage_path, exist_ok=True)

    def save_stream(self, file_stream, file_content_type):
        ext = mimetypes.guess_all_extensions(file_content_type)[-1]
        name = '{uuid}{ext}'.format(uuid=self._uuidgen(), ext=ext)
        file_path = os.path.join(self._storage_path, name)

        with self._fopen(file_path, 'wb') as file:
            while True:
                chunk = file_stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                file.write(chunk)
        return name

    def save_data(self):
        pass

    def save_url(self):
        pass

    def open(self, name):
        # Always validate untrusted input!
        if not self._NAME_PATTERN.match(name):
            raise IOError('File not found')

        file_path = os.path.join(self._storage_path, name)
        stream = self._fopen(file_path, 'rb')
        stream_len = os.path.getsize(file_path)

        return stream, stream_len
