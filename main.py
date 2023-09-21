import tkinter as tk
from tkinter import *
from tkinter import Scrollbar, ttk
from tkinter import scrolledtext
import asyncio
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows
import os
import pandas as pd
import pyperclip
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import messagebox as msgbox
import traceback
import time

serviceChrome = None


"""
----------------- UI ----------------------

"""


def TTkStyleConfigure(style):
    style.theme_use("clam")
    style.configure(
        "InputLabel.TLabel",
        background="#fff",
        foreground="#212121",
        borderwidth=0,
        font=("Arial", 12),
        width=10,
    )
    style.configure(
        "LabelFrame.TLabel",
        background="#fff",
        foreground="#212121",
        borderwidth=0,
        font=("Arial", 14, "bold"),
        width=20,
    )

    style.configure(
        "FullLabel.TLabel",
        background="#fff",
        foreground="#212121",
        borderwidth=0,
        font=("Arial", 12),
        cursor="xterm",
    )

    style.configure(
        "Input.TEntry",
        padding=10,
        background="#fff",
        foreground="#212121",
        bordercolor="#FF5733",
        font=("Arial", 12),
    )
    style.configure("InputLabel.TFrame", background="#fff")
    style.configure(
        "Radiobutton.TRadiobutton",
        background="#fff",
        font=("Arial", 12),
        foreground="#212121",
    )
    style.configure("Content.TLabelframe", background="#fff", padding=20)
    return style


def WindowConfigure(window):
    window.title("네이버 자동 서이추 프로그램")
    window.geometry("640x950+100+100")
    window.resizable(False, False)
    window.iconbitmap()
    window.configure(bg="#fff")


"""
----------------- Util ----------------------

"""


def write_csv(file_name, error):
    errorType = type(error).__name__
    errorMessage = str(traceback.format_exc())
    date = datetime.datetime.now()
    with open(file_name, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Date", "Type", "Message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({"Date": date, "Type": errorType, "Message": errorMessage})
    msgbox.showinfo("Error", "에러가 발생했습니다. error_log.csv 파일과 함께 문의 부탁드립니다.")


async def sendNeighborRequest(id, pw, msg, listbox, sum_label):
    try:
        success_count = 0
        fail_count = 0
        listbox.config(state="normal")
        id_list_txt = "id_list.txt"
        if not os.path.exists(id_list_txt):
            msgbox.showinfo("안내", "ID 파일이 없습니다. [검색하기]를 다시 진행해주세요.")
            return

        id_list = []
        with open(id_list_txt, "r") as file:
            for line in file:
                id_value = line.strip()
                id_list.append(id_value)

        if not os.stat(id_list_txt).st_size > 0:
            msgbox.showinfo("안내", "검색된 ID가 없습니다. [검색하기]를 다시 진행해주세요.")
            return

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        options.add_argument(
            f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        )
        global serviceChrome
        driver = webdriver.Chrome(service=serviceChrome)

        url = "https://nid.naver.com/nidlogin.login"
        driver.get(url)

        pyperclip.copy(id)
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="id"]'))
        )
        driver.find_element(By.XPATH, '//*[@id="id"]').send_keys(Keys.CONTROL + "V")
        pyperclip.copy(pw)
        driver.find_element(By.XPATH, '//*[@id="pw"]').send_keys(Keys.CONTROL + "V")

        driver.find_element(By.ID, "log.login").click()

        # 로그인 실패 감지
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#err_common > .error_message")
                )
            )
            msgbox.showinfo("안내", "로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
            return
        except:
            pass

        for id in id_list:
            try:
                blog_url = "https://m.blog.naver.com/BuddyAddForm.naver?blogId=" + id
                driver.get(blog_url)
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dsc"))
                )

                if len(driver.find_elements(By.ID, "_confirmLayerOk")) > 0:
                    exceptional_text = driver.find_element(
                        By.CSS_SELECTOR, ".txt_area > .dsc"
                    ).text

                    if True in [
                        "제한된" in exceptional_text,
                        "하루에" in exceptional_text,
                    ]:
                        msgbox.showinfo("안내", "일일 서이추 신청 횟수가 마감되었습니다.")
                        listbox.insert("end", "일일 서이추 신청 횟수가 마감되었습니다.")
                        return

                    if True in [
                        "이웃수가" in exceptional_text,
                        "초과되어" in exceptional_text,
                    ]:
                        msgbox.showinfo(
                            "안내", "최대 이웃 + 신청이 초과되었습니다. 이웃 + 신청을 정리 부탁드립니다."
                        )
                        listbox.insert("end", "최대 이웃 + 신청이 초과되었습니다")
                        return

                    if True in [
                        "진행중입니다." in exceptional_text,
                        "취소하시겠습니까?" in exceptional_text,
                    ]:
                        fail_count += 1
                        driver.find_element(By.ID, "_confirmLayercancel").click()
                        listbox.insert("end", id + " : 이미 서이추 진행중인 유저입니다.")
                        continue

                else:
                    if not driver.find_element(By.ID, "bothBuddyRadio").is_enabled():
                        fail_count += 1
                        listbox.insert("end", id + " : 서이추 신청이 불가능한 유저입니다.")
                        continue

                    driver.find_element(By.ID, "bothBuddyRadio").click()

                    driver.find_element(By.TAG_NAME, "textarea").clear()
                    driver.find_element(By.TAG_NAME, "textarea").send_keys(msg)

                    driver.find_element(By.CLASS_NAME, "btn_ok").click()
                    success_count += 1
                    listbox.insert("end", id + " : 서로이웃 신청을 했습니다.")
            # 일시정지
            except Exception as e:
                await write_csv("error_log.csv", e)
                return

    except Exception as e:
        await write_csv("error_log.csv", e)
    finally:
        if "driver" in locals():
            driver.quit()
            sum_label.config(
                text="성공 : " + str(success_count) + "\n실패 : " + str(fail_count)
            )
            msgbox.showinfo("안내", str(success_count) + "명에게 신청을 보냈습니다.")
            listbox.config(state="disabled")


