import random
import tkinter as tk
from tkinter import messagebox, filedialog
import pyttsx3
import json
import threading


class EntryApp:
    def __init__(self, root):
        self.words = {}
        self.engine = pyttsx3.init()
        self.voices = {voice.name: voice.id for voice in self.engine.getProperty('voices')}
        # Load saved voice selection
        try:
            with open("voice_selection.json", "r") as f:
                selected_voice = json.load(f)
            self.engine.setProperty('voice', selected_voice)
        except FileNotFoundError:
            selected_voice = list(self.voices.values())[0]

        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        root.title("蒸馍？你不服气？？")
        root.geometry("400x600")
        self.listbox = tk.Listbox(root)
        self.listbox.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()

        self.translate_entry = tk.Entry(root)
        self.translate_entry.pack()

        self.add_button = tk.Button(root, text="添加单词", command=self.add_word)
        self.add_button.pack()

        self.edit_button = tk.Button(root, text="回显", command=self.edit_word)
        self.edit_button.pack()

        self.save_button = tk.Button(root, text="保存单词表", command=self.save_words)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="加载", command=self.load_words)
        self.load_button.pack()

        self.start_button = tk.Button(root, text="开始练习", command=self.start_practice)
        self.start_button.pack()

        self.selected_voice = tk.StringVar(value=[name for name, id in self.voices.items() if id == selected_voice][0])
        self.voice_menu = tk.OptionMenu(root, self.selected_voice, *self.voices.keys())
        self.voice_menu.pack()

        self.sample_button = tk.Button(root, text="示例发音", command=self.sample_voice)
        self.sample_button.pack()

    def change_voice(self, selection):
        selected_voice = self.voices[selection]
        self.engine.setProperty('voice', selected_voice)
        with open("voice_selection.json", "w") as f:
            json.dump(selected_voice, f)

    def sample_voice(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            item = self.listbox.get(index)
            word, translation = item.split(": ")
            self.engine.say(word)
        else:
            self.engine.say('apple')
        self.engine.runAndWait()

    def load_words(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON Files", "*.json"),
                                                          ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                self.words = json.load(f)
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for word, translation in self.words.items():
            self.listbox.insert(tk.END, f"{word}: {translation}")

    def add_word(self):
        word = self.entry.get()
        translation = self.translate_entry.get()
        if word and translation:
            self.words[word] = translation
            self.entry.delete(0, tk.END)
            self.translate_entry.delete(0, tk.END)
            self.update_listbox()

    def edit_word(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            item = self.listbox.get(index)
            word, translation = item.split(": ")
            self.entry.delete(0, tk.END)
            self.translate_entry.delete(0, tk.END)
            self.entry.insert(tk.END, word)
            self.translate_entry.insert(tk.END, translation)

    def save_words(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json"),
                                                            ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.words, f)
            self.update_listbox()

    def start_practice(self):
        if self.words:
            selected_voice = self.voices[self.selected_voice.get()]
            self.practice_app = PracticeApp(self.words, selected_voice)



class PracticeApp:
    def __init__(self, words, selected_voice):
        self.stop_event = threading.Event()
        self.root = tk.Toplevel()
        self.words = words.copy()
        self.all_words = words
        self.practiced_words = []
        self.current_word = None
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate',150)
        self.engine.setProperty('volume', 1.0)
        self.engine.setProperty('voice', selected_voice)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.next_button = tk.Button(self.root, text="下一个", command=self.next_word)
        self.next_button.pack()

        self.answer_button = tk.Button(self.root, text="显示答案", command=self.show_answer)
        self.answer_button.pack()

        self.answer_label = tk.Label(self.root, text="")
        self.answer_label.pack()

        self.stop_event = threading.Event()
        self.repeat_thread = threading.Thread(target=self.repeat_word)
        self.repeat_thread.start()

    def on_closing(self):
        self.stop_event.set()
        self.root.destroy()

    def repeat_word(self):
        while not self.stop_event.is_set():
            if self.current_word:
                self.engine.say(self.current_word)
                self.engine.runAndWait()
                for i in range(3):
                    if not self.current_word:
                        break
                    threading.Event().wait(1)

    def next_word(self):
        if self.words:
            self.current_word = random.choice(list(self.words.keys()))
            self.practiced_words.append(self.current_word)
            self.words.pop(self.current_word)
        else:
            self.current_word = None
            self.show_all_answers()
            messagebox.showinfo("结束", "你完成了设定的所有的单词.")
            self.root.destroy()

    def show_answer(self):
        if self.current_word:
            translation = self.all_words[self.current_word]
            messagebox.showinfo("答案", f"{self.current_word}: {translation}")

    def show_all_answers(self):
        answers = "\n".join([f"{word}: {self.all_words[word]}" for word in self.practiced_words])
        messagebox.showinfo("所有答案", answers)

root = tk.Tk()
app = EntryApp(root)
root.mainloop()