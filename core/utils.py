import errno
import sys
from re import compile
from os import makedirs, walk, listdir
from os.path import isfile, exists, dirname
from csv import reader

from core import constants
from core.model import Student, Task


VARIANT = '# Вариант:'
regex = compile(r'# Вариант:*')


class as_stdin:
    def __init__(self, buffer):
        self.buffer = buffer()
        self.original_stdin = sys.stdin

    def __enter__(self):
        sys.stdin = next(self.buffer)

    def __exit__(self, *exc):
        sys.stdin = self.original_stdin


def read_key():
    f = open(constants.KEY_PATH)
    key = f.readline().strip()
    f.close()

    return key


def write_key(key):
    with open(constants.KEY_PATH, 'w') as f:
        f.write(key)


def has_key() -> bool:
    return isfile(constants.KEY_PATH)


def read_students() -> list:
    if not isfile(constants.STUDENTS_PATH):
        return []

    f = open(constants.STUDENTS_PATH)
    student_reader = reader(f, delimiter=',')

    students = [
        Student(
            identifier=int(student_line[constants.STUDENT_ID]),
            last_name=student_line[constants.STUDENT_LAST_NAME],
            first_name=student_line[constants.STUDENT_FIRST_NAME],
            middle_name=student_line[constants.STUDENT_MIDDLE_NAME] if len(student_line) == 4 else None
        )
        for student_line in student_reader
    ]

    f.close()

    return students


def read_tasks() -> list:
    f = open(constants.TASKS_PATH)

    tasks_reader = reader(f, delimiter='/')

    tasks = [
        Task(
            variant=int(task_line[constants.TASK_VARIANT]),
            identifier=int(task_line[constants.TASK_ID]),
            text=task_line[constants.TASK_TEXT]
        )
        for task_line in tasks_reader
    ]

    f.close()

    return tasks


def read_mapping() -> dict:
    f = open(constants.MAPPING_PATH)

    mapping_reader = reader(f, delimiter=',')

    mapping = dict(
        [
            (int(mapping_line[constants.MAPPING_STUDENT]), int(mapping_line[constants.MAPPING_VARIANT]))
            for mapping_line in mapping_reader
        ]
    )

    return mapping


def generate_file(name: str, task: int, text: str):
    path = f'{constants.ASSIGNMENTS_PATH}/{name}/{task}.py'
    directory = dirname(path)

    if not exists(directory):
        try:
            makedirs(directory)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(path, 'w') as f:
        f.write('#! /usr/bin/env python\n')
        f.write('# -*- coding: utf-8 -*-\n')

        for line in text.split(sep='\n'):
            for subline in line.split(sep='\\n'):
                f.write(f'# {subline}\n')

        f.write(f'# {constants.TEXT_SOLUTION_BELOW}\n')


def parse_files() -> dict:
    paths = []

    for root, dirs, files in walk(constants.ASSIGNMENTS_PATH):
        for file in files:
            if file.lower().endswith('.py'):
                paths.append(f'{root}/{file}')

    files = dict()

    for file in paths:
        with open(file) as f:
            for line in f:
                if regex.match(line):
                    identifier = line.strip(f'{VARIANT} ').rstrip('\n')
                    files[identifier] = file
                    break

    return files


def get_tests(variant: int, task: int) -> list:
    count = sum([len(files) for r, d, files in walk(f'{constants.TESTS_PATH}/{variant}/')]) // 2

    if count == 0:
        return []
    elif count == 1:
        return [get_test(variant, task)]
    else:
        return [get_test(variant, task, test) for test in range(count)]


def get_test(variant: int, task: int, test: int = None) -> tuple:
    path = f'{constants.TESTS_PATH}/{variant}/{task}{f"-{test}" if test is not None else ""}'

    _input = []
    output = None
    runs = 1

    try:
        with open(f'{path}.input') as f:
            for line in f:
                _input.append(line.strip())

        if exists(f'{path}.output'):
            output = []
            with open(f'{path}.output') as f:
                for line in f:
                    output.append(line.strip())
        elif exists(f'{path}.py'):
            output = f'{path}.py'
            runs = constants.TEST_RUNS
        else:
            raise FileNotFoundError('No output file or script found')
    except ValueError:
        pass

    return _input, output, runs
