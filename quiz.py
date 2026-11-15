"""
Quiz Master - upgraded version
Features: categories, 15-second timer, score, restart button,
          SQLite database, and a leaderboard (high scorer in each category).
"""

import os
import random
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

# ----------------------------------------------------------------------
# Settings (you can change these)
# ----------------------------------------------------------------------
TIME_PER_QUESTION = 15      # seconds for each question
QUESTIONS_PER_QUIZ = 5      # how many questions in one game

# Colors
BG = "#1b2540"
CARD = "#2a3860"
ACCENT = "#4f8cff"
GOOD = "#2ecc71"
BAD = "#e74c3c"
GOLD = "#f1c40f"
TEXT = "#ffffff"
MUTED = "#aab4cf"

# The database file is saved next to this quiz.py file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_scores.db")

# ----------------------------------------------------------------------
# Questions: each one is (question, correct answer, [3 wrong answers])
# To add a question, copy one line and change the text.
# ----------------------------------------------------------------------
QUESTION_BANK = {
    "Science": [
        ("Which element has the atomic number 26?", "Iron", ["Nickel", "Cobalt", "Copper"]),
        ("Which gas makes up most of Earth's atmosphere?", "Nitrogen", ["Oxygen", "Argon", "Carbon dioxide"]),
        ("What is the approximate speed of light?", "300,000 km/s", ["150,000 km/s", "30,000 km/s", "3,000,000 km/s"]),
        ("Which blood cells mainly fight infections?", "White blood cells", ["Red blood cells", "Platelets", "Hemoglobin"]),
        ("What is the pH of a neutral solution at 25 degrees C?", "7", ["0", "1", "14"]),
        ("Which law says every action has an equal and opposite reaction?", "Newton's third law", ["Newton's first law", "Newton's second law", "Law of gravitation"]),
        ("What is the SI unit of electrical resistance?", "Ohm", ["Volt", "Ampere", "Watt"]),
        ("Which vitamin does the skin make when exposed to sunlight?", "Vitamin D", ["Vitamin A", "Vitamin C", "Vitamin K"]),
        ("Which part of a plant cell is the site of photosynthesis?", "Chloroplast", ["Mitochondrion", "Nucleus", "Ribosome"]),
        ("Which type of chemical bond involves sharing electrons?", "Covalent bond", ["Ionic bond", "Hydrogen bond", "Metallic bond"]),
    ],
    "Geography": [
        ("What is the capital of Australia?", "Canberra", ["Sydney", "Melbourne", "Perth"]),
        ("Which is the deepest lake in the world?", "Lake Baikal", ["Lake Victoria", "Lake Superior", "Caspian Sea"]),
        ("What is the capital of Canada?", "Ottawa", ["Toronto", "Vancouver", "Montreal"]),
        ("Which strait separates Europe from Africa?", "Strait of Gibraltar", ["Bosphorus", "Strait of Hormuz", "Strait of Malacca"]),
        ("Which is the smallest country in the world by area?", "Vatican City", ["Monaco", "San Marino", "Liechtenstein"]),
        ("The Sundarbans mangrove forest is shared by Bangladesh and which country?", "India", ["Myanmar", "Nepal", "Bhutan"]),
        ("Which is the longest mountain range on land?", "Andes", ["Himalayas", "Rockies", "Alps"]),
        ("What is the capital of Turkey?", "Ankara", ["Istanbul", "Izmir", "Bursa"]),
        ("The Great Barrier Reef lies off the coast of which country?", "Australia", ["Indonesia", "Philippines", "Brazil"]),
        ("Which is the largest island in the world?", "Greenland", ["Madagascar", "Borneo", "New Guinea"]),
    ],
    "General Knowledge": [
        ("In which year did Bangladesh gain independence?", "1971", ["1947", "1952", "1975"]),
        ("Who was the first person to walk on the Moon?", "Neil Armstrong", ["Buzz Aldrin", "Yuri Gagarin", "Michael Collins"]),
        ("Who is known as the National Poet of Bangladesh?", "Kazi Nazrul Islam", ["Rabindranath Tagore", "Jibanananda Das", "Sukanta Bhattacharya"]),
        ("Who wrote the novel 'Pather Panchali'?", "Bibhutibhushan Bandyopadhyay", ["Sarat Chandra Chattopadhyay", "Bankim Chandra Chattopadhyay", "Humayun Ahmed"]),
        ("Which is the largest organ of the human body?", "Skin", ["Liver", "Lungs", "Heart"]),
        ("In which year did World War II end?", "1945", ["1939", "1944", "1950"]),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["Michelangelo", "Pablo Picasso", "Vincent van Gogh"]),
        ("Which language has the most native speakers in the world?", "Mandarin Chinese", ["English", "Spanish", "Hindi"]),
        ("The ancient Olympic Games were first held in which country?", "Greece", ["Italy", "Egypt", "Turkey"]),
        ("International Mother Language Day is observed on which date?", "21 February", ["26 March", "16 December", "14 April"]),
    ],
    "Computer & Python": [
        ("What does print(type(5 / 2)) show in Python 3?", "<class 'float'>", ["<class 'int'>", "<class 'str'>", "<class 'double'>"]),
        ("What is len([1, 2, [3, 4]]) in Python?", "3", ["4", "2", "5"]),
        ("Which of these Python data types is immutable?", "tuple", ["list", "dictionary", "set"]),
        ("What does HTML stand for?", "HyperText Markup Language", ["HighText Machine Language", "Hyperlink Text Mode Language", "Home Tool Markup Language"]),
        ("What is 7 // 2 in Python?", "3", ["3.5", "4", "2"]),
        ("Which Python block runs only when an error occurs?", "except", ["finally", "else", "continue"]),
        ("What does SQL stand for?", "Structured Query Language", ["Simple Question Language", "Sequential Query Logic", "Standard Query Link"]),
        ("What is the decimal number 5 in binary?", "101", ["110", "111", "100"]),
        ("Which of these is NOT a programming language?", "HTTP", ["Rust", "Swift", "Go"]),
        ("What is the result of 'Hi' * 3 in Python?", "HiHiHi", ["Hi3", "Hi Hi Hi", "Error"]),
    ],
}