async def searchKeyword(keyword, num, orderBy, progress):
    try:
        # 숫자 입력 오류 처리
        if num <= 0 or num > 100:
            msgbox.showinfo("안내", "페이지 수 항목은 1 ~ 99 사이 숫자로 입력해주세요.")
            return

        # 키워드 미입력 처리
        if len(keyword) == 0:
            msgbox.showinfo("안내", "설정된 키워드가 없습니다. 키워드를 설정해주세요.")
            return

        id_url_list = []

        global serviceChrome
        driver = webdriver.Chrome(service=serviceChrome)

        for i in range(1, num + 1):
            web_url = f"https://section.blog.naver.com/Search/Post.naver?pageNo={i}&rangeType=ALL&orderBy={orderBy}&keyword={keyword}"
            driver.get(web_url)

            if i == 1:
                try:
                    WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".none > .title")
                        )
                    )
                    msgbox.showinfo("안내", "키워드로 검색된 인원이 없습니다. 다른 키워드를 입력해주세요.")
                    return
                except:
                    pass

            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "author"))
            )

            id_url = driver.find_elements(By.CLASS_NAME, "author")
            for i in id_url:
                id_url_list.append(i.get_attribute("href"))

        id_list = []
        for i in id_url_list:
            result = i.split("/")
            id_list.append(result[3])

        set_list = set(id_list)
        final_id_list = list(set_list)
        data = pd.DataFrame(final_id_list)
        data.to_csv("id_list.txt", mode="w", header=False, index=False)

        progress.config(text="검색된 인원 : " + str(len(set_list)) + "명")
    except Exception as e:
        write_csv("error_log.csv", e)
    finally:
        if "driver" in locals():
            driver.quit()
            msgbox.showinfo("안내", str(len(set_list)) + "명이 검색되었습니다.")


def validate_input(P):
    if len(P) == 0 or P.isdigit() and (1 <= len(P) <= 2):
        return True
    return False


