from flask import request, jsonify
from app import app, db, bcrypt
from app.models import User, Question, Option, Vote
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func

@app.route('/')
def home():
    return "Welcome to the Fantasy Voting App!"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    questions = Question.query.all()
    output = []
    for question in questions:
        options = Option.query.filter_by(question_id=question.id).all()
        option_list = [{"id": option.id, "text": option.option_text} for option in options]
        output.append({
            "id": question.id,
            "text": question.question_text,
            "options": option_list
        })
    return jsonify(output), 200

@app.route('/vote', methods=['POST'])
@jwt_required()
def vote():
    data = request.get_json()
    user_id = get_jwt_identity()
    for vote_data in data['votes']:
        vote = Vote.query.filter_by(user_id=user_id, option_id=vote_data['option_id']).first()
        if vote:
            vote.choice = vote_data['choice']
        else:
            vote = Vote(user_id=user_id, option_id=vote_data['option_id'], choice=vote_data['choice'])
            db.session.add(vote)
    db.session.commit()
    return jsonify({"message": "Votes recorded successfully"}), 200



@app.route('/api/results', methods=['GET'])
def get_results():
    results = []

    questions = Question.query.all()
    for question in questions:
        options = Option.query.filter_by(question_id=question.id).all()
        option_results = []
        
        for option in options:
            votes = db.session.query(
                Vote.choice,
                func.count(Vote.choice)
            ).filter_by(option_id=option.id).group_by(Vote.choice).all()

            option_results.append({
                "option_text": option.option_text,
                "votes": {vote[0]: vote[1] for vote in votes}
            })

        results.append({
            "question_text": question.question_text,
            "options": option_results
        })

    return jsonify(results), 200