import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup


os.environ['DATABASE_URL'] = "postgresql:///warbler_test_db"
from app import app, CURR_USER_KEY
db.create_all()
app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="tester123",
                                    email="test123@test.com",
                                    password="testuser654321",
                                    image_url=None)
        self.testuser_id = 11223344
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("John", "test1@test.com", "password", None)
        self.u1_id = 7784
        self.u1.id = self.u1_id

        self.u2 = User.signup("Alex", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id



        self.u3 = User.signup("Henry", "test3@test.com", "password", None)
        self.u4 = User.signup("William", "test4@test.com", "password", None)

        db.session.commit()
    
    def setup_followers(self):
        follow1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        follow2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        follow3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([follow1,follow2,follow3])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_users_index(self):
        with self.client as client:
            resp = client.get("/users")

            self.assertIn("@tester123", str(resp.data))
            self.assertIn("@john", str(resp.data))
            self.assertIn("@Alex", str(resp.data))
            self.assertIn("@Henry", str(resp.data))
            self.assertIn("@william", str(resp.data))

    def test_users_search(self):
        with self.client as client:
            resp = client.get("/users?q=test")

            self.assertIn("@tester123", str(resp.data))           

            self.assertNotIn("@abc", str(resp.data))
            self.assertNotIn("@efg", str(resp.data))
            self.assertNotIn("@hij", str(resp.data))

    def test_user_show(self):
        with self.client as client:
            res = client.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)

            self.assertIn("@tester123", str(res.data))

    def setup_likes(self):
        msg1 = Message(text="woe is me", user_id=self.testuser_id)
        msg2 = Message(text="to be or not to be", user_id=self.testuser_id)
        msg3 = Message(id=1234, text="Drake music is kewl", user_id=self.u1_id)
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()
        like1 = Likes(user_id=self.testuser_id, message_id=1234)

        db.session.add(like1)
        db.session.commit()
    
    def test_show_following(self):

        self.setup_followers()
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            resp = client.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@John", str(resp.data))
            self.assertIn("@Alex", str(resp.data))
            self.assertNotIn("@henry", str(resp.data))
            self.assertNotIn("@william", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as client:

            resp = client.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@John", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))