# 네이버 서이추 자동 프로그램

## 언어
python 3.11.5
## 사용 라이브러리
- selenium
- tkinter
- asyncio
- webdriver_manager
- selenium
- pandas

## 실행
가상 머신\Scripts\activate.bat
> python ../main.py
## 실행 파일 생성
가상 머신\Scripts\activate.bat
pyinstaller -F -n "프로그램" -w --upx-dir C:\...\upx ../main.py

## version
1.0.4
- 2차 인증 시간을 위해 로그인 초기화면 5분 대기 추가