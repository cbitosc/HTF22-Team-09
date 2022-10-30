from flask import Flask , render_template , request, redirect, url_for
import sqlite3
from matrix2 import run , write ,missing,read
import time

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("home.html" )
@app.route("/About")
def about():
    return render_template("aboutus.html")
@app.route("/login",methods=['GET','POST'])
def login():
	error = None
	if request.method=='POST':
		email = request.form['email']
		password = request.form['psw']
		if email =="admin" and password == "admin":
			return  redirect(url_for('admin'))
		else:
			error = "INVALID DETAILS"
	return render_template("login.html",error=error)


room_numbers={}

@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/admin")
def admin():
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		data = cursor.execute("SELECT * FROM room")
		data = cursor.fetchall()
		for i in data:
			room_numbers[i[0]]=0
	return render_template("admin.html",data=data)



@app.route("/addroom",methods=['GET','POST'])
def addroom():
	data=None
	error = None
	if request.method == 'POST':
		room_no = request.form['room_no']
		row = request.form['row']
		col = request.form['col']
		seat = request.form['seat']
		room_numbers[room_no]=0;
		myconn = sqlite3.connect("room_details.db")
		if (int(seat) <= int(row) * int(col)):
			with myconn:
				cursor = myconn.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
				temp_no = cursor.execute("SELECT room_no from room where room_no=?",[room_no])
				temp_no = cursor.fetchone()	
			if temp_no is None:
				with myconn:
					cursor = myconn.cursor()
					cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
					cursor.execute("INSERT INTO room VALUES(?,?,?,?)",[room_no,col,row,seat]) 
					error = room_no + " is added"
			else:
				error = room_no + " is already exist"
		else:
			error = "Invalid number of seat" 
	return render_template("addroom.html",error = error,data=data)
@app.route("/Generate",methods=['GET','POST'])
def generate():
	error= None
	myconn = sqlite3.connect("room_details.db")
	myconn1=sqlite3.connect("user.db")
	with myconn:
		cursor = myconn.cursor()
		# cursor1=myconn.cursor()
		# cursor1.execute("CREATE TABLE IF NOT EXISTS user(user integer(10),room_no integer(10)")
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		temp_no = cursor.execute("SELECT room_no from room ")
		temp_no = cursor.fetchall()
	if request.method == 'POST':
		room_no  = request.form['room']
		it_start = request.form['it_start']
		it_end   = request.form['it_end']
		ec_start = request.form['ec_start']
		ec_end   = request.form['ec_end']
		el_start = request.form['el_start']
		el_end   = request.form['el_end']
		r_missing = request.form['missing']
		with myconn1:
			cursor=myconn1.cursor()
			for i in range(int(it_start),int(it_end)+1):
				cursor.execute("CREATE TABLE IF NOT EXISTS user(id integer(10),room_no integer(10))")
				cursor.execute("INSERT INTO user values(?,?)",(i,room_no))
			for i in range(int(ec_start),int(ec_end)+1):
				cursor.execute("CREATE TABLE IF NOT EXISTS user(id integer(10),room_no integer(10))")
				cursor.execute("INSERT INTO user values(?,?)",(i,room_no))
			for i in range(int(el_start),int(el_end)+1):
				cursor.execute("CREATE TABLE IF NOT EXISTS user(id integer(10),room_no integer(10))")
				cursor.execute("INSERT INTO user values(?,?)",(i,room_no))

		with myconn:
			cursor = myconn.cursor()
			
			# for i in range(it_start,it_end+1):
			# 	cursor1.execute("INSERT INTO user values(i,room_no)")
			row    = cursor.execute("SELECT row FROM room WHERE room_no = ?",[room_no])
			row = cursor.fetchone()
			row = row[0]
			col    = cursor.execute("SELECT col FROM room WHERE room_no = ?",[room_no])
			col = cursor.fetchone()
			col = col[0]
			seat    = cursor.execute("SELECT seat FROM room WHERE room_no = ?",[room_no])
			seat = cursor.fetchone()
			seat= seat[0]
		it_start = int(it_start)
		it_end   = int(it_end)
		ec_start = int(ec_start) 
		ec_end   = int(ec_end)   
		el_start = int(el_start)
		el_end   = int(el_end) 
		r_missing = r_missing.split()
		for  i in range(len(r_missing)):
			r_missing[i] = int(r_missing[i])
		it_list = list(range(it_start,it_end+1))
		it_list = missing(r_missing,it_list)
		ec_list = list(range(ec_start,ec_end+1))
		ec_list = missing(r_missing,ec_list)
		el_list = list(range(el_start,el_end+1))
		el_list = missing(r_missing,el_list)
		check =len(el_list)+len(ec_list)+len(it_list)
		if( check <= int(seat) ): 
			data = run(el_list,ec_list,it_list,row,col)
			write(data,room_no)
			error = "Seating Arrangment For "+ room_no + " Is generated "
		else:
			error = " Total Number of student is Not More than " + str(seat) + " " +  str(check)	
	return render_template("generate.html",room_no = temp_no,error=error )



