import pandas as pd
from typing import Dict, List, Any, Tuple
from app.models import ClassroomType, Degree, SemesterType


class ExcelParser:
    def parse_file(self, file_content: bytes) -> Dict[str, List[Dict[str, Any]]]:
        xls = pd.ExcelFile(file_content)
        data = {}

        if "Teachers" in xls.sheet_names:
            data["teachers"] = self._parse_teachers(pd.read_excel(xls, "Teachers"))

        if "Classrooms" in xls.sheet_names:
            data["classrooms"] = self._parse_classrooms(
                pd.read_excel(xls, "Classrooms")
            )

        if "Courses" in xls.sheet_names:
            data["courses"] = self._parse_courses(pd.read_excel(xls, "Courses"))

        if "StudentGroups" in xls.sheet_names:
            data["student_groups"] = self._parse_student_groups(
                pd.read_excel(xls, "StudentGroups")
            )

        if "TeacherCourses" in xls.sheet_names:
            data["teacher_courses"] = self._parse_teacher_courses(
                pd.read_excel(xls, "TeacherCourses")
            )

        if "StudentGroupCourses" in xls.sheet_names:
            data["student_group_courses"] = self._parse_student_group_courses(
                pd.read_excel(xls, "StudentGroupCourses")
            )

        if "Lessons" in xls.sheet_names:
            data["lessons"] = self._parse_lessons(pd.read_excel(xls, "Lessons"))

        return data

    def _parse_teachers(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        teachers = []
        for _, row in df.iterrows():
            if pd.notna(row.get("Name")):
                teachers.append({"name": str(row["Name"]).strip()})
        return teachers

    def _parse_classrooms(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        classrooms = []
        for _, row in df.iterrows():
            if pd.notna(row.get("Name")):
                # Handle Enum conversion safely
                try:
                    c_type = ClassroomType(
                        str(row["Type"]).lower().strip().replace(" ", "_")
                    )
                except ValueError:
                    c_type = ClassroomType.NORMAL

                classrooms.append(
                    {
                        "name": str(row["Name"]).strip(),
                        "faculty": str(row["Faculty"]).strip(),
                        "capacity": int(row["Capacity"]),
                        "type": c_type,
                        "accessibility_features": (
                            str(row.get("Accessibility", ""))
                            if pd.notna(row.get("Accessibility"))
                            else None
                        ),
                    }
                )
        return classrooms

    def _parse_courses(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        courses = []
        for _, row in df.iterrows():
            if pd.notna(row.get("Name")):
                try:
                    r_type = ClassroomType(
                        str(row["RequiredRoomType"]).lower().strip().replace(" ", "_")
                    )
                except ValueError:
                    r_type = ClassroomType.NORMAL

                # New fields
                units = int(row.get("Units", 2))
                min_pop = (
                    int(row.get("MinPopulation"))
                    if pd.notna(row.get("MinPopulation"))
                    else None
                )
                max_pop = (
                    int(row.get("MaxPopulation"))
                    if pd.notna(row.get("MaxPopulation"))
                    else None
                )

                courses.append(
                    {
                        "name": str(row["Name"]).strip(),
                        "required_room_type": r_type,
                        "units": units,
                        "min_population": min_pop,
                        "max_population": max_pop,
                    }
                )
        return courses

    def _parse_student_groups(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        groups = []
        for _, row in df.iterrows():
            if pd.notna(row.get("Name")):
                try:
                    degree = Degree(str(row["Degree"]).lower().strip())
                except ValueError:
                    degree = Degree.BACHELOR

                allowed_days = (
                    str(row.get("AllowedDays", "")).strip()
                    if pd.notna(row.get("AllowedDays"))
                    else None
                )

                groups.append(
                    {
                        "name": str(row["Name"]).strip(),
                        "field": str(row["Field"]).strip(),
                        "degree": degree,
                        "entrance_year": int(row["EntranceYear"]),
                        "entrance_semester": int(row["EntranceSemester"]),
                        "population": int(row["Population"]),
                        "allowed_days": allowed_days,
                    }
                )
        return groups

    def _parse_student_group_courses(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        links = []
        for _, row in df.iterrows():
            if pd.notna(row.get("GroupName")) and pd.notna(row.get("CourseName")):
                links.append(
                    {
                        "group_name": str(row["GroupName"]).strip(),
                        "course_name": str(row["CourseName"]).strip(),
                    }
                )
        return links

    def _parse_teacher_courses(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        links = []
        for _, row in df.iterrows():
            if pd.notna(row.get("TeacherName")) and pd.notna(row.get("CourseName")):
                links.append(
                    {
                        "teacher_name": str(row["TeacherName"]).strip(),
                        "course_name": str(row["CourseName"]).strip(),
                    }
                )
        return links

    def _parse_lessons(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        lessons = []
        for _, row in df.iterrows():
            if pd.notna(row.get("Course")) and pd.notna(row.get("Group")):
                lessons.append(
                    {
                        "course_name": str(row["Course"]).strip(),
                        "group_name": str(row["Group"]).strip(),
                        "teacher_name": (
                            str(row["Teacher"]).strip()
                            if pd.notna(row.get("Teacher"))
                            else None
                        ),
                        "duration_slots": int(row.get("DurationSlots", 1)),
                    }
                )
        return lessons
