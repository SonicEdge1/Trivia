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
TEST_QUESTION_TEXT = "How many different actors have portrayed the character" \
                     " James Bond in the 26 films released between 1962-2015"
DUPLICATE_TEXT = "What is the largest lake in Africa?"
DELETE_QUESTION_TEST = "What movie earned Tom Hanks his third straight Oscar" \
                       " nomination, in 1996?"


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_port = "localhost:5432"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            self.database_port,
            self.database_name)

        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': TEST_QUESTION_TEXT,
            'answer': "Seven",
            'difficulty': 4,
            'category': "5"
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

    def test_fail_post_categories(self):
        """Test fail a POST to '/categories'"""
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_put_categories(self):
        """Test fail a PUT to '/categories'"""
        res = self.client().put('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_patch_categories(self):
        """Test fail a PATCH to '/categories'"""
        res = self.client().patch('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_delete_categories(self):
        """Test fail a DELETE to '/categories'"""
        res = self.client().delete('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_success_get_questions(self):
        """Test success at GET '/questions'"""
        category_name = "Science"
        total_questions = 36
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], category_name)
        self.assertEqual(data['total_questions'], total_questions)

    def test_fail_delete_questions_at_base_question_url(self):
        """Test fail DELETE at '/questions'"""
        res = self.client().delete('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_put_questions(self):
        """Test fail PUT at '/questions'"""
        res = self.client().put('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_patch_questions(self):
        """Test fail PATCH at '/questions'"""
        res = self.client().patch('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

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

    def test_fail_get_questions_of_missing_category(self):
        """Test fail at GET '/categories/<int:category_id>/questions'
         w category not in DB"""
        category_id = 7
        category_name = "Non-Existant"
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, UNPROCESSABLE_ENTITY)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], UNPROCESSABLE_ENTITY_MSG)

    def test_success_delete_question_by_id(self):
        """Test success at DELETE '/questions/<int:question_id>"""
        question_id = 2
        question_text = DELETE_QUESTION_TEST
        question = Question.query.get(question_id)
        res = self.client().delete(f'/questions/{question_id}')
        removed_question = Question.query.filter_by(
            id=question_id).one_or_none()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question_text'], question_text)
        self.assertEqual(data['deleted_question_id'], question_id)
        self.assertEqual(removed_question, None)
        make_transient(question)
        Question.insert(question)

    def test_fail_delete_question_by_missing_id(self):
        """Test success at DELETE '/questions/<int:question_id>'
         w non-existant ID"""
        question_id = 200
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, UNPROCESSABLE_ENTITY)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], UNPROCESSABLE_ENTITY_MSG)

    def test_fail_post_question_by_id(self):
        """Test fail at POST '/questions/<int:question_id>'"""
        question_id = 200
        res = self.client().post(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_get_question_by_id(self):
        """Test fail at GET '/questions/<int:question_id>'"""
        question_id = 200
        res = self.client().get(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_put_question_by_id(self):
        """Test fail at PUT '/questions/<int:question_id>'"""
        question_id = 200
        res = self.client().put(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_patch_question_by_id(self):
        """Test fail at PATCH '/questions/<int:question_id>'"""
        question_id = 200
        res = self.client().patch(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

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

    def test_success_search_question_by_string_no_results(self):
        """Test success at POST '/questions' with json searchTerm"""
        term = "ignoramus"
        num_questions_with_term = 0
        res = self.client().post('/questions', json={'searchTerm': f'{term}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], num_questions_with_term)
        self.assertEqual(data['questions'], [])
        self.assertTrue(data['current_category'])

    def test_fail_search_question_by_string_with_malformed_json(self):
        """Test fail at POST '/questions' with bad json"""
        term = "ignoramus"
        res = self.client().post('/questions', json={'badJson': f'{term}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, UNPROCESSABLE_ENTITY)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], UNPROCESSABLE_ENTITY_MSG)

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

    def test_fail_add_question_missing_data(self):
        """Test success at POST '/questions' missing json"""
        res = self.client().post('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, UNPROCESSABLE_ENTITY)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], UNPROCESSABLE_ENTITY_MSG)

    def test_success_wont_add_duplicate_question(self):
        """Test success at POST '/questions'
         with json to add DUPLICATE question, no question added to DB"""
        res = self.client().post('/questions', json=self.duplicate_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['question'], DUPLICATE_TEXT)
        self.assertTrue(data['total_questions'])

    def test_success_qet_quiz_question(self):
        """Test success at POST '/quizzes'
         with json providing category and previous question list"""
        quiz_category = {"type": "Science", "id": "1"}
        previous_questions = [20, 21, 22, 27, 28]
        remaining_question_id = 29
        res = self.client().post(
            '/quizzes',
            json={
                'quiz_category': quiz_category,
                'previous_questions': previous_questions})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], remaining_question_id)
        self.assertEqual(data['quiz_category'], quiz_category)

    def test_success_qet_quiz_question_when_no_questions_left(self):
        """Test success at POST '/quizzes'
         when there are no questions left in category"""
        quiz_category = {"type": "Sports", "id": "6"}
        num_sports_questions_left = 0
        previous_questions = [10, 11]
        res = self.client().post(
            '/quizzes',
            json={
                'quiz_category': quiz_category,
                'previous_questions': previous_questions})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, OK)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)
        self.assertEqual(data['total_questions'], num_sports_questions_left)

    def test_fail_qet_quiz_question_wout_json(self):
        """Test fail at POST '/quizzes' without json"""
        res = self.client().post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, UNPROCESSABLE_ENTITY)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], UNPROCESSABLE_ENTITY_MSG)

    def test_fail_qet_quiz_question_bad_url(self):
        """Test fail at POST '/quizzes/1' no url"""
        res = self.client().post('/quizzes/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, RESOURCE_NOT_FOUND)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], RESOURCE_NOT_FOUND_MSG)

    def test_fail_GET_quiz_question_method(self):
        """Test fail at GET '/quizzes'"""
        res = self.client().get('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_patch_quiz_question(self):
        """Test fail at PATCH '/quizzes'"""
        res = self.client().patch('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_PUT_quiz_question(self):
        """Test fail at PUT '/quizzes'"""
        res = self.client().put('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)

    def test_fail_DELETE_quiz_question(self):
        """Test fail at DELETE '/quizzes'"""
        res = self.client().delete('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, METHOD_NOT_ALLOWED)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], METHOD_NOT_ALLOWED_MSG)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
