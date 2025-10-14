import json
import base64
import hmac
import hashlib
import time
from typing import Optional, Dict, List, Any

# --- 전역 상수 정의 ---
NICKNAME = ""
# 토큰 서명에 사용되는 비밀 키
SECRET_KEY = "My_Super_Secret_Key_JWT"
# 토큰 유효 시간: 10초
TOKEN_LIFETIME_SECONDS = 10

# ===================start: DB 대체====================
# 임의의 사용자 정보
USER_INFORMATIONS = [
    {"user_id": 1, "username": "이건우", "password": "qwerqwer!", "nickname": "게임 만드는 자"},
    {"user_id": 2, "username": "최건희", "password": "asdfasdf!", "nickname": "건희"},
    {"user_id": 3, "username": "이아진", "password": "zxcvzxcv!", "nickname": "아진"},
    {"user_id": 4, "username": "송호창", "password": "tyuityui!", "nickname": "송호창"},
]

# 임의의 게시글 정보
POSTS = [
    {"post_id": 1, "user_id": 1, "content": "아무도 몰랐던 심화반 사전과제 코드의 정체!!!"},
    {"post_id": 2, "user_id": 1, "content": "아 피곤하다....."},
    {"post_id": 3, "user_id": 2, "content": "건희건희건희 테스트"},
    {"post_id": 4, "user_id": 2, "content": "건??? 희????"},
    {"post_id": 5, "user_id": 3, "content": "친구들이 미쳐가는 것 같아요!! 살려줘요!!!"},
    {"post_id": 6, "user_id": 3, "content": "그 친구가 나야나!! 나야나!!!"},
    {"post_id": 7, "user_id": 4, "content": "나만 정상인듯....."},
]
# ===================end: DB 대체====================

# --- Base64URL 암,복호화 ---
def b64url_encode(data: Dict[str, Any]) -> str:
    '''
    JSON 딕셔너리를 Base64URL로 인코딩합니다.

    json을 base64url로 변환해야하는 이유:
        * base64Url 인코딩은 base64 인코딩 문자열이 URL에 사용될 수 있도록 변경한 인코딩 방법이다.
        * 표준 Base64 인코딩에는 URL에 사용될 경우 문제를 일으킬 수 있는 '+', '/' 문자가 포함되기에 이를 해결하고자 
          Base64URL에서는 그것들을 URL에 안전한 '-', '_' 문자로 대체하고, 
          URL에 불필요한 패딩 문자 '='를 제거하여 URL에서 데이터를 안전하게 사용할 수 있도록하는것이 목적이다.
    '''
    json_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
    encoded = base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')
    return encoded

# Optional: None 이 허용되는 함수의 매개 변수에 대한 타입을 명시할 때 유용
def b64url_decode(encoded_str: str) -> Optional[Dict[str, Any]]:
    """
        Base64URL 문자열을 디코딩하여 JSON 딕셔너리로 변환합니다.

        * Base64 문자열의 길이는 4의 배수여야 한다.
        * Base64 표준 길이를 맞추기 위해 제거된 패딩('=' 기호)를 다시 추가한다.
    """
    padding_needed = 4 - (len(encoded_str) % 4)
    padded_encoded_str = encoded_str + ('=' * padding_needed)
    try:
        decoded_bytes = base64.urlsafe_b64decode(padded_encoded_str.encode('utf-8'))
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception:
        return None

