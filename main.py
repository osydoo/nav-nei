import tkinter as tk
from tkinter import Scrollbar, ttk
from tkinter import scrolledtext
import asyncio

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
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
from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows

from custom_ui import TTkStyleConfigure, WindowConfigure
from util import (
    initSetting,
    searchKeyword,
    sendNeighborRequest,
    validate_input,
    write_csv,
)


def main():
    try:
        window = tk.Tk()
        style = ttk.Style()
        TTkStyleConfigure(style)
        WindowConfigure(window)
        asyncio.run(initSetting())

        service = ChromeService(ChromeDriverManager().install())
        service.creationflags = CREATE_NO_WINDOW

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

        frame_keyword = ttk.Frame(keyword_frame, style="InputLabel.TFrame")
        ttk.Label(frame_keyword, text="키워드", style="InputLabel.TLabel").pack(
            side="left"
        )
        keyword_text = ttk.Entry(
            frame_keyword,
            width=25,
            style="InputLabel.TEntry",
            textvariable=keyword_entry,
        )
        keyword_text.pack(side="left")
        frame_keyword.pack(fill="x")

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
                    get_id_progress,
                    service,
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
                    service,
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

        window.mainloop()

    except Exception as e:
        write_csv("error_log.csv", e)


if __name__ == "__main__":
    main()
