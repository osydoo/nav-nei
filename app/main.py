# Generated by Selenium IDE
import time
import json
import pyperclip
import random
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



with open("../login_info.json", "r") as json_file:
    st_python = json.load(json_file)


NAVER_ID = st_python.get("naver_id")
NAVER_PWD = st_python.get("naver_pwd")
buddy_add_comment = "안녕하세요. 공감글 타고 들어와 서이추 드립니다. 자주 소통하는 이웃이 되었으면 좋겠어요. 그럼 오늘도 행복한 하루 보내세요~"

def random_sleep_time():
    time.sleep(random.uniform(0.5, 1))
    

class NaverBlogAutoAddBuddy():
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
    
    def teardown_method(self):
        self.driver.quit()
    
    def wait_next_window(self):
        print("start wait")
        WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".link_slogan")))
        print("start done")
        
        
    def get_blog_post_list(self):
        print("start_blog_post_list")
        self.driver.find_element(By.LINK_TEXT, "주제별 보기").click()
        random_sleep_time()
        
        
        blog_len = len(self.driver.find_elements(By.CSS_SELECTOR, ".desc_inner"))
        for blog_i in range(blog_len):
            try:
                blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".desc_inner")
                blog = blog_list[blog_i]
                print(blog)
                blog.click()
                blog_title = blog.text
                print(f"start blog ||| {blog_title}")
                random_sleep_time()
                
                tabs = self.driver.window_handles
                tag_id_blog_post = tabs[-1]
                self.driver.switch_to.window(tag_id_blog_post)
                
                # 블로그 내 frame이 있어 frame 속으로 접근
                self.driver.switch_to.frame("mainFrame") 
                
                # 공감글 접근, 이것도 frame로 되어있어서 frame를 찾아야됨.
                # self.driver.find_element(By.XPATH, "//a[contains(@class, 'btn_arr')]").click()
                empathy_a_herf = self.driver.find_element(By.XPATH, "//a[contains(@id, 'Sympathy')]")
                empathy_a_herf.click()
                random_sleep_time()
                empathy_iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@id, 'sympathyFrm')]")
                empathy_iframe_id = empathy_iframe.get_attribute("id")
                self.driver.switch_to.frame(empathy_iframe_id)
                    
                
                # 공감한 이웃 모두 받아오기
                buddy_list = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'btn_buddy')]")
                
                
                for buddy_i in range(len(buddy_list)):
                    # 두번재 서이추 할 때 frame 이 벗어나
                    # frame 맞추기 추가
                    if buddy_i >= 1:
                        self.driver.switch_to.frame("mainFrame")
                        empathy_iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@id, 'sympathyFrm')]")
                        empathy_iframe_id = empathy_iframe.get_attribute("id")
                        self.driver.switch_to.frame(empathy_iframe_id)
                    buddy = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'wrap_bloger')]")[buddy_i]
                    buddy_add_buddy_buttom = buddy.find_element(By.XPATH, "//a[contains(@class, 'btn_buddy')]")
                    user_name = buddy.find_element(By.XPATH, "//a[contains(@class, 'pcol2')]")
                    
                    # + 이웃 추가 버튼이 있는 경우에만 클릭
                    if "이웃추가" in buddy_add_buddy_buttom.get_attribute("text"):
                        buddy_add_buddy_buttom.click()
                        random_sleep_time()
                        tag_id_add_buddy = self.driver.window_handles[-1]
                        self.driver.switch_to.window(tag_id_add_buddy)
                        
                        # 서이추 버튼 disable
                        each_buddy_add_button = self.driver.find_element(By.XPATH, "//input[contains(@id, 'each_buddy_add')]")
                        if each_buddy_add_button.get_attribute("disabled"):
                            self.driver.close()
                            
                        else:
                            self.driver.find_element(By.XPATH, "//label[contains(@for, 'each_buddy_add')]").click()
                            random_sleep_time()
                            next_button = self.driver.find_element(By.XPATH, "//a[contains(@class, '_buddyAddNext')]")
                            next_button.click()
                            random_sleep_time()
                            
                            
                            is_alert = False
                            # 서이추 버튼 클릭 후 알림창 대응
                            try:
                                alert_dialog = self.driver.switch_to.alert
                                alert_text = alert_dialog.text # TODO 서이추 그룹 추가여부 확인 필요
                                alert_dialog.accept()
                                is_alert = True
                                
                                # 1일 500명 모두 종료
                                if "더 이상 이웃을 추가할 수 없습니다" in alert_text:
                                    print("1일 500명 모두 완료!!")
                                    self.driver.quit()
                                    exit()
                            except:
                                pass


                            if not is_alert:
                                # 서로이웃 신청 메시지 쓰는 칸 입장
                                textarea = self.driver.find_element(By.XPATH, "//textarea[contains(@id, 'message')]")
                                textarea.click()
                                random_sleep_time()
                                textarea.send_keys(buddy_add_comment)
                                
                                # 다음 
                                textarea_popup_next_button = self.driver.find_element(By.XPATH, "//a[contains(@class, '_addBothBuddy')]")
                                textarea_popup_next_button.click()
                                random_sleep_time()
                                
                                # 최종 닫기 버튼 클릭
                                finsh_close_button = self.driver.find_element(By.XPATH, "//a[contains(@class, 'button_close')]")
                                finsh_close_button.click()
                                random_sleep_time()
                            
                    self.driver.switch_to.window(tag_id_blog_post)
                    random_sleep_time()

                
                # 1개의 블로그 모두 끝
                # 현재 블로그 닫기
                print(f"end blog ||| {blog_title}")
                self.driver.switch_to.window(tag_id_blog_post)
                self.driver.close()
                
                # 블로그 목록 가기
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                print(f"ERROR {blog_title} {user_name}")
                traceback.format_exc()
            
        print(1)


    def login_naver(self):
        self.driver.get("https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0")
        self.driver.set_window_size(1920, 1080)
        self.driver.find_element(By.CSS_SELECTOR, ".login_button").click()
        random_sleep_time()
        
        
        # 3. id 복사 붙여넣기
        elem_id = self.driver.find_element(By.ID, "id")
        random_sleep_time()
        elem_id.click()
        pyperclip.copy(NAVER_ID)
        random_sleep_time()
        elem_id.send_keys(Keys.CONTROL, 'v')
        
        # 4. pw 복사 붙여넣기
        elem_pw = self.driver.find_element(By.ID, "pw")
        random_sleep_time()
        elem_pw.click()
        random_sleep_time()
        pyperclip.copy(NAVER_PWD)
        random_sleep_time()
        elem_pw.send_keys(Keys.CONTROL, 'v')
        random_sleep_time()
        
        # 8 | click | id=log.login | 
        self.driver.find_element(By.ID, "log.login").click()
        

if __name__ == "__main__":
    t = NaverBlogAutoAddBuddy()
    t.setup_method()
    t.login_naver()
    t.wait_next_window()
    t.get_blog_post_list()