from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'db')


app.config["SECRET_KEY"] = "sec ret"
db = SQLAlchemy(app)
socketio = SocketIO(app)



# Define the database model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    mobile = db.Column(db.String(100))
    roomcode = db.Column(db.Integer)

    def __init__(self, name, email, password, mobile):
        self.name = name
        self.email = email
        self.password = password
        self.mobile = mobile


class RoomCode(Employee):



    def __init__(self, roomcode):
        self.roomcode = roomcode


# Routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        checkemail = Employee.query.filter_by(email=email).first()

        if not name or not email or not password:
            flash('Please enter all the fields', 'error')

        if len(mobile) != 10:
            return redirect(url_for('errormobile'))


        if checkemail:
            return redirect(url_for('error'))






        employee = Employee(name=name, email=email, password=password, mobile=mobile)
        db.session.add(employee)
        db.session.commit()
        flash('Record was successfully added')
        return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        employee = Employee.query.filter_by(email=email).first()

        if employee and employee.password == password:
            return redirect(url_for('room'))
        else:
            return redirect(url_for('emandpass'))

    return render_template('login.html')



@app.route('/errormobile', methods=['GET', 'POST'])
def errormobile():
    return render_template('mobileError.html')

@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('emailerror.html')

@app.route('/emandpass', methods=['GET', 'POST'])
def emandpass():
    return render_template('wrongpass.html')

@app.route('/room', methods=['GET', 'POST'])
def room():
    return render_template('room.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    return render_template('create.html')

@app.route('/join', methods=['GET', 'POST'])
def join():
    return render_template('join.html')

@app.route("/creation", methods=["GET", "POST"])
def creation():
    if request.method == "POST":
        match=request.form["room_id"]
        delete = Employee.query.filter_by(roomcode=match).first()

        if delete:
            db.session.delete(delete)
            db.session.commit()


        room=RoomCode(match)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for("sender"))
    return render_template("create.html")





@app.route("/joining", methods=["GET", "POST"])
def joining():
    if request.method == "POST":
        match=request.form["match"]
        matched_room = Employee.query.filter_by(roomcode=match).first()
        if matched_room:
            return redirect(url_for("receiver"))
        else:
            return render_template("join.html", message="Room not found!")
    return render_template("join.html")


@app.route('/sender')
def sender():
    return render_template('sender.html')

@app.route('/receiver')
def receiver():
    return render_template('receiver.html')

# WebSocket handlers

@socketio.on('message_from_client', namespace='/chat')
def receive_message(data):
    message = data['message']
    sender_role = data['role']
    receiver_role = 'receiver' if sender_role == 'sender' else 'sender'

    emit('message_from_server', {'message': message, 'role': receiver_role}, broadcast=True, namespace='/chat')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)











