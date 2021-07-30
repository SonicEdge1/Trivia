'''
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
'''

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

OK = 200
BAD_REQUEST = 400
BAD_REQUEST_MSG = "Bad Request"
RESOURCE_NOT_FOUND = 404
RESOURCE_NOT_FOUND_MSG = "Resource Not Found"
METHOD_NOT_ALLOWED = 405
METHOD_NOT_ALLOWED_MSG = "Method Not Allowed"
UNPROCESSABLE_ENTITY = 422
UNPROCESSABLE_ENTITY_MSG = "Unprocessable Entity"
QUESTIONS_PER_PAGE = 10
current_category = "Science"


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # https://flask-cors.corydolphin.com/en/latest/api.html#extension //future reference for configuration
  # https://flask-cors.readthedocs.io/en/latest/
  CORS(app, origin='*')
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  def paginate_questions(request, question_selection):
    ''' 
    Returns a Paginated and fomatted selection of trivia questions
        Parameters:
                 request: the http request arguments
                 question_selection: a selection of questions from the trivia question db
                    
        Returns:
                formatted_questions: An array of formated trivia questions
    '''
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in question_selection]
    return formatted_questions[start:end]
  
  def get_formatted_categories():
    '''
    Returns a dictionary of all trivia game categories
    '''    
    all_categories = Category.query.order_by(Category.id).all()
    formatted_categories = {}
    for category in all_categories:
      formatted_categories.update({f'{category.id}' : f'{category.type}'})
    return formatted_categories

  @app.route('/categories')
  def get_categories():
    '''
    Endpoint to handle GET requests for all available categories
    '''
    try:
      formatted_categories = get_formatted_categories()
      return jsonify({
        'success':True,
        'categories': formatted_categories,
        'total_categories': len(formatted_categories)
      })
    except:
      abort(UNPROCESSABLE_ENTITY)
  '''
  test using:
  curl http://127.0.0.1:5000/categories
  reference FormView.js : 20, and QuizView.js : 25
  '''


  @app.route('/questions')
  def get_questions():
    '''endpoint to handle GET requests for all available questions'''
    all_questions = Question.query.order_by(Question.id).all()
    paginated_questions = paginate_questions(request, all_questions)
    formatted_categories = get_formatted_categories()
    return jsonify({
      'success':True,
      'questions': paginated_questions,
      'total_questions': len(all_questions),
      'categories': formatted_categories,
      'current_category': current_category
    })
  '''
  test using:
  curl http://127.0.0.1:5000/questions
  reference QuestionView.js : 26
  '''


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
    '''endpoint to DELETE a question using a question ID'''
    try:
      question = Question.query.get(question_id)
      question_text = question.question
      question.delete()
      return jsonify({
      'success':True,
      'question': question_text,
      'question_id': question_id
      })
    except:
      abort(UNPROCESSABLE_ENTITY)
  '''
  test using:
  curl -X DELETE http://127.0.0.1:5000/questions/5
  reference QuestionView.js : 108
  '''


  @app.route('/questions', methods=['POST'])
  def search_question_by_string_or_add_question():
    '''a POST endpoint to either get questions based on a search term or create a new question'''
    try:
      body = request.get_json()
      searchTerm = body.get('searchTerm')
      # see if it is a search
      if(searchTerm):
        question_selection = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
        count = len(question_selection)
        paginated_questions = paginate_questions(request, question_selection)
        return jsonify({
          'success': True,
          'questions': paginated_questions,
          'total_questions': count,
          'current_category': current_category
        })
      # if not a search, then try to add a new question
      else:
        new_question = Question(
          question=body.get('question', None),
          answer=body.get('answer', None),
          difficulty=body.get('difficulty', None),
          category=body.get('category', None)
        )
        # don't add duplicate questions
        duplicate_question = Question.query.filter_by(question=body.get('question')).one_or_none()
        if (duplicate_question):
          return jsonify({
            'success': False,
            'question': new_question.question,
            'total_questions': len(Question.query.all()),
          })
        else:
          new_question.insert()
          unique_question = Question.query.filter_by(question=body.get('question')).one_or_none()
          return jsonify({
            'success': True,
            'question': new_question.question,
            'total_questions': len(Question.query.all()),
            'new_question_id': unique_question.id
          })

    except:
      abort(UNPROCESSABLE_ENTITY)
  '''
  test using:
  curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"soccer"}' http://127.0.0.1:5000/questions
  curl -X POST -H "Content-Type: application/json" -d '{"question":"How many different actors have portrayed the character James Bond in the 26 films released between 1962-2015?", "answer":"Seven", "difficulty":"4", "category":"5"}' http://127.0.0.1:5000/questions
  references  QuestionView.js : 81  &  FormView.js : 37
  '''


  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_of_category(category_id):
    '''a GET endpoint to get questions based on category'''
    try:
      question_selection = Question.query.filter_by(category = f'{category_id}').order_by(Question.id).all()
      paginated_questions = paginate_questions(request, question_selection)
      category = Category.query.get(category_id)
      current_category = category.type

      return jsonify({
        'success':True,
        'questions': paginated_questions,
        'total_questions': len(question_selection),
        'current_category': current_category
     })
    except:
      abort(UNPROCESSABLE_ENTITY)
  '''
  test using:
  curl http://127.0.0.1:5000/categories/5/questions
  reference QuestionView.js : 63
  '''


  def get_random_question(question_selection, previous_questions):
    '''
    Returns a random, previously unchosen question from a given selection
        Parameters:
                 question_selection: a list of questions to choose from
                 previous_questions: a list of previously asked question id's

        Returns:
                formatted_questions: One formatted trivia question
    '''
    formatted_questions = [question.format() for question in question_selection]
    # single_question = Question.query.filter(Question.id.notin_(previous_questions)).all() //may want to refactor using similar query
    num_questions = len(formatted_questions)
    rand_num = -1
    unique_question = False
    while not(unique_question):
      rand_num = random.randint(0, (num_questions - 1))
      if formatted_questions[rand_num]['id'] not in previous_questions:
        unique_question = True
    return formatted_questions[rand_num]  


  def get_question_selection_from_category(quiz_category):
    '''
    Returns a selection of trivia questions given a quiz category
        Parameters:
                 quiz_category: the desired quiz category

        Returns:
                question_selection: a list of questions from the given category or all questions if category id is 0
    '''
    category_id = quiz_category["id"]
    if category_id == 0:
      question_selection = Question.query.all()
    else:
      question_selection = Question.query.filter_by(category = f'{category_id}').all()
    return question_selection


  @app.route('/quizzes', methods=['POST'])
  def get_new_quiz_question():
    '''a POST endpoint to get questions to play the quiz'''
    try:
      min_num_of_questions = 6
      body = request.get_json()
      previous_questions = body.get('previous_questions')
      quiz_category = body.get('quiz_category')
      question_selection = get_question_selection_from_category(quiz_category)
      # conditional prevents an infinite loop of searching when less than min_num_of_questions exists
      if len(question_selection) < min_num_of_questions:
        return jsonify({
          'success': True,
          'question': None,
          'total_questions': len(question_selection)
        }), OK

      quiz_question = get_random_question(question_selection, previous_questions)
      return jsonify({
        'success':True,
        'quiz_category': quiz_category,
        'question': quiz_question,
        'total_questions': 1
      }), OK
    except:
      abort(UNPROCESSABLE_ENTITY)
  '''
  test using:
  curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[20, 21, 22, 27, 28], "quiz_category":{"type": "Science", "id": "1"}}' http://127.0.0.1:5000/quizzes
  reference QuizView.js : 51
  '''


  '''
  Error Handlers
  '''
  @app.errorhandler(BAD_REQUEST)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": BAD_REQUEST,
          "message": BAD_REQUEST_MSG,
          }), BAD_REQUEST
  
  @app.errorhandler(RESOURCE_NOT_FOUND)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": RESOURCE_NOT_FOUND,
          "message": RESOURCE_NOT_FOUND_MSG,
          }), RESOURCE_NOT_FOUND

  @app.errorhandler(METHOD_NOT_ALLOWED)
  def not_allowed(error):
      return jsonify({
          "success": False, 
          "error": METHOD_NOT_ALLOWED,
          "message": METHOD_NOT_ALLOWED_MSG,
          }), METHOD_NOT_ALLOWED

  @app.errorhandler(UNPROCESSABLE_ENTITY)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": UNPROCESSABLE_ENTITY,
          "message": UNPROCESSABLE_ENTITY_MSG,
          }), UNPROCESSABLE_ENTITY
  return app