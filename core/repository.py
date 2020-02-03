import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

from core.constants import PASS
from core.model import Student, Task
from core.utils import read_students, read_tasks, read_key, write_key, has_key


class StudentsRepository(object):
    def __init__(self):
        self.students = read_students()

    def get_student(self, identifier: int) -> Optional[Student]:
        try:
            return next(student for student in self.students if student.identifier == identifier)
        except StopIteration:
            return None


class TasksRepository(object):
    def __init__(self):
        self.__tasks = read_tasks()

    def get_tasks(self, variant: int) -> list:
        return [task for task in self.__tasks if task.variant == variant]

    def get_task(self, variant: int, identifier: int) -> Optional[Task]:
        try:
            return next(task for task in self.__tasks if task.variant == variant and task.identifier == identifier)
        except StopIteration:
            return None


class Keystore(object):
    def __init__(self):
        key_present = has_key()
        self.__key = read_key() if key_present else _generate_key()

        if not key_present:
            write_key(self.__key.decode())

    def execute(self, func: callable, *args) -> any:
        return func(self.__key, *args)


def _generate_key() -> any:
    password = PASS.encode()

    salt = bytes(os.urandom(16))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return base64.urlsafe_b64encode(kdf.derive(password))
