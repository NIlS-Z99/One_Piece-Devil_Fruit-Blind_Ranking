
import os
import tkinter as tk
from gui import DevilFruitGameGUI
from game_backend import GameBackend
from devil_fruit_crawler import crawl_and_save_all


if not os.path.exists("devil_fruits.json"):
    crawl_and_save_all()

if __name__ == "__main__":
    root = tk.Tk()
    backend = GameBackend()
    app = DevilFruitGameGUI(root,backend)
    root.mainloop()
