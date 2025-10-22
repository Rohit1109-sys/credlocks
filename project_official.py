import os
import cv2
import hashlib
import random
import string
import requests
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
from customtkinter import CTkImage
from zxcvbn import zxcvbn

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
VIDEO_PATH = os.path.join(VIDEOS_DIR, "creadlocklogo.mp4")

# ---------------- Utility Functions ----------------
def resource_path(*paths):
    return os.path.join(BASE_DIR, *paths)

def check_hibp(password):
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1pass[:5], sha1pass[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return -1
        for line in resp.text.splitlines():
            h, count = line.split(":")
            if h == suffix:
                return int(count)
        return 0
    except:
        return -2

def check_password_strength(password):
    if not password:
        return 0, "Password is empty"
    score = zxcvbn(password)['score']
    suggestions = ["Very Weak","Weak","Fair","Good","Strong"]
    return score, suggestions[min(score, 4)]

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation)
    ]
    password += [random.choice(chars) for _ in range(length - len(password))]
    random.shuffle(password)
    return "".join(password)

def create_gradient(width, height, start_color, end_color):
    gradient = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(gradient)
    for i in range(height):
        ratio = i / height
        r = int(start_color[0]*(1-ratio)+end_color[0]*ratio)
        g = int(start_color[1]*(1-ratio)+end_color[1]*ratio)
        b = int(start_color[2]*(1-ratio)+end_color[2]*ratio)
        draw.line([(0,i),(width,i)], fill=(r,g,b))
    return gradient

# ---------------- Splash Video ----------------
def play_splash(video_path):
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    delay = int(1000 / fps)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Splash Screen", frame)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# ---------------- Main App ----------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.screens = {}
        self.data = {"wifi": [], "passkeys": [], "codes": []}
        self.deleted = {"usernames": [], "codes": []}
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.after(100, self.start_splash)

    def start_splash(self):
        play_splash(VIDEO_PATH)
        self.deiconify()
        self.show_login()

    # ---------------- Login ----------------
    def show_login(self):
        login_win = ctk.CTkToplevel(self)
        login_win.title("Login")
        login_win.geometry("600x400")
        login_win.configure(fg_color="white")
        login_win.grab_set()
        ctk.CTkLabel(login_win, text="Enter Master Password", font=("Arial", 18)).pack(pady=20)
        password_entry = ctk.CTkEntry(login_win, width=200, show="*")
        password_entry.pack(pady=10)

        def check_password():
            if password_entry.get() == "A1@bcdef":
                login_win.destroy()
                self.open_main_screen()
            else:
                messagebox.showerror("Error", "Incorrect Password")

        ctk.CTkButton(login_win, text="Login", command=check_password).pack(pady=10)

    # ---------------- Main Screen ----------------
    def open_main_screen(self):
        window = ctk.CTkToplevel(self)
        try:
            window.state("zoomed")
        except:
            window.attributes("-fullscreen", True)
        window.title("Credlock - Main")
        window.configure(fg_color="white")
        self.screens["main"] = window

        # Gradient Bar
        width, height = window.winfo_screenwidth(), 120
        gradient_img = create_gradient(width, height, (0,90,200),(0,150,255))
        gradient_ctk = ctk.CTkImage(light_image=gradient_img, size=(width,height))
        top_bar = ctk.CTkLabel(window, image=gradient_ctk, text="")
        top_bar.image = gradient_ctk
        top_bar.pack(fill="x", side="top")

        # Buttons Frame
        btn_frame = ctk.CTkFrame(window, fg_color="white")
        btn_frame.pack(pady=50)
        for i, name in enumerate(["Passkeys","Wifi","Codes","Deleted"]):
            ctk.CTkButton(btn_frame, text=name, width=200, height=80).grid(row=0, column=i, padx=20)

    def close_app(self):
        for win in self.screens.values():
            win.destroy()
        self.destroy()

if __name__ == "__main__":
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    app = App()
    app.mainloop()
