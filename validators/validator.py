import pandas as pd
from typing import Dict
from .models import DegreePlan, Course


class DegreeValidator:
    MIN_SEMESTER_UNITS = 36
    MAX_SEMESTER_UNITS = 54

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
            "EAI": {
                "min_units": 144,
            "core_units": 72,
            "core_sections": {
                "Math Fundamentals": ["18-751", "04-650"],
                "Intro to AI": ["04-655", "18-662"],
                "Intro to ML": ["18-661"],
                "Data Science": ["18-785", "18-787-K3", "18-788-K4"],
                "Advanced AI and ML": ["04-654", "11-785"],
                "EAI Systems Design": ["04-652"]
            },
                "engineering_electives": 48,
                "project_units": 24,
                "project_areas": ["04-651", "04-701", "04-990"]
            }
        }

    def validate_full_plan(self, plan: DegreePlan) -> Dict:
        """
        Validates the entire degree plan against program requirements.
        Returns a detailed validation report.
        """
        print("HERE-1 in validate_full_plan")
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

        # Initialize trackers
        total_units = 0
        core_units = 0
        project_units = 0
        core_courses_completed = set()
        project_courses_completed = set()
        missing_core_courses = {}

        print("Starting validation")

        # Analyze each semester
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
                for section, courses in program_reqs.get("core_sections", {}).items():
                    if course.course_code in courses:
                        core_units += course.units
                        core_courses_completed.add(course.course_code)
                        #break  # Prevent double-counting in multiple sections
                    print('Core courses completed:', core_courses_completed)

                # Check if the course is a project course and track project units
                if course.course_code in program_reqs.get("project_areas", []):
                    project_units += int(course.units)
                    project_courses_completed.add(course.course_code)
                    print('Project courses completed:', project_courses_completed)

            print("This is the first dummy print")

            # Validate semester units
            if semester_units < self.MIN_SEMESTER_UNITS:
                semester_analysis["issues"].append(
                    f"Insufficient units in semester {semester_index + 1}: {semester_units}/{self.MIN_SEMESTER_UNITS}"
                )
                validation_report["issues"].append(
                    f"Semester {semester_index + 1} has insufficient units ({semester_units})"
                )
                print ("This is the second dummy print")

            elif semester_units > self.MAX_SEMESTER_UNITS:
                semester_analysis["issues"].append(
                    f"Too many units in semester {semester_index + 1}: {semester_units}/{self.MAX_SEMESTER_UNITS}"
                )
                validation_report["issues"].append(
                    f"Semester {semester_index + 1} has too many units ({semester_units})"
                )
                print ("This is the third dummy print")

            validation_report["semester_analysis"].append(semester_analysis)

        # # Track missing core courses
        # for section, courses in program_reqs.get("core_sections", {}).items():
        #     missing_courses = set(courses) - core_courses_completed
        #     if missing_courses:
        #         missing_core_courses[section] = [
        #             {"code": course, "name": self._get_course_name(course)} for course in missing_courses
        #         ]

        # # Add missing core courses to the report
        # if missing_core_courses:
        #     validation_report["missing_core_courses"] = missing_core_courses
        #     for section, courses in missing_core_courses.items():
        #         validation_report["issues"].append(
        #             f"Missing core courses in section '{section}': {', '.join([course['code'] + ' (' + course['name'] + ')' for course in courses])}"
        #         )

        # Program-specific validation
        if plan.program.value == "MSIT":
            # MSIT-specific validation (not fully implemented here)
            pass
        elif plan.program.value == "MSECE":
            self._validate_msece_requirements(
                validation_report, total_units, core_courses_completed
            )
        elif plan.program.value == "EAI":
            self._validate_mseai_requirements(
                validation_report, total_units, core_units, project_units, core_courses_completed, project_courses_completed
            )

        # Set overall validity
        validation_report["is_valid"] = len(validation_report["issues"]) == 0
        validation_report["total_units"] = total_units
        validation_report["core_units"] = core_units
        validation_report["project_units"] = project_units
        validation_report["elective_units"] = total_units - (core_units + project_units)

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
        missing_core_courses = set(
            reqs["core_courses"]) - core_courses_completed
        if missing_core_courses:
            report["issues"].append(
                f"Missing core courses: {', '.join(missing_core_courses)}"
            )
        

        
    def _validate_mseai_requirements(self, report: Dict, total_units: int, core_units: int,
                                 project_units: int, core_courses_completed: set, project_courses_completed: set):
        """Validate MSEAI-specific requirements"""
        reqs = self.program_requirements["EAI"]

        # Validate total units
        if total_units < reqs["min_units"]:
            report["issues"].append(
                f"Insufficient total units: {total_units}/{reqs['min_units']}"
            )

        # Validate core units
        if core_units < reqs["core_units"]:
            report["issues"].append(
                f"Insufficient core units: {core_units}/{reqs['core_units']}"
            )

        # Validate project units
        if project_units < reqs["project_units"]:
            report["issues"].append(
                f"Insufficient project units: {project_units}/{reqs['project_units']}"
            )

        # Validate core course categories and show missing courses with names
        # for section, courses in reqs["core_sections"].items():
        #     completed_in_section = core_courses_completed.intersection(courses)
        #     if not completed_in_section:
        #         # Get missing courses with their names
        #         missing_courses = [
        #             f"{course} - {self.courses_df.loc[self.courses_df['course_code'] == course, 'course_name'].values[0]}"
        #             for course in courses
        #             if course not in core_courses_completed
        #         ]
        #         report["issues"].append(
        #             f"Missing course from section '{section}': Choose one from {', '.join(missing_courses)}"
        #         )
        #     else:
        #         print(f"Section '{section}' validated with completed courses: {', '.join(completed_in_section)}")

        # # Validate project course completion and show missing courses with names
        # missing_project_courses = set(reqs["project_areas"]) - project_courses_completed
        # if missing_project_courses:
        #     for missing_course in missing_project_courses:
        #         course_name = self.courses_df.loc[self.courses_df['course_code'] == missing_course, 'course_name'].values[0]
        #         report["issues"].append(
        #             f"Missing project course: {missing_course} - {course_name}"
        #         )
        
        # Validate core course categories and show missing courses with names
        # Validate core course categories and show missing courses with names
        missing_sections = []
        for section, courses in reqs["core_sections"].items():
            completed_in_section = core_courses_completed.intersection(courses)
            if not completed_in_section:
                # Collect missing courses for this section
                missing_courses = [
                    f"{course} - {self.courses_df.loc[self.courses_df['course_code'] == course, 'course_name'].values[0]}"
                    for course in courses
                    if course not in core_courses_completed
                ]
                missing_sections.append(section)
                print('Missing sections:', missing_sections)
                # Append a detailed issue for the section
                report["issues"].append(
                    f"Missing course(s) from section '{section}': Choose one from {', '.join(missing_courses)}"
                )
            else:
                print(f"Section '{section}' validated with completed courses: {', '.join(completed_in_section)}")

        print('Missing sections:', missing_sections)

        # Log the overall missing sections
        if missing_sections:
            report["warnings"].append(
                f"The student has not completed required courses from the following sections: {', '.join(missing_sections)}"
            )

        # Validate project course completion and show missing courses with names
        missing_project_courses = set(reqs["project_areas"]) - project_courses_completed
        if missing_project_courses:
            for missing_course in missing_project_courses:
                course_name = self.courses_df.loc[self.courses_df['course_code'] == missing_course, 'course_name'].values[0]
                report["issues"].append(
                    f"Missing project course: {missing_course} - {course_name}"
                )
