# modified: W. Eick 05.02.2025

from WebClient import *
from tkinter import *


S7PLC = S7ApiClient('192.168.178.25', 'https://192.168.178.25/awp//Motorsteuerung//api.io', 'PythonWebClient/MiniWebCA_Cer.crt')
S7PLC.login(username, password)

# Window with Tkinter
window = Tk()
window.title("Motorsteuerung")
window.minsize(400, 200)

# Create StringVar class
txt1 = StringVar()
# Create label
label1 = Label(window, textvariable=txt1)

def getData():
    Motorschütz, Motorschutzschalter = S7PLC.getData()
    if Motorschütz == 1:
        label1.config(bg="light green")  # set background
    elif Motorschütz == 0 and Motorschutzschalter == 0:
        label1.config(bg="red")
    else:
        label1.config(bg="light grey")

    txt1.set("Motorschütz=" + str(Motorschütz) + "\nMotorschutzschalter=" + str(Motorschutzschalter))
    window.after(2000, getData)    # refresh after 2 seconds


# Commands
def start():
    S7PLC.postData(1,1)
    Motorschütz, Motorschutzschalter = S7PLC.getData()
    txt1.set("Motorschütz=" + str(Motorschütz))
    
def stop():
    S7PLC.postData(0,0)
    Motorschütz, Motorschutzschalter = S7PLC.getData()
    txt1.set("Motorschütz=" + str(Motorschütz))


buttonStart = Button(text="start", command=start, foreground="green")
buttonStop = Button(text="stop", command=stop, foreground="red")
label1.pack()
buttonStart.pack()
buttonStop.pack()


window.after(0, getData)
# Start the event loop.
window.mainloop()

S7PLC.logout()