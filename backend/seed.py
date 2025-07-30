# backend/seed.py
import click
from flask.cli import with_appcontext
from extensions import db
from models.student import Student
from models.course import Course
from models.enrollment import Enrollment
from models.result import Result
from models.degree import Degree
from models.lecturer import Lecturer
from models.advising_resource import AdvisingResource
from models.note import AdvisingNote


@click.command('seed-data')
@with_appcontext
def seed_data_command():
    """Seeds the database with comprehensive sample data including guardian info."""
    click.echo("--- Starting to seed data ---")

    # --- 1. Add Sample Degrees with Faculty ---
    click.echo("--- Adding/Ensuring Sample Degrees ---")
    degrees_to_add = [
        {'name': 'BSc Computer Science', 'faculty': 'Faculty of Computing and Mathematical Sciences'},
        {'name': 'BEng Electrical Engineering', 'faculty': 'Faculty of Engineering'},
        {'name': 'BA History', 'faculty': 'Faculty of Arts and Humanities'},
        {'name': 'BSc Physics', 'faculty': 'Faculty of Physical Sciences'}
    ]
    created_degrees = {}
    for deg_data in degrees_to_add:
        degree = Degree.query.filter_by(name=deg_data['name']).first()
        if not degree:
            degree = Degree(name=deg_data['name'], faculty=deg_data['faculty'])
            db.session.add(degree)
        else:
            if degree.faculty != deg_data.get('faculty'):
                degree.faculty = deg_data.get('faculty')
        created_degrees[deg_data['name']] = degree
    try: db.session.commit(); click.echo("Degrees committed/checked.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error degrees: {e}"); return

    # --- 2. Add Sample Lecturers ---
    click.echo("--- Adding/Ensuring Sample Lecturers ---")
    lecturers_to_add = [
        {'first_name': 'Test', 'last_name': 'Lecturer', 'email': 'lecturer@test.com', 'department': 'Computer Science', 'office_location': 'Room A101', 'password': 'password123'},
        {'first_name': 'Ada', 'last_name': 'Lovelace', 'email': 'ada@test.com', 'department': 'Mathematics', 'office_location': 'Room B203', 'password': 'password123'}
    ]
    created_lecturers = {}
    for lect_data in lecturers_to_add:
        lecturer = Lecturer.query.filter_by(email=lect_data['email']).first()
        if not lecturer:
            lecturer = Lecturer(first_name=lect_data['first_name'], last_name=lect_data['last_name'], email=lect_data['email'], department=lect_data['department'], office_location=lect_data['office_location'])
            lecturer.set_password(lect_data['password'])
            db.session.add(lecturer)
        created_lecturers[lect_data['email']] = lecturer
    try: db.session.commit(); click.echo("Lecturers committed/checked.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error lecturers: {e}"); return

    # --- 3. Add Sample Students (with Guardian Info) ---
    click.echo("--- Adding/Ensuring Sample Students ---")
    csc_degree = created_degrees.get('BSc Computer Science')
    phy_degree = created_degrees.get('BSc Physics')
    test_lecturer = created_lecturers.get('lecturer@test.com')
    ada_lecturer = created_lecturers.get('ada@test.com')

    students_to_add = [
        {
            'first_name': 'Test', 'last_name': 'Student', 'email': 'chidiisking7@gmail.com', 
            'matric_number': 'CST/00/001', 'password': 'password123', 
            'degree_obj': csc_degree, 'advisor_obj': test_lecturer, 'gpa': 3.75,
            'guardian_name': 'Mr. Guardian Sr.', 'guardian_email': 'guardian.sr@example.com', # Replace with a testable email if needed
            'guardian_phone': '08012345678', 'guardian_relationship': 'Parent'
        },
        {
            'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@test.com', 
            'matric_number': 'PHY/00/002', 'password': 'password123', 
            'degree_obj': phy_degree, 'advisor_obj': ada_lecturer, 'gpa': 2.1, # Lower GPA for testing guardian contact
            'guardian_name': 'Ms. Protector', 'guardian_email': 'protector.jane@example.com',
            'guardian_phone': '09087654321', 'guardian_relationship': 'Guardian'
        },
    ]
    created_students = {}
    for stud_data in students_to_add:
        student = Student.query.filter_by(matric_number=stud_data['matric_number']).first()
        if not student:
            student = Student(
                first_name=stud_data['first_name'], last_name=stud_data['last_name'],
                email=stud_data['email'], matric_number=stud_data['matric_number'],
                gpa=stud_data.get('gpa'),
                guardian_name=stud_data.get('guardian_name'), # Add guardian fields
                guardian_email=stud_data.get('guardian_email'),
                guardian_phone=stud_data.get('guardian_phone'),
                guardian_relationship=stud_data.get('guardian_relationship')
            )
            student.set_password(stud_data['password'])
            if stud_data['degree_obj']: student.degree_id = stud_data['degree_obj'].id
            if stud_data['advisor_obj']: student.advisor_id = stud_data['advisor_obj'].id
            db.session.add(student)
            click.echo(f"Added student: {student.matric_number} with guardian info.")
        else: # Update existing student if needed
            student.guardian_name = stud_data.get('guardian_name', student.guardian_name)
            student.guardian_email = stud_data.get('guardian_email', student.guardian_email)
            student.guardian_phone = stud_data.get('guardian_phone', student.guardian_phone)
            student.guardian_relationship = stud_data.get('guardian_relationship', student.guardian_relationship)
            if stud_data['degree_obj'] and student.degree_id != stud_data['degree_obj'].id: student.degree_id = stud_data['degree_obj'].id
            if stud_data['advisor_obj'] and student.advisor_id != stud_data['advisor_obj'].id: student.advisor_id = stud_data['advisor_obj'].id
            if stud_data.get('gpa') and student.gpa != stud_data.get('gpa'): student.gpa = stud_data.get('gpa')
            click.echo(f"Student {student.matric_number} already exists/updated with guardian info.")
        created_students[stud_data['matric_number']] = student
    try: db.session.commit(); click.echo("Students committed/checked.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error students: {e}"); return

    # --- 4. Add Sample Courses (Code remains the same as your last version) ---
    click.echo("--- Adding/Ensuring Sample Courses ---")
    courses_to_add = [
        {'code': 'MTH101', 'title': 'Algebra I', 'units': 3, 'level': 100, 'status': 'Core'},
        {'code': 'CSC101', 'title': 'Intro to Computer Science', 'units': 3, 'level': 100, 'status': 'Core'},
        {'code': 'GST101', 'title': 'Use of English I', 'units': 2, 'level': 100, 'status': 'Required'},
        {'code': 'PHY101', 'title': 'General Physics I', 'units': 3, 'level': 100, 'status': 'Elective'},
        {'code': 'CSC201', 'title': 'Data Structures I', 'units': 3, 'level': 200, 'status': 'Core'},
        {'code': 'CSC202', 'title': 'Discrete Mathematics', 'units': 3, 'level': 200, 'status': 'Core'}
    ]
    created_courses = {} 
    for course_data in courses_to_add:
        course = Course.query.filter_by(code=course_data['code']).first()
        if not course:
            course = Course(code=course_data['code'], title=course_data['title'], units=course_data['units'], level=course_data['level'], status=course_data['status'])
            db.session.add(course); 
        created_courses[course_data['code']] = course
    try: db.session.commit(); click.echo("Courses committed/checked.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error courses: {e}"); return

    # --- 5. Enroll Students & Add Results (Code remains similar, ensure student objects are used) ---
    click.echo("\n--- Processing Enrollments and Results ---")
    student_cst001 = created_students.get('CST/00/001')
    student_phy002 = created_students.get('PHY/00/002')

    enrollments_results_map = {
        student_cst001: [
            {'course_code': 'CSC101', 'academic_year': '2023/2024', 'semester_number': 1, 'grade': 'A', 'grade_points': 5.0, 'official_semester_string': '2023/2024 - Semester 1'},
            {'course_code': 'MTH101', 'academic_year': '2023/2024', 'semester_number': 1, 'grade': 'B', 'grade_points': 4.0, 'official_semester_string': '2023/2024 - Semester 1'},
            {'course_code': 'GST101', 'academic_year': '2023/2024', 'semester_number': 1, 'grade': 'A', 'grade_points': 5.0, 'official_semester_string': '2023/2024 - Semester 1'},
            {'course_code': 'PHY101', 'academic_year': '2023/2024', 'semester_number': 2, 'grade': 'C', 'grade_points': 3.0, 'official_semester_string': '2023/2024 - Semester 2'},
            {'course_code': 'CSC201', 'academic_year': '2024/2025', 'semester_number': 1, 'grade': None, 'grade_points': None, 'official_semester_string': '2024/2025 - Semester 1'}
        ],
        student_phy002: [ # Results for Jane Doe
            {'course_code': 'PHY101', 'academic_year': '2023/2024', 'semester_number': 1, 'grade': 'D', 'grade_points': 1.0, 'official_semester_string': '2023/2024 - Semester 1'}, # Low grade
            {'course_code': 'MTH101', 'academic_year': '2023/2024', 'semester_number': 1, 'grade': 'C', 'grade_points': 2.0, 'official_semester_string': '2023/2024 - Semester 1'},
        ]
    }

    for student_obj, er_data_list in enrollments_results_map.items():
        if not student_obj: continue
        click.echo(f"-- Processing for student: {student_obj.matric_number} --")
        for enroll_data in er_data_list:
            course_obj = created_courses.get(enroll_data['course_code'])
            if course_obj:
                # Enrollment
                existing_enrollment = Enrollment.query.filter_by(student_id=student_obj.id, course_id=course_obj.id, academic_year=enroll_data['academic_year'], semester=enroll_data['semester_number']).first()
                if not existing_enrollment:
                    enrollment_to_add = Enrollment(student_id=student_obj.id, course_id=course_obj.id, academic_year=enroll_data['academic_year'], semester=enroll_data['semester_number'])
                    db.session.add(enrollment_to_add)
                # Result
                if enroll_data.get('grade') is not None:
                    existing_result = Result.query.filter_by(student_id=student_obj.id, course_id=course_obj.id, semester=enroll_data['official_semester_string']).first()
                    if not existing_result:
                        new_result = Result(student_id=student_obj.id, course_id=course_obj.id, grade=enroll_data['grade'], semester=enroll_data['official_semester_string'], gpa=enroll_data['grade_points'])
                        db.session.add(new_result)
    try: db.session.commit(); click.echo("All Enrollments and Results committed.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error committing enrollments/results: {e}")

    # --- 6. Add Sample Advising Notes (Code remains similar) ---
    click.echo("--- Adding Sample Advising Notes ---")
    if student_cst001 and test_lecturer and student_phy002 and ada_lecturer:
        notes_to_add = [
            {'content': 'Discussed course selection for CST/00/001.', 'student_obj': student_cst001, 'lecturer_obj': test_lecturer},
            {'content': 'PHY/00/002 needs to improve performance in PHY101.', 'student_obj': student_phy002, 'lecturer_obj': ada_lecturer},
        ]
        for note_data in notes_to_add:
            existing_note = AdvisingNote.query.filter_by(student_id=note_data['student_obj'].id, lecturer_id=note_data['lecturer_obj'].id, content=note_data['content']).first()
            if not existing_note:
                note = AdvisingNote(content=note_data['content'], student_id=note_data['student_obj'].id, lecturer_id=note_data['lecturer_obj'].id)
                db.session.add(note)
        try: db.session.commit(); click.echo("Advising notes committed.")
        except Exception as e: db.session.rollback(); click.echo(f"!!! Error notes: {e}")
    
    # --- 7. Add Sample Advising Resources (Code remains the same) ---
    click.echo("--- Adding Sample Advising Resources ---")
    resources_to_add = [
        {"title": "Academic Calendar 2024-2025", "description": "Official university academic calendar.", "url": "#", "category": "Calendar"},
        {"title": "Course Registration Guide", "description": "Step-by-step guide for course registration.", "url": "#", "category": "Guide"},
        {"title": "Student Handbook", "description": "Policies and regulations for students.", "url": "#", "category": "Policy"}
    ]
    for res_data in resources_to_add:
        resource = AdvisingResource.query.filter_by(title=res_data['title']).first()
        if not resource:
            resource = AdvisingResource(title=res_data['title'], description=res_data['description'], url=res_data['url'], category=res_data['category'])
            db.session.add(resource)
    try: db.session.commit(); click.echo("Advising resources committed.")
    except Exception as e: db.session.rollback(); click.echo(f"!!! Error resources: {e}")

    click.echo("--- Seeding data finished ---")
