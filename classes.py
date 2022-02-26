from typing import List, Tuple, Dict, Union
from dataclasses import dataclass

class Tutor:
    def __init__(self, name: str, available_times: List[str], genres: List[str], requested_schedule: Dict[int, List[str]] = None):
        availability: List[Tuple[int, int]] = [(int(times.split("-")[0]), int(times.split("-")[1])) for times in available_times]
        self.name = name
        self.available = [range(s, e) for s, e in availability]
        self.genres = genres
        self.requested_schedule = requested_schedule
        self.schedule = {t: [] for time_ranges in self.available for t in time_ranges}

    def assign_requested_timetable(self, student_list):
        if self.requested_schedule:
            for t, names in zip(self.requested_schedule.keys(), self.requested_schedule.values()):
                for name in names:
                    for student in student_list:
                        if name.upper() == student.name.upper():
                            self.schedule[t].append(student)
                            student.movable = False
            

class Student:
    def __init__(self, name: str, pref_tutors: List[Tutor], availability: List[Tuple[int, int]], genres: List[str], skill_level) -> None:
        self.name = name
        self.available = [range(s, e) for s, e in availability]
        self.pref_tutors: List[Tutor] = pref_tutors
        self.genres = genres
        self.skill_level = skill_level
        self.movable = True

@dataclass
class Slot:
    tutor: Tutor
    time: int

class DJtimetabler:
    not_assigned = []
    prev_clashes = []

    def __init__(self, students: List[Student], tutors: List[Tutor], max_students: int):
        self.students = students
        self.tutors = tutors
        self.max_students = max_students
        self.schedule = {t: {} for t in self.tutors}
        self.make_timetable()
    
    def __repr__(self) -> str:
        outstr = ''
        for tutor in self.tutors:
            outstr += f"{tutor.name}'s schedule:\n"
            for time in tutor.schedule.keys():
                outstr += f"Time: {time}: {[s.name for s in tutor.schedule[time]]}\n"

        outstr += f"Not assigned: {[s.name for s in self.not_assigned]}\n"
        return outstr

    def assign_tutor(self, time: str, tutor: Tutor, student: Student):
        if time in tutor.schedule.keys() and len(tutor.schedule[time]) < self.max_students:
            tutor.schedule[time].append(student)
            return True
        else:
            return False

    def get_available_times(self, obj: Union[Student, Tutor]):
        return [t for time_ranges in obj.available for t in time_ranges]

    def get_preferred_tutors(self, student: Student):
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

    def get_suitable_tutors(self, student: Student):
        """A function that returns all tutors sharing genres with student who are available at suitable times"""
        suitable_tutors = []
        matching_tutors = list(filter(lambda t: any(g in t.genres for g in student.genres), self.tutors))
        student_times = [t for time_ranges in student.available for t in time_ranges]
        for tutor in matching_tutors:
            tutor_times = [t for time_ranges in tutor.available for t in time_ranges]
            for time in student_times:
                if time in tutor_times:
                    suitable_tutors.append(tutor)
                    break
        return suitable_tutors

    def get_best_slots(self, student) -> List[Slot]:
        '''A function to return a list of all matching slots between a student and tutors regardless of available space'''
        student_times = self.get_available_times(student)
        pref_tutors = self.get_preferred_tutors(student)
        suitable_tutors = self.get_suitable_tutors(student)
        tutor_list = []
        for tutor in pref_tutors + suitable_tutors:
            if tutor not in tutor_list:
                tutor_list.append(tutor)
        priority1, priority2, priority3, priority4, priority5, priority6 = ([],[],[],[],[],[])
        for tutor in tutor_list:
            for time in self.get_available_times(tutor):
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

    def attempt_assignment(self, student: Student) -> bool:
        """A function that attempts to assign a student to a list of slots in order of suitability and recursively deals with clashes"""
        global prev_clashes
        slots = self.get_best_slots(student)
        for slot in self.get_best_slots(student):
            if self.assign_tutor(slot.time, slot.tutor, student):
                return True  # student has been booked onto session with tutor
            elif len(slot.tutor.schedule[slot.time]) >= self.max_students and student not in slot.tutor.schedule[slot.time] and student not in self.prev_clashes: # tutor available but full at this time, attempt to move previous student to make space
                clashes = slot.tutor.schedule[slot.time]
                for clash in clashes:
                    if clash.movable:
                        self.prev_clashes.append(clash)
                        if clash_resolved := self.attempt_assignment(clash):
                            prev_clashes = []
                            slot.tutor.schedule[slot.time].remove(clash)
                            return self.assign_tutor(slot.time, slot.tutor, student)

        return False  # no matching time between the student and any suitable tutors could be found

    def get_all_assigned(self) -> List[Student]:
        assigned = []
        for t in self.tutors:
            for students in t.schedule.values():
                if students:
                    [assigned.append(s) for s in students]
        return assigned

    def make_timetable(self):
        # Initial assignment
        [t.assign_requested_timetable(self.students) for t in self.tutors]
        pre_assigned = self.get_all_assigned()
        for student in self.students:
            if student not in pre_assigned:
                assigned = self.attempt_assignment(student)
                if not assigned:
                    self.not_assigned.append(student)