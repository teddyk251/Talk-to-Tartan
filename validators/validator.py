import pandas as pd
from typing import Dict
from .models import DegreePlan, Course

class DegreeValidator:
    MIN_SEMESTER_UNITS = 12
    MAX_SEMESTER_UNITS = 21

    def __init__(self, course_data_path: str):
        """Initialize validator with course data and program requirements"""
        self.courses_df = pd.read_csv(course_data_path)
        self._init_program_requirements()

    def _init_program_requirements(self):
        """Initialize detailed program requirements"""
        self.program_requirements = {
            "MSIT": {
                "min_units": 144,
                "core_units": 60,
                "core_areas": {
                    "IT_Entrepreneurship": 12,
                    "Software": 12,
                    "Applied_Machine_Learning": 12,
                    "Secure_IT_Networks": 12,
                    "Leadership": 12
                },
                "min_elective_units": 60,
                "project_units": 24
            },
            "MSECE": {
                "min_units": 97,
                "core_courses": [
                    "ECE501", "ECE502", "ECE503"
                ],
                "elective_requirements": {
                    "min_ece_electives": 36,
                    "min_general_electives": 24
                }
            },
            "MSEAI": {
                "min_units": 144,
                "core_units": 72,
                "core_areas": {
                    "Math_Fundamentals": 12,
                    "Intro_AI": 12,
                    "Intro_ML": 12,
                    "Data_Science": 12,
                    "Advanced_AI_ML": 12,
                    "EAI_Systems_Design": 12
                },
                "engineering_electives": 48,
                "project_units": 24
            }
        }

    def validate_full_plan(self, plan: DegreePlan) -> Dict:
        """
        Validates the entire degree plan against program requirements.
        Returns a detailed validation report.
        """
        program_reqs = self.program_requirements[plan.program.value]
        validation_report = {
            "is_valid": True,
            "total_units": 0,
            "core_units": 0,
            "elective_units": 0,
            "issues": [],
            "warnings": [],
            "requirements_met": {},
            "semester_analysis": []
        }

        # Calculate total units and analyze each semester
        total_units = 0
        core_units = 0
        core_courses_completed = set()
        
        for semester_index, semester in enumerate(plan.semesters):
            semester_units = semester.total_units
            total_units += semester_units
            
            # Analyze courses in semester
            semester_analysis = {
                "semester_index": semester_index + 1,
                "units": semester_units,
                "courses": [],
                "issues": []
            }

            for course in semester.courses:
                semester_analysis["courses"].append({
                    "code": course.course_code,
                    "name": course.course_name,
                    "units": course.units
                })

                # Check if the course is a core course and track core units
                if course.course_code in program_reqs.get("core_courses", []):
                    core_units += course.units
                    core_courses_completed.add(course.course_code)

                # Check prerequisites
                if course.prerequisites:
                    completed_courses = plan.get_completed_courses(semester_index)
                    for prereq in course.prerequisites:
                        if prereq not in completed_courses:
                            semester_analysis["issues"].append(
                                f"Prerequisite {prereq} for course {course.course_code} is not met."
                            )
                            validation_report["issues"].append(
                                f"Prerequisite {prereq} for course {course.course_code} in semester {semester_index + 1} is not met."
                            )

            # Validate the number of units for the semester
            if semester_units < self.MIN_SEMESTER_UNITS:
                semester_analysis["issues"].append(
                    f"Insufficient units in semester {semester_index + 1}: {semester_units}/{self.MIN_SEMESTER_UNITS}"
                )
                validation_report["issues"].append(
                    f"Semester {semester_index + 1} has insufficient units ({semester_units})"
                )
            elif semester_units > self.MAX_SEMESTER_UNITS:
                semester_analysis["issues"].append(
                    f"Too many units in semester {semester_index + 1}: {semester_units}/{self.MAX_SEMESTER_UNITS}"
                )
                validation_report["issues"].append(
                    f"Semester {semester_index + 1} has too many units ({semester_units})"
                )

            validation_report["semester_analysis"].append(semester_analysis)

        # Program-specific validation
        if plan.program.value == "MSIT":
            # MSIT-specific validation (not fully implemented here)
            pass
        elif plan.program.value == "MSECE":
            self._validate_msece_requirements(validation_report, total_units, core_courses_completed)
        elif plan.program.value == "MSEAI":
            # MSEAI-specific validation (not fully implemented here)
            pass

        # Set overall validity
        validation_report["is_valid"] = len(validation_report["issues"]) == 0
        validation_report["total_units"] = total_units
        validation_report["core_units"] = core_units
        validation_report["elective_units"] = total_units - core_units

        return validation_report

    def _validate_msece_requirements(self, report: Dict, total_units: int, core_courses_completed: set):
        """Validate MSECE specific requirements"""
        reqs = self.program_requirements["MSECE"]
        
        # Check total units
        if total_units < reqs["min_units"]:
            report["issues"].append(
                f"Insufficient total units: {total_units}/{reqs['min_units']}"
            )
        
        # Check core courses completion
        missing_core_courses = set(reqs["core_courses"]) - core_courses_completed
        if missing_core_courses:
            report["issues"].append(
                f"Missing core courses: {', '.join(missing_core_courses)}"
            )
