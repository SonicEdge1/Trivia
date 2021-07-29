'''
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
'''

#how would you write an aPI to return different error codes when the try catch method catches all aborts???
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy.sql.expression import null

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
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # this wasn't discussed in the lessons.  Need to find documentation on what this does.  Don't understand what the todo is instructing.
  # https://flask-cors.corydolphin.com/en/latest/api.html#extension
  # https://flask-cors.readthedocs.io/en/latest/
  CORS(app, origin='*')
  # I'm hoping this is what the todo referred to.
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
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

  '''
  @TODO: DONE
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  QuestionView.js : 26

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    all_questions = Question.query.order_by(Question.id).all()
    paginated_questions = paginate_questions(request, all_questions)
    formatted_categories = get_formatted_categories()

    # if len(paginated_questions) == 0:
    #   abort(RESOURCE_NOT_FOUND)
    return jsonify({
      'success':True,
      'questions': paginated_questions,
      'total_questions': len(all_questions),
      'categories': formatted_categories,
      'current_category': current_category
    })


  '''
  @TODO: DONE
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
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
  @TODO: DONE
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: DONE
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  ### are search and add going to be the same url ? YES!
  #search QuestionView.js : 81
  #add FormView.js : 37
  # curl -X POST -H "Content-Type: application/json" -d '{"question":"How many different actors have portrayed the character James Bond in the 26 films released between 1962-2015?", "answer":"Seven", "difficulty":"4", "category":"5"}' http://127.0.0.1:5000/questions
  # curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"soccer"}' http://127.0.0.1:5000/questions
  @app.route('/questions', methods=['POST'])
  def search_question_by_string_or_add_question():
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
          'current_category': 1  ##where is this supposed to come from ?
        })

      # if not a search, then try to add a new question
      else:
        new_question = Question(
          question=body.get('question', None),
          answer=body.get('answer', None),
          difficulty=body.get('difficulty', None),
          category=body.get('category', None)
        )
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
  @TODO: DONE
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_of_category(category_id):
    try:
      question_selection = Question.query.filter_by(category = f'{category_id}').order_by(Question.id).all()
      paginated_questions = paginate_questions(request, question_selection)
      category = Category.query.get(category_id)
      current_category = category.type
      # print("*** QUESTIONS: ",paginated_questions )
      # print("*** TOTAL Q'S: ",len(question_selection) )
      # print("*** C_CATEGORY: ",current_category)

      return jsonify({
        'success':True,
        'questions': paginated_questions,
        'total_questions': len(question_selection),
        'current_category': current_category
     })
    except:
      abort(UNPROCESSABLE_ENTITY)  

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  QuizView.js : 51

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":"[1, 4, 20, 15]", "quiz_category":"Sports"}' http://127.0.0.1:5000/quizzes
  '''
  
  # def get_random_question_in_category(quiz_category):
  #   question_selection = Question.query.filter_by(category = f'{quiz_category}').order_by(Question.id).all()
  #   paginated_questions = paginate_questions(request, question_selection)
  #   num_questions = len(paginated_questions)
  #   rand_num = random.randint(0, num_questions - 1)
  #   print("*** Random Number:", rand_num)
  #   return paginated_questions[0]  

  def get_random_question(question_selection, previous_questions):
    formatted_questions = [question.format() for question in question_selection]
    # single_question = Question.query.filter(Question.id.notin_(previous_questions)).all()
    num_questions = len(formatted_questions)
    rand_num = -1
    unique_question = False
    while not(unique_question):
      rand_num = random.randint(0, (num_questions - 1))
      if formatted_questions[rand_num]['id'] not in previous_questions:
        unique_question = True
    return formatted_questions[rand_num]  

  def get_question_selection_from_category(quiz_category):
    category_id = quiz_category["id"]
    question_selection = []
    if category_id == 0:
      question_selection = Question.query.all()
    else:
      question_selection = Question.query.filter_by(category = f'{category_id}').all()
    return question_selection

  @app.route('/quizzes', methods=['POST'])
  def get_new_quiz_question():
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
      abort(RESOURCE_NOT_FOUND)



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
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

    