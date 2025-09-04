import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
import keyring
import asyncio
# Import only necessary functions to avoid inquirer conflicts in GUI
try:
    from .srtgo import (
        get_station, get_options, STATIONS, DEFAULT_STATIONS
    )
    # Import classes directly to avoid inquirer
    from .srt import SRT
    from .ktx import Korail
except ImportError:
    from srtgo.srtgo import (
        get_station, get_options, STATIONS, DEFAULT_STATIONS
    )
    from srtgo.srt import SRT
    from srtgo.ktx import Korail


class SRTGoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SRTGo - 기차표 예약 프로그램")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.rail_type = tk.StringVar(value="SRT")
        self.debug_mode = tk.BooleanVar(value=False)
        
        # Style configuration
        self.setup_styles()
        
        # Create main interface
        self.create_main_interface()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        
    def create_main_interface(self):
        # Main title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(title_frame, text="SRTGo - 기차표 예약 프로그램", 
                 style='Title.TLabel').pack()
        
        # Rail type selection
        rail_frame = ttk.LabelFrame(self.root, text="열차 선택", padding=10)
        rail_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Radiobutton(rail_frame, text="SRT", variable=self.rail_type, 
                       value="SRT").pack(side='left', padx=10)
        ttk.Radiobutton(rail_frame, text="KTX", variable=self.rail_type, 
                       value="KTX").pack(side='left', padx=10)
        
        # Debug mode
        ttk.Checkbutton(rail_frame, text="디버그 모드", 
                       variable=self.debug_mode).pack(side='right')
        
        # Main menu buttons
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left column - Main functions
        left_frame = ttk.LabelFrame(menu_frame, text="주요 기능", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Button(left_frame, text="예매 시작", 
                  command=self.start_reservation).pack(fill='x', pady=5)
        ttk.Button(left_frame, text="예매 확인/결제/취소", 
                  command=self.check_reservations).pack(fill='x', pady=5)
        
        # Right column - Settings
        right_frame = ttk.LabelFrame(menu_frame, text="설정", padding=10)
        right_frame.pack(side='right', fill='both', expand=True)
        
        ttk.Button(right_frame, text="로그인 설정", 
                  command=self.setup_login).pack(fill='x', pady=2)
        ttk.Button(right_frame, text="카카오톡 알림 설정", 
                  command=self.setup_kakao).pack(fill='x', pady=2)
        ttk.Button(right_frame, text="역 설정", 
                  command=self.setup_stations).pack(fill='x', pady=2)
        ttk.Button(right_frame, text="예매 옵션 설정", 
                  command=self.setup_options).pack(fill='x', pady=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x', padx=5, pady=5)
        
    def start_reservation(self):
        ReservationWindow(self.root, self.rail_type.get(), self.debug_mode.get())
        
    def check_reservations(self):
        ReservationCheckWindow(self.root, self.rail_type.get(), self.debug_mode.get())
        
    def setup_login(self):
        LoginSetupWindow(self.root, self.rail_type.get(), self.debug_mode.get())
        
    def setup_kakao(self):
        KakaoSetupWindow(self.root)
        
    def setup_stations(self):
        StationSetupWindow(self.root, self.rail_type.get())
        
    def setup_options(self):
        OptionsSetupWindow(self.root)
        
    def run(self):
        self.root.mainloop()


class ReservationWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"{rail_type} 예매")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        self.create_interface()
        
    def create_interface(self):
        # Get default values
        now = datetime.now() + timedelta(minutes=10)
        today = now.strftime("%Y%m%d")
        this_time = now.strftime("%H%M%S")
        
        is_srt = self.rail_type == "SRT"
        
        defaults = {
            "departure": keyring.get_password(self.rail_type, "departure") or ("수서" if is_srt else "서울"),
            "arrival": keyring.get_password(self.rail_type, "arrival") or "동대구",
            "date": keyring.get_password(self.rail_type, "date") or today,
            "time": keyring.get_password(self.rail_type, "time") or "120000",
            "adult": int(keyring.get_password(self.rail_type, "adult") or 1),
            "child": int(keyring.get_password(self.rail_type, "child") or 0),
            "senior": int(keyring.get_password(self.rail_type, "senior") or 0),
            "disability1to3": int(keyring.get_password(self.rail_type, "disability1to3") or 0),
            "disability4to6": int(keyring.get_password(self.rail_type, "disability4to6") or 0),
        }
        
        # Station selection
        station_frame = ttk.LabelFrame(self.window, text="역 선택", padding=10)
        station_frame.pack(fill='x', padx=10, pady=5)
        
        stations, station_keys = get_station(self.rail_type)
        
        ttk.Label(station_frame, text="출발역:").grid(row=0, column=0, sticky='w', padx=5)
        self.departure_var = tk.StringVar(value=defaults["departure"])
        departure_combo = ttk.Combobox(station_frame, textvariable=self.departure_var, 
                                     values=station_keys, width=15)
        departure_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(station_frame, text="도착역:").grid(row=0, column=2, sticky='w', padx=5)
        self.arrival_var = tk.StringVar(value=defaults["arrival"])
        arrival_combo = ttk.Combobox(station_frame, textvariable=self.arrival_var, 
                                   values=station_keys, width=15)
        arrival_combo.grid(row=0, column=3, padx=5, pady=2)
        
        # Date and time selection
        datetime_frame = ttk.LabelFrame(self.window, text="날짜/시간 선택", padding=10)
        datetime_frame.pack(fill='x', padx=10, pady=5)
        
        # Date selection
        ttk.Label(datetime_frame, text="출발 날짜:").grid(row=0, column=0, sticky='w', padx=5)
        self.date_var = tk.StringVar()
        date_combo = ttk.Combobox(datetime_frame, textvariable=self.date_var, width=15)
        
        # Generate date choices
        date_choices = []
        for i in range(28):
            date_obj = now + timedelta(days=i)
            date_str = date_obj.strftime("%Y/%m/%d %a")
            date_val = date_obj.strftime("%Y%m%d")
            date_choices.append(f"{date_val} ({date_str})")
        
        date_combo['values'] = date_choices
        default_date_display = f"{defaults['date']} ({datetime.strptime(defaults['date'], '%Y%m%d').strftime('%Y/%m/%d %a')})"
        self.date_var.set(default_date_display)
        date_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Time selection
        ttk.Label(datetime_frame, text="출발 시각:").grid(row=1, column=0, sticky='w', padx=5)
        self.time_var = tk.StringVar(value=defaults["time"][:2])
        time_combo = ttk.Combobox(datetime_frame, textvariable=self.time_var, width=15)
        time_combo['values'] = [f"{h:02d}:00" for h in range(24)]
        time_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Passenger selection
        passenger_frame = ttk.LabelFrame(self.window, text="승객 선택", padding=10)
        passenger_frame.pack(fill='x', padx=10, pady=5)
        
        # Adult passengers (always shown)
        ttk.Label(passenger_frame, text="성인:").grid(row=0, column=0, sticky='w', padx=5)
        self.adult_var = tk.IntVar(value=defaults["adult"])
        adult_spin = ttk.Spinbox(passenger_frame, from_=0, to=9, textvariable=self.adult_var, width=5)
        adult_spin.grid(row=0, column=1, padx=5, pady=2)
        
        # Optional passengers based on settings
        options = get_options()
        row = 1
        
        self.child_var = tk.IntVar(value=defaults["child"])
        self.senior_var = tk.IntVar(value=defaults["senior"])
        self.disability1to3_var = tk.IntVar(value=defaults["disability1to3"])
        self.disability4to6_var = tk.IntVar(value=defaults["disability4to6"])
        
        if "child" in options:
            ttk.Label(passenger_frame, text="어린이:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Spinbox(passenger_frame, from_=0, to=9, textvariable=self.child_var, width=5).grid(row=row, column=1, padx=5, pady=2)
            row += 1
            
        if "senior" in options:
            ttk.Label(passenger_frame, text="경로우대:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Spinbox(passenger_frame, from_=0, to=9, textvariable=self.senior_var, width=5).grid(row=row, column=1, padx=5, pady=2)
            row += 1
            
        if "disability1to3" in options:
            ttk.Label(passenger_frame, text="중증장애인:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Spinbox(passenger_frame, from_=0, to=9, textvariable=self.disability1to3_var, width=5).grid(row=row, column=1, padx=5, pady=2)
            row += 1
            
        if "disability4to6" in options:
            ttk.Label(passenger_frame, text="경증장애인:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Spinbox(passenger_frame, from_=0, to=9, textvariable=self.disability4to6_var, width=5).grid(row=row, column=1, padx=5, pady=2)
        
        # Seat type selection
        seat_frame = ttk.LabelFrame(self.window, text="좌석 선택", padding=10)
        seat_frame.pack(fill='x', padx=10, pady=5)
        
        self.seat_type_var = tk.StringVar(value="일반실 우선")
        seat_types = ["일반실 우선", "일반실만", "특실 우선", "특실만"]
        for i, seat_type in enumerate(seat_types):
            ttk.Radiobutton(seat_frame, text=seat_type, variable=self.seat_type_var, 
                          value=seat_type).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
        
        
        # Control buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="예매 시작", 
                  command=self.start_booking).pack(side='left', padx=5)
        ttk.Button(button_frame, text="취소", 
                  command=self.window.destroy).pack(side='right', padx=5)
        
        # Status display
        self.status_text = tk.Text(self.window, height=8, wrap='word')
        self.status_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
    def start_booking(self):
        # Validate input
        if self.departure_var.get() == self.arrival_var.get():
            messagebox.showerror("오류", "출발역과 도착역이 같습니다.")
            return
            
        total_passengers = (self.adult_var.get() + self.child_var.get() + 
                          self.senior_var.get() + self.disability1to3_var.get() + 
                          self.disability4to6_var.get())
        
        if total_passengers == 0:
            messagebox.showerror("오류", "승객수는 0이 될 수 없습니다.")
            return
            
        if total_passengers >= 10:
            messagebox.showerror("오류", "승객수는 10명을 초과할 수 없습니다.")
            return
        
        # Save preferences
        keyring.set_password(self.rail_type, "departure", self.departure_var.get())
        keyring.set_password(self.rail_type, "arrival", self.arrival_var.get())
        
        # Extract date from combo selection
        date_val = self.date_var.get().split(' ')[0]
        keyring.set_password(self.rail_type, "date", date_val)
        
        # Convert time
        time_val = self.time_var.get().replace(':', '') + "00"
        keyring.set_password(self.rail_type, "time", time_val)
        
        keyring.set_password(self.rail_type, "adult", str(self.adult_var.get()))
        keyring.set_password(self.rail_type, "child", str(self.child_var.get()))
        keyring.set_password(self.rail_type, "senior", str(self.senior_var.get()))
        keyring.set_password(self.rail_type, "disability1to3", str(self.disability1to3_var.get()))
        keyring.set_password(self.rail_type, "disability4to6", str(self.disability4to6_var.get()))
        
        # Start reservation in separate thread
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "예매를 시작합니다...\n")
        
        thread = threading.Thread(target=self.run_reservation)
        thread.daemon = True
        thread.start()
        
    def run_reservation(self):
        try:
            # This would integrate with the existing reserve function
            # For now, we'll show a placeholder
            self.update_status("예매 시스템에 연결 중...")
            # Here you would call the actual reserve function
            # reserve(self.rail_type, self.debug)
            
        except Exception as e:
            self.update_status(f"오류 발생: {str(e)}")
            
    def update_status(self, message):
        def update():
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
        
        self.window.after(0, update)


class LoginSetupWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"{rail_type} 로그인 설정")
        self.window.geometry("400x200")
        
        self.create_interface()
        
    def create_interface(self):
        # Get existing credentials
        current_id = keyring.get_password(self.rail_type, "id") or ""
        
        # Input fields
        ttk.Label(self.window, text=f"{self.rail_type} 계정 정보", 
                 style='Heading.TLabel').pack(pady=10)
        
        input_frame = ttk.Frame(self.window)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="아이디:").grid(row=0, column=0, sticky='w', pady=5)
        self.id_var = tk.StringVar(value=current_id)
        ttk.Entry(input_frame, textvariable=self.id_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="비밀번호:").grid(row=1, column=0, sticky='w', pady=5)
        self.pass_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.pass_var, show='*', width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save_login).pack(side='left', padx=10)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side='left', padx=10)
        
    def save_login(self):
        if not self.id_var.get() or not self.pass_var.get():
            messagebox.showerror("오류", "아이디와 비밀번호를 모두 입력하세요.")
            return
            
        try:
            # Test login - use already imported classes
            rail = SRT if self.rail_type == "SRT" else Korail
            test_rail = rail(self.id_var.get(), self.pass_var.get(), verbose=self.debug)
            
            # Save credentials
            keyring.set_password(self.rail_type, "id", self.id_var.get())
            keyring.set_password(self.rail_type, "pass", self.pass_var.get())
            keyring.set_password(self.rail_type, "ok", "1")
            
            messagebox.showinfo("성공", "로그인 정보가 저장되었습니다.")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"로그인 실패: {str(e)}")


class KakaoSetupWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("카카오톡 설정")
        self.window.geometry("500x200")
        
        self.create_interface()
        
    def create_interface(self):
        current_key = keyring.get_password("kakao", "rest_api_key") or ""
        
        ttk.Label(self.window, text="카카오톡 나에게 보내기 설정", 
                 style='Heading.TLabel').pack(pady=10)
        
        input_frame = ttk.Frame(self.window)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="REST API Key:").grid(row=0, column=0, sticky='w', pady=5)
        self.api_key_var = tk.StringVar(value=current_key)
        ttk.Entry(input_frame, textvariable=self.api_key_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        # Instructions
        instructions = tk.Text(self.window, height=6, wrap='word')
        instructions.pack(fill='x', padx=20, pady=10)
        
        instruction_text = """카카오 개발자 앱 생성 방법:
1. https://developers.kakao.com에서 앱을 생성합니다
2. 앱 설정 > 플랫폼에서 Web 플랫폼을 추가합니다
3. 앱 키의 REST API 키를 복사해서 위에 입력하세요"""
        
        instructions.insert(tk.END, instruction_text)
        instructions.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="저장 및 인증", command=self.save_and_auth).pack(side='left', padx=10)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side='left', padx=10)
        
    def save_and_auth(self):
        if not self.api_key_var.get():
            messagebox.showerror("오류", "REST API 키를 입력하세요.")
            return
            
        try:
            # Save API key and trigger authentication process
            keyring.set_password("kakao", "rest_api_key", self.api_key_var.get())
            
            # Call the existing set_kakao function from srtgo module
            try:
                from .srtgo import set_kakao
            except ImportError:
                from srtgo.srtgo import set_kakao
            if set_kakao():
                messagebox.showinfo("성공", "카카오톡 알림 설정이 완료되었습니다!")
                self.window.destroy()
            else:
                messagebox.showerror("실패", "카카오톡 인증에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 실패: {str(e)}")


