import tkinter as tk
import tkinter.messagebox as msgbox
import pymysql
from pymysql.cursors import DictCursor
import re  # 用于正则表达式校验（如身份证号）
from tkinter import ttk
from tkcalendar import DateEntry  # 需安装：pip install tkcalendar


class VaccineManager:
    def __init__(self):
        # 初始化主窗口
        self.app = tk.Tk()
        self.app.title("疫苗信息管理系统")
        self.app.geometry("600x400")
        self.app.resizable(False, False)

        # 数据库配置
        self.db_name = "test1"  # 使用test数据库
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "zhengyi520",  # 请替换为你的数据库密码
            "charset": "utf8mb4",
            "cursorclass": DictCursor
        }

        # 字段中文映射
        self.FIELD_MAPPING = {
            "user_info": {
                "user_name": "管理员姓名",
                "user_code": "管理员编号"
            },
            # 其他字段映射保持不变...
            "vaccine_info": {
                "vaccine_num": "疫苗批号",
                "vaccine_name": "疫苗名称",
                "company_name": "企业名称",
                "company_num": "企业编号",
                "size": "规格",
                "buy_price": "进价",
                "pre_sale_price": "预售价",
                "limit_up": "企业上限",
                "limit_down": "企业下限"
            }
        }

        # 显示主窗口
        self.main_window()
        self.app.mainloop()

    # ------------------------------ 修复数据库连接方法 ------------------------------
    def connect_DBS(self, sql, params=None, fetch_all=False):
        """修复了sql_upper变量作用域问题"""
        db = None
        cursor = None
        sql_upper = ""  # 初始化变量，避免未定义错误
        try:
            # 建立数据库连接
            db = pymysql.connect(database=self.db_name, **self.db_config)
            cursor = db.cursor()

            # 执行SQL
            cursor.execute(sql, params or ())
            sql_upper = sql.strip().upper()  # 现在在所有代码路径中都有定义

            # 处理查询操作
            if sql_upper.startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return cursor.fetchall() if fetch_all else cursor.fetchone()
            # 处理写操作
            else:
                db.commit()
                return cursor.rowcount

        except pymysql.MySQLError as e:
            # 写操作失败时回滚
            if db and not sql_upper.startswith(('SELECT', 'SHOW')):
                db.rollback()
            msgbox.showerror("数据库错误", f"错误代码：{e.args[0]}\n错误信息：{e.args[1]}")
            return None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ------------------------------ 修复用户注册功能 ------------------------------
    def register(self):
        """创建注册窗口，修复了salt字段问题"""
        register_win = tk.Toplevel(self.app)
        register_win.title('用户注册')
        register_win.geometry("600x400")
        register_win.resizable(False, False)

        # 标题
        tk.Label(register_win, text="欢迎注册", font=("KaiTi", 40)).place(x=200, y=20)

        # 表单字段配置
        fields = [
            ("添加管理员姓名：", 120, False, "user_name"),
            ("确认管理员编号：", 150, True, "user_code")  # 密码类型
        ]
        entries = self.create_form(register_win, fields)

        # 注册逻辑（修复了salt字段问题）
        def user_register():
            # 获取并验证输入
            valid_data = self.validate_input(register_win, entries, "user_info")
            if not valid_data:
                return

            # 生成随机盐值（解决salt字段无默认值问题）
            import random
            import string
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            # 执行注册（包含salt字段）
            sql = """
                INSERT INTO user_info (user_name, user_code, salt) 
                VALUES (%s, %s, %s);
            """
            affected_rows = self.connect_DBS(sql=sql, params=(
                valid_data["user_name"],
                valid_data["user_code"],
                salt  # 添加salt字段值
            ))
            if affected_rows and affected_rows > 0:
                msgbox.showinfo("成功", "注册成功！请登录")
                register_win.destroy()

        # 注册按钮
        tk.Button(register_win, text="注册", bg='white', font=("Arial", 9), width=12,
                  command=user_register).place(x=250, y=250)

    # ------------------------------ 其他方法保持不变 ------------------------------
    def main_window(self):
        # 保持不变...
        for widget in self.app.winfo_children():
            widget.destroy()

        tk.Label(self.app, text="疫苗信息管理系统", font=("KaiTi", 24)).place(x=150, y=80)

        btn_style = {
            "bg": "white",
            "font": ("Arial", 12),
            "width": 12,
            "height": 1
        }
        tk.Button(self.app, text='登录', command=self.login, **btn_style).place(x=260, y=200)
        tk.Button(self.app, text='注册', command=self.register, **btn_style).place(x=260, y=240)
        tk.Button(self.app, text='退出', command=self.app.quit, **btn_style).place(x=260, y=280)

    def login(self):
        # 保持不变...
        login_win = tk.Toplevel(self.app)
        login_win.title('用户登录')
        login_win.geometry("600x400")
        login_win.resizable(False, False)

        tk.Label(login_win, text="欢迎登录", font=("KaiTi", 40)).place(x=200, y=20)

        fields = [
            ("管理员姓名：", 120, False, "user_name"),
            ("管理员编号：", 150, True, "user_code")
        ]
        entries = self.create_form(login_win, fields)

        def user_check():
            user_name = entries["user_name"][0].get().strip()
            user_code = entries["user_code"][0].get().strip()

            if not user_name or not user_code:
                msgbox.showwarning("警告", "用户名或编号不能为空！")
                return

            sql = "SELECT * FROM user_info WHERE user_name = %s;"
            user_data = self.connect_DBS(sql=sql, params=(user_name,))

            if not user_data:
                msgbox.showerror("错误", "用户不存在，请先注册！")
                return
            if user_data["user_code"] != user_code:
                msgbox.showerror("错误", "编号错误！")
                return

            msgbox.showinfo("成功", f"欢迎您，{user_name}！")
            login_win.destroy()
            self.options()

        tk.Button(login_win, text="登录", bg='white', font=("Arial", 9), width=12,
                  command=user_check).place(x=250, y=250)

    # 其他方法（options, create_form, validate_input等）保持不变...
    def options(self):
        options_win = tk.Toplevel(self.app)
        options_win.title('功能选项')
        options_win.geometry("600x500")
        options_win.resizable(False, False)

        tk.Label(options_win, text="欢迎使用！", font=("KaiTi", 40)).place(x=180, y=15)

        buttons = [
            ("新建疫苗信息", self.add_vacc_info, 100, 100),
            ("新建疫苗分配信息", self.add_vaccine_distr_info, 100, 160),
            ("新建疫苗养护信息", self.add_vaccine_maintenance_info, 100, 220),
            ("新建接种人员信息", self.add_vaccination_person_info, 100, 280),
            ("查询疫苗分配信息", self.vaccine_distr_info_query, 100, 340),
            ("查询疫苗养护信息", self.vaccination_maintenance_info_query, 320, 100),
            ("查询接种人员信息", self.vaccination_person_info_query, 320, 160),
            ("查询疫苗信息", self.vaccine_info_query, 320, 220),
            ("修改疫苗信息", self.modify_vaccine_info, 320, 280),
            ("删除疫苗信息", self.del_vaccine_info, 320, 340)
        ]

        btn_style = {
            "bg": "white",
            "font": ("Arial", 12),
            "width": 20,
            "height": 2
        }
        for text, cmd, x, y in buttons:
            tk.Button(options_win, text=text, command=cmd, **btn_style).place(x=x, y=y)

    def create_form(self, parent, fields):
        form_data = {}
        for label_text, y_pos, is_password, field_name in fields:
            tk.Label(parent, text=label_text, font=("Arial", 9)).place(x=80, y=y_pos)
            if "date" in field_name or "Date" in field_name:
                entry = DateEntry(parent, font=("Arial", 9), width=44, date_pattern='yyyy-MM-dd')
            else:
                entry = tk.Entry(parent, font=("Arial", 9), width=46, show="*" if is_password else "")
            entry.place(x=180, y=y_pos, width=350, height=25)
            form_data[field_name] = (entry, is_password)
        return form_data

    def validate_input(self, parent, form_data, table_name):
        valid_data = {}
        for field_name, (entry, is_password) in form_data.items():
            value = entry.get().strip()
            field_cn = self.FIELD_MAPPING.get(table_name, {}).get(field_name, field_name)

            if not value:
                msgbox.showwarning("警告", f"{field_cn}不能为空！")
                entry.focus()
                return None

            if field_name == "id_card":
                if not re.match(r'^\d{17}[\dXx]$', value):
                    msgbox.showwarning("警告", f"{field_cn}格式错误（需18位）！")
                    entry.focus()
                    return None
            elif field_name == "phone":
                if not re.match(r'^\d{11}$', value):
                    msgbox.showwarning("警告", f"{field_cn}格式错误（需11位数字）！")
                    entry.focus()
                    return None
            elif field_name in ["age", "storage_temp", "storage_humidity", "num",
                                "buy_price", "pre_sale_price", "limit_up", "limit_down"]:
                try:
                    num_value = float(value)
                    valid_data[field_name] = num_value
                    if field_name == "age" and not (0 <= num_value <= 120):
                        msgbox.showwarning("警告", f"{field_cn}应在0-120之间！")
                        entry.focus()
                        return None
                    elif field_name == "storage_temp" and not (2 <= num_value <= 8):
                        msgbox.showwarning("警告", f"{field_cn}应在2-8℃之间！")
                        entry.focus()
                        return None
                    elif field_name == "storage_humidity" and not (30 <= num_value <= 60):
                        msgbox.showwarning("警告", f"{field_cn}应在30%-60%之间！")
                        entry.focus()
                        return None
                    elif num_value <= 0:
                        msgbox.showwarning("警告", f"{field_cn}必须为正数！")
                        entry.focus()
                        return None
                except ValueError:
                    msgbox.showwarning("警告", f"{field_cn}必须输入有效数字！")
                    entry.focus()
                    return None
            else:
                valid_data[field_name] = value
        return valid_data

    # 其余方法保持不变...
    def add_vacc_info(self):
        add_win = tk.Toplevel(self.app)
        add_win.title('添加疫苗信息')
        add_win.geometry("600x400")
        add_win.resizable(False, False)

        fields = [
            ("疫苗批号：", 60, False, "vaccine_num"),
            ("疫苗名称：", 90, False, "vaccine_name"),
            ("企业名称：", 120, False, "company_name"),
            ("企业编号：", 150, False, "company_num"),
            ("    规格：", 180, False, "size"),
            ("    进价：", 210, False, "buy_price"),
            ("  预售价：", 240, False, "pre_sale_price"),
            ("企业上限：", 270, False, "limit_up"),
            ("企业下限：", 300, False, "limit_down")
        ]
        form_data = self.create_form(add_win, fields)

        def clear():
            for entry, _ in form_data.values():
                entry.delete(0, tk.END)
            msgbox.showinfo("信息", "数据已清空，请继续添加！")

        def add():
            valid_data = self.validate_input(add_win, form_data, "vaccine_info")
            if not valid_data:
                return

            sql = """
                INSERT INTO vaccine_info (
                    vaccine_num, vaccine_name, company_name, company_num,
                    size, buy_price, pre_sale_price, limit_up, limit_down
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                valid_data["vaccine_num"], valid_data["vaccine_name"], valid_data["company_name"],
                valid_data["company_num"], valid_data["size"], valid_data["buy_price"],
                valid_data["pre_sale_price"], valid_data["limit_up"], valid_data["limit_down"]
            )

            affected_rows = self.connect_DBS(sql=sql, params=params)
            if affected_rows and affected_rows > 0:
                msgbox.showinfo("成功", "疫苗信息添加成功！")
                clear()

        tk.Button(add_win, text="添加", bg='white', font=("Arial", 9), width=9, command=add).place(x=400, y=360)
        tk.Button(add_win, text="清空", bg='white', font=("Arial", 9), width=9, command=clear).place(x=160, y=360)

if __name__ == "__main__":
    app = VaccineManager()


