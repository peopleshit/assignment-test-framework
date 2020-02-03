import subprocess
from core.utils import read_mapping, parse_files, get_tests
from core.security import EncryptionUtil
from core.model import Assignment
from core.repository import Keystore, StudentsRepository, TasksRepository

files = parse_files()
encryption_util = EncryptionUtil(Keystore())

students = StudentsRepository()
tasks = TasksRepository()
mapping = read_mapping()

for identifier, path in parse_files().items():
    assignment = Assignment.generate_from_code(
        identifier, encryption_util.decrypt, students.get_student, tasks.get_task
    )

    if assignment is None:
        continue

    if mapping[assignment.student.identifier] != assignment.task.variant:
        print(f'Student: {assignment.student.get_name()} seems to have incorrect variant')
        continue

    tests = get_tests(assignment.task.variant, assignment.task.identifier)

    for test_input, test_output, runs in tests:
        unsuccessful_runs = 0
        for _ in range(runs):
            task = subprocess.Popen(['python3', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            for item in test_input:
                task.stdin.write(f'{item}\n')
                task.stdin.flush()

            output = task.stdout.read().split('\n')
            output.pop()
            task.stdin.close()

            if isinstance(test_output, str):
                test = subprocess.Popen(['python3', test_output], stdin=subprocess.PIPE, encoding='utf-8')

                for item in output:
                    test.stdin.write(f'{item}\n')
                    test.stdin.flush()

                test.stdin.close()
                returncode = test.wait(3000)

                if returncode != 0:
                    unsuccessful_runs += 1

            else:
                if len(test_output) != len(output):
                    unsuccessful_runs += 1
                else:
                    for i in range(len(test_output)):
                        if test_output[i] != output[i]:
                            unsuccessful_runs += 1
                            break

        print(assignment, path, f'{runs - unsuccessful_runs}/{runs}' )
