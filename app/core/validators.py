import re
from app.core.exceptions import bad_request, unprocessable

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NICKNAME_SPACE = re.compile(r"\s")

def validate_email(email: str):
    if not email:
        raise bad_request("email_required")
    if not EMAIL_RE.match(email):
        raise bad_request("invalid_email_format")
    if not re.fullmatch(r"[A-Za-z0-9@._+-]+", email):
        raise bad_request("invalid_email_character", {"allowed": "영문, @, ."})
    return True

def validate_password(pw: str, field="password"):
    if not pw:
        raise bad_request(f"{field}_required")
    if len(pw) < 8 or len(pw) > 20 or \
       not re.search(r"[A-Z]", pw) or \
       not re.search(r"[a-z]", pw) or \
       not re.search(r"[0-9\W_]", pw):
        raise bad_request("invalid_password_format")
    return True

def validate_password_pair(pw: str, pw_check: str, raise_validation_failed=False):
    """비밀번호 쌍 검증. raise_validation_failed=True일 경우 password_validation_failed 형식으로 반환"""
    if not pw:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", {"reason": "password_blank"})
        raise bad_request("password_required")
    if not pw_check:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", {"reason": "password_check_blank"})
        raise bad_request("password_check_required")
    
    # 비밀번호 형식 검증
    if len(pw) < 8 or len(pw) > 20:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", {"reason": "password_too_short"})
        raise bad_request("invalid_password_format")
    if not re.search(r"[A-Z]", pw) or not re.search(r"[a-z]", pw) or not re.search(r"[0-9\W_]", pw):
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", {"reason": "password_invalid_format"})
        raise bad_request("invalid_password_format")
    
    if pw != pw_check:
        if raise_validation_failed:
            raise unprocessable("password_validation_failed", {"reason": "password_mismatch"})
        raise unprocessable("password_mismatch")
    return True

def validate_nickname(nickname: str, raise_validation_failed=False):
    """닉네임 검증. raise_validation_failed=True일 경우 validation_failed 형식으로 반환"""
    if not nickname:
        if raise_validation_failed:
            raise unprocessable("validation_failed", {"field": "nickname", "reason": "nickname_blank"})
        raise bad_request("nickname_required")
    if NICKNAME_SPACE.search(nickname):
        if raise_validation_failed:
            raise unprocessable("validation_failed", {"field": "nickname", "reason": "nickname_has_space"})
        raise bad_request("nickname_contains_space")
    if len(nickname) > 10:
        if raise_validation_failed:
            raise unprocessable("validation_failed", {"field": "nickname", "reason": "nickname_too_long"})
        raise bad_request("nickname_too_long", {"max_length": 10})
    return True

def validate_title(title: str):
    if len(title) > 26:
        raise unprocessable("title_too_long", {"max_length": 26})

