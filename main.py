from tkinter import PhotoImage, filedialog
import customtkinter
import customtkinter as ctk
import qrcode
import cv2
import os
import numpy as np
from pyzbar.pyzbar import decode
import pyttsx3
def pop_up(msg: str):
    win = customtkinter.CTkToplevel()
    win.wm_title("For you!")
    win.maxsize(300, 180)
    win.minsize(300, 180)
    icon = PhotoImage("code.ico")
    win.iconbitmap(icon)

    frame = customtkinter.CTkFrame(master=win)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    label = customtkinter.CTkLabel(master=frame, text=msg, font=("Berlin Sans FB", 16))
    label.pack(pady=10, padx=10)

    btn = customtkinter.CTkButton(master=frame, text="OK", font=("Berlin Sans FB", 16), command=win.destroy)
    btn.pack(ipady=5, ipadx=5, pady=10, padx=10)


def generate_code(url_input: customtkinter.CTkEntry):
    url = url_input.get()
    code = qrcode.make(url)
    downloads = f"{os.getenv('USERPROFILE')}\\Downloads"
    code.save(downloads + '/code.png')
    pop_up("The QR code is at >>\n" + downloads)


def start_decoding():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say("Please wait! The Q R Decoder is starting.")
    engine.runAndWait()

    # Create a separate thread for camera initialization
    import threading
    def init_camera():
        global cap
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(4, 800)
        cap.set(3, 600)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    camera_thread = threading.Thread(target=init_camera)
    camera_thread.start()
    # Wait for the camera to initialize
    camera_thread.join()

    while True:
        ret, img = cap.read()
        for barcode in decode(img):
            mydata = barcode.data.decode('utf-8')
            print(mydata)
            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (0, 255, 0), 5)
            pts2 = barcode.rect
            cv2.putText(img, mydata, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 255, 255), 3)

        cv2.imshow('QR Decoder', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
def decodes():
    qr_code = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(("image", ".jpg"), ("image", ".jpeg"), ("image", ".png")))
    code_detector = cv2.QRCodeDetector()
    code_str, _, _ = code_detector.detectAndDecode(cv2.imread(qr_code))
    pop_up(code_str)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_default_color_theme("green")

        customtkinter.set_appearance_mode("light")
        self.title("QR Code Generator")
        icon = PhotoImage("code.ico")
        self.iconbitmap(icon)

        height = 300
        width = 300

        self.geometry(f"{width}x{height}")
        self.minsize(300, 350)
        self.maxsize(300, 300)

        frame = customtkinter.CTkFrame(master=self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        label = customtkinter.CTkLabel(master=frame,
                text="QR Code\nGenerator & Decoder", font=("Berlin Sans FB", 18))
        label.pack(pady=10, padx=10)

        url_input = customtkinter.CTkEntry(master=frame,
                    placeholder_text="Enter Text Here", justify="center",
                                           width=200, font=("Consolas", 16))
        url_input.pack(ipady=5, ipadx=5, pady=5)
        btn_gen = customtkinter.CTkButton(master=frame,text="Generate Code",
                                          font=("Berlin Sans FB", 16),
                                          command=lambda: generate_code(url_input),
                                          hover=True,
                                          hover_color="red")
        btn_gen.pack(ipady=5, ipadx=5, pady=10, padx=10)

        btn_dec = customtkinter.CTkButton(master=frame,text="Decode QR Code",
                                          font=("Berlin Sans FB", 16),
                                          command=start_decoding,
                                          hover=True,
                                          hover_color="red")
        btn_dec.pack(ipady=5, ipadx=5, pady=10, padx=10)
        
        btn_dec = customtkinter.CTkButton(master=frame,text="Upload QR Code",
                                          font=("Berlin Sans FB", 16),
                                          command=decodes,
                                          hover=True,
                                          hover_color="red")
        btn_dec.pack(ipady=5, ipadx=5, pady=10, padx=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
