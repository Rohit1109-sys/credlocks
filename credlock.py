import os
import cv2
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
from customtkinter import CTkImage
import requests
import hashlib
from zxcvbn import zxcvbn
import random
import string

# --------------------- Helper ---------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory where script is
def resource_path(*paths):
    """Build a full path relative to the script folder."""
    return os.path.join(BASE_DIR, *paths)

# --------------------- HIBP Checker Function ---------------------
def check_hibp(password):
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1pass[:5]
    suffix = sha1pass[5:]
    url = f'https://api.pwnedpasswords.com/range/{prefix}'
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
            return 0
        else:
            print(f"HIBP API error: Status code {response.status_code}")
            return -1
    except requests.exceptions.RequestException as e:
        print(f"HIBP connection error: {e}")
        return -2

# --------------------- Password Strength Checker Function ---------------------
def check_password_strength(password):
    if not password:
        return 0, "Password is empty."
    results = zxcvbn(password)
    score = results['score']
    suggestions = [
        "Very Weak (Only 1 or 2 distinct characters or short length)",
        "Weak (Short, simple, or common patterns)",
        "Fair (Better mix, but could be longer or more complex)",
        "Good (Long, varied characters, not easily guessed)",
        "Strong (Excellent combination of length and complexity)"
    ]
    suggestion = suggestions[min(score, 4)]
    return score, suggestion

# --------------------- Password Generator Function ---------------------
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

# --------------------- Splash Video ---------------------
def play_video(video_path=None):
    if video_path is None:
        video_path = resource_path("videos", "creadlocklogo.mp4")
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print("Error opening video:", video_path)
        return

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30
    delay = int(1000 / fps)

    while capture.isOpened():
        ret, frame = capture.read()
        if ret:
            cv2.imshow("Credlock", frame)
            if cv2.waitKey(delay) & 0xFF == ord("q"):
                break
        else:
            break

    capture.release()
    cv2.destroyAllWindows()

# --------------------- Gradient Creation ---------------------
def create_gradient(width, height, start_color, end_color):
    gradient = Image.new("RGB", (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    for i in range(height):
        ratio = i / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    return gradient

# --------------------- Main App ---------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.overrideredirect(True)
        self.after(0, self.withdraw)
        self.screens = {}
        self.history = []
        self.history_index = -1
        self.data = {"wifi": [], "passkeys": [], "codes": []}
        self.deleted = {"usernames": [], "codes": []}
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # ---------------- Gradient Bar ----------------
    def gradient_bar(self, window, bar_height=120):
        bar_width = window.winfo_screenwidth()
        gradient_img = create_gradient(bar_width, bar_height, (0, 90, 200), (0, 150, 255))
        gradient_ctk = ctk.CTkImage(light_image=gradient_img, size=(bar_width, bar_height))
        top_bar = ctk.CTkLabel(window, image=gradient_ctk, text="")
        top_bar.image = gradient_ctk
        top_bar.pack(fill="x", side="top")

    # ---------------- Main Screen ----------------
    def main_screen(self):
        window = ctk.CTkToplevel(self)
        window.state("zoomed")
        window.configure(fg_color="white")
        window.title("Credlock - Main")
        window.protocol("WM_DELETE_WINDOW", self.close_app)

        # Gradient bar
        self.gradient_bar(window, 120)

        # Credtext image
        try:
            pil_img = Image.open(resource_path("images", "credtext.jpg"))
            img_obj = ctk.CTkImage(light_image=pil_img, size=(300, 100))
            img_label = ctk.CTkLabel(window, image=img_obj, text="")
            img_label.image = img_obj
            img_label.pack(anchor="w", padx=20, pady=(10, 20))
        except Exception as e:
            print("Image not found:", e)

        # The rest of your GUI code remains the same...
        return window

# --------------------- Login Window ---------------------
def login_window(app: ctk.CTk):
    login = ctk.CTkToplevel(app)
    login.state("zoomed")
    login.title("Login")
    login.geometry("1000x500+300+200")
    login.resizable(False, False)
    login.configure(fg_color="white")
    login.grab_set()
    login.focus_force()
    login.lift()

    # Left image
    try:
        original_img = Image.open(resource_path("images", "loginimg.jpg"))
        bg_img = CTkImage(light_image=original_img, size=(500, 500))
        img_label = ctk.CTkLabel(login, image=bg_img, text="")
        img_label.place(x=300, y=200)
    except Exception as e:
        print("Image load error:", e)
        img_label = ctk.CTkLabel(login, text="Image failed to load", font=("Arial", 20))
        img_label.place(x=100, y=200)

# --------------------- Run ---------------------
if __name__ == "__main__":
    play_video()  # splash video
    app = App()
    login_window(app)
    app.mainloop()
