
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from cache import redis_client
from database.orm import User
from database.repository import UserRepository
from schema.request import SignUpRequest, LogInRequest, CreateOTPRequest, VerifyOTPRequest
from schema.response import UserSchema, JWTResponse
from security import get_access_token
from service.user import UserService

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
):
    # 1. request body(username, password)
    # 2. password -> hashing -> hashed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
    )

    # 3. User(username, hashed_password)
    user: User = User.create(
        username=request.username, hashed_password=hashed_password
    )

    # 4. user -> db save
    user: User = user_repo.save_user(user=user) # id=int

    # 5. return user(id, username)
    return UserSchema.from_orm(user)

@router.post("/log-in")
def user_log_in_handler(
        request: LogInRequest,
        user_repo: UserRepository = Depends(),
        user_service: UserService = Depends(),
):
    # 1. request body(username, password)
    # 2. db -> read user
    user: User | None = user_repo.get_user_by_username(
        username=request.username
    )

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    # 3. user.password, request.password -> bycrypt.checkpw
    verfied: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password,
    )

    if not verfied:
        raise HTTPException(status_code=401, detail="Not Authorized")

    # 4. if passed -> create jwt
    access_token: str = user_service.create_jwt(username=user.username)

    # 5. return jwt
    return JWTResponse(access_token=access_token)

# 현재 구현된 기능 : 회원가입 (username, password) / 로그인
# 이메일 알림 : 회원가입 -> 이메일 인증 (OTP로 인증) -> 유저 이메일 저장 -> 이메일 알림

# POST /users/email/otp -> key: email, value: otp random 4-digit key, exp: 3min)
# POST /users/email/otp/verify -> request(email, otp) -> user(email)

@router.post("/email/otp")
def create_otp_handler(
    request: CreateOTPRequest,
    # accesss_token을 검증만하고 사용은 안할거기 때문에 _ 처리
    _: str = Depends(get_access_token),
    user_service: UserService = Depends(),
):
    # 1. access_token
    # 2. request body(email)
    # 3. otp create(random 4 digit)
    otp: int = user_service.create_otp()

    # 4. redis otp(email, 1234, emp=3min)
    redis_client.set(request.email, otp)
    redis_client.expire(request.email, 3*60) # 3분

    # 5. send otp to email
    return {"otp": otp}

@router.post("/email/otp/verify")
def create_otp_handler(
    request: VerifyOTPRequest,
    background_task: BackgroundTasks,
    access_token: str = Depends(get_access_token),
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
):
    # 1. access_token
    # 2. request body(email, otp)

    otp: str | None = redis_client.get(request.email)
    if not otp:
        raise HTTPException(status_code=400, detail="Bad Request")

    if request.otp == otp:
        pass

    if request.otp != int(otp):
        raise HTTPException(status_code=400, detail="Bad Request")

    # 3. request.otp == redis.get(email)
    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    # save email to user

    # send email to user
    # 메인 로직과 별개로 backround_task는 새로운 쓰레드로 함수를 동작시킴
    background_task.add_task(
        user_service.send_email_to_user,
        email="admin@fastapi.com"
    )

    return UserSchema.from_orm(user)