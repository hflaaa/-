from os import path
from aiohttp import web
import jinja2
from pathlib import Path
from dbconn import db_block
from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet

secret_key = Fernet.generate_key()
fernet = Fernet(secret_key)
home_path = str(Path(__file__).parent)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(home_path))


with db_block() as db:
    db.execute('''
    select no,sn from student order by no asc;
    ''')
    items = tuple([tuple(row) for row in db])
passwords=dict((y, x) for x, y in items)   ######密码是序号


with db_block() as db:
    db.execute('''
    select sn,no from course order by sn asc;
    ''')
    items = tuple([tuple(row) for row in db])
passwords2=dict((y, x) for x, y in items)
passwords3= {"tom": "666"}

###学生
async def login_form_page(request):
    return web.Response(text=f"""
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="css/mystyle1.css">
    </head>
    <body>
    <div id="header" >
    <h1>
    <img src="pic/logo.png">    
    </h1></div>
    <div id="section">
    <form action="/login" method="post">
        学号: <input type="text" name="username">
        密码: <input type="password" name="password">
        <input type="submit" value="登录">
    </form>
    </div>
    <div id="footer" >
    <form action="/" method="get">
            <input type="submit" value="退出,返回身份选择界面">
    </form></div>
    </body></html>
    """, content_type="text/html")
#####教师
async def login_form_page2(request):
    return web.Response(text=f"""
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="css/mystyle1.css">
    </head>
    <body>
    <div id="header" >
    <h1>
    <img src="pic/logo.png">    
    </h1></div>
<div id="section">
    <form id='two' action="/login2" method="post">
        教工号: <input type="text" name="username">
        密码: <input type="password" name="password">
        <input type="submit" value="登录">
    </form>
</div>
 <div id="footer" >

    <form id='one' action="/" method="get">
            <input type="submit" value="退出,返回身份选择界面">
    </form></div>
    </body></html>
    """, content_type="text/html")

#####管理人员
async def login_form_page3(request):
    return web.Response(text=f"""
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="css/mystyle1.css">
    </head>
    <body>
    <div id="header" >
    <h1>
    <img src="pic/logo.png">    
    </h1></div>
<div id="section">
    <form action="/login3" method="post">
        账号: <input type="text"  name="username">
        密码: <input type="password" name="password">
        <input type="submit" value="登录">
    </form>
</div>
 <div id="footer" >
    <form action="/" method="get" >
            <input type="submit" value="退出,返回身份选择界面">
    </form></div>
    </body></html>
    """, content_type="text/html")



