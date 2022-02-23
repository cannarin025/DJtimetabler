import pandas as pd
from typing import List, Tuple, Union
from classes import Tutor, Student, Slot

tutors: List[Tutor] = [
    Tutor("Zhengli", genres=["Commercial"], available_times=["19-22"], requested_schedule={19: ['claudia', 'matija', 'steph']}),
    Tutor("Can", genres=["EDM", "Commercial"], available_times=["19-22"], requested_schedule={20: ['patrick', 'konrad', 'priam']}),
    Tutor("Suley", genres=["Underground"], available_times=['19-22']),
    Tutor("Nico", genres=["Underground"], available_times=['19-22']),
    #Tutor("Chris", genres=["Underground"], available_times=["19-21"])
    #Tutor("Nico", genres=["Underground"], available_times=['19-21'])
]

students: List[Student] = []
df = pd.read_csv('./responses.csv')
for index, row in df.iterrows():
    name = row['Full name'].strip()
    pref_tutors = list(filter(lambda t: t.name in [row['Preferred tutor'].strip()], tutors))
    available_times = [(int(x.split(':')[0]) for x in time.split('-')) for time in row["Available times"].split(",")]
    pref_genres = [row["Preferred genres"].split(" ")[0].strip()]
    skill_level = row["Experience level"].split(' ')[0]
    students.append(Student(name, pref_tutors, available_times, pref_genres, skill_level))

MAX_STUDENTS = 3

schedule = {t: {} for t in tutors}

prev_clashes = []

def assign_tutor(time: str, tutor: Tutor, student: Student):
    if time in tutor.schedule.keys() and len(tutor.schedule[time]) < MAX_STUDENTS:
        tutor.schedule[time].append(student)
        return True
    else:
        return False

def get_available_times(obj: Union[Student, Tutor]):
    return [t for time_ranges in obj.available for t in time_ranges]

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

def get_best_slots(student) -> List[Slot]:
    '''A function to return a list of all matching slots between a student and tutors regardless of available space'''
    student_times = get_available_times(student)
    pref_tutors = get_preferred_tutors(student)
    suitable_tutors = get_suitable_tutors(student)
    tutor_list = []
    for tutor in pref_tutors + suitable_tutors:
        if tutor not in tutor_list:
            tutor_list.append(tutor)
    priority1, priority2, priority3, priority4, priority5, priority6 = ([],[],[],[],[],[])
    for tutor in tutor_list:
        for time in get_available_times(tutor):
            if time in student_times:
                # all students in session with preferred tutor are of same skill level
                if all(
                    current_student.skill_level in student.skill_level
                    for current_student in tutor.schedule[time]
                ) and tutor in student.pref_tutors:
                    priority1.append(Slot(tutor, time))
                # some students in session with preferred tutor are of same skill level
                elif any(
                    current_student.skill_level in student.skill_level
                    for current_student in tutor.schedule[time]
                ) and tutor in student.pref_tutors:
                    priority2.append(Slot(tutor, time))
                # tutor is preferred tutor
                elif tutor in student.pref_tutors:
                    priority3.append(Slot(tutor, time))
                # all students in session with suitable tutor are of same skill level
                elif all(
                    current_student.skill_level in student.skill_level
                    for current_student in tutor.schedule[time]
                ):
                    priority4.append(Slot(tutor, time))
                # some students in session with suitable tutor are of same skill level
                elif any(
                    current_student.skill_level in student.skill_level
                    for current_student in tutor.schedule[time]
                ):
                    priority5.append(Slot(tutor, time))
                # no students in session with suitable tutor are of same skill level
                else:
                    priority6.append(Slot(tutor,time))
    return priority1+priority2+priority3+priority4+priority5+priority6

def attempt_assignment(student: Student):
    """A function that attempts to assign a student to the first available tutor in a list"""
    global prev_clashes
    slots = get_best_slots(student)
    for slot in get_best_slots(student):
        if assign_tutor(slot.time, slot.tutor, student):
            return True  # student has been booked onto session with tutor
        elif len(slot.tutor.schedule[slot.time]) >= MAX_STUDENTS and student not in slot.tutor.schedule[slot.time] and student not in prev_clashes: # tutor available but full at this time, attempt to move previous student to make space
                clashes = slot.tutor.schedule[slot.time]
                for clash in clashes:
                    if clash.movable:
                        prev_clashes.append(clash)
                        clash_resolved = attempt_assignment(clash)
                        if clash_resolved:
                            prev_clashes = []
                            slot.tutor.schedule[slot.time].remove(clash)
                            return assign_tutor(slot.time, slot.tutor, student)

    return False  # no matching time between the student and any suitable tutors could be found

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
        assigned = attempt_assignment(student)
        if not assigned:
            not_assigned.append(student)

for tutor in tutors:
    print(f"{tutor.name}'s schedule:")
    for time in tutor.schedule.keys():
        print(f"Time: {time}: {[s.name for s in tutor.schedule[time]]}")

print(f"Not assigned: {[s.name for s in not_assigned]}")