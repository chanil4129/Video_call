import tkinter as tk

def display():
    input_text = text_entry.get()
    print(f'You entered: {input_text}')

root = tk.Tk()

text_entry = tk.Entry(root)
text_entry.pack()

submit_button = tk.Button(root, text="Submit", command=display)
submit_button.pack()

root.mainloop()
