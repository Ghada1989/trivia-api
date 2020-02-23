import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
# create and configure the app 
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={r"/*": {"origins": "*"}})


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, PATCH, POST, DELETE')
    return response

  def format_objects(objects):
    return [obj.format() for obj in objects]
  
  def format_categories(objects):
    return [obj.format()['id'] for obj in objects]

  def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = format_objects(questions)
    current_questions = questions[start:end]

    return current_questions

  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.all()
    formatted_categories = format_categories(categories)
    if len(categories) == 0:
      abort(404)
    
    return jsonify({
       'success': True,
       'categories': formatted_categories,
    })

  @app.route('/questions')
  def retrieve_questions():
    questions = Question.query.all()
  
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    categories_ids = []
    current_category = None
    for current_question in current_questions:
      if current_question['category'] not in categories_ids:
        categories_ids.append(current_question['category'])

    categories = db.session.query(Category.type).filter(Category.id.in_(categories_ids)).all()

    if len(categories) > 0:
      current_category = categories[0]
      
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'current_category': current_category,
      'categories': categories
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
          abort(404)

      question.delete()
      questions = Question.query.all()
      current_questions = paginate_questions(request,questions)

    except Exception as excep:
      abort(404)
    
    return jsonify({
      'success': True,
      'question': current_questions,
      'total_questions': len(questions)
    })
    

  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    if 'search' in body:
      return search_questions(body)
    else:
      return create_question(body)

  def create_question(body):
    try:
      question = body.get('question', None)
      answer = body.get('answer', None)
      category = body.get('category', None)
      difficulty = body.get('difficulty', None)
      if (not question or not answer):
        abort(422)

      question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      question.insert()

      questions = Question.query.all()
      current_questions = paginate_questions(request,questions)


      return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(questions)
      })
    except:
        abort(422)

  def search_questions(body):
    term= body.get('search')
    questions = list(Question.query.filter(Question.question.ilike('%' + str(term) +'%')))
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions)
      })


  @app.route('/categories/<int:category_id>/questions')
  def retrieve_category_questions(category_id):
    questions = Question.query.filter_by(category=category_id).all()
  
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)
    category = Category.query.get(category_id).type

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'category': category,
    })

  @app.route('/quizzes', methods=['POST'])
  def play():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    category_id =  body.get('quiz_category', None)['id']
    if category_id != 0:
      questions = Question.query.filter_by(category=category_id).all()
    else:
      questions = Question.query.all()

    for q in questions:
      if q.id not in previous_questions:
        return jsonify({
          'success': True,
          'question': q.format(),
        })
    abort(404)
      

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "unprocessable"
      }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "bad request"
      }), 400
  
  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
          "success": False, 
          "error": 500,
          "message": "interanl server error"
      }), 500

  return app

    