@app.route('/user')
def user():
	# myconn=sqlite3.connect("user.db")
	# if request.method=='POST':
	# 	roll=request.form['rollno']
	# 	with myconn:
	# 		cursor=myconn.cursor()
	# 		room_no=cursor.execute("SELECT room_no from user WHERE id=?",[roll])
	# 		print(room_no.fetchone()[0])
	# 		obj=room_no.fetchone()[0]
	return render_template("userk.html")


@app.route('/user1',methods = ['POST','GET'])
def user1():
	if request.method=='POST':

		myconn=sqlite3.connect("user.db")
	
		roll=request.form["rollno"]
		with myconn:
			cursor=myconn.cursor()
			room_no=cursor.execute("SELECT room_no from user WHERE id=?",[roll]).fetchall()
			# print(room_no.fetchone()[0])
			# obj=str(room_no.fetchone()[0])
			# print(room_no.fetchone())
			# print(room_no)
			# f(int(room_no.fetchone()[0]))
			# print(room_no.fetchmany()[0])
			a=str(room_no[0][0])
			
		data =  read(a)
		# print(data)
		data= data.to_html()

	return render_template("user1.html",obj=a,roll=roll,data=data)
## @app.route('/user')
# def f(n):
# 	return render_template("user1.html",room_no=n)




# @app.route('/')
# def student():
#    return render_template('student.html')

# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#    if request.method == 'POST':
#       result = request.form
#       return render_template("result.html",result = result)
	
@app.route('/result',methods=['GET','POST'])
def show():
	data=None
	filename = None
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		temp_no = cursor.execute("SELECT room_no from room ")
		temp_no = cursor.fetchall()
	if request.method == 'POST':
		room_no = request.form['room']
		data =  read(room_no)
		# print(data)
		data= data.to_html()
		filename = '/static/execl/'+room_no+'.xlsx'
	return render_template("show_result.html",data=data,room_no=temp_no,filename=filename)



# @app.route('/show1/<room_no>',methods=['GET','POST'])
# def show1(room_no):
# 	data=None
# 	filename = None
# 	myconn = sqlite3.connect("room_details.db")
# 	with myconn:
# 		cursor = myconn.cursor()
# 		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
# 		temp_no = cursor.execute("SELECT room_no from room ")
# 		temp_no = cursor.fetchall()
# 	if request.method == 'POST':
		
# 		data =  read(room_no)
# 		data= data.to_html()
# 		filename = '/static/execl/'+room_no+'.xlsx'
# 	return render_template("show_result1.html",data=data,room_no=temp_no,filename=filename)



@app.route('/delete/<id>')
def delete(id):
	myconn = sqlite3.connect("room_details.db")
	del room_numbers[int(id)]
	myconn1=sqlite3.connect("user.db")
	with myconn1:
		cursor=myconn1.cursor()
		cursor.execute("DELETE FROM user WHERE room_no=?",[id])
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		cursor.execute("DELETE FROM room WHERE room_no=?",[id])
	return  redirect(url_for('admin'))
@app.route('/edit/<id>',methods=['GET','POST'])
def edit(id):
	myconn = sqlite3.connect("room_details.db")
	
	myconn1=sqlite3.connect("user.db")
	with myconn1:
		cursor=myconn1.cursor()
		cursor.execute("DELETE FROM user WHERE room_no=?",[id])
	if request.method == 'POST':

		room_no = request.form['room_no']
		row = request.form['row']
		col = request.form['col']
		seat = request.form['seat']
		myconn = sqlite3.connect("room_details.db")
		if (int(seat) <= int(row) * int(col)):
			with myconn:
				cursor = myconn.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
				cursor.execute("UPDATE room SET row=?,col=?,seat=? where room_no=?",[row,col,seat,room_no]) 
				error = room_no + " is added"
		else:
			error = "Invalid number of seat" 
	error = None
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		data = cursor.execute("SELECT * FROM room WHERE room_no = ?",[id])
		data = cursor.fetchall()
	room_no = data[0][0]
	col = 	data[0][1]
	row = data[0][2]
	seat = data[0][3]
	return render_template("addroom.html",error = error,room = room_no,col = col, row = row, seat = seat)


@app.route('/teacher')
def teacher():
	return render_template("teacher.html")

@app.route('/teacher1',methods = ['POST','GET'])
def teacher1():
	if request.method=='POST':
		roll=request.form["rollno"]
		for i in room_numbers:
			if room_numbers[i]==roll:
				return render_template("teacher1.html",obj=i)
		else:
			for i in room_numbers:
				if room_numbers[i]==0:
					room_numbers[i]=roll
					return render_template("teacher1.html",obj=i)
	return render_template("teacher1.html",obj="No room left")
			
# @app.route('/user')
# def user():

# 	return render_template("user.html")


# @app.route('/user1',methods = ['POST','GET'])
# def user1():
# 	if request.method=='POST':

# 		myconn=sqlite3.connect("user.db")
	
# 		roll=request.form["rollno"]
# 		with myconn:
# 			cursor=myconn.cursor()
# 			room_no=cursor.execute("SELECT room_no from user WHERE id=?",[roll]).fetchall()
# 			a=str(room_no[0][0])

# 	return render_template("user1.html",obj=a)


if __name__ == "__main__":
    app.run(debug=True)