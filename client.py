from customtkinter import *
from tkinter import filedialog
import socket
import threading
from PIL import Image
import io
import struct
import auth




win = auth.AuthApp()
win.mainloop()
env = win.env

set_appearance_mode("Dark")
set_default_color_theme("blue")

class Window(CTk):
    def __init__(self, fg_color=None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.geometry("600x700")
        self.title("LogiTalk Modern Chat")
        
        self.name = env.get("name", "ANONIM") if env else "ANONIM"
        
        self.header_label = CTkLabel(self, text=f"LogiTalk — {self.name}", font=("Arial", 18, "bold"))
        self.header_label.pack(pady=10)

        self.chat_frame = CTkScrollableFrame(self, width=550, height=500, fg_color="transparent")
        self.chat_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.messages_list = []

        self.input_frame = CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=20, padx=10, fill="x", side="bottom")

        self.image_button = CTkButton(self.input_frame, text="📷", width=40, command=self.select_and_send_image)
        self.image_button.pack(side="left", padx=5)

        self.sent_text = CTkEntry(self.input_frame, placeholder_text="Введіть повідомлення...")
        self.sent_text.pack(side="left", fill="x", expand=True, padx=5)
        self.sent_text.bind("<Return>", lambda e: self.sent_message())

        self.sent_btn = CTkButton(self.input_frame, text="Відправити", command=self.sent_message)
        self.sent_btn.pack(side="left", padx=5)
        
        self.host = "localhost"
        self.port = 8080
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            
            self.send_framed_packet("TEXT", f"{self.name}@приєднався до чату")
            
            threading.Thread(target=self.recv_msg_stream, daemon=True).start()
        
        except Exception as e:
            self.add_text_message_to_gui("Система", "Не вдалося приєднатися до сервера.", is_system=True)

    def send_framed_packet(self, p_type, payload):
        try:
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload

            type_bytes = p_type.encode('utf-8')[:4].ljust(4)
            length_bytes = struct.pack('!I', len(payload_bytes))
            
            self.sock.sendall(type_bytes + length_bytes + payload_bytes)
        except Exception as e:
            print(f"Помилка відправки пакета: {e}")

    def recv_msg_stream(self):
        while True:
            try:
                header = self.recv_all(self.sock, 8)
                if not header:
                    break
                
                p_type = header[:4].decode('utf-8', errors='ignore').strip()
                p_len = struct.unpack('!I', header[4:])[0]
                
                p_payload = self.recv_all(self.sock, p_len)
                if not p_payload:
                    break
                
                self.after(0, self.handle_incoming_data, p_type, p_payload)

            except Exception as e:
                print(f"Помилка зв'язку з сервером: {e}")
                break
        try:
            self.sock.close()
        except: pass

    def recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def handle_incoming_data(self, p_type, payload):
        try:
            if p_type == "TEXT":
                parts = payload.decode('utf-8').split("@", 1)
                if len(parts) == 2:
                    self.add_text_message_to_gui(parts[0], parts[1])
                    
            elif p_type == "IMAG":
                if b'@' in payload:
                    sender_bytes, img_bytes = payload.split(b'@', 1)
                    sender = sender_bytes.decode('utf-8', errors='ignore')
                    
                    self.add_image_message_to_gui(sender, img_bytes)
        except Exception as e:
            print(f"Помилка обробки вхідних даних: {e}")

    def add_text_message_to_gui(self, sender, text, is_system=False):
        is_my_msg = (sender == self.name and not is_system)
        
        msg_frame = CTkFrame(self.chat_frame, fg_color="transparent")
        
        pack_side = "right" if is_my_msg else "left"
        anchor_val = "e" if is_my_msg else "w"
        bubble_color = "#1f6aa5" if is_my_msg else "#2b2b2b"
        
        if is_system:
            bubble_color = "transparent"
            sender = "[Система]"

        bubble = CTkFrame(msg_frame, fg_color=bubble_color, corner_radius=10)
        bubble.pack(side=pack_side, pady=2)

        label = CTkLabel(bubble, text=text, wraplength=350, justify="left", text_color="white", padx=10, pady=5)
        label.pack()

        info_label = CTkLabel(msg_frame, text=sender, font=("Arial", 10), text_color="gray50")
        info_label.pack(side=pack_side, anchor=anchor_val, padx=5)

        msg_frame.pack(fill="x", pady=5)
        self.scroll_to_bottom()

    def add_image_message_to_gui(self, sender, image_bytes):
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            original_width, original_height = pil_image.size
            target_width = 250
            ratio = target_width / float(original_width)
            target_height = int(float(original_height) * float(ratio))
            
            pil_resized = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            ctk_image = CTkImage(light_image=pil_resized, dark_image=pil_resized, size=(target_width, target_height))
            
            is_my_msg = (sender == self.name)
            pack_side = "right" if is_my_msg else "left"
            bubble_color = "#1f6aa5" if is_my_msg else "#2b2b2b"

            msg_frame = CTkFrame(self.chat_frame, fg_color="transparent")
            msg_frame.pack(fill="x", pady=5)

            bubble = CTkFrame(msg_frame, fg_color=bubble_color, corner_radius=10)
            bubble.pack(side=pack_side, pady=2)

            image_label = CTkLabel(bubble, text="", image=ctk_image)
            image_label.pack(padx=5, pady=5)
            
            info_label = CTkLabel(msg_frame, text=sender, font=("Arial", 10), text_color="gray50")
            info_label.pack(side=pack_side, anchor="e" if is_my_msg else "w", padx=5)
            
            self.messages_list.append(ctk_image)
            self.scroll_to_bottom()
            
        except Exception as e:
            print(f"Не вдалося відобразити фото: {e}")

    def scroll_to_bottom(self):
        self.chat_frame._scrollbar.set(1.0, 1.0)
        self.chat_frame._on_mousewheel(struct.pack('i', 1000))

    def sent_message(self):
        message = self.sent_text.get()
        if message:
            data = f"{self.name}@{message}"
            self.send_framed_packet("TEXT", data)
        self.sent_text.delete(0, END)

    def select_and_send_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.gif")])
        if not file_path:
            return
        
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            if len(image_bytes) > 5 * 1024 * 1024:
                self.add_text_message_to_gui("Система", "Файл занадто великий (>5MB)", is_system=True)
                return

            payload = self.name.encode('utf-8') + b'@' + image_bytes
            self.send_framed_packet("IMAG", payload)

        except Exception as e:
            print(f"Помилка читання/відправки фото: {e}")
            self.add_text_message_to_gui("Система", "Не вдалося відправити фото.", is_system=True)

if __name__ == "__main__":
    try:
        env = win.env
    except:
        class DummyEnv:
            def get(self, key, default): return default
        env = DummyEnv()
        
    app = Window()
    app.mainloop()