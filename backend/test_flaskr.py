import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': 'This is a question',
            'answer': 'This is an answer',
            'category': 1,
            'difficulty' : 100
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        categories = Category.query.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), len(categories))


    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        questions = Question.query.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], len(questions))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        q_count = len(Question.query.all())
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
        self.assertEqual(data['total_questions'], q_count-1)

    def test_404_a_non_existing_question(self):
        q_count = len(Question.query.all())
        res = self.client().delete('/questions/1000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_questions(self):
        q_count = len(Question.query.all())
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        question_id = data['created']
        question = Question.query.filter(Question.id == question_id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(question)
        self.assertEqual(data['total_questions'], q_count+1)
    
    def test_422_faild_create_questions(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_questions(self):
        res = self.client().post('/questions', json={'search': 'This is a question'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])

    def test_404_search_term_not_exist_in_questions(self):
        res = self.client().post('/questions', json={'search': 'Nonsense not real texr'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_retrieve_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        questions_count = len(Question.query.filter_by(category=1).all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), questions_count)
    
    def test_404_category_not_exist_in_questions(self):
        res = self.client().get('/categories/1847474/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_play(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':{},
            'quiz_category': {'id': 0}
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()