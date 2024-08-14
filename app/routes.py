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
    questions = Question.query.order_by(Question.id).all()
    output = []
    for question in questions:
        # Order options by id or another column that defines the correct order
        options = Option.query.filter_by(question_id=question.id).order_by(Option.id).all()
        option_list = [{"id": option.id, "text": option.option_text} for option in options]
        output.append({
            "id": question.id,
            "text": question.question_text,
            "type": question.type, 
            "options": option_list
        })
    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response, 200




@app.route('/vote', methods=['POST'])
@jwt_required()
def vote():
    data = request.get_json()
    user_id = get_jwt_identity()

    yes_no_waiver_questions = ['Trade draft picks?', 'DST?', 'Kickers?', 'Re-seed playoffs?', 'Waivers']

    for vote_data in data['votes']:
        option = Option.query.filter_by(id=vote_data['option_id']).first()
        question = Question.query.filter_by(id=option.question_id).first()
        if question.question_text in yes_no_waiver_questions:
           Vote.query.filter(Vote.user_id == user_id, Vote.option_id.in_(
                [opt.id for opt in question.options]
            )).delete(synchronize_session=False)

       
        existing_vote = Vote.query.filter_by(user_id=user_id, option_id=vote_data['option_id']).first()

        if existing_vote:
            existing_vote.choice = vote_data['choice']
        else:
            new_vote = Vote(user_id=user_id, option_id=vote_data['option_id'], choice=vote_data['choice'])
            db.session.add(new_vote)

    db.session.commit()
    response = jsonify({"message": "Votes recorded successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@app.route('/results', methods=['GET'])
def get_results():
    results = []
    questions = Question.query.order_by(Question.id).all()

    for question in questions:
        options = Option.query.filter_by(question_id=question.id).order_by(Option.id).all()
        option_results = []

        for option in options:
            vote_counts = db.session.query(
                Vote.choice, func.count(Vote.choice)
            ).filter_by(option_id=option.id).group_by(Vote.choice).all()

            option_results.append({
                "option_text": option.option_text,
                "votes": {vote[0]: vote[1] for vote in vote_counts}
            })

        results.append({
            "question_text": question.question_text,
            "options": option_results
        })

    return jsonify(results), 200
