from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from schema.request import CreateToDoRequest

Base = declarative_base()

class ToDo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"Todo(id={self.id}, contents={self.contents}, is_done={self.is_done})"

    @classmethod
    def create(cls, request: CreateToDoRequest):
        return cls(
            contents= request.contents,
            is_done= request.is_done,
        )

    def done(self) -> "ToDo":
        self.is_done = True
        #send email과 같이 인스턴스 메서드에 작성해놓으면 추가 기능 구현에 유리
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    # relationship으로 User와 Toodo의 관계를 명시해두면
    # scalar로 조회했을 때 두 테이블이 조인되어 결과가 나옴
    todos = relationship("ToDo", lazy="joined")

    @classmethod
    def create(cls, username: str, hashed_password: str) -> "User":
        return cls(
            username=username,
            password=hashed_password,
        )

# ORM의 데이터 조회 방법
# Lazy Loading
#   지연 로딩 : 연관된 객체의 데이터가 실제 필요한 시점에 조회
#   장점 : 첫 조회 속도가 더 빠름
#   단점 : N+1 문제 발생
# N+1 문제란?
# 데이터의 갯수만큼 조인이 발생함.
#   for td in todos:
#       print(td.user.username)

# Eager Loading
#   즉시 로딩 : 데이터를 조회할 때 처음부터 연관된 객체를 같이 읽어옴
#   장점 : 데이터를 더 효율적으로 가져올 수 있음 (N+1 발생X)
#   단점 : 꼭 필요하지 않은 데이터까지 JOIN하여 읽어올 수 있음.