import os, threading

from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog as tkFileDialog

from PIL import Image, ImageTk

from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import nltk.stem
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import speech_recognition as sr

class analysis_text:
        # Main function in program
    def center(self, toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def callback(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.main.destroy()

    def setResult(self, type, res):
        self.main.update()
        if (type == "neg"):
            self.negpercentLabel.configure(text = "{} % \n".format(str(res)))
            self.negativeBar.configure(value=str(res))

        if (type == "neu"):
            self.neupercentLabel.configure( text = "{} % \n".format(str(res)))
            self.neutralBar.configure(value=str(res))

        if (type == "pos"):
            self.pospercentLabel.configure(text = "{} % \n".format(str(res)))
            self.positiveBar.configure(value=str(res))

        self.main.update()

    def runAnalysis(self):
        if not self.sentences: self.sentences.append(self.line.get())

        sid = SentimentIntensityAnalyzer()
        for sentence in self.sentences:
            ss = sid.polarity_scores(sentence)
            self.analysis_matrix.append([ss['neg'], ss['neu'], ss['pos']])
            for k in sorted(ss):
                self.setResult(k, ss[k])

        self.sentences = []

    def stem_text(self):
        if not self.sentences: self.sentences.append(self.line.get())

        porter = nltk.stem.porter.PorterStemmer(mode='ORIGINAL_ALGORITHM')
        self.stemsentence = ''
        for sentence in self.sentences:
            self.stemsentence += porter.stem(sentence)

        self.typedText.configure(text = self.stemsentence)
        self.line.delete(0, END)
        self.line.insert(0, self.stemsentence)
        self.sentences = []
        if self.stemsentence:
            self.savebt.configure(state=NORMAL)

    def editedText(self, event):
        self.typedText.configure(text = self.line.get() + event.char)

    def save_stem_text(self):
        file = tkFileDialog.asksaveasfilename(filetypes=[("Text files", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, 'w') as f:
                f.write(self.stemsentence)
            self.savebt.configure(state=DISABLED)
            self.confirmsave.configure(text="Saved to : {}".format(os.path.split(file)[-1]), fg = "light green")

        else:
            self.confirmsave.configure(text="No file selected!", fg="orange")

    def open_file(self):
        self.sentences = []
        file = tkFileDialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All Files", "*.*")])
        try:
            if file:
                with open(file, 'r') as f:
                    self.filelabel.configure(text="file = {}".format(os.path.split(file)[-1]), fg = "White")
                    for line in f.readlines():
                        self.sentences.append(line)
                        text = self.sentences[0] if (len(self.sentences[0]) < 50) else self.sentences[0][:50] + ' . . .'
                        self.typedText.configure(text = text)
                        self.runAnalysis()

        except Exception as exp:
            print(exp)
            self.filelabel.configure(text="Sorry, I can't analyse.", fg="orange")

    def display_graph(self):
        style.use("fast")

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.clear()
        ax1.set_ylabel("Result Percentage(s)")
        ax1.set_xlabel("Data Set(s)")
        ax1.set_title("Sentimental Analysis")

        def animate(i):
            if not self.analysis_matrix:
                return

            neg, neu, pos = [], [], []
            for data in self.analysis_matrix:
                neg.append(data[0])
                neu.append(data[1])
                pos.append(data[2])

            ax1.plot(neg, 'r', neu, 'y', pos, 'g')

        ani = animation.FuncAnimation(fig, animate, interval=1000)
        return plt.show()

    def start_audio_thread(self):
        self.filelabel.configure(text="Start talking")

        def audio_to_text():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                try:
                    self.filelabel.configure(text="Processing...")
                    # text = r.recognize_sphinx(audio)
                    text = r.recognize_google(audio)
                    self.sentences.append(text)
                    self.typedText.configure(text=text)
                    self.line.delete(0, END)
                    self.line.insert(0, text)
                    self.runAnalysis()

                except Exception as exp:
                    print(exp)
                    self.typedText.configure(text="Sorry could not recognize your voice")

            return self.filelabel.configure(text="")

        thread = threading.Thread(target=audio_to_text)
        thread.start()

    def runByEnter(self, event):
        self.filelabel.configure(text="")
        return self.runAnalysis()

    def reset(self):
        self.sentences = []
        self.analysis_matrix = []
        self.filelabel.configure(text="")
        self.typedText.configure(text="")
        self.line.icursor(0)
        self.line.delete(0, END)
        self.confirmsave.configure(text="")
        self.savebt.configure(state=DISABLED)
        self.runAnalysis()
        return

    def __init__(self):
        # Create main window
        self.main = Tk()
        self.main.title("Sentimental Analysis")
        ws = self.main.winfo_screenwidth()
        hs = self.main.winfo_screenheight()

        self.main.geometry('%dx%d+%d+%d' % (ws, hs, ws, hs))

        self.main.configure(bg="dark slate gray")

        self.main.protocol("WM_DELETE_WINDOW", self.callback)
        self.main.focus()
        self.center(self.main)
        self.sentences = []
        self.analysis_matrix = []

        # addition item on window
        self.label1 = ttk.Label(text = "Input text:", font=("Helvetica", 15), background="dark slate gray", foreground="White")
        self.label1.pack(pady=8)

        # Add a hidden button Enter
        self.line = ttk.Entry(self.main, width=50, font=("Helvetica", 15), background="dark slate gray", foreground="Blue")
        self.line.pack()
        self.line.focus()

        # addition item on window
        self.label1 = Label(text = "Or", font=("Helvetica", 15), bg="dark slate gray", fg="White")
        self.label1.pack(fill=BOTH, pady=8)

        ttk.Style().configure('W.TButton', background='dark slate gray')
        self.micImage = ImageTk.PhotoImage(Image.open('icon/mic_icon.png'))
        self.audiobt = ttk.Button(image=self.micImage, style='W.TButton', command=self.start_audio_thread)
        self.audiobt.place(x=560, y=123)

        self.filebt = ttk.Button(text="Choose file", command=self.open_file, width=16)
        self.filebt.pack(pady=8)

        self.filelabel = Label(text="", fg = "White", font=("Helvetica", 14), bg="dark slate gray")
        self.filelabel.place(x=750, y=125)

        self.classifbt = ttk.Button(text="Graph", command=self.display_graph, width=16)
        self.classifbt.place(x=200, y=95)

        self.porterbt = ttk.Button(text="Porter Stemmer", command=self.stem_text, width=16)
        self.porterbt.place(x=200, y=125)

        self.savebt = ttk.Button(text="Save To File", command=self.save_stem_text, width=16)
        self.savebt.place(x=200, y=155)
        self.savebt.configure(state=DISABLED)

        self.confirmsave = Label(text="", fg = "White", font=("Helvetica", 14), bg="dark slate gray")
        self.confirmsave.place(x=310, y=155)

        self.resetbt = ttk.Button(text="Reset All", command=self.reset, width=20)
        self.resetbt.place(x=200, y=650)

        self.textLabel = Label(text = "\nReceived Text:", font=("Helvetica", 15), bg="dark slate gray", fg="White")
        self.textLabel.pack()

        self.typedText = Label(text = "Welcome To Sentimental Analysis", fg = "Khaki1", font=("Helvetica", 14, 'bold'), bg="dark slate gray")
        self.typedText.pack()

        self.line.bind("<Key>",self.editedText)
        self.line.bind("<Return>",self.runByEnter)

        self.result = Label(text = "\nResults", font=("Helvetica", 15), bg="dark slate gray", fg="White")
        self.result.pack(pady=10)

        self.negativeLabel = Label(text = "Negativity", fg = "red", font=("Helvetica", 18), bg="dark slate gray")
        self.negativeLabel.place(x=300, y=300)

        self.negativeBar = ttk.Progressbar(mode="determinate", length=200, maximum=1.0, orient="vertical")
        self.negativeBar.place(x=350, y=350)

        self.negpercentLabel = Label(text = "", fg = "red", font=("Helvetica", 18), bg="dark slate gray")
        self.negpercentLabel.place(x=325, y=560)

        self.neutralLabel  = Label(text = "Neutral", fg = "orange", font=("Helvetica", 18), bg="dark slate gray")
        self.neutralLabel.place(x=640, y=300)

        self.neutralBar = ttk.Progressbar(mode="determinate", length=200, maximum=1.0, orient="vertical")
        self.neutralBar.place(x=680, y=350)

        self.neupercentLabel = Label(text = "", fg = "orange", font=("Helvetica", 18), bg="dark slate gray")
        self.neupercentLabel.place(x=665, y=560)

        self.positiveLabel = Label(text = "Positivity", fg = "green", font=("Helvetica", 18), bg="dark slate gray")
        self.positiveLabel.place(x=1000, y=300)

        self.positiveBar = ttk.Progressbar(mode="determinate", length=200, maximum=1.0, orient="vertical")
        self.positiveBar.place(x=1050, y=350)

        self.pospercentLabel = Label(text = "", fg = "green", font=("Helvetica", 18), bg="dark slate gray")
        self.pospercentLabel.place(x=1025, y=560)

        self.autherLabel = ttk.Label(text = "Auther: Hamza Amir", foreground = "silver", font=("Helvetica", 12), background="dark slate gray")
        self.autherLabel.pack(fill=BOTH, side=BOTTOM, ipady=8, padx=45)
        # Run program

if __name__ == '__main__':
    #nltk.download('vader_lexicon')
    
    myanalysis = analysis_text()
    mainloop()
