import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import subprocess
import shutil
import os
import re

class Editor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)

        self.filename = ''
        self.basepath =''
        self.text = ''
        self.png_path = ''
        self.mode =''

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for col in range(8):
            self.main_frame.grid_columnconfigure(col, weight=10, uniform="equal")
            self.main_frame.grid_rowconfigure(col, weight=10, uniform="equal")

        self.buttons(self.main_frame)
        self.editor(self.main_frame)
        self.line(self.main_frame)
        self.plot_image(self.main_frame)
        

    def buttons(self, parent):
        self.new_button = tk.Button(parent, text="New", command=self.new_file)
        self.open_button = tk.Button(parent, text="Open", command=self.open_file)
        self.save_button = tk.Button(parent, text="Save", command=self.save_file)
        self.run_button = tk.Button(parent, text="> Run", command=self.run_file)
        
        self.new_button.grid(row=8, column=1, rowspan=1, columnspan=1, sticky="new")#, padx=5, pady=5)
        self.open_button.grid(row=8, column=0, rowspan=1, columnspan=1, sticky="new")#, padx=5, pady=5)
        self.save_button.grid(row=8, column=2, rowspan=1, columnspan=1, sticky="new")#, padx=5, pady=5)
        self.run_button.grid(row=8, column=3, rowspan=1, columnspan=1, sticky="new")#, padx=5, pady=5)

    def new_file(self):
        self.filename = fd.asksaveasfilename(filetypes=[("All files", "*.*"), ("R Script", "*.r"), ("Python Script", "*.py")])
        self.basepath = os.path.dirname(self.filename)
        if self.filename[-3:] == ".py":
            self.mode = "python"
        else:
            self.mode = "r"
        self.writer.configure(state="normal")
        self.writer.delete("1.0", tk.END)

    def editor(self, parent):
        self.writer = tk.Text(parent)
        self.writer.grid(row=0, column=0, rowspan=7, columnspan=5, sticky="nsew")
        self.writer.insert("1.0", "Open or create a new file to get started...\nDon't forget R: png(filename=\"\") or Python: savefig('filename.png') for plotting action\n\nVersion: 0.3 - Now with python and working filepaths!")
        
        self.writer_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.writer.yview)
        self.writer_scrollbar.grid(row=0, column=5, rowspan=7, sticky="ns")
        self.writer.configure(yscrollcommand=self.writer_scrollbar.set, state="disabled")

    def line(self, parent):
        self.debug = tk.Text(parent)
        self.debug.insert("1.0", "Output will be here...")
        self.debug.grid(row=0, column=6, rowspan=2, columnspan=2, sticky="nsew")

        self.debug_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.debug.yview)
        self.debug_scrollbar.grid(row=0, column=8, rowspan=2, sticky="ns")

        self.debug.configure(yscrollcommand=self.debug_scrollbar.set, state="disabled")



    def plot_image(self, parent):
        if self.png_path != '':
            path = os.path.join(self.basepath, self.png_path)
            shutil.move(self.png_path, path) # Will always be generated in the base dir
            self.disp = tk.PhotoImage(file=path)

        else:
            self.disp = tk.PhotoImage(file="plotd.png")

        self.disp_label = tk.Label(parent, image=self.disp)
        self.disp_label.grid(row=5, column=6, rowspan=2, columnspan=2, sticky="nsew")

    # Command tasks

    def command(self, path):
        if self.mode == 'r':
            pipe = subprocess.Popen(['Rscript', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.basepath)
        else:
            pipe = subprocess.Popen(['python', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.basepath)
        output, err = pipe.communicate(b"input data that is passed to subprocess' stdin")

        return output+err

    def open_file(self):
        self.filename = fd.askopenfilename(title='Open a file', initialdir=os.getcwd())
        self.basepath = os.path.dirname(self.filename)
        with open(self.filename) as file:
            self.text = file.read()
        if self.filename[-3:] == ".py":
            self.mode = "python"
        else:
            self.mode = "r"
        self.writer.configure(state="normal")
        self.writer.delete("1.0", tk.END)
        self.writer.insert("1.0", self.text)

    def save_file(self):
        with open(self.filename, 'w') as file:
            self.text = self.writer.get("1.0", tk.END)
            file.write(self.text)

        self.basepath = os.path.dirname(self.filename)
        
    def run_file(self):
        self.save_file()
        self.file_name()
        outpipe = self.command(self.filename)
        self.debug.configure(state="normal")
        self.debug.delete("1.0", tk.END)
        self.debug.insert("1.0", outpipe)
        self.debug.configure(state="disabled")

        self.plot_image(self.main_frame)

    def file_name(self):
        if self.mode == "r":
            pattern = r'(?:filepath|filename)="([^"]+)"'
        else:
            pattern = r"savefig\(['\"](.*?\.png)['\"]\)"

        match = re.search(pattern, self.text)
        if match:
            self.png_path = match.group(1)

root = tk.Tk()
root.title("Editor - Made in China Edition")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

editor = Editor(root)
root.mainloop()