import pytest
import requests
from lib.log import log
from main import main as server_main
address = "http://localhost:5000"

import threading
import time
server_thread = threading.Thread(target=server_main)
server_thread.start()
time.sleep(3)


class TestApi:
    class TestApiUser:
        def test_right(self):
            item = requests.get(address + "/api/user/1")
            log.debug(item.content)
            assert item.ok
            assert server_thread.is_alive()

        def test_wrong_id(self):
            item = requests.get(address + "/api/user/999")
            assert not item.ok
            assert server_thread.is_alive()

        def test_wrong_id_type(self):
            item = requests.get(address + "/api/user/aba")
            assert not item.ok
            assert server_thread.is_alive()

    class TestApiUsers:
        def test_right(self):
            item = requests.get(address + "/api/users")
            log.debug(item.content)
            assert item.ok
            assert server_thread.is_alive()

        def test_wrong_url(self):
            item = requests.get(address + "/api/users/1")
            assert not item.ok
            assert server_thread.is_alive()

    class TestApiNote:
        def test_right(self):
            item = requests.get(address + "/api/note/1")
            log.debug(item.content)
            assert item.ok
            assert server_thread.is_alive()

        def test_wrong_id(self):
            item = requests.get(address + "/api/note/999")
            assert not item.ok
            assert server_thread.is_alive()

        def test_wrong_id_type(self):
            item = requests.get(address + "/api/note/aba")
            assert not item.ok
            assert server_thread.is_alive()

    class TestApiNotes:
        def test_right(self):
            item = requests.get(address + "/api/notes")
            assert item.ok
            assert server_thread.is_alive()

        def test_wrong_url(self):
            item = requests.get(address + "/api/notes/1")
            assert not item.ok
            assert server_thread.is_alive()
