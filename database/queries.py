from database.connect import start_session
# from connect import start_session
# from database.schema import Customer
from database.schema import Customer

from functools import wraps

session = start_session()

def session_committer(func):
    """Decorator to commit the DB session.

    Use this from high-level functions such as handler so that the session is always committed or
    closed.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            commit_session()

    return wrapper


def commit_session(_raise=True):
    if not session:
        return
    try:
        session.commit()
    except Exception:
        session.rollback()
        if _raise:
            raise

def get_customers():
    return session.query(Customer). \
        all()




