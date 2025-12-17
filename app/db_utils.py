from app import db
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps


class BusinessError(Exception):
    """Erro de regra de negócio (não técnico)."""
    pass

def transactional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            db.session.commit()
            return result
        
        except BusinessError:
            db.session.rollback()
            raise
        
        except SQLAlchemyError:
            db.session.rollback()
            raise 
        
        except Exception:
            db.session.rollback()
            raise 
    return wrapper
