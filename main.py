import pandas as pd
from typing import List, Tuple, Union
from classes import DJtimetabler, Tutor, Student, Slot

tutors: List[Tutor] = [
    Tutor("Zhengli", genres=["Commercial"], available_times=["19-22"]),
    Tutor("Can", genres=["EDM", "Commercial"], available_times=["19-22"]),
    Tutor("Nico", genres=["Underground"], available_times=['19-21']),
    Tutor("Joao", genres=["Commerical", "Underground"], available_times=['19-22']),
    #Tutor("Chris", genres=["Underground"], available_times=["19-21"])
    #Tutor("Nico", genres=["Underground"], available_times=['19-21'])
    # example: Tutor("Can", genres=["EDM", "Commercial"], available_times=["19-22"], requested_schedule={20: ['patrick', 'konrad', 'priam']}
]

students: List[Student] = []
df = pd.read_csv('./responses.csv')
for index, row in df.iterrows():
    name = row['Full name'].strip()
    pref_tutors = list(filter(lambda t: t.name in [str(row[f'Preferred tutor [Preference {i}]']).strip() for i in range(1,4)], tutors))
    
    available_times = [(int(x.split(':')[0]) for x in time.split('-')) for time in row["Available times"].split(",")]
    pref_genres = [row["Preferred genres"].split(" ")[0].strip()]
    skill_level = row["Experience level"].split(' ')[0]
    students.append(Student(name, pref_tutors, available_times, pref_genres, skill_level))

timetable = DJtimetabler(students, tutors, 3)
print(timetable)