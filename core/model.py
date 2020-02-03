from typing import Optional


class Student(object):
    def __init__(self, identifier: int, last_name: str, first_name: str, middle_name: str = None):
        self.identifier = identifier
        self.__last_name = last_name
        self.__first_name = first_name
        self.__middle_name = middle_name

    def get_name(self) -> str:
        return f'{self.__last_name} {self.__first_name}' \
               f'{" " + self.__middle_name if self.__middle_name is not None else ""}'


class Task(object):
    def __init__(self, variant: int, identifier: int, text: str):
        self.__variant = variant
        self.__identifier = identifier
        self.__text = text

    @property
    def variant(self):
        return self.__variant

    @property
    def identifier(self):
        return self.__identifier

    @property
    def text(self):
        return self.__text


class Assignment(object):
    def __init__(self, student: Student, task: Task, identifier: str):
        self.__student = student
        self.__task = task
        self.__identifier = identifier

    @property
    def student(self):
        return self.__student

    @property
    def task(self):
        return self.__task

    @classmethod
    def generate_from_data(
            cls: callable, student: Student, task: Task, encrypt_function: callable) -> 'Assignment':
        identifier = encrypt_function(f'{student.identifier}-{task.variant}-{task.identifier}')
        return cls(student, task, identifier)

    @classmethod
    def generate_from_code(
            cls, identifier: str, decrypt_function: callable,
            students_function: callable, tasks_function: callable) -> Optional['Assignment']:
        student_identifier, task_variant, task_identifier = decrypt_function(identifier).split('-')

        try:
            student = students_function(int(student_identifier))
            task = tasks_function(int(task_variant), int(task_identifier))
        except ValueError:
            return None

        return None if student is None or task is None else cls(student, task, identifier)

    def generate(self) -> tuple:
        return self.__student.get_name(), \
               self.__task.identifier, \
               f'Студент: {self.__student.get_name()}\nВариант: {self.__identifier}\n{self.__task.text}'
