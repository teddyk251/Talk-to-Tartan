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
                "core_areas": [
                    "18-751", "04-650", "04-655", "18-662", "18-661", "18-785", "18-787-K3", "18-788-K4",
                    "04-654", "11-785", "18-797/11-755", "04-652"
                ],
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

        # Calculate total units and analyze each semester
        total_units = 0
        core_units = 0
        project_units = 0
        core_courses_completed = set()
        project_courses_completed = set()
        
        print('Starting validation')

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
                if course.course_code in program_reqs.get("core_areas", []):
                    core_units += course.units
                    core_courses_completed.add(course.course_code)

                # check if the course is a project course
                if course.course_code in program_reqs.get("project_areas", []):
                    project_units += course.units
                    project_courses_completed.add(course.course_code)
            print(f"Program plan {plan.program.value}")
                # # Check prerequisites
                # if course.prerequisites:
                #     completed_courses = plan.get_completed_courses(semester_index)
                #     for prereq in course.prerequisites:
                #         if prereq not in completed_courses:
                #             semester_analysis["issues"].append(
                #                 f"Prerequisite {prereq} for course {course.course_code} is not met."
                #             )
                #             validation_report["issues"].append(
                #                 f"Prerequisite {prereq} for course {course.course_code} in semester {semester_index + 1} is not met."
                #             )
            #print('Semester analysis:', semester_analysis)
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
            self._validate_msece_requirements(
                validation_report, total_units, core_courses_completed)
        elif plan.program.value == "EAI":
            # MSEAI-specific validation (not fully implemented here)
            print("MSEAI validation not implemented yet")
            self._validate_mseai_requirements(
                validation_report, total_units, core_units, project_units, core_courses_completed, project_courses_completed)

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
        missing_core_courses = set(
            reqs["core_courses"]) - core_courses_completed
        if missing_core_courses:
            report["issues"].append(
                f"Missing core courses: {', '.join(missing_core_courses)}"
            )
        

        # Similarly, implement _validate_mseai_requirements
    def _validate_mseai_requirements(self, report: Dict, total_units: int, core_units: int,
                    project_units: int, core_courses_completed: set, project_courses_completed: set):
        """Validate MSEAI-specific requirements"""
        print("Validating MSEAI requirements")
        
        reqs = self.program_requirements["EAI"]
        
        print(reqs)

        print('Checking total units')
        # Total units check
        if total_units < reqs["min_units"]:
            report["issues"].append(
                f"Insufficient total units: {total_units}/{reqs['min_units']}"
            )

        print('Checking core units')
        # Core units check
        if core_units < reqs["core_units"]:
            report["issues"].append(
                f"Insufficient core units: {core_units}/{reqs['core_units']}"
            )

        print('Checking project units')
        # core units check
        if project_units < reqs["project_units"]:
            report["issues"].append(
                f"Insufficient project units: {project_units}/{reqs['project_units']}"
            )
          
        print('checking missing core courses')  
        # Check core courses completion
        missing_core_courses = set(
            reqs["core_areas"]) - core_courses_completed
        if missing_core_courses:
            # report["issues"].append(
            #     f"Missing core courses: {', '.join(missing_core_courses)}"
            # )
            ## add course names to the course codes
            for missing_course in missing_core_courses:
                print(missing_course)
                course_name = self.courses_df.loc[self.courses_df['course_code'] == missing_course, 'course_name'].values[0]
                print(course_name)
                report["issues"].append(
                    f"Missing core course: {missing_course} - {course_name}"
                )
        
        print('checking missing project courses')
        # Check project courses completion
        missing_project_courses = set(
            reqs["project_areas"]) - project_courses_completed
        if missing_project_courses:
            # report["issues"].append(
            #     f"Missing project courses: {', '.join(missing_project_courses)}"
            # )
        ### add course names to the course codes
            for missing_course in missing_project_courses:
                course_name = self.courses_df.loc[self.courses_df['course_code'] == missing_course, 'course_name'].values[0]
                print(course_name)
                report["issues"].append(
                    f"Missing project course: {missing_course} - {course_name}"
                )
            
        


        # Core area requirements can be similarly validated
        # e.g., check each area in reqs["core_areas"] as needed
