import customtkinter as ctk
from PIL import Image

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Авторизація - Logika")
        self.geometry("800x500")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

      
        self.left_frame = ctk.CTkFrame(self, fg_color="#4B2C85", corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.left_frame, 
            text="Logika", 
            text_color="white",
            font=ctk.CTkFont(size=40, weight="bold")
        )
        self.logo_label.pack(expand=True)

        self.sub_text = ctk.CTkLabel(
            self.left_frame,
            text="Школа програмування майбутнього",
            text_color="#D1C4E9",
            font=ctk.CTkFont(size=14)
        )
        self.sub_text.pack(pady=(0, 50))

        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        self.title_label = ctk.CTkLabel(
            self.right_frame, 
            text="Вхід", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(20, 30))

      
        self.username_entry = ctk.CTkEntry(
            self.right_frame, 
            placeholder_text="Логін",
            width=250,
            height=40,
            corner_radius=10
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.right_frame, 
            placeholder_text="Пароль", 
            show="*",
            width=250,
            height=40,
            corner_radius=10
        )
        self.password_entry.pack(pady=10)


        self.login_button = ctk.CTkButton(
            self.right_frame, 
            text="Увійти", 
            fg_color="#7B1FA2",
            hover_color="#6A1B9A",
            width=250,
            height=45,
            corner_radius=20, 
            command=self.go_to_app
        )
        self.login_button.pack(pady=30)

        self.forgot_pass = ctk.CTkLabel(
            self.right_frame, 
            text="Забули пароль?", 
            font=ctk.CTkFont(size=12, underline=True),
            cursor="hand2"
        )
        self.forgot_pass.pack()

    def go_to_app(self):
            print(f"Спроба входу: {self.username_entry.get()}")
            self.env={"name":self.username_entry.get()}
            self.destroy()

        
if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()