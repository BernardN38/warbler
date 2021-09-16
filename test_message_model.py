import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"



from app import app



db.create_all()

class UserModelTestCase(TestCase):


    def setUp(self):

        db.drop_all()
        db.create_all()

        self.uid = 8675309
        u = User.signup("tester", "tester@gmail.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_message_model(self):

        msg = Message(
            text="the world is yours",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "the world is yours")

    def test_message_likes(self):
        msg1 = Message(
            text="the world is yours",
            user_id=self.uid
        )

        msg2 = Message(
            text="live laugh love",
            user_id=self.uid 
        )

        u = User.signup("obi_wan", "tatooine@email.com", "password", None)
        uid = 45923
        u.id = uid
        db.session.add_all([msg1, msg2, u])
        db.session.commit()

        u.likes.append(msg1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, msg1.id)