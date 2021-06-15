from app.controllers.base import Controller
from app.models.user import User
from datetime import date
from datetime import datetime

class UserController(Controller):

    async def get_student_by_ocourse_id(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).get_student_by_ocourse_id(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def login(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).login(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))
    
    async def register_admin(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).register_admin(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def register_teacher(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).register_teacher(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def get_faces(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).get_face(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def add_face_students(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).save_face(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))
            
    async def get_all_courses(self, request):
        try:
            response = await User(request.app).get_all_courses()
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def get_all_student(self, request):
        try:
            response = await User(request.app).get_all_students()
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def add_student_in_course(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).add_student_in_course(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def add_announcement(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).add_announce(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def add_student_attendants(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            list_response = dict()
            success = []
            fail = []
            for student in payload['students']:
                response = await User(request.app).add_student_attendants(payload['date'],student['enroll_id'],student['attendant'])
                if response['status'] == 'success.':
                    success.append(student['enroll_id'])
                else:
                    fail.append(student['enroll_id'])
            list_response['success'] = success
            list_response['fail'] = fail
            await self.write(request, self.json_response({'list_response':list_response}))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def get_attendants(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).get_attendants(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def find_ip_by_room(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).find_ip_by_room(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def add_course(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).add_course(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))
            
    async def delete_student_in_system(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).delete_student_in_system(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def delete_student_in_course(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).delete_student_in_course(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))

    async def delete_course(self, request):
        try:
            payload = await request.json()
            try:
                if payload is not None:
                    print('can get payload')
            except (NameError, AttributeError):
                print('not found payload')
            response = await User(request.app).delete_course(**payload)
            await self.write(request, self.json_response(response))
        except:
            response = {'status': 'Bad Request.',
                        'reason': 'Controller rejected. Please check input.'}
            await self.write(request, self.json_response(response))