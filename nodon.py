import flet as ft
import mariadb
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthApp:
    def __init__(self):
        self.page = None
        self.connection = None
        self.reset_code = None
        self.reset_email = None
        
        # إعداد قاعدة البيانات
        self.setup_database()
    
    def setup_database(self):
        """إعداد الاتصال بقاعدة البيانات وإنشاء الجدول"""
        try:
            self.connection = mariadb.connect(
                user="your_username",  # ضع اسم المستخدم هنا
                password="your_password",  # ضع كلمة المرور هنا
                host="localhost",
                port=3306,
                database="auth_app"  # ضع اسم قاعدة البيانات هنا
            )
            
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            self.connection.commit()
            cursor.close()
        except mariadb.Error as e:
            print(f"Database error: {e}")
    
    def create_styled_button(self, text, on_click=None, width=300):
        """إنشاء زر بالستايل المطلوب"""
        return ft.ElevatedButton(
            text=text,
            width=width,
            height=50,
            style=ft.ButtonStyle(
                color=ft.colors.BLACK,
                bgcolor=ft.colors.GREY_200,
                elevation=3,
                shadow_color=ft.colors.BLACK26,
            ),
            on_click=on_click
        )
    
    def create_styled_textfield(self, label, password=False, width=300):
        """إنشاء حقل نص بالستايل المطلوب"""
        return ft.TextField(
            label=label,
            width=width,
            height=50,
            password=password,
            border_color=ft.colors.GREY_400,
            color=ft.colors.BLACK,
            bgcolor=ft.colors.GREY_200,
        )
    
    def create_background_container(self, content):
        """إنشاء حاوية بالخلفية"""
        return ft.Container(
            content=content,
            width=self.page.width,
            height=self.page.height,
            # ضع رابط صورة الخلفية هنا بدلاً من "your_background_image_url.jpg"
            image_src="https://i.pinimg.com/564x/a0/4d/ed/a04dedf8315f1e919bcf3f0522d7776c.jpg",
            image_fit=ft.ImageFit.COVER,
        )
    
    def show_error(self, message):
        """عرض رسالة خطأ"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def check_user_exists(self, username, email):
        """التحقق من وجود المستخدم"""
        cursor = self.connection.cursor()
        
        # التحقق من اسم المستخدم
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            cursor.close()
            return "Username already taken"
        
        # التحقق من البريد الإلكتروني
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            cursor.close()
            return "Email Already used"
        
        cursor.close()
        return None
    
    def create_user(self, username, email, password):
        """إنشاء مستخدم جديد"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        self.connection.commit()
        cursor.close()
    
    def verify_login(self, identifier, password):
        """التحقق من بيانات تسجيل الدخول"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
            (identifier, identifier, password)
        )
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def user_exists_by_identifier(self, identifier):
        """التحقق من وجود المستخدم بالاسم أو البريد"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier, identifier)
        )
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def email_exists(self, email):
        """التحقق من وجود البريد الإلكتروني"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def generate_reset_code(self):
        """توليد رمز إعادة تعيين كلمة المرور"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    def send_reset_email(self, email, code):
        """إرسال رمز إعادة التعيين عبر البريد الإلكتروني"""
        # هنا يجب إعداد خدمة البريد الإلكتروني
        # مثال بسيط - في التطبيق الحقيقي استخدم خدمة بريد إلكتروني
        print(f"Reset code for {email}: {code}")
        return True
    
    def update_password(self, email, new_password):
        """تحديث كلمة المرور"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        self.connection.commit()
        cursor.close()
    
    def main_page(self, e):
        """الصفحة الرئيسية"""
        def go_to_signup(e):
            self.signup_page(e)
        
        def go_to_login(e):
            self.login_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=100),  # مساحة فارغة
                ft.Text(
                    "Welcome",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=200),  # مساحة فارغة
                ft.Row(
                    [
                        self.create_styled_button("Sign Up", go_to_signup),
                        ft.Container(width=50),  # مساحة بين الأزرار
                        self.create_styled_button("Login", go_to_login),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def signup_page(self, e):
        """صفحة التسجيل"""
        username_field = self.create_styled_textfield("Username")
        email_field = self.create_styled_textfield("Email")
        password_field = self.create_styled_textfield("Password", password=True)
        repeat_password_field = self.create_styled_textfield("Repeat Password", password=True)
        
        def create_account(e):
            username = username_field.value
            email = email_field.value
            password = password_field.value
            repeat_password = repeat_password_field.value
            
            if not all([username, email, password, repeat_password]):
                self.show_error("Please fill all fields")
                return
            
            # التحقق من وجود المستخدم
            error = self.check_user_exists(username, email)
            if error:
                self.show_error(error)
                return
            
            # التحقق من تطابق كلمات المرور
            if password != repeat_password:
                self.show_error("Passwords do not match")
                return
            
            # إنشاء المستخدم
            self.create_user(username, email, password)
            self.soon_page(e)
        
        def go_to_login(e):
            self.login_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=50),
                ft.Text(
                    "Create new account",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                username_field,
                ft.Container(height=20),
                email_field,
                ft.Container(height=20),
                password_field,
                ft.Container(height=20),
                repeat_password_field,
                ft.Container(height=30),
                ft.Row(
                    [
                        self.create_styled_button("Create Now", create_account),
                        ft.Container(width=50),
                        self.create_styled_button("I have account", go_to_login),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def login_page(self, e):
        """صفحة تسجيل الدخول"""
        identifier_field = self.create_styled_textfield("Email or Username")
        password_field = self.create_styled_textfield("Password", password=True)
        
        def login(e):
            identifier = identifier_field.value
            password = password_field.value
            
            if not all([identifier, password]):
                self.show_error("Please fill all fields")
                return
            
            # التحقق من وجود المستخدم
            if not self.user_exists_by_identifier(identifier):
                self.show_error("User not found")
                return
            
            # التحقق من كلمة المرور
            if not self.verify_login(identifier, password):
                self.show_error("Incorrect password")
                return
            
            self.soon_page(e)
        
        def go_to_signup(e):
            self.signup_page(e)
        
        def forgot_password(e):
            self.forgot_password_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=80),
                ft.Text(
                    "Welcome back",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                identifier_field,
                ft.Container(height=20),
                password_field,
                ft.Container(height=30),
                ft.Row(
                    [
                        self.create_styled_button("Login", login),
                        ft.Container(width=50),
                        self.create_styled_button("Don't have account", go_to_signup),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Container(height=20),
                ft.TextButton(
                    "Forget password??",
                    style=ft.ButtonStyle(color=ft.colors.LIGHT_BLUE),
                    on_click=forgot_password
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def forgot_password_page(self, e):
        """صفحة نسيان كلمة المرور"""
        email_field = self.create_styled_textfield("Email")
        
        def send_code(e):
            email = email_field.value
            
            if not email:
                self.show_error("Please enter your email")
                return
            
            if not self.email_exists(email):
                self.show_error("Email not found")
                return
            
            self.reset_code = self.generate_reset_code()
            self.reset_email = email
            self.send_reset_email(email, self.reset_code)
            self.verify_code_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=100),
                ft.Text(
                    "Reset Password",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                email_field,
                ft.Container(height=30),
                self.create_styled_button("Send Code", send_code),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def verify_code_page(self, e):
        """صفحة التحقق من الرمز"""
        code_field = self.create_styled_textfield("Enter the code")
        
        def verify_code(e):
            entered_code = code_field.value
            
            if not entered_code:
                self.show_error("Please enter the code")
                return
            
            if entered_code != self.reset_code:
                self.show_error("Invalid code")
                return
            
            self.new_password_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=100),
                ft.Text(
                    "Verify Code",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                code_field,
                ft.Container(height=30),
                self.create_styled_button("Verify", verify_code),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def new_password_page(self, e):
        """صفحة كلمة المرور الجديدة"""
        new_password_field = self.create_styled_textfield("New Password", password=True)
        repeat_password_field = self.create_styled_textfield("Repeat Password", password=True)
        
        def update_password(e):
            new_password = new_password_field.value
            repeat_password = repeat_password_field.value
            
            if not all([new_password, repeat_password]):
                self.show_error("Please fill all fields")
                return
            
            if new_password != repeat_password:
                self.show_error("Passwords do not match")
                return
            
            self.update_password(self.reset_email, new_password)
            self.login_page(e)
        
        content = ft.Column(
            [
                ft.Container(height=100),
                ft.Text(
                    "New Password",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                new_password_field,
                ft.Container(height=20),
                repeat_password_field,
                ft.Container(height=30),
                self.create_styled_button("Update Password", update_password),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()
    
    def soon_page(self, e):
        """صفحة قريباً"""
        content = ft.Column(
            [
                ft.Text(
                    "Soon",
                    size=50,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=50),
                self.create_styled_button("Back to Main", self.main_page),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.page.controls.clear()
        self.page.add(self.create_background_container(content))
        self.page.update()

def main(page: ft.Page):
    page.title = "Authentication App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = False
    
    app = AuthApp()
    app.page = page
    app.main_page(None)

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)