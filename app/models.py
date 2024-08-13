from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Question(db.Model):
    __tablename__ = 'questions' 
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False) 

class Option(db.Model):
    __tablename__ = 'options' 
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False) 
    option_text = db.Column(db.String(255), nullable=False)
    question = db.relationship('Question', backref=db.backref('options', lazy=True))

class Vote(db.Model):
    __tablename__ = 'votes'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)  
    choice = db.Column(db.String(50), nullable=False)
 