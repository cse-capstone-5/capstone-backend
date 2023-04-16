import sys
import json

def test(x):
    ret={"result":x}
    # 표준입출력으로 출력된것을 nodejs에서 인식합니다.
    print(json.dumps(ret,ensure_ascii = False))

if __name__ == '__main__':
    # sys.argv로 test.py 뒤에 인자 받기
    test(sys.argv[1])