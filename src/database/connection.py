from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:todos@127.0.0.1:3306/todos"

#echo=True 쿼리 실행 시 해당 쿼리 print해준다. 디버깅용.
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#generator
def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()