class StationSetupWindow:
    def __init__(self, parent, rail_type):
        self.rail_type = rail_type
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"{rail_type} 역 설정")
        self.window.geometry("400x500")
        
        self.create_interface()
        
    def create_interface(self):
        ttk.Label(self.window, text=f"{self.rail_type} 역 선택", 
                 style='Heading.TLabel').pack(pady=10)
        
        # Station listbox with checkboxes
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Get current station selection
        stations, selected_stations = get_station(self.rail_type)
        
        self.station_vars = {}
        
        # Create scrollable frame
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add checkboxes for each station
        for station in stations:
            var = tk.BooleanVar(value=station in selected_stations)
            self.station_vars[station] = var
            ttk.Checkbutton(scrollable_frame, text=station, variable=var).pack(anchor='w', pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="전체 선택", command=self.select_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="전체 해제", command=self.deselect_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="저장", command=self.save_stations).pack(side='left', padx=10)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side='left', padx=5)
        
    def select_all(self):
        for var in self.station_vars.values():
            var.set(True)
            
    def deselect_all(self):
        for var in self.station_vars.values():
            var.set(False)
            
    def save_stations(self):
        selected = [station for station, var in self.station_vars.items() if var.get()]
        
        if not selected:
            messagebox.showerror("오류", "최소 하나의 역을 선택하세요.")
            return
            
        try:
            keyring.set_password(self.rail_type, "station", ",".join(selected))
            messagebox.showinfo("성공", f"선택된 역: {', '.join(selected)}")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")


class OptionsSetupWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("예매 옵션 설정")
        self.window.geometry("300x250")
        
        self.create_interface()
        
    def create_interface(self):
        ttk.Label(self.window, text="예매 옵션 선택", 
                 style='Heading.TLabel').pack(pady=10)
        
        option_frame = ttk.Frame(self.window)
        option_frame.pack(fill='x', padx=20, pady=10)
        
        current_options = get_options()
        
        self.child_var = tk.BooleanVar(value="child" in current_options)
        ttk.Checkbutton(option_frame, text="어린이", variable=self.child_var).pack(anchor='w', pady=5)
        
        self.senior_var = tk.BooleanVar(value="senior" in current_options)
        ttk.Checkbutton(option_frame, text="경로우대", variable=self.senior_var).pack(anchor='w', pady=5)
        
        self.disability1to3_var = tk.BooleanVar(value="disability1to3" in current_options)
        ttk.Checkbutton(option_frame, text="중증장애인", variable=self.disability1to3_var).pack(anchor='w', pady=5)
        
        self.disability4to6_var = tk.BooleanVar(value="disability4to6" in current_options)
        ttk.Checkbutton(option_frame, text="경증장애인", variable=self.disability4to6_var).pack(anchor='w', pady=5)
        
        self.ktx_var = tk.BooleanVar(value="ktx" in current_options)
        ttk.Checkbutton(option_frame, text="KTX만", variable=self.ktx_var).pack(anchor='w', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save_options).pack(side='left', padx=10)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side='left', padx=10)
        
    def save_options(self):
        options = []
        if self.child_var.get():
            options.append("child")
        if self.senior_var.get():
            options.append("senior")
        if self.disability1to3_var.get():
            options.append("disability1to3")
        if self.disability4to6_var.get():
            options.append("disability4to6")
        if self.ktx_var.get():
            options.append("ktx")
            
        try:
            keyring.set_password("SRT", "options", ",".join(options))
            messagebox.showinfo("성공", "예매 옵션이 저장되었습니다.")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")


class ReservationCheckWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"{rail_type} 예매 확인")
        self.window.geometry("600x400")
        
        self.create_interface()
        self.load_reservations()
        
    def create_interface(self):
        ttk.Label(self.window, text="예매 내역", 
                 style='Heading.TLabel').pack(pady=10)
        
        # Reservation list
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview for reservations
        columns = ('Status', 'Train', 'Route', 'Date', 'Time')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="새로고침", command=self.load_reservations).pack(side='left', padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel_reservation).pack(side='left', padx=5)
        ttk.Button(button_frame, text="닫기", command=self.window.destroy).pack(side='left', padx=5)
        
    def load_reservations(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # This would integrate with the existing check_reservation function
            # For now, show placeholder data
            self.tree.insert('', 'end', values=('예약완료', 'SRT', '수서→부산', '2024-01-01', '10:00'))
            self.tree.insert('', 'end', values=('결제대기', 'KTX', '서울→대구', '2024-01-02', '14:30'))
            
        except Exception as e:
            messagebox.showerror("오류", f"예매 내역 조회 실패: {str(e)}")
            
    def cancel_reservation(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("경고", "취소할 예매를 선택하세요.")
            return
            
        if messagebox.askyesno("확인", "선택한 예매를 취소하시겠습니까?"):
            # Implement cancellation logic here
            messagebox.showinfo("안내", "취소 기능은 콘솔 버전에서 사용하세요.")


def main():
    app = SRTGoGUI()
    app.run()


if __name__ == "__main__":
    main()