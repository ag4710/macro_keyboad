import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json
import os
import sys
import webbrowser
from PIL import Image, ImageTk

settings_file = 'settings.json'
main_label = None  # 전역 변수로 main_label 설정
default_main_image = "main.png"  # 기본 메인 이미지 사진

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 설정 파일에서 경로 불러옴
def load_settings():
    if os.path.exists(resource_path(settings_file)):
        with open(resource_path(settings_file), 'r') as f:
            return json.load(f)
    return {}

# 설정 파일에 경로 저장
def save_settings(settings):
    with open(resource_path(settings_file), 'w') as f:
        json.dump(settings, f)

settings = load_settings()

# 메인 이미지 변경 함수
def change_main_image():
    file_path = filedialog.askopenfilename(title="Select a new main image:", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_path:
        settings["main_image"] = file_path
        save_settings(settings)

# 파일 또는 URL 열기 함수
def open_file_dialog(macro_key):
    dialog_window = tk.Toplevel(root)
    dialog_window.title("Select Type")

    # 파일 또는 URL 선택 함수
    def handle_choice():
        choice = var.get()
        if choice == 'file':
            file_path = filedialog.askopenfilename(title=f"Select a file for {macro_key}:", initialdir=settings.get(macro_key, ""))
            if file_path:
                settings[macro_key] = file_path
                save_settings(settings)
                switch_to_macro_keyboard()
        elif choice == 'url':
            url = simpledialog.askstring("Enter URL", "Enter the URL for the macro:")
            if url:
                settings[macro_key] = url
                save_settings(settings)
                switch_to_macro_keyboard()
        dialog_window.destroy()

    var = tk.StringVar(value='file')

    tk.Radiobutton(dialog_window, text="File", variable=var, value='file').pack(anchor='w')
    tk.Radiobutton(dialog_window, text="URL", variable=var, value='url').pack(anchor='w')
    
    confirm_button = tk.Button(dialog_window, text="Confirm", command=handle_choice)
    confirm_button.pack(pady=10)

# 파일 또는 URL 실행 함수
def run_file(macro_key):
    path_or_url = settings.get(macro_key)
    if path_or_url:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            try:
                webbrowser.open(path_or_url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {path_or_url}\n{e}")
        else:
            try:
                os.startfile(path_or_url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {path_or_url}\n{e}")

# 설정 창 열기
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    # 화면 중앙에 설정 창 위치
    window_width = settings_window.winfo_reqwidth()
    window_height = settings_window.winfo_reqheight()
    position_right = int(settings_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(settings_window.winfo_screenheight() / 2 - window_height / 2)
    settings_window.geometry("+{}+{}".format(position_right, position_down))

    # 추가 버튼
    add_button = tk.Button(settings_window, text="Add Macro", command=add_macro)
    add_button.pack(pady=10)

    # 삭제 버튼
    delete_button = tk.Button(settings_window, text="Delete Macro", command=delete_macro)
    delete_button.pack(pady=5)

    # 메인 이미지 사진 변경 버튼
    main_image_button = tk.Button(settings_window, text="Change main Image", command=change_main_image)
    main_image_button.pack(pady=5)

# 매크로 추가 함수
def add_macro():
    macro_key = simpledialog.askstring("Add Macro", "Enter macro key:")
    if macro_key:
        open_file_dialog(macro_key)

# 매크로 삭제 함수
def delete_macro():
    macro_key = simpledialog.askstring("Delete Macro", "Enter macro key to delete:")
    if macro_key in settings:
        del settings[macro_key]
        save_settings(settings)
        switch_to_macro_keyboard()

# 매크로 키보드 화면으로 전환
def switch_to_macro_keyboard():
    for widget in root.winfo_children():
        widget.destroy()

    # 설정 버튼 생성
    settings_btn = tk.Button(root, text="Settings", command=open_settings)
    settings_btn.pack(pady=10)

    # 매크로 버튼 생성
    for macro_key in settings:
        if macro_key != "main_image":
            btn = tk.Button(root, text=macro_key, command=lambda key=macro_key: run_file(key))
            btn.pack(pady=10)

    # Exit 버튼 생성
    exit_btn = tk.Button(root, text="Exit", command=switch_to_image_only_screen)
    exit_btn.pack(pady=10)

# 메인 이미지만 표시하는 화면으로 전환
def switch_to_image_only_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # 메인 이미지 화면으로 전환
    switch_to_main_screen()

# 메인 이미지 화면으로 전환
def switch_to_main_screen():
    global main_label  # 전역 변수 선언
    if main_label:
        main_label.destroy()

    # 메인 이미지 이미지 로드 및 표시
    main_image_path = settings.get("main_image", resource_path(default_main_image))
    main_image = Image.open(main_image_path)
    main_photo = ImageTk.PhotoImage(main_image)
    main_label = tk.Label(root, image=main_photo)
    main_label.image = main_photo  # 참조를 유지하여 이미지가 표시되게 함
    main_label.pack(expand=True)

    # 메인 이미지 클릭 이벤트 설정
    if main_image_path != resource_path(default_main_image):
        main_label.bind("<Button-1>", lambda e: switch_to_macro_keyboard())

    # 항상 위에 유지
    root.attributes('-topmost', True)

# 초기 창 설정
root = tk.Tk()
root.title("Macro Keyboard")
root.iconbitmap('keyboard.ico')

# 메인 이미지 화면으로 전환
switch_to_main_screen()

# Tkinter 이벤트 루프 시작
root.mainloop()
