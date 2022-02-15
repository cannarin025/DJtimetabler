from typing import List, Tuple, Dict

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
                        if name.upper() in student.name.upper().split(' '):
                            self.schedule[t].append(student)
                            student.movable = False
            

class Student:
    def __init__(self, name: str, pref_tutors: List[Tutor], availability: List[Tuple[int, int]], genres: List[str]) -> None:
        self.name = name
        self.available = [range(s, e) for s, e in availability]
        self.pref_tutors: List[Tutor] = pref_tutors
        self.genres = genres
        self.movable = True