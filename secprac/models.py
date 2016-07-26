import cryptacular.bcrypt
from sqlalchemy import Column, Integer, Text, Unicode

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, synonym

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()
def hash_password(password):
    return unicode(crypt.encode(password))

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    _password = Column(Unicode(60), nullable=False)
    name = Column(Unicode(255))
    about_me = Column(Unicode(255))

    #########################################################
    # Hashing the password ####################################
    def _get_password(self):                         ####   ####
        return self._password                       # ## #  ####
    def _set_password(self, password):               ####   ####
        self._password = hash_password(password)            ####
                                                            ####
    password = property(_get_password, _set_password)       ####
    password = synonym('_password', descriptor=password)    ####
    ###########################################################
    #########################################################

    # Checking the password
    @classmethod
    def check_password(cls, login, password):
        user = DBSession.query(cls).filter(cls.username==login).first()
        if user:
            return crypt.check(user.password, password)
        else:
            return False