# --- JWT 생성 및 검증 ---
def create_jwt(user_id: str) -> str:
    """
        Access Token을 생성하고 반환합니다.
        
        헤더(Header), 페이로드(Payload), 서명(Signature) 세 부분으로 구성한다.
    """
    # 토큰을 사용하는 측의 토큰 유형이 JWT임을 확신할 수 있다면 typ필드는 생략 가능하다.
    header = {"alg": "HS256", "typ": "JWT"}
    
    '''
    payload: 
        사용자의 정보 혹은 데이터 속성 등을 나타내는 클레임(Claim) 이라는 정보 단위로 구성
    클레임(Claim): 3가지로 구분된다.
        * 등록된 클레임(Registered Claim): JWT 사양에 이미 정의된 클레임(7개의 등록된 클레임이 정의)
        * 공개 클레임(Public Claim): JWT를 사용하는 사람들에 의해 정의되는 클레임(url형태의 이름 또는 IANA JSON Web Token Claims Registry claim등록)
        * 비공개 클레임(Private Claim): 서버와 클라이언트 사이에서만 협의된 클레임 <<
    '''
    # 유효 시간(Expiration Time, 'exp')을 현재 시간 + 유효 시간(초)으로 설정
    payload = {
        "user_id": user_id, 
        "exp": int(time.time()) + TOKEN_LIFETIME_SECONDS
    }
    # JSON → base64url 인코딩
    encoded_header = b64url_encode(header)
    encoded_payload = b64url_encode(payload)
    
    header_payload = f"{encoded_header}.{encoded_payload}"
    
    # 서명 생성 (HMAC-SHA256) -> SHA-256 해시 함수는 단방향 해시 함수이기 때문에, 일반적으로 복호화가 불가능. 따라서 SHA-256을 사용하여 암호화할 데이터를 저장할 때, 복호화가 필요한 경우에는 대안적인 방법을 사용해야 한다.
    # 암호화 방식을 공유하여 서명이 맞는것인지 비교할것.
    # 바이너리(bytes) 형식으로 반환 (Base64사용을 위해서)
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        header_payload.encode('utf-8'),
        hashlib.sha256).digest()
    # URL에 불필요한 패딩 문자 '='를 제거
    encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    # {헤더.페이로드}.{SHA-256로 해싱(hmac암호화서명(비밀키+헤더+페이로드))}
    return f"{header_payload}.{encoded_signature}"

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Access Token의 유효성(서명 및 만료 시간)을 검증하고 페이로드를 반환합니다."""
    
    # 헤더.페이로드.서명
    parts = token.split('.')
    if len(parts) != 3:
        print("토큰 형식이 올바르지 않습니다.")
        return None

    encoded_header, encoded_payload, encoded_signature = parts
    header_payload = f"{encoded_header}.{encoded_payload}"

    # 서명을 재계산하여 토큰검증
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        header_payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected_signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')

    # 파라미터값과 재계산값이 맞는지 검증
    if encoded_signature != expected_signature:
        print("🚨 오류: 서명이 일치하지 않습니다. 토큰이 변조되었을 수 있습니다.")
        return None

    # 유효시간 검증을 위한 페이로드 디코딩
    payload = b64url_decode(encoded_payload)
    if not payload:
        return None

    # 유효시간 검증
    current_time = int(time.time())
    if 'exp' in payload and current_time > payload['exp']:
        print(f"🚨 오류: 토큰이 만료되었습니다. ({time.ctime(payload['exp'])} 만료)")
        return None
        
    return payload

# --- 사용자 인증 및 데이터 접근 로직 ---
def authenticate_user(user_id: str, password: str) -> Optional[Dict[str, Any]]:
    """ 
        ID/PW로 사용자 정보를 반환합니다.
    """
    for user in USER_INFORMATIONS:
        if str(user["user_id"]) == user_id and user["password"] == password:
            return user
    return None

def get_posts_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """
        user_id에 해당하는 게시글만 필터링하여 반환합니다.
    """
    return [post for post in POSTS if post["user_id"] == user_id]


# --- 사용자로그인 및 token 사용 ---
def run_login_flow():
    """
        사용자 로그인 및 Access Token을 발급합니다.
    """
    print("\n=========================================")
    print("          로그인을 진행합니다.")
    print("=========================================")
    
    username = input("아이디: ")
    password = input("비밀번호: ")
    
    authenticated_user = authenticate_user(username, password)
    access_token = None
    
    if authenticated_user:
        user_id = authenticated_user["user_id"]
        NICKNAME = authenticated_user["nickname"]
        
        # Access Token 발급
        access_token = create_jwt(user_id)
        
        print(f"\n✅ 로그인 성공! ({NICKNAME}님)환영합니다. \nAccess Token:\n{access_token}")
    else:
        print("\n❌ 로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.")
    
    return access_token

def run_verification_flow(token: str):
    """
        발급된 Access Token으로 게시글을 조회합니다.
    """
    print("\n=========================================")
    print("          사용자의 게시글을 조회합니다.")
    print("=========================================")
    
    if not token:
        print("토큰이 없어 검증을 진행할 수 없습니다.")
        return

    # 1. 토큰 검증
    verified_payload = verify_jwt(token)

    if verified_payload:
        user_id = verified_payload.get("user_id")
        
        # 2. user_id를 이용해 게시글 정보 가져오기 (인가된 접근)
        user_posts = get_posts_by_user_id(user_id)

        print(f"\n✅ 토큰 검증 성공!")
        print(f"   >>> {NICKNAME} 님의 게시글 목록:")
        
        if user_posts:
            for post in user_posts:
                print(f"   - [Post ID: {post['post_id']}] {post['content']}")
        else:
            print("   - 작성된 게시글이 없습니다.")
            
    else:
        # verify_jwt 함수 내에서 오류 메시지가 이미 출력됨
        print("\n❌ 토큰 검증에 실패하여 게시글을 가져올 수 없습니다.")

