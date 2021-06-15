from app.controllers.users_controller import UserController
from aiohttp_cors import setup, ResourceOptions


def map_routes(app):

    cors = setup(app, defaults={
        '*': ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
        )
    })

    user_controller = UserController()

    ### 0
    resource = app.router.add_resource('/registerAdmin', name='register_admin')
    resource.add_route('POST', user_controller.register_admin)

    ### 0
    resource = app.router.add_resource('/registerTeacher', name='register_teacher')
    resource.add_route('POST', user_controller.register_teacher)

    ### 1
    resource = app.router.add_resource('/login', name='login')
    resource.add_route('POST', user_controller.login)

    ### 2
    resource = app.router.add_resource('/getAllStudent', name='student_in_system')
    resource.add_route('GET', user_controller.get_all_student)

    ### 3
    resource = app.router.add_resource('/addFace', name='add_face')
    resource.add_route('POST', user_controller.add_face_students)

    ### 4
    resource = app.router.add_resource('/getAllCourse', name='all_course')
    resource.add_route('GET', user_controller.get_all_courses)

    ### 5
    resource = app.router.add_resource('/addCourse', name='add_course')
    resource.add_route('POST', user_controller.add_course)

    ### 6
    resource = app.router.add_resource('/getStudentByOCourseID', name='student_in_course')
    resource.add_route('POST', user_controller.get_student_by_ocourse_id)

    ### 7
    resource = app.router.add_resource('/addStudentInCourse', name='add_student_in_course')
    resource.add_route('POST', user_controller.add_student_in_course)

    ### 8
    resource = app.router.add_resource('/addAnnouncement', name='add_announcement')
    resource.add_route('POST', user_controller.add_announcement)

    ### 9
    resource = app.router.add_resource('/findIpByRoomID', name='find_ip')
    resource.add_route('POST', user_controller.find_ip_by_room)

    ### 10
    resource = app.router.add_resource('/getFace', name='face_student')
    resource.add_route('POST', user_controller.get_faces)

    ### 11
    resource = app.router.add_resource('/addAttendants', name='add_student_attendants')
    resource.add_route('POST', user_controller.add_student_attendants)
    
    # 12
    resource = app.router.add_resource('/deleteStudentInSystem', name='delete_student_in_system')
    resource.add_route('POST', user_controller.delete_student_in_system)

    # 13
    resource = app.router.add_resource('/deleteStudentInCourse', name='delete_student_in_course')
    resource.add_route('POST', user_controller.delete_student_in_course)

    # 14
    resource = app.router.add_resource('/deleteCourse', name='delete_course')
    resource.add_route('POST', user_controller.delete_course)





    for route in app.router.routes():
        cors.add(route)
