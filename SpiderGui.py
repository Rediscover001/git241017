import tkinter as tk
from tkinter import messagebox

# 创建主窗口
root = tk.Tk()
root.title("Tkinter Input Example")

# 创建标签
label = tk.Label(root, text="Enter something:")
label.pack(pady=10)

# 创建输入框
entry = tk.Entry(root)
entry.pack(pady=10)

# 创建按钮
def on_button_click():
    user_input = entry.get()
    messagebox.showinfo("User Input", f"You entered: {user_input}")

button = tk.Button(root, text="Submit", command=on_button_click)
button.pack(pady=10)

# 运行主循环
root.mainloop()