def initSetting():
    # id_list 초기화
    id_list_txt = "id_list.txt"
    with open(id_list_txt, "w"):
        pass

    # CSV 파일을 읽어서 데이터를 수정한 후, 덮어쓰기
    error_log_csv = "error_log.csv"
    if os.path.exists(error_log_csv):
        max_line = 1000
        with open(error_log_csv, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            all_rows = list(reader)
            rows_to_keep = [header] + all_rows[-max_line:]

        with open(error_log_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows_to_keep)


def getChrome():
    global serviceChrome
    printDivide(serviceChrome, "serviceChrome")
    if serviceChrome is None:
        serviceChrome = ChromeService(ChromeDriverManager().install())
        serviceChrome.creationflags = CREATE_NO_WINDOW


"""
----------------- DEV Util ----------------------

"""


def printDivide(msg, name):
    print(
        "---------- * ---------- * ---------- * ---------- * ---------- "
        + name
        + " ---------- * ---------- * ---------- * ----------"
    )
    print(msg)
    print(
        "---------- * ---------- * ---------- * ---------- * ---------- * ---------- * ---------- * ---------- * ----------"
    )


def write_testcode(file_name, index):
    with open(file_name, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["index"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({"index": index})


def main():
    try:
        # 프로그램 시작 시간 기록
        start_time = time.time()

        window = tk.Tk()
        style = ttk.Style()
        TTkStyleConfigure(style)
        WindowConfigure(window)

        orderBy_var = tk.StringVar(value="sim")
        keyword_entry = tk.StringVar(window)
        page_number_entry = tk.StringVar(value="10")
        id_entry = tk.StringVar(value="")
        pw_entry = tk.StringVar(value="")

        # Id 리스트 뽑기 UI
        keyword_frame = ttk.LabelFrame(
            window,
            style="Content.TLabelframe",
            labelwidget=ttk.Label(
                text=f"ID 리스트 만들기",
                style="LabelFrame.TLabel",
            ),
        )

        frame_orderBy = ttk.Frame(keyword_frame, style="InputLabel.TFrame")
        ttk.Label(frame_orderBy, text="정렬순서", style="InputLabel.TLabel").pack(
            side="left"
        )
        ttk.Radiobutton(
            frame_orderBy,
            text="정확도순",
            width=15,
            style="Radiobutton.TRadiobutton",
            variable=orderBy_var,
            value="sim",
        ).pack(side="left")
        ttk.Radiobutton(
            frame_orderBy,
            text="최신순",
            width=15,
            style="Radiobutton.TRadiobutton",
            variable=orderBy_var,
            value="recentdate",
        ).pack(side="left")
        frame_orderBy.pack(fill="x")

        frame_keyword = ttk.Frame(keyword_frame, style="InputLabel.TFrame")
        ttk.Label(frame_keyword, text="키워드", style="InputLabel.TLabel").pack(
            side="left"
        )
        ttk.Entry(
            frame_keyword,
            width=25,
            style="InputLabel.TEntry",
            textvariable=keyword_entry,
        ).pack(side="left")
        frame_keyword.pack(fill="x", pady=(20, 0))

        frame_page_number = ttk.Frame(keyword_frame, style="InputLabel.TFrame")
        ttk.Label(frame_page_number, text="페이지 수", style="InputLabel.TLabel").pack(
            side="left"
        )
        ttk.Entry(
            frame_page_number,
            width=5,
            style="InputLabel.TEntry",
            textvariable=page_number_entry,
            validate="key",
            validatecommand=(window.register(validate_input), "%P"),
        ).pack(side="left")
        frame_page_number.pack(fill="x", pady=(20, 0))

        action_frame = ttk.Frame(keyword_frame, style="InputLabel.TFrame")
        get_id_progress = ttk.Label(
            action_frame, style="InputLabel.TLabel", text="검색된 ID : 0명", width=50
        )
        get_id_progress.pack(side="left", pady=(20, 0))
        ttk.Button(
            action_frame,
            text="검색하기",
            command=lambda: asyncio.run(
                searchKeyword(
                    keyword_entry.get(),
                    int(page_number_entry.get()),
                    orderBy_var.get(),
                    get_id_progress,
                )
            ),
        ).pack(side="right", pady=(20, 0))
        action_frame.pack(fill="x", pady=(20, 0))

        keyword_frame.pack(fill="x", padx=20, pady=20)

        # 서이추 UI
        request_frame = ttk.LabelFrame(
            window,
            style="Content.TLabelframe",
            labelwidget=ttk.Label(
                text=f"서이추하기",
                style="LabelFrame.TLabel",
            ),
        )

        id_frame = ttk.Frame(request_frame, style="InputLabel.TFrame")
        ttk.Label(id_frame, text="아이디", style="InputLabel.TLabel").pack(side="left")
        ttk.Entry(
            id_frame, width=50, style="InputLabel.TEntry", textvariable=id_entry
        ).pack(side="left")
        id_frame.pack(fill="x")

        password_frame = ttk.Frame(request_frame, style="InputLabel.TFrame")
        ttk.Label(password_frame, text="비밀번호", style="InputLabel.TLabel").pack(
            side="left"
        )
        ttk.Entry(
            password_frame, width=50, style="InputLabel.TEntry", textvariable=pw_entry
        ).pack(side="left")
        password_frame.pack(fill="x", pady=(20, 0))

        message_frame = ttk.Frame(request_frame, style="InputLabel.TFrame")
        ttk.Label(
            message_frame, text="서이추 요청 메시지", wraplength=50, style="InputLabel.TLabel"
        ).pack(side="left")
        message_frame.pack(fill="x", pady=(20, 0))

        message = scrolledtext.ScrolledText(
            message_frame, width=50, height=8, font=("Arial", 12)
        )
        message.pack(side="left")

        btn_frame = ttk.Frame(request_frame, style="InputLabel.TFrame")
        ttk.Button(
            btn_frame,
            text="서이추 신청하기",
            command=lambda: asyncio.run(
                sendNeighborRequest(
                    id_entry.get(),
                    pw_entry.get(),
                    message.get("1.0", "end-1c"),
                    listbox,
                    sum_label,
                )
            ),
        ).pack(side="right", pady=(20, 0))
        sum_label = ttk.Label(btn_frame, style="InputLabel.TLabel", text="", width=50)
        sum_label.pack(side="left", pady=(20, 0))

        btn_frame.pack(fill="x", pady=(20, 0))
        list_frame = ttk.Frame(request_frame, style="InputLabel.TFrame", height=100)
        listbox = tk.Listbox(list_frame, selectmode="single")
        listbox.config(state="disabled", width=77)
        listbox.pack(side="left")

        scrollbar = Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="left", fill="y")

        listbox.config(yscrollcommand=scrollbar.set)

        list_frame.pack(fill="x", pady=(20, 0))

        request_frame.pack(fill="x", padx=20, pady=20)

        frame_info = ttk.LabelFrame(
            window,
            style="Content.TLabelframe",
            labelwidget=ttk.Label(
                style="LabelFrame.TLabel",
            ),
        )

        # frame_info_name = ttk.Frame(frame_info, style="InputLabel.TFrame")

        # ttk.Label(
        #     frame_info_name,
        #     text="개발 및 판매처 : 뿅마켙",
        #     style="FullLabel.TLabel",
        # ).pack(side="left")

        # frame_info_name.pack(fill="x")

        # frame_info_inquiry = ttk.Frame(frame_info, style="InputLabel.TFrame")

        # ttk.Label(
        #     frame_info_inquiry,
        #     text="프로그램 관련 문의 : be_trillionaire@naver.com",
        #     style="FullLabel.TLabel",
        # ).pack(side="left")

        # frame_info_inquiry.pack(fill="x", pady=(20, 0))

        # frame_info_kakaoNickname = ttk.Frame(frame_info, style="InputLabel.TFrame")

        # ttk.Label(
        #     frame_info_kakaoNickname,
        #     text="카카오톡 채널 @bbiyongmarket",
        #     style="FullLabel.TLabel",
        # ).pack(side="left")

        # frame_info_kakaoNickname.pack(fill="x", pady=(20, 0))

        # frame_info_kakaoId = ttk.Frame(frame_info, style="InputLabel.TFrame")

        # ttk.Label(
        #     frame_info_kakaoId,
        #     text="http://pf.kakao.com/_xjBXAG",
        #     style="FullLabel.TLabel",
        # ).pack(side="left")

        text = tk.Text(window, borderwidth=0)

        text.insert(INSERT, "개발 및 판매처 : 뿅마켙\n")
        text.insert(INSERT, "프로그램 관련 문의 : be_trillionaire@naver.com\n")
        text.insert(INSERT, "카카오톡 채널 @bbiyongmarket\n")
        text.insert(INSERT, "http://pf.kakao.com/_xjBXAG")
        text.insert(END, "")

        text.configure(state="disabled")

        text.pack()

        # frame_info_kakaoId.pack(fill="x", pady=(20, 0))

        frame_info.pack(fill="x", padx=20, pady=20)

        window.after(100, getChrome)
        window.after(100, initSetting)

        # 프로그램 종료 시간 기록
        end_time = time.time()

        # 실행 시간 계산
        execution_time = end_time - start_time

        print(f"프로그램 실행 시간: {execution_time} 초")

        window.mainloop()

    except Exception as e:
        write_csv("error_log.csv", e)


if __name__ == "__main__":
    main()
