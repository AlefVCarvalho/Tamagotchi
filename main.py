import tkinter as tk
from app.ui.tkinter_app import TamagotchiApp


def main():
    root = tk.Tk()
    app = TamagotchiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()