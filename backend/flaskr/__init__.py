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
    # //future reference for configuration
    # https://flask-cors.corydolphin.com/en/latest/api.html#extension
    # https://flask-cors.readthedocs.io/en/latest/
    CORS(app, origin='*')
    # CORS Headers

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    def get_current_index(request):
        '''
        Returns a formatted list of trivia questions
            Parameters:
                     request: http request data

            Returns:
                    formatted_questions: a beginning question index based on
                     the 'page' value contained in the request data
        '''
        selected_page = request.args.get('page', 1, type=int)
        return selected_page - 1

    def format_questions(question_selection):
        '''
        Returns a formatted list of trivia questions
            Parameters:
                     question_selection: a list of unformatted questions

            Returns:
                    formatted_questions: a formatted list of trivia questions
        '''
        formatted_questions = [question.format()
                               for question in question_selection]
        return formatted_questions

    def get_formatted_categories():
        '''
        Returns a dictionary of all trivia game categories
        '''
        all_categories = Category.query.order_by(Category.id).all()
        formatted_categories = {}
        for category in all_categories:
            formatted_categories.update({f'{category.id}': f'{category.type}'})
        return formatted_categories

    @app.route('/categories')
    def get_categories():
        '''
        Endpoint to handle GET requests for all available categories
        '''
        try:
            formatted_categories = get_formatted_categories()
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(formatted_categories)
            })
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
    '''
    test using:
    curl http://127.0.0.1:5000/categories
    reference FormView.js : 20, and QuizView.js : 25
    '''

    @app.route('/questions')
    def get_questions():
        '''endpoint to handle GET requests for all available questions'''
        try:
            current_index = get_current_index(request)
            questions = Question.query.order_by(
                Question.id).limit(QUESTIONS_PER_PAGE).offset(
                current_index * QUESTIONS_PER_PAGE).all()
            formatted_questions = format_questions(questions)
            total_questions = Question.query.count()
            formatted_categories = get_formatted_categories()
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': total_questions,
                'categories': formatted_categories,
                'current_category': current_category
            })
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
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
                'success': True,
                'deleted_question_text': question_text,
                'deleted_question_id': question_id
            })
        except AttributeError as attribute_error:
            print("ATTRIBUTE ERROR: ", attribute_error)
            abort(UNPROCESSABLE_ENTITY)
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
    '''
    test using:
    curl -X DELETE http://127.0.0.1:5000/questions/5
    reference QuestionView.js : 108
    '''

    def search_by_term(request, searchTerm):
        '''
        Searches the DB for a trivia question based on the given search term
            Parameters:
                     request: the http request data
                     searchTerm: a string of the desired term to search for

            Returns:
                    jsonified data:
                        success: True if the search did not throw an error
                        questions: A list of question matching the criteria
                        total_questions: The count of total questions returned
                        current_category: The game's current category
        '''
        current_index = get_current_index(request)
        question_selection = Question.query.filter(
            Question.question.ilike(f'%{searchTerm}%')).order_by(
            Question.id).limit(QUESTIONS_PER_PAGE).offset(
            current_index *
            QUESTIONS_PER_PAGE).all()
        count = Question.query.filter(
            Question.question.ilike(f'%{searchTerm}%')).order_by(Question.id
                                                                 ).count()
        formatted_questions = format_questions(question_selection)
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': count,
            'current_category': current_category
        })

    def add_new_question(body):
        '''
        Adds a question to the DB and returns json data representing
        the new question added
            Parameters:
                     body: the http request body containing json data

            Returns:
                    jsonified data:
                        success: False if a duplicate question, True otherwise
                        question: The text of the trivia question inserted
                        total_questions: The count of questions in the DB
                        new_question_id: id of the new question inserted
        '''
        new_question = Question(
            question=body.get('question', None),
            answer=body.get('answer', None),
            difficulty=int(body.get('difficulty', None)),  # int
            category=body.get('category', None)  # string
        )
        # don't add duplicate questions
        duplicate_question = Question.query.filter_by(
            question=body.get('question')).one_or_none()
        if (duplicate_question):
            return jsonify({
                'success': False,
                'question': new_question.question,
                'total_questions': len(Question.query.all()),
            })
        else:
            new_question.insert()
            unique_question = Question.query.filter_by(
                question=body.get('question')).one_or_none()
            return jsonify({
                'success': True,
                'question': new_question.question,
                'total_questions': len(Question.query.all()),
                'new_question_id': unique_question.id
            })

    @app.route('/questions', methods=['POST'])
    def search_questions_by_string_or_add_question():
        '''a POST endpoint to either get questions based on a search term
        or create a new question'''
        try:
            body = request.get_json()
            searchTerm = body.get('searchTerm')
            # see if it is a search
            if(searchTerm):
                return search_by_term(request, searchTerm)
            else:
                return add_new_question(body)
        except AttributeError as attribute_error:
            print("ATTRIBUTE ERROR: ", attribute_error)
            abort(UNPROCESSABLE_ENTITY)
        except TypeError as type_error:
            print("TYPE ERROR: ", type_error)
            abort(UNPROCESSABLE_ENTITY)
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
    '''
    test using:
    curl -X POST -H "Content-Type: application/json" -d
     '{"searchTerm":"soccer"}' http://127.0.0.1:5000/questions
    curl -X POST -H "Content-Type: application/json" -d
     '{"question":"How many different actors have portrayed the character
      James Bond in the 26 films released between 1962-2015?",
       "answer":"Seven", "difficulty":"4", "category":"5"}'
        http://127.0.0.1:5000/questions
    references  QuestionView.js : 81  &  FormView.js : 37
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_of_category(category_id):
        '''a GET endpoint to get questions based on category'''
        try:
            current_index = get_current_index(request)
            question_selection = Question.query.filter_by(
                category=f'{category_id}').order_by(
                Question.id).limit(QUESTIONS_PER_PAGE).offset(
                current_index *
                QUESTIONS_PER_PAGE).all()
            count = Question.query.filter_by(
                category=f'{category_id}').order_by(
                Question.id).count()
            formatted_questions = format_questions(question_selection)
            category = Category.query.get(category_id)
            current_category = category.type

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': count,
                'current_category': current_category
            })
        except AttributeError as attribute_error:
            print("ATTRIBUTE ERROR: ", attribute_error)
            abort(UNPROCESSABLE_ENTITY)
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
    '''
    test using:
    curl http://127.0.0.1:5000/categories/5/questions
    reference QuestionView.js : 63
    '''

    def get_a_random_question(question_selection):
        '''
        Returns a random question from a given selection
            Parameters:
                     question_selection: a list of questions to choose from

            Returns:
                    formatted_questions: One formatted trivia question
        '''
        formatted_questions = format_questions(question_selection)
        num_questions = len(formatted_questions)
        if num_questions == 0:
            return None
        else:
            rand_num = random.randint(0, (num_questions - 1))
            return formatted_questions[rand_num]

    def get_question_selection_from_category(
            quiz_category, previous_questions):
        '''
        Returns a selection of trivia questions given a quiz category
            Parameters:
                     quiz_category: the desired quiz category
                     previous_questions: a list of previously asked question
                     id's not wanted in the returned selection

            Returns:
                    question_selection: a list of questions from the given
                    category or all questions if category id is 0
        '''
        category_id = quiz_category["id"]
        if category_id == 0:
            question_selection = Question.query.filter(
                Question.id.notin_(previous_questions)).all()
        else:
            question_selection = Question.query.filter_by(
                category=f'{category_id}').filter(
                Question.id.notin_(previous_questions)).all()
        return question_selection

    @app.route('/quizzes', methods=['POST'])
    def get_new_quiz_question():
        '''a POST endpoint to get questions to play the quiz'''
        try:
            min_num_of_questions = 6
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            question_selection = get_question_selection_from_category(
                quiz_category, previous_questions)
            quiz_question = get_a_random_question(question_selection)
            count = 0
            if quiz_question:
                count = 1
            return jsonify({
                'success': True,
                'quiz_category': quiz_category,
                'question': quiz_question,
                'total_questions': count
            }), OK
        except AttributeError as attribute_error:
            print("ATTRIBUTE ERROR: ", attribute_error)
            abort(UNPROCESSABLE_ENTITY)
        except Exception as e:
            print("Exception: ", e)
            abort(UNPROCESSABLE_ENTITY)
    '''
    test using:
    curl -X POST -H "Content-Type: application/json" -d
     '{"previous_questions":[20, 21, 22, 27, 28],
      "quiz_category":{"type": "Science", "id": "1"}}'
       http://127.0.0.1:5000/quizzes
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
