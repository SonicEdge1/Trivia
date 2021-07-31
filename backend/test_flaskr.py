import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from sqlalchemy.orm.session import make_transient

OK = 200
BAD_REQUEST = 400
BAD_REQUEST_MSG = "Bad Request"
RESOURCE_NOT_FOUND = 404
RESOURCE_NOT_FOUND_MSG = "Resource Not Found"
METHOD_NOT_ALLOWED = 405
METHOD_NOT_ALLOWED_MSG = "Method Not Allowed"
UNPROCESSABLE_ENTITY = 422
UNPROCESSABLE_ENTITY_MSG = "Unprocessable Entity"
TEST_QUESTION_TEXT = 'How many different actors have portrayed the character James Bond in the 26 films released between 1962-2015'
DUPLICATE_TEXT = "What is the largest lake in Africa?"
DELETE_QUESTION_TEST = "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': TEST_QUESTION_TEXT,
            'answer': 'Seven',
            'difficulty': 4,
            'category': '5'
        }

        self.duplicate_question = {
            'question': DUPLICATE_TEXT,
            'answer': 'Lake Victoria',
            'difficulty': 2,
            'category': "3"
        }



        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    

    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_success_get_categories(self):
        """Test success at GET '/categories'"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['categories'])


    def test_success_get_questions_of_category(self):
        """Test success at GET '/categories/<int:category_id>/questions'"""
        category_id = 1
        category_name = "Science"
        questions_in_category = 6
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], category_name)
        self.assertEqual(data['total_questions'], questions_in_category)
        self.assertTrue(data['questions'])


    def test_success_delete_question_by_id(self):
        """Test success at DELETE '/questions/<int:question_id>"""
        question_id = 2
        question_text = DELETE_QUESTION_TEST
        question = Question.query.get(question_id)
        res = self.client().delete(f'/questions/{question_id}')
        removed_question = Question.query.filter_by(id = question_id).one_or_none()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question_text'], question_text)
        self.assertEqual(data['deleted_question_id'], question_id)
        self.assertEqual(removed_question, None)
        make_transient(question)
        Question.insert(question)


    def test_success_search_question_by_string(self):
        """Test success at POST '/questions' with json searchTerm"""
        term = "soccer"
        num_questions_with_term = 2
        res = self.client().post('/questions', json={'searchTerm': f'{term}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], num_questions_with_term)
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])


    def test_success_add_question(self):
        """Test success at POST '/questions' with json to add question"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], TEST_QUESTION_TEXT)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['new_question_id'])
        new_id = data['new_question_id']
        self.client().delete(f'/questions/{new_id}')


    def test_fail_to_add_duplicate_question(self):
        """Test fail at POST '/questions' with json to add DUPLICATE question"""
        res = self.client().post('/questions', json=self.duplicate_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['question'], DUPLICATE_TEXT)
        self.assertTrue(data['total_questions'])


    def test_success_qet_quiz_question(self):
        """Test success at POST '/quizzes' with json providing category and previous question list"""
        quiz_category = {"type": "Science", "id": "1"}
        previous_questions = [20, 21, 22, 27, 28]
        remaining_question_id = 29
        res = self.client().post('/quizzes', json={'quiz_category': quiz_category, 'previous_questions' : previous_questions})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], remaining_question_id)
        self.assertEqual(data['quiz_category'], quiz_category)


    def test_success_qet_quiz_question_when_not_enough_questions(self):
        """Test success at POST '/quizzes' when there are too few questions in category"""
        quiz_category = {"type": "Sports", "id": "6"}
        num_sports_questions = 2
        previous_questions = [10]
        res = self.client().post('/quizzes', json={'quiz_category': quiz_category, 'previous_questions' : previous_questions})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)
        self.assertEqual(data['total_questions'], num_sports_questions)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()