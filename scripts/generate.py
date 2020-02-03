from core.utils import read_mapping, generate_file
from core.security import EncryptionUtil
from core.model import Assignment
from core.repository import Keystore, StudentsRepository, TasksRepository

encryption_util = EncryptionUtil(Keystore())

students = StudentsRepository()
tasks = TasksRepository()
mapping = read_mapping()

assignments = []

for (student_id, variant_id) in mapping.items():
    variant = tasks.get_tasks(variant_id)
    student = students.get_student(student_id)

    for task in variant:
        assignments.append(Assignment.generate_from_data(student, task, encryption_util.encrypt))

for assignment in assignments:
    generate_file(*assignment.generate())
