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


def write_testcode(file_name, index):
    with open(file_name, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["index"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({"index": index})


async def sendNeighborRequest(id, pw, msg, listbox, sum_label, service):
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

        driver = webdriver.Chrome(service=service)

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
                WebDriverWait(driver, 2).until(
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
                write_csv("error_log.csv", e)
                return

    except Exception as e:
        write_csv("error_log.csv", e)
    finally:
        if "driver" in locals():
            driver.quit()
            sum_label.config(
                text="성공 : " + str(success_count) + "\n실패 : " + str(fail_count)
            )
            msgbox.showinfo("안내", str(success_count) + "명에게 신청을 보냈습니다.")
            listbox.config(state="disabled")


async def searchKeyword(keyword, num, progress, service):
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

        driver = webdriver.Chrome(service=service)

        for i in range(1, num + 1):
            web_url = f"https://section.blog.naver.com/Search/Post.naver?pageNo={i}&rangeType=ALL&orderBy=sim&keyword={keyword}"
            driver.get(web_url)

            if i == 1:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".none > .title")
                        )
                    )
                    msgbox.showinfo("안내", "키워드로 검색된 인원이 없습니다. 다른 키워드를 입력해주세요.")
                    return
                except:
                    pass

            WebDriverWait(driver, 2).until(
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


async def initSetting():
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
