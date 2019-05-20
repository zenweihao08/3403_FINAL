from  _datetime import datetime
import unittest, os
from flaskpoll import app, db, bcrypt
from flaskpoll.models import User, Poll

class UserModelCase(unittest.TestCase):

    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI']= \
            'sqlite:///'+os.path.join(basedir,'test.db')
        self.app = app.test_client()#creates a virtual test environment
        db.create_all()
        u1 = User(
            id=1,username='Tom',email="tom@test.com",
            password=bcrypt.generate_password_hash("test").decode('utf-8')
        )
        u2 = User(
            id=2,username='Tom2',email="tom2@test.com",
            password=bcrypt.generate_password_hash("test2").decode('utf-8')
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        user = User.query.filter_by(id=1).first()
        self.assertFalse(user.password=='test')

class PollModelCase(unittest.TestCase):

    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI']= \
            'sqlite:///'+os.path.join(basedir,'test.db')
        self.app = app.test_client()#creates a virtual test environment
        db.create_all()
        p1 = Poll(
            id=1,
            title='title1',
            release_date = datetime.strptime('1997-12-19' ,'%Y-%m-%d').date(),
            introduction= 'some introduction',
            rank = 0,
            image_url='https://ss1.baidu.com/9vo3dSag_xI4khGko9WTAnF6hhy/image/h%3D300/sign=92afee66fd36afc3110c39658318eb85/908fa0ec08fa513db777cf78376d55fbb3fbd9b3.jpg',
            initiator=1
        )
        p2 = Poll(
            id=2,
            title='title1',
            release_date = datetime.strptime('1997-12-19' ,'%Y-%m-%d').date(),
            introduction= 'some introduction',
            rank = 0,
            image_url='https://ss1.baidu.com/9vo3dSag_xI4khGko9WTAnF6hhy/image/h%3D300/sign=92afee66fd36afc3110c39658318eb85/908fa0ec08fa513db777cf78376d55fbb3fbd9b3.jpg',
            initiator=1
        )
        u1 = User(
            id=1,username='Tom',email="tom@test.com",
            password=bcrypt.generate_password_hash("test").decode('utf-8')
        )
        u2 = User(
            id=2,username='Tom2',email="tom2@test.com",
            password=bcrypt.generate_password_hash("test2").decode('utf-8')
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_poll(self):
        poll = Poll.query.filter_by(id=1).first()
        user =User.query.filter_by(id=1).first()
        user.cast_to=1
        user.voted=True
        poll.rank+=1


        self.assertTrue(user.voted)
        self.assertEqual(poll.rank,1)


if __name__=='__main__':
    unittest.main(verbosity=2)