###学生
async def handle_login(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username
    username = parmas.get("username")
    password = parmas.get("password")

    if passwords.get(username) != password:  # 比较密码
        return web.HTTPFound('/login')  # 比对失败重新登录
    resp = web.HTTPFound('/student')
    set_secure_cookie(resp, "session_id", username)
    return resp

#####教师
async def handle_login2(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    global username2
    username2 = parmas.get("username")
    password = parmas.get("password")
    # print("username2:",username2,type(username2))
    # print("password:",password,type(password))
    # print("passwords2.get(username2):",passwords2.get(username2),type(passwords2.get(username2)))
    print("username2:{}, passowrd: {}".format(passwords2.get(username2), password))
    print(passwords2.get(username2) != password)
    if passwords2.get(username2) != password:  # 比较密码
        return web.HTTPFound('/login2')  # 比对失败重新登录
    resp = web.HTTPFound('/teacher')
    set_secure_cookie(resp, "session_id", username2)
    return resp

#####管理人员
async def handle_login3(request):
    parmas = await request.post()  # 获取POST请求的表单字段数据
    username = parmas.get("username")
    password = parmas.get("password")
    if passwords3.get(username) != password:  # 比较密码
        return web.HTTPFound('/login3')  # 比对失败重新登录
    resp = web.HTTPFound('/manger')
    set_secure_cookie(resp, "session_id", username)
    return resp


async def handle_logout(request):
    resp = web.HTTPFound('/login')
    resp.del_cookie("session_id")
    return resp 

def get_current_user(request):
    user_id = get_secure_cookie(request, "session_id")
    return user_id


def get_secure_cookie(request, name):
    value = request.cookies.get(name)
    if value is None:
        return None
    try:
        buffer = value.encode('utf-8')  # 将文本转换成字节串
        buffer = fernet.decrypt(buffer)
        secured_value = buffer.decode('utf-8')  # 将加密的字节串转换成文本
        return secured_value
    except InvalidToken:
        print("Cannot decrypt cookie value")
        return None

def set_secure_cookie(response, name, value, **kwargs):
    value = fernet.encrypt(value.encode('utf-8')).decode('utf-8')
    response.set_cookie(name, value, **kwargs)

async def home_page(request):
    template = jinja_env.get_template('home.html')
    return web.Response(text=template.render(),
                        content_type="text/html")
###学生
async def student(request):
    with db_block() as db:
        db.execute('''
        select student.name,stu_sn,student.clss,course.name,course.data,grade
        from course_grade,student,course
        where stu_sn=student.sn
        and cou_sn=course.no
        and stu_sn=%(sn)s 
        order by student.sn asc;
        ''',dict(sn=username))
        items2 = [row for row in db]
    template = jinja_env.get_template('list.html')
    return web.Response(text=template.render(items2=items2),
                        content_type="text/html")

#####教师
async def teacher(request):
    with db_block() as db:
        db.execute('''
        select teacher,name,data
        from course
        where no=%(no)s 
        order by sn asc;
        ''',dict(no=username2))
        items4 = [row for row in db]
    template = jinja_env.get_template('teacher.html')
    return web.Response(text=template.render(items4=items4),
                        content_type="text/html")
####管理者
async def manger(request):
    template = jinja_env.get_template('manger.html')
    return web.Response(text=template.render(),
                        content_type="text/html")


######学生
async def check_semester(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select course.name,course.data,grade
        from course_grade,student,course
        where stu_sn=student.sn
        and cou_sn=course.no
        and stu_sn=%(sn)s 
        and data=%(data)s 
        order by course.sn asc;
        """,dict(sn=username,data=data))
        items3 = [row for row in db]
        template = jinja_env.get_template('list2.html')
    return web.Response(text=template.render(items3=items3),
                           content_type="text/html")



#####教师
async def check_schedule(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select teacher,name,data
        from course
        where no=%(no)s 
        and data=%(data)s
        order by course.sn asc;
        """,dict(no=username2,data=data))
        items5 = [row for row in db]
        print(items5)
        template = jinja_env.get_template('teacher2.html')
    return web.Response(text=template.render(items5=items5),
                           content_type="text/html")


####管理者
async def plan(request):
    with db_block() as db:
        db.execute("""
        select distinct clss,course.name, course.data from student,course,course_grade
        where cou_sn=course.no
        and stu_sn=student.sn
        order by course.data desc;
        """,)
        items6 = [row for row in db]
        template = jinja_env.get_template('manger2.html')
    return web.Response(text=template.render(items6=items6),
                           content_type="text/html")
###管理者
async def check_plan(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select distinct clss,course.name, course.data from student,course,course_grade
        where cou_sn=course.no
        and stu_sn=student.sn
        and clss=%(clss)s
        order by course.data desc;
        """,dict(clss=data))

        items7 = [row for row in db]
        template = jinja_env.get_template('manger3.html')
    return web.Response(text=template.render(items7=items7),
                           content_type="text/html")
###管理者
async def class_pf(request):
    with db_block() as db:
        db.execute("""
        select clss,student.name,course.name,grade,course.data
        from course,student,course_grade
        where cou_sn=course.no
        and stu_sn=student.sn
        order by course.data desc, student.sn asc
        """,)
        items8 = [row for row in db]
        template = jinja_env.get_template('manger4.html')
    return web.Response(text=template.render(items8=items8),
                           content_type="text/html")


####管理者
async def check_results(request):
    datas =await request.post() 
    data = datas.get("semester")
    with db_block() as db:
        db.execute("""
        select clss,student.name,course.name,grade,course.data
        from course,student,course_grade
        where cou_sn=course.no
        and stu_sn=student.sn
        and clss=%(clss)s
        order by course.data desc, course.sn asc, student.no asc;
        """,dict(clss=data))

        items9 = [row for row in db]
        template = jinja_env.get_template('manger5.html')
    return web.Response(text=template.render(items9=items9),
                           content_type="text/html")

app = web.Application()
app.add_routes([
    web.get('/',home_page),
    web.get('/student',student),
    web.get('/teacher',teacher),
    web.get('/manger',manger),   
    web.get('/login', login_form_page),
    web.get('/login2', login_form_page2),
    web.get('/login3', login_form_page3),
    web.get('/plan', plan),
    web.get('/class_pf', class_pf),
    web.post('/student/semester', check_semester),
    web.post('/teacher/schedule', check_schedule),
    web.post('/manger/plan',check_plan),
    web.post('/manger/results',check_results),
    web.post('/login', handle_login),
    web.post('/login2', handle_login2),
    web.post('/login3', handle_login3),
    web.post('/logout', handle_logout),
    ])

app.router.add_static('/css/',path='../v1_0/static/css',name='css')

app.router.add_static('/pic/',path='../v1_0/static/pic',name='pic')


if __name__ == "__main__":
    web.run_app(app, port=8080)
