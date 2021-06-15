from app.models.base import BaseModel
from datetime import datetime
from secrets import token_hex
from hashlib import sha512
from uuid import uuid4
from re import search, compile

import numpy as np

class User(BaseModel):

    async def get_student_by_ocourse_id(self, ocourse_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT  en.enroll_id,\
                s.student_id AS student_id, s.std_firstname AS first_name, s.std_lastname AS last_name, \
                s.std_nickname AS nickname, s.std_gpax AS gpax, s.std_embedding AS embedded \
                FROM student s \
                LEFT JOIN enrollment en ON s.student_id = en.std_id\
                WHERE en.ocoursse_id = %s'
            value = (ocourse_id,)
            cursor.execute(stmt,value)
            students = cursor.fetchall()
            if len(students) > 0:
                users = [
                    {
                        'enroll_id': user[0],
                        'student_id': user[1],
                        'student_first_name': user[2],
                        'student_last_name': user[3],
                        'student_nickname': user[4],
                        'gpax': user[5],
                        'embedded_face': np.loads(user[6]).tolist(),
                    }
                    for user in students
                ]
            else: 
                course = 'not found this course'
                users = []
            cursor.close()
            return {'status': 'success', 'student': users}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def get_face(self, course_id, section, teacher_id, **kwargs):
        try:
            ## fixed
            academic_year = '2564'
            semester = '2'
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT c.course_id , c.teacher_id ,en.enroll_id,\
                s.student_id AS student_id, s.std_firstname AS first_name, s.std_lastname AS last_name, \
                s.std_nickname AS nickname, s.std_gpax AS gpax, s.std_embedding AS embedded \
                FROM student s \
                LEFT JOIN enrollment en ON s.student_id = en.std_id\
                LEFT JOIN course c ON c.ocourse_id = en.ocoursse_id\
                WHERE c.course_id = %s AND c.section = %s AND\
                c.academic_year = %s AND c.semester = %s'
            value = (course_id,section,academic_year, semester)
            cursor.execute(stmt,value)
            students = cursor.fetchall()
            if len(students) > 0:
                course = students[0][0]
                teacher = students[0][1]
                users = [
                    {
                        'enroll_id': user[2],
                        'student_id': user[3],
                        'student_first_name': user[4],
                        'student_last_name': user[5],
                        'student_nickname': user[6],
                        'gpax': user[7],
                        'embedded_face': np.loads(user[8]).tolist(),
                    }
                    for user in students
                ]
                if teacher_id != teacher:
                    return {'status': 'fail', 'reason': 'teacher is not teach this course'}
            else: 
                course = 'not found this course'
                users = []
                return {'status': 'fail', 'course': course, 'student': users}
            cursor.close()
            return {'status': 'success', 'course': course, 'student': users}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}


    async def save_face(self, first_name, last_name, nickname, gpax, student_id, face, **kwargs):
        try:
            face = np.array(face).dumps()
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'INSERT INTO student (student_id, std_firstname, std_lastname,\
                std_nickname, std_gpax, std_embedding)\
                VALUES (%s,%s,%s,%s,%s,%s)'
            value = (student_id, first_name, last_name, nickname, gpax, face)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def get_all_courses(self, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT DISTINCT * FROM course c'
            cursor.execute(stmt,)
            courses = [
                {
                    'ocourse_id': course[0],
                    'course_name': course[1],
                    'course_id': course[2],
                    'academic_year': course[3],
                    'semester': course[4],
                    'section': course[5],
                    'teacher_id': course[6]
                }
                for course in cursor.fetchall()
            ]
            cursor.close()
            return {'status': 'success', 'courses': courses}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}
    
    async def get_all_students(self, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT DISTINCT * FROM student'
            cursor.execute(stmt,)
            students = [
                {
                    'student_id': student[0],
                    'first_name': student[1],
                    'last_name': student[2],
                    'nick_name': student[3],
                    'gpax': student[4],
                    'embedded_face': np.loads(student[5]).tolist(),
                }
                for student in cursor.fetchall()
            ]
            
            cursor.close()
            return {'status': 'success', 'students': students}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}
    
    async def add_student_in_course(self, ocourse_id, student_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'INSERT INTO enrollment (ocoursse_id, std_id) VALUES (%s,%s)'
            value = (ocourse_id, student_id)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def add_announce(self, user_id, date, begin, end, room_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'INSERT INTO announcement (user_id, date, start_time, end_time, room_id) VALUES (%s,%s,%s,%s,%s)'
            value = (user_id, date, begin, end, room_id)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def add_student_attendants(self, date, enroll_id, attendant, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'INSERT INTO attendants (enroll_id, date, attendant) VALUES (%s,%s,%s)'
            value = (enroll_id, date, attendant)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def get_attendants(self, course_id, semester, academic_year, date,**kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT DISTINCT * FROM student s \
                LEFT JOIN attendants at ON at.student_id = s.student_id\
                WHERE at.course_id = %s AND at.semester = %s AND at.academic_year = %s AND at.date = %s'
            value = (course_id, semester, academic_year, date)
            cursor.execute(stmt,value)
            students = cursor.fetchall()
            if len(students) > 0:
                users = [
                    {
                        'student_id': user[0],
                        'student_first_name': user[1],
                        'student_last_name': user[2],
                        'student_nickname': user[3],
                        'gpax': user[4],
                        # 'embedded_face': np.loads(user[5]).tolist(),
                    }
                    for user in students
                ]
            else: 
                course = 'not found student'
                users = []
            cursor.close()
            return {'status': 'success', 'student': users}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def find_ip_by_room(self, room_id,**kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT * FROM classroom \
                WHERE room_id = %s'
            value = (room_id,)
            cursor.execute(stmt,value)
            ip_address = cursor.fetchone()
            cursor.close()
            if ip_address:
                return {'status': 'success', 'ip_address': ip_address[1]}
            else:
                return {'status': 'fail', 'reason': 'can not find your room_id'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def add_course(self, course_id, course_name, section, academic_year, semester, teacher_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'INSERT INTO course (course_id, course_title, academic_year,\
                semester, section, teacher_id)\
                VALUES (%s,%s,%s,%s,%s,%s)'
            value = (course_id, course_name, academic_year, semester, section, teacher_id)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def login(self, username, password, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT user_id, password, role, teacher_id FROM user \
                WHERE user_name = %s'
            value = (username,)
            cursor.execute(stmt,value)
            result = cursor.fetchone()
            cursor.close()
            if result and result[1] == sha512((password).encode('utf-8')).hexdigest():
                user = {
                    'user_id': result[0],
                    'role': result[2],
                    'teacher_id': result[3]
                }
                return {'status': 'success', 'user': user}
            else:
                return {'status': 'fail', 'reason': 'password incorrect'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def register_teacher(self, username, password, teacher_id, **kwargs):
        try:
            hashed_password = sha512((password).encode('utf-8')).hexdigest()
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT * FROM user \
                WHERE user_name = %s OR teacher_id = %s'
            value = (username, teacher_id)
            cursor.execute(stmt,value)
            result = cursor.fetchall()
            if len(result) > 0:
                cursor.close()
                return {'status': 'already registered.'}
            stmt = 'INSERT INTO user (user_name, password, role, teacher_id) VALUES (%s,%s,%s,%s)'
            value = (username, hashed_password, 'admin', teacher_id)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}

    async def register_admin(self, username, password, **kwargs):
        try:
            hashed_password = sha512((password).encode('utf-8')).hexdigest()
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'SELECT * FROM user \
                WHERE user_name = %s'
            value = (username,)
            cursor.execute(stmt,value)
            result = cursor.fetchall()
            if len(result) > 0:
                cursor.close()
                return {'status': 'already registered.'}
            stmt = 'INSERT INTO user (user_name, password, role) VALUES (%s,%s,%s)'
            value = (username, hashed_password, 'admin')
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}
         
    async def delete_student_in_system(self, student_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'DELETE FROM student WHERE student_id = %s'
            value = (student_id,)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}
    
    async def delete_student_in_course(self, enroll_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'DELETE FROM enrollment WHERE enroll_id = %s'
            value = (enroll_id,)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}
         
    async def delete_course(self, ocourse_id, **kwargs):
        try:
            cursor = self.app.mysql_conn.cursor(buffered=True)
            stmt = 'DELETE FROM course WHERE ocourse_id = %s'
            value = (ocourse_id,)
            cursor.execute(stmt,value)
            self.app.mysql_conn.commit()
            cursor.close()
            return {'status': 'success.'}
        except:
            try:
                cursor.close()
            except:
                pass
            return {'status': 'err'}