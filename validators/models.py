from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

class Semester(Enum):
    FALL = "Fall"
    SPRING = "Spring"

class Program(Enum):
    MS_IT = "IT"
    MS_ECE = "MSECE"
    MS_ECE_AD = "MS_ECE_AD"
    MS_EAI = "EAI"

@dataclass
class Course:
    course_code: str
    course_name: str
    units: int
    semester_availability: List[str]
    prerequisites: List[str]
    program: str

@dataclass
class SemesterPlan:
    semester: str
    courses: List[Course]
    
    @property
    def total_units(self) -> int:
        return sum(int(course.units) for course in self.courses)

@dataclass
class DegreePlan:
    student_id: str
    program: Program
    semesters: List[SemesterPlan]
    
    @property
    def total_units(self) -> int:
        return sum(sem.total_units for sem in self.semesters)
    
    def get_completed_courses(self, up_to_semester: str) -> Set[str]:
        """Get all completed course codes up to a specific semester"""
        completed = set()
        for semester in self.semesters:
            completed.update(course.course_code for course in semester.courses)
        print(f"Completed courses in the degree plan: {completed}")
        return completed
    
    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "program": self.program.value,
            "semesters": [
                {
                    "semester": sem.semester,
                    "courses": [
                        {
                            "course_code": course.course_code,
                            "course_name": course.course_name,
                            "units": course.units,
                            "semester_availability": course.semester_availability,
                            "prerequisites": course.prerequisites,
                            "program": course.program
                        }
                        for course in sem.courses
                    ]
                }
                for sem in self.semesters
            ]
        }
