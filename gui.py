import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO


FONT_LARGE = ("Arial", 24)
FONT_MEDIUM = ("Arial", 20)
FONT_SMALL = ("Arial", 18)


class DevilFruitGameGUI:
    def __init__(self, root, backend):
        self.root = root
        self.backend = backend
        self.root.title("One Piece Devil Fruit Ranking Game")
        self.root.geometry("2250x1024")

        self.username = None
        self.current_fruit = None
        self.ranking = [None] * 10

        self.create_widgets()
        self.show_login_screen()

    def create_widgets(self):
        self.header = tk.Label(self.root, text="One Piece Devil Fruit Ranking", font=("Arial", 28, "bold"))
        self.header.pack(pady=10)

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.ranking_frame = tk.Frame(self.root, bd=4, relief="ridge", bg="#f2f2f2")
        self.ranking_labels = []

    def show_login_screen(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.ranking_frame.pack_forget()

        tk.Label(self.content_frame, text="Enter your player name:", font=FONT_LARGE).pack(pady=30)
        self.name_entry = tk.Entry(self.content_frame, font=FONT_LARGE)
        self.name_entry.pack(pady=10)
        tk.Button(self.content_frame, text="Start Game", font=FONT_MEDIUM,
                  command=self.start_game, height=2, width=20).pack(pady=20)

    def start_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter your name.")
            return
        self.username = name
        self.backend.start_new_round(name)
        self.ranking = [None] * 10

        for widget in self.ranking_frame.winfo_children():
            widget.destroy()

        self.ranking_labels.clear()
        self.ranking_frame.pack(side="right", padx=10, pady=10)
        tk.Label(self.ranking_frame, text="Top 10 Ranking", font=("Arial", 24, "bold"), bg="#f2f2f2").pack(pady=10)

        grid_container = tk.Frame(self.ranking_frame, bg="#9c9c9c")
        grid_container.pack(pady=5)
        
        for i in range(10):
            row = i % 5
            col = i // 5  # 0 for left column, 1 for right column
        
            cell = tk.Frame(grid_container, bg="#d3d3d3", bd=2, relief="groove", padx=4, pady=4)
            cell.grid(row=row, column=col, padx=10, pady=5)
        
            rank_row = tk.Frame(cell, bg="#d3d3d3")
            rank_row.pack()

            rank_btn = tk.Button(rank_row, text=f"{i+1}. (Empty)", font=FONT_MEDIUM, width=33, height=3,
                                 command=lambda i=i: self.place_in_rank_from_button(i))
            rank_btn.pack(side="left", padx=4)

            img_label = tk.Label(rank_row, bg="#d3d3d3")  # adjust width/height if needed
            img_label.pack(side="left", padx=4)
            self.ranking_labels.append((rank_btn, img_label))

        self.show_next_fruit()

    def show_next_fruit(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.current_fruit = self.backend.get_random_fruit()

        tk.Label(self.content_frame, text=self.current_fruit['name'], font=FONT_LARGE).pack(pady=(150,10))
        img = self.load_image(self.current_fruit['img_url'])
        if img:
            img_label = tk.Label(self.content_frame, image=img)
            img_label.image = img
            img_label.pack()

        tk.Label(self.content_frame, text=f"User: {self.current_fruit['user']}", font=FONT_MEDIUM).pack(pady=6)
        tk.Label(self.content_frame, text=self.current_fruit['power'], font=FONT_SMALL, wraplength=650,
                 justify="left").pack(pady=10)

        tk.Label(self.content_frame, text="Click a rank on the right to place this fruit.", font=FONT_MEDIUM).pack(pady=20)

    def place_in_rank_from_button(self, index):
        self.ranking[index] = self.current_fruit
        self.update_ranking_display()
        if None not in self.ranking:
            self.show_final_score()
        else:
            self.show_next_fruit()

    def update_ranking_display(self):
        for i, fruit in enumerate(self.ranking):
            btn, img_label = self.ranking_labels[i]
            if fruit:
                btn.config(text=f"{i+1}. {fruit['name']}", state="disabled")
                image = self.load_image(fruit['img_url'], size=(100, 100))
                if image:
                    img_label.config(image=image)
                    img_label.image = image
                else:
                    img_label.config(image="")
            else:
                btn.config(text=f"{i+1}. (Empty)", state="normal")
                img_label.config(image="")

    def show_final_score(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.ranking_frame.pack_forget()  # Hide the rank panel

        tk.Label(self.content_frame, text="Final Results", font=("Arial", 24, "bold")).pack(pady=10)
        result_frame = tk.Frame(self.content_frame)
        result_frame.pack(pady=10)

        tk.Label(result_frame, text="Rank", font=FONT_MEDIUM, width=6).grid(row=0, column=0)
        tk.Label(result_frame, text="Fruit", font=FONT_MEDIUM, width=20).grid(row=0, column=1)
        tk.Label(result_frame, text="Image", font=FONT_MEDIUM, width=10).grid(row=0, column=2)
        tk.Label(result_frame, text="Avg Rank", font=FONT_MEDIUM, width=10).grid(row=0, column=3)

        fruit_scores = self.backend.finish_round(self.ranking)

        for i, (fruit, avg) in enumerate(fruit_scores):
            tk.Label(result_frame, text=f"{i+1}", font=FONT_SMALL).grid(row=i+1, column=0)
            tk.Label(result_frame, text=fruit['name'], font=FONT_SMALL).grid(row=i+1, column=1)
            image = self.load_image(fruit['img_url'], size=(60, 60))
            img_label = tk.Label(result_frame)
            if image:
                img_label.config(image=image)
                img_label.image = image
            img_label.grid(row=i+1, column=2)
            tk.Label(result_frame, text=f"{avg:.2f}", font=FONT_SMALL).grid(row=i+1, column=3)

        tk.Label(self.content_frame, text=f"Your score: {self.backend.last_score}", font=FONT_MEDIUM).pack(pady=10)
        btn_row = tk.Frame(self.content_frame, bg="#d3d3d3")
        btn_row.pack()
        tk.Button(btn_row, text="Play Again", font=FONT_MEDIUM, command=self.show_login_screen).pack(side='left',padx=(0,20))
        tk.Button(btn_row, text="View Scoreboard", font=FONT_MEDIUM, command=self.show_scoreboard).pack(side='left',padx=(20,0))

    def load_image(self, url, size=(100, 100)):
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            image = image.resize(size)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Image load failed: {e}")
            return None
        
    def show_scoreboard(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Top 10 Player Scores", font=("Arial", 26, "bold")).pack(pady=20)

        scores = self.backend.get_top_scores()  # Returns list of (name, score)
        player_score = self.backend.last_score
        player_name = self.username

        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(pady=10)

        # Table headers
        tk.Label(table_frame, text="Rank", font=FONT_MEDIUM, width=6).grid(row=0, column=0)
        tk.Label(table_frame, text="Player", font=FONT_MEDIUM, width=20).grid(row=0, column=1)
        tk.Label(table_frame, text="Score", font=FONT_MEDIUM, width=10).grid(row=0, column=2)

        for i, (name, score) in enumerate(scores):
            tk.Label(table_frame, text=f"{i+1}", font=FONT_SMALL).grid(row=i+1, column=0)
            tk.Label(table_frame, text=name, font=FONT_SMALL).grid(row=i+1, column=1)
            tk.Label(table_frame, text=score, font=FONT_SMALL).grid(row=i+1, column=2)

        # Show the current player's score
        tk.Label(self.content_frame, text=f"Your Score: {player_score} ({player_name})", font=FONT_MEDIUM).pack(pady=20)

        # Buttons to restart or exit
        btns = tk.Frame(self.content_frame)
        btns.pack(pady=10)

        tk.Button(btns, text="Play Again", font=FONT_MEDIUM, command=self.show_login_screen, width=15).pack(side="left", padx=20)
        tk.Button(btns, text="Exit", font=FONT_MEDIUM, command=self.root.quit, width=15).pack(side="right", padx=20)