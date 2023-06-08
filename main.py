import customtkinter as tk
from LeftFrameClass import LeftFrame
from RightFrameClass import RightFrame

tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")
root=tk.CTk()
root.resizable(0,0)
root.geometry("1280x720")

MainFrame=tk.CTkFrame(master=root)
MainFrame.pack(pady=5, padx=5, fill="both", expand=True)

LeftFrameClass=LeftFrame()
LeftFrame=LeftFrameClass.buildFrame(MainFrame)

RightFrameClass=RightFrame()
RightFrame=RightFrameClass.buildFrame(MainFrame)

LeftFrameClass.setRightFrame(RightFrameClass) #Setting RightFrame to LeftFrame

#bttn = False #Initial state
#ConnectBttn=tk.Button(root,width=150,text="Connect",bg="green",fg="white",command=ConnectButton)
#ConnectBttn.place(x=50, y=0)
#TopFrameClass=TopFrameClass()
#TopFrame=TopFrameClass.buildFrame(MainFrame)

"""
def ConnectButton():
    global bttn #variable global
    if not bttn:
        ConnectBttn['text']='Disconnect'
        ConnectBttn['bg'] = 'red'
        print("Disconnect")
        MainFrame.pack(fill='both', expand='yes', padx=10, pady=50)
        bttn = True

    else:
        ConnectBttn['text'] = 'Connect'
        ConnectBttn['bg'] = 'Green'
        print("Connect")
        bttn = False
        MainFrame.pack_forget()

"""
root.mainloop()