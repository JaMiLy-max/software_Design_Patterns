import time
from jwt_functions import (
    run_login_flow,
    run_verification_flow,
    TOKEN_LIFETIME_SECONDS
)

if __name__ == "__main__":
    
    # 1. 로그인 및 토큰 발급
    issued_token = run_login_flow()
    
    if issued_token:
        # 2. 토큰 검증 및 리소스 접근
        run_verification_flow(issued_token)
        
        # 3. (option) 만료 시간 테스트
        test_expiry = input(f"만료 테스트를 위해 {TOKEN_LIFETIME_SECONDS + 1}초 대기하시겠습니까? (y/n): ").lower()
        
        if test_expiry == 'y':
            print("\n=========================================")
            print("          Token 만료 테스트 (10초)")
            print("=========================================")
            wait_time = TOKEN_LIFETIME_SECONDS + 1
            print(f"{wait_time}초 동안 대기합니다. 토큰은 {TOKEN_LIFETIME_SECONDS}초에 만료됩니다...")
            time.sleep(wait_time)
            print("대기 완료. 만료된 토큰으로 재시도합니다.")
            
            run_verification_flow(issued_token)
        else:
            run_verification_flow(issued_token)



