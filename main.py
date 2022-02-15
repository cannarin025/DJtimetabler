import pandas as pd
from typing import List, Tuple
from classes import Tutor, Student

tutors: List[Tutor] = [
    Tutor("Can", genres=["EDM", "Commercial"], available_times=["19-22"], requested_schedule={20: ['patrick', 'konrad', 'priam']}),
    Tutor("Zhengli", genres=["Commercial"], available_times=["19-22"], requested_schedule={19: ['claudia', 'matija', 'steph']}),
    #Tutor("Suley", genres=["Underground"], available_times=['19-21']),
    Tutor("Nico", genres=["Underground"], available_times=['19-21'])
    #Tutor("Zhengli", genres=["Commercial"], available_times=["19-22"]),
    #Tutor("Nico", genres=["Underground"], available_times=['19-21'])
]

students: List[Student] = []
df = pd.read_csv('./responses.csv')
for index, row in df.iterrows():
    name = row['Name'].strip()
    pref_tutors = list(filter(lambda t: t.name in [row['Preferred tutor'].strip()], tutors))
    available_times = [(int(x.split(':')[0]) for x in time.split('-')) for time in row["Available times (select all possible times for best chance of getting a slot)"].split(",")]
    pref_genres = [row["Preferred genres"].split(" ")[0].strip()]
    students.append(Student(name, pref_tutors, available_times, pref_genres))

MAX_STUDENTS = 3

schedule = {t: {} for t in tutors}

prev_clashes = []

def assign_tutor(time: str, tutor: Tutor, student: Student):
    if time in tutor.schedule.keys() and len(tutor.schedule[time]) < MAX_STUDENTS:
        tutor.schedule[time].append(student)
        return True
    else:
        return False

def get_preferred_tutors(student: Student):
    """A function that returns all of a student's preferred tutors who are available at suitable times"""
    suitable_pref_tutors = []
    pref_tutors = student.pref_tutors
    student_times = [t for time_ranges in student.available for t in time_ranges]
    for tutor in pref_tutors:
        tutor_times = [t for time_ranges in tutor.available for t in time_ranges]
        for time in student_times:
            if time in tutor_times:
                suitable_pref_tutors.append(tutor)
                break
    return suitable_pref_tutors

def get_suitable_tutors(student: Student):
    """A function that returns all tutors sharing genres with student who are available at suitable times"""
    suitable_tutors = []
    matching_tutors = list(filter(lambda t: any(g in t.genres for g in student.genres), tutors))
    student_times = [t for time_ranges in student.available for t in time_ranges]
    for tutor in matching_tutors:
        tutor_times = [t for time_ranges in tutor.available for t in time_ranges]
        for time in student_times:
            if time in tutor_times:
                suitable_tutors.append(tutor)
                break
    return suitable_tutors

def attempt_assignment(student: Student, tutor_list: List[Tutor]):
    """A function that attempts to assign a student to the first available tutor in a list"""
    global prev_clashes
    student_times = [t for time_ranges in student.available for t in time_ranges]
    for tutor in tutor_list:
        for time in student_times:
            assigned = assign_tutor(time, tutor, student)
            if assigned:
                return assigned  # student has been booked onto session with tutor
            elif time in tutor.schedule.keys() and student not in tutor.schedule[time] and student not in prev_clashes: # tutor available but full at this time, attempt to move previous student to make space
                clashes = tutor.schedule[time]
                for clash in clashes:
                    if clash.movable:
                        prev_clashes.append(clash)
                        clash_resolved = assign_suitable_tutor(clash)
                        if clash_resolved:
                            prev_clashes = []
                            tutor.schedule[time].remove(clash)
                            assigned = assign_tutor(time, tutor, student)
                            return assigned

    return assigned  # no matching time between the student and any suitable tutors could be found


def assign_suitable_tutor(student: Student):
    """A function that attempts to assign a student to a suitable tutor based on tutor and genre preferences"""
    tutors = get_preferred_tutors(student)
    if not tutors:
        tutors = get_suitable_tutors(student)
        if not tutors:
            return False # no suitable tutors could be found
    assigned = attempt_assignment(student, tutors)
    return assigned

def get_all_assigned():
    assigned = []
    for t in tutors:
        for students in t.schedule.values():
            if students:
                [assigned.append(s) for s in students]
    return assigned

not_assigned = []
# Initial assignment
[t.assign_requested_timetable(students) for t in tutors]
pre_assigned = get_all_assigned()
for student in students:
    if student not in pre_assigned:
        assigned = assign_suitable_tutor(student)
        if not assigned:
            not_assigned.append(student)

for tutor in tutors:
    print(f"{tutor.name}'s schedule:")
    for time in tutor.schedule.keys():
        print(f"Time: {time}: {[s.name for s in tutor.schedule[time]]}")

print(f"Not assigned: {[s.name for s in not_assigned]}")