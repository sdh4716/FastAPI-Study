import random
import time

import bcrypt

from datetime import datetime, timedelta
from jose import jwt

class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "a1b8d61ec0f4fbd1cc5162602e61f2a2b2ded7026a41fd2320a1fa77245ec12a"
    jwt_algorithm: str = "HS256"

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding),
            salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.encoding)

    def verify_password(
            self, plain_password: str,
            hashed_password: str
    ) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding)
        )

    def create_jwt(self, username: str) -> str:
        return jwt.encode(
            {
                # subject : 식별자
                "sub": username, # unique한 식별자 사용해야함
                # expire : 토큰 만료시간
                "exp": datetime.now() + timedelta(days=1)
             },
            self.secret_key, algorithm=self.jwt_algorithm
        )

    def decode_jwt(self, access_token: str):
        payload: dict = jwt.decode(
            access_token, self.secret_key, algorithms=[self.jwt_algorithm]
        )

        # expire
        return payload["sub"] #username

    @staticmethod
    def create_otp() -> int:
        return random.randint(1000, 9999)

    @staticmethod
    def send_email_to_user(email: str) -> None:
        time.sleep(10)
        print(f"Sending email to {email}!")