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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def resource_path(*paths):
    return os.path.join(BASE_DIR, *paths)

# --------------------- HIBP Checker ---------------------
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
            return -1
    except requests.exceptions.RequestException:
        return -2

# --------------------- Password Strength ---------------------
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

# --------------------- Password Generator ---------------------
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
    capture = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)  # Use FFmpeg backend
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

    # ---------------- Screen Management ----------------
    def close_app(self):
        for win in self.screens.values():
            win.destroy()
        self.destroy()

# --------------------- Run ---------------------
if __name__ == "__main__":
    # Make sure videos/images folder exists
    play_video()  # splash video
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.close_app)
    # login_window(app)  # Uncomment after adding login window
    # app.mainloop()