# ----------------------------------------------------------------------
# Database functions (SQLite)
# ----------------------------------------------------------------------
def init_db():
    """Create the scores table if it does not exist yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS scores (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               category TEXT NOT NULL,
               score INTEGER NOT NULL,
               total INTEGER NOT NULL,
               played_on TEXT NOT NULL
           )"""
    )
    conn.commit()
    conn.close()


def save_score(name, category, score, total):
    """Save one finished game."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scores (name, category, score, total, played_on) VALUES (?, ?, ?, ?, ?)",
        (name, category, score, total, datetime.now().strftime("%d %b %Y")),
    )
    conn.commit()
    conn.close()


def get_top(category, limit=5):
    """Return the best scores of one category (best first)."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT name, score, total, played_on FROM scores "
        "WHERE category = ? ORDER BY score DESC, id ASC LIMIT ?",
        (category, limit),
    ).fetchall()
    conn.close()
    return rows


def get_rank(category, score):
    """Rank of a score inside its category (1 = best)."""
    conn = sqlite3.connect(DB_PATH)
    better = conn.execute(
        "SELECT COUNT(*) FROM scores WHERE category = ? AND score > ?",
        (category, score),
    ).fetchone()[0]
    conn.close()
    return better + 1


# ----------------------------------------------------------------------
# The app
# ----------------------------------------------------------------------
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Master")
        self.root.geometry("640x680")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.player_name = tk.StringVar()
        self.timer_id = None
        self.category = None
        self.show_start()

    # ---------- small helpers ----------
    def clear(self):
        """Remove everything from the window (and stop the timer)."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def label(self, parent, text, size=12, color=TEXT, bold=False, **kwargs):
        font = ("Segoe UI", size, "bold" if bold else "normal")
        return tk.Label(parent, text=text, font=font, fg=color, bg=kwargs.pop("bg", BG), **kwargs)

    def button(self, parent, text, command, color=ACCENT, width=22, size=12):
        return tk.Button(
            parent, text=text, command=command, font=("Segoe UI", size, "bold"),
            bg=color, fg=TEXT, activebackground=color, activeforeground=TEXT,
            disabledforeground=TEXT, relief="flat", width=width, pady=6, cursor="hand2",
        )

    # ---------- screen 1: start ----------
    def show_start(self):
        self.clear()
        self.label(self.root, "Quiz Master", 28, ACCENT, True).pack(pady=(25, 5))
        self.label(self.root, "Test your knowledge and beat the high score!", 11, MUTED).pack()

        self.label(self.root, "Your name:", 12, TEXT, True).pack(pady=(20, 5))
        entry = tk.Entry(self.root, textvariable=self.player_name, font=("Segoe UI", 13),
                         justify="center", width=24, relief="flat")
        entry.pack(ipady=5)

        self.label(self.root, "Choose a category", 13, TEXT, True).pack(pady=(20, 8))

        for category in QUESTION_BANK:
            row = tk.Frame(self.root, bg=CARD, padx=10, pady=8)
            row.pack(pady=4, padx=40, fill="x")
            self.button(row, category, lambda c=category: self.start_quiz(c), width=20).pack(side="left")

            top = get_top(category, 1)
            if top:
                champ = "Top: %s (%d/%d)" % (top[0][0], top[0][1], top[0][2])
            else:
                champ = "No score yet"
            self.label(row, champ, 10, GOLD if top else MUTED, bg=CARD).pack(side="right", padx=5)

        self.button(self.root, "View Leaderboard", lambda: self.show_leaderboard(None),
                    color="#8e44ad", width=24).pack(pady=(18, 5))

    # ---------- start a game ----------
    def start_quiz(self, category):
        if not self.player_name.get().strip():
            messagebox.showwarning("Name needed", "Please type your name first.")
            return
        self.category = category
        self.quiz = random.sample(QUESTION_BANK[category], QUESTIONS_PER_QUIZ)
        self.index = 0
        self.score = 0
        self.show_question()

    # ---------- screen 2: question ----------
    def show_question(self):
        self.clear()
        question, answer, wrong = self.quiz[self.index]
        self.current_answer = answer
        self.options = wrong + [answer]
        random.shuffle(self.options)
        self.answered = False

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=30, pady=(20, 0))
        self.label(top, "%s" % self.category, 12, MUTED).pack(side="left")
        self.label(top, "Score: %d" % self.score, 12, GOLD, True).pack(side="right")

        self.label(self.root, "Question %d of %d" % (self.index + 1, len(self.quiz)),
                   13, TEXT, True).pack(pady=(15, 0))

        self.timer_label = self.label(self.root, "", 20, TEXT, True)
        self.timer_label.pack(pady=5)

        card = tk.Frame(self.root, bg=CARD, padx=15, pady=20)
        card.pack(padx=30, pady=10, fill="x")
        self.label(card, question, 16, TEXT, True, bg=CARD, wraplength=520, justify="center").pack()

        self.buttons = []
        for i, option in enumerate(self.options):
            b = self.button(self.root, option, lambda i=i: self.check_answer(i), width=34)
            b.pack(pady=5)
            self.buttons.append(b)

        self.feedback = self.label(self.root, "", 14, TEXT, True)
        self.feedback.pack(pady=10)

        last = self.index == len(self.quiz) - 1
        self.next_button = self.button(self.root, "Finish" if last else "Next",
                                       self.next_question, color=GOOD, width=14)
        self.next_button.pack(pady=5)
        self.next_button.config(state="disabled")

        self.time_left = TIME_PER_QUESTION
        self.tick()

    # ---------- timer ----------
    def tick(self):
        color = BAD if self.time_left <= 5 else TEXT
        self.timer_label.config(text="Time: %ds" % self.time_left, fg=color)
        if self.time_left <= 0:
            self.check_answer(None)          # time is over
            return
        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.tick)

    # ---------- check the answer ----------
    def check_answer(self, chosen_index):
        if self.answered:
            return
        self.answered = True
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        if chosen_index is None:
            self.feedback.config(text="Time's up! Answer: " + self.current_answer, fg=BAD)
        elif self.options[chosen_index] == self.current_answer:
            self.score += 1
            self.feedback.config(text="Correct!", fg=GOOD)
        else:
            self.feedback.config(text="Wrong! Answer: " + self.current_answer, fg=BAD)

        # Color the buttons: right answer green, chosen wrong answer red
        for i, b in enumerate(self.buttons):
            b.config(state="disabled", cursor="arrow")
            if self.options[i] == self.current_answer:
                b.config(bg=GOOD)
            elif i == chosen_index:
                b.config(bg=BAD)
        self.next_button.config(state="normal")

    def next_question(self):
        self.index += 1
        if self.index < len(self.quiz):
            self.show_question()
        else:
            self.show_result()

    # ---------- screen 3: result ----------
    def show_result(self):
        self.clear()
        name = self.player_name.get().strip()
        total = len(self.quiz)
        save_score(name, self.category, self.score, total)
        rank = get_rank(self.category, self.score)

        self.label(self.root, "Quiz Finished!", 26, ACCENT, True).pack(pady=(40, 10))
        self.label(self.root, "Well played, %s!" % name, 14, TEXT).pack()
        self.label(self.root, "%d / %d" % (self.score, total), 48, GOLD, True).pack(pady=15)

        if self.score == total:
            msg = "Perfect score!"
        elif self.score >= total * 0.6:
            msg = "Great job!"
        else:
            msg = "Keep practicing!"
        self.label(self.root, msg, 16, TEXT, True).pack()

        self.label(self.root, "Your rank in %s: #%d" % (self.category, rank), 13, MUTED).pack(pady=10)

        self.button(self.root, "Play Again", lambda: self.start_quiz(self.category),
                    color=GOOD, width=24).pack(pady=(25, 6))
        self.button(self.root, "View Leaderboard", lambda: self.show_leaderboard(self.category),
                    color="#8e44ad", width=24).pack(pady=6)
        self.button(self.root, "Main Menu", self.show_start, width=24).pack(pady=6)

    # ---------- screen 4: leaderboard ----------
    def show_leaderboard(self, selected):
        self.clear()
        if selected is None:
            selected = list(QUESTION_BANK)[0]

        self.label(self.root, "Leaderboard", 26, GOLD, True).pack(pady=(20, 5))
        self.label(self.root, "Top 5 players in each category", 11, MUTED).pack()

        tabs = tk.Frame(self.root, bg=BG)
        tabs.pack(pady=12)
        for category in QUESTION_BANK:
            color = ACCENT if category == selected else CARD
            self.button(tabs, category, lambda c=category: self.show_leaderboard(c),
                        color=color, width=15, size=9).pack(side="left", padx=3)

        table = tk.Frame(self.root, bg=CARD, padx=15, pady=15)
        table.pack(padx=30, pady=10, fill="x")

        header = tk.Frame(table, bg=CARD)
        header.pack(fill="x")
        for text, w in (("Rank", 6), ("Player", 18), ("Score", 8), ("Date", 13)):
            self.label(header, text, 11, MUTED, True, bg=CARD, width=w, anchor="w").pack(side="left")

        rows = get_top(selected, 5)
        if not rows:
            self.label(table, "No scores yet. Be the first!", 12, MUTED, bg=CARD).pack(pady=30)
        for position, (name, score, total, date) in enumerate(rows, start=1):
            color = GOLD if position == 1 else TEXT
            line = tk.Frame(table, bg=CARD)
            line.pack(fill="x", pady=4)
            for text, w in (("#%d" % position, 6), (name, 18),
                            ("%d/%d" % (score, total), 8), (date, 13)):
                self.label(line, text, 12, color, position == 1, bg=CARD, width=w, anchor="w").pack(side="left")

        self.button(self.root, "Back to Menu", self.show_start, width=20).pack(pady=20)


# ----------------------------------------------------------------------
# Start the program
# ----------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    window = tk.Tk()
    QuizApp(window)
    window.mainloop()
