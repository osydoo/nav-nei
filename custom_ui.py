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
        "Input.TEntry",
        padding=10,
        background="#fff",
        foreground="#212121",
        bordercolor="#FF5733",
        font=("Arial", 12),
    )
    style.configure("InputLabel.TFrame", background="#fff")
    style.configure("Content.TLabelframe", background="#fff", padding=20)
    return style


def WindowConfigure(window):
    window.title("네이버 자동 서이추 프로그램")
    window.geometry("640x800+100+100")
    window.resizable(False, False)
    window.iconbitmap()
    window.configure(bg="#fff")
