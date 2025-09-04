#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRTGo GUI - Standalone version without CLI dependencies
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import keyring
try:
    # Test keyring functionality
    keyring.get_password("test", "test")
except keyring.errors.NoKeyringError:
    # Fallback to file-based storage for environments without keyring
    import os
    import json
    
    class FileKeyring:
        def __init__(self):
            self.config_dir = os.path.expanduser("~/.srtgo")
            self.config_file = os.path.join(self.config_dir, "config.json")
            os.makedirs(self.config_dir, exist_ok=True)
            
        def _load_config(self):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
                
        def _save_config(self, config):
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        def get_password(self, service, username):
            config = self._load_config()
            return config.get(f"{service}:{username}")
            
        def set_password(self, service, username, password):
            config = self._load_config()
            config[f"{service}:{username}"] = password
            self._save_config(config)
            
        def delete_password(self, service, username):
            config = self._load_config()
            key = f"{service}:{username}"
            if key in config:
                del config[key]
                self._save_config(config)
    
    # Replace keyring with file-based implementation
    keyring = FileKeyring()
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from srtgo.srt import SRT
from srtgo.ktx import Korail


STATIONS = {
    "SRT": [
        "수서", "동탄", "평택지제", "경주", "곡성", "공주", "광주송정", "구례구",
        "김천(구미)", "나주", "남원", "대전", "동대구", "마산", "목포", "밀양",
        "부산", "서대구", "순천", "여수EXPO", "여천", "오송", "울산(통도사)",
        "익산", "전주", "정읍", "진영", "진주", "창원", "창원중앙", "천안아산", "포항"
    ],
    "KTX": [
        "서울", "용산", "영등포", "광명", "수원", "천안아산", "오송", "대전",
        "서대전", "김천구미", "동대구", "경주", "포항", "밀양", "구포", "부산",
        "울산(통도사)", "마산", "창원중앙", "경산", "논산", "익산", "정읍",
        "광주송정", "목포", "전주", "순천", "여수EXPO", "청량리", "강릉", "행신", "정동진"
    ]
}

DEFAULT_STATIONS = {
    "SRT": ["수서", "대전", "동대구", "부산"],
    "KTX": ["서울", "대전", "동대구", "부산"]
}


def get_station(rail_type):
    """Get available stations for rail type"""
    stations = STATIONS[rail_type]
    station_key = keyring.get_password(rail_type, "station")
    
    if not station_key:
        return stations, DEFAULT_STATIONS[rail_type]
    
    valid_keys = [x for x in station_key.split(",")]
    return stations, valid_keys


def get_options():
    """Get passenger options"""
    options = keyring.get_password("SRT", "options") or ""
    return options.split(",") if options else []


class SRTGoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚅 SRTGo - 기차표 예약 프로그램")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Center window on screen
        self.center_window()
        
        # Variables
        self.rail_type = tk.StringVar(value="SRT")
        self.debug_mode = tk.BooleanVar(value=False)
        
        # Style configuration
        self.setup_styles()
        
        # Create main interface
        self.create_main_interface()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure fonts with Korean support
        import sys
        if sys.platform.startswith('win'):
            # Windows Korean fonts
            default_font = ('Malgun Gothic', 10)
            title_font = ('Malgun Gothic', 20, 'bold')
            heading_font = ('Malgun Gothic', 14, 'bold')
            button_font = ('Malgun Gothic', 11)
        else:
            # Linux/macOS fonts
            default_font = ('Sans', 10)
            title_font = ('Sans', 20, 'bold') 
            heading_font = ('Sans', 14, 'bold')
            button_font = ('Sans', 11)
        
        # Color scheme
        primary_color = '#2E86AB'    # Blue
        secondary_color = '#A23B72'  # Purple  
        success_color = '#F18F01'    # Orange
        danger_color = '#C73E1D'     # Red
        bg_color = '#F5F5F5'         # Light gray
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=title_font, 
                       foreground=primary_color,
                       background='white')
        
        style.configure('Heading.TLabel', 
                       font=heading_font, 
                       foreground='#333333')
        
        style.configure('Success.TLabel', 
                       foreground=success_color, 
                       font=(default_font[0], 11, 'bold'))
        
        style.configure('Error.TLabel', 
                       foreground=danger_color, 
                       font=(default_font[0], 11, 'bold'))
        
        # Button styles
        style.configure('Primary.TButton',
                       font=button_font,
                       foreground='white',
                       background=primary_color,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Primary.TButton',
                 background=[('active', '#1E5F7A'),
                            ('pressed', '#154A61')])
        
        style.configure('Secondary.TButton',
                       font=button_font,
                       foreground='white', 
                       background=secondary_color,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Secondary.TButton',
                 background=[('active', '#8B2F5A'),
                            ('pressed', '#6B2346')])
        
        # Frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='raised',
                       borderwidth=1)
        
        style.configure('Primary.TLabelFrame',
                       background='white',
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Primary.TLabelFrame.Label',
                       font=heading_font,
                       foreground=primary_color,
                       background='white')
        
        # Set default font and colors
        self.root.option_add('*Font', default_font)
        self.root.configure(bg=bg_color)
        
    def create_main_interface(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header section with title and subtitle
        header_frame = ttk.Frame(main_container, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_content = ttk.Frame(header_frame)
        header_content.pack(fill='x', padx=30, pady=25)
        
        # Title with icon
        title_label = ttk.Label(header_content, 
                               text="🚅 SRTGo", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_content, 
                                  text="기차표 예약 프로그램 설정 도구", 
                                  font=('Malgun Gothic' if self.root.tk.call('tk', 'windowingsystem') == 'win32' else 'Sans', 12))
        subtitle_label.pack(pady=(5, 0))
        
        # Rail type selection card
        rail_card = ttk.LabelFrame(main_container, 
                                  text="🚂 열차 선택", 
                                  style='Primary.TLabelFrame',
                                  padding=20)
        rail_card.pack(fill='x', pady=(0, 20))
        
        rail_buttons_frame = ttk.Frame(rail_card)
        rail_buttons_frame.pack(fill='x')
        
        # SRT/KTX selection with better styling
        srt_frame = ttk.Frame(rail_buttons_frame)
        srt_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Radiobutton(srt_frame, 
                       text="🚄 SRT (수서고속철도)", 
                       variable=self.rail_type, 
                       value="SRT",
                       style='TRadiobutton').pack(anchor='w', pady=5)
        
        ktx_frame = ttk.Frame(rail_buttons_frame) 
        ktx_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        ttk.Radiobutton(ktx_frame, 
                       text="🚅 KTX (한국고속철도)", 
                       variable=self.rail_type, 
                       value="KTX",
                       style='TRadiobutton').pack(anchor='w', pady=5)
        
        # Debug mode (smaller, less prominent)
        debug_frame = ttk.Frame(rail_card)
        debug_frame.pack(fill='x', pady=(15, 0))
        ttk.Checkbutton(debug_frame, 
                       text="🔧 디버그 모드 (고급 사용자용)", 
                       variable=self.debug_mode).pack(anchor='w')
        
        # Main content area with cards
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill='both', expand=True)
        
        # Settings card
        settings_card = ttk.LabelFrame(content_frame,
                                     text="⚙️ 설정 관리",
                                     style='Primary.TLabelFrame',
                                     padding=25)
        settings_card.pack(fill='both', expand=True)
        
        # Settings grid
        settings_grid = ttk.Frame(settings_card)
        settings_grid.pack(fill='both', expand=True)
        
        # Row 0: Reservation (most prominent)
        reservation_frame = ttk.Frame(settings_grid)
        reservation_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(reservation_frame, 
                  text="🎫 기차표 예매하기",
                  style='Primary.TButton',
                  command=self.start_reservation).pack(side='left', padx=(0, 10))
        
        reservation_desc = ttk.Label(reservation_frame, 
                              text="실시간 기차표 예매 및 예약 확인",
                              foreground='#666666')
        reservation_desc.pack(side='left', anchor='w')
        
        # Separator
        separator = ttk.Separator(settings_grid, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Settings header
        settings_header = ttk.Label(settings_grid,
                                   text="⚙️ 계정 및 환경 설정",
                                   style='Heading.TLabel')
        settings_header.pack(anchor='w', pady=(10, 15))
        
        # Row 1: Login settings
        login_frame = ttk.Frame(settings_grid)
        login_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(login_frame, 
                  text="🔐 로그인 설정",
                  style='Secondary.TButton',
                  command=self.setup_login).pack(side='left', padx=(0, 10))
        
        login_desc = ttk.Label(login_frame, 
                              text="SRT/KTX 계정 정보를 설정합니다",
                              foreground='#666666')
        login_desc.pack(side='left', anchor='w')
        
        # Row 2: Station settings  
        station_frame = ttk.Frame(settings_grid)
        station_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(station_frame,
                  text="🚉 역 설정", 
                  style='Secondary.TButton',
                  command=self.setup_stations).pack(side='left', padx=(0, 10))
        
        station_desc = ttk.Label(station_frame,
                               text="예매할 출발/도착 역을 선택합니다",
                               foreground='#666666')
        station_desc.pack(side='left', anchor='w')
        
        # Row 3: Options settings
        options_frame = ttk.Frame(settings_grid) 
        options_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(options_frame,
                  text="🎫 예매 옵션 설정",
                  style='Secondary.TButton', 
                  command=self.setup_options).pack(side='left', padx=(0, 10))
        
        options_desc = ttk.Label(options_frame,
                               text="승객 유형 및 기타 옵션을 설정합니다",
                               foreground='#666666')
        options_desc.pack(side='left', anchor='w')
        
        # Quick actions
        quick_frame = ttk.Frame(settings_card)
        quick_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(quick_frame,
                  text="📋 예매 확인/취소",
                  command=self.check_reservations).pack(side='left', padx=(0, 10))
        
        # Notice section
        notice_frame = ttk.Frame(settings_card)
        notice_frame.pack(fill='x', pady=(15, 0))
        
        notice_label = ttk.Label(notice_frame,
                               text="💡 GUI에서 편리하게 예매하거나 CLI 명령어 'srtgo'를 사용하세요",
                               style='Success.TLabel')
        notice_label.pack(anchor='w')
        
        # Status bar with better styling
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x', padx=30, pady=(10, 20))
        
        self.status_var = tk.StringVar(value="✅ 준비 완료")
        status_bar = ttk.Label(status_frame, 
                              textvariable=self.status_var,
                              style='Success.TLabel',
                              anchor='w')
        status_bar.pack(side='left')
        
        # Version info
        version_label = ttk.Label(status_frame,
                                text="v2.0.0",
                                foreground='#999999',
                                anchor='e')
        version_label.pack(side='right')
        
    def start_reservation(self):
        # Check if login is configured
        rail_type = self.rail_type.get()
        if not keyring.get_password(rail_type, "id"):
            messagebox.showwarning("로그인 필요", 
                                 f"{rail_type} 로그인 정보가 설정되지 않았습니다.\n먼저 로그인 설정을 완료해주세요.")
            self.setup_login()
            return
            
        ReservationWindow(self.root, rail_type, self.debug_mode.get())
        
    def check_reservations(self):
        # Check if login is configured
        rail_type = self.rail_type.get()
        if not keyring.get_password(rail_type, "id"):
            messagebox.showwarning("로그인 필요", 
                                 f"{rail_type} 로그인 정보가 설정되지 않았습니다.\n먼저 로그인 설정을 완료해주세요.")
            self.setup_login()
            return
            
        ReservationCheckWindow(self.root, rail_type, self.debug_mode.get())
        
    def setup_login(self):
        LoginSetupWindow(self.root, self.rail_type.get(), self.debug_mode.get())
        
    def setup_stations(self):
        StationSetupWindow(self.root, self.rail_type.get())
        
    def setup_options(self):
        OptionsSetupWindow(self.root)
        
    def run(self):
        self.root.mainloop()


class LoginSetupWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"🔐 {rail_type} 로그인 설정")
        self.window.geometry("450x280")
        self.window.resizable(False, False)
        self.window.grab_set()  # Modal dialog
        
        # Center the window
        self.center_window()
        
        self.create_interface()
        
    def center_window(self):
        """Center the window on parent"""
        self.window.update_idletasks()
        parent_x = self.window.master.winfo_x()
        parent_y = self.window.master.winfo_y()
        parent_width = self.window.master.winfo_width()
        parent_height = self.window.master.winfo_height()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def create_interface(self):
        # Get existing credentials
        current_id = keyring.get_password(self.rail_type, "id") or ""
        
        # Main container with padding
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        rail_icon = "🚄" if self.rail_type == "SRT" else "🚅"
        ttk.Label(header_frame, 
                 text=f"{rail_icon} {self.rail_type} 로그인 설정", 
                 style='Heading.TLabel').pack()
        
        ttk.Label(header_frame,
                 text="계정 정보를 입력하여 자동 로그인을 설정하세요",
                 foreground='#666666').pack(pady=(5, 0))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="계정 정보", padding=15)
        input_frame.pack(fill='x', pady=(0, 20))
        
        # ID field
        id_frame = ttk.Frame(input_frame)
        id_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(id_frame, text="아이디:", width=12).pack(side='left')
        self.id_var = tk.StringVar(value=current_id)
        id_entry = ttk.Entry(id_frame, textvariable=self.id_var, width=25)
        id_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Help text for ID
        ttk.Label(input_frame, 
                 text="멤버십 번호, 이메일 주소 또는 전화번호",
                 foreground='#999999',
                 font=('Malgun Gothic' if self.window.tk.call('tk', 'windowingsystem') == 'win32' else 'Sans', 9)).pack(anchor='w', pady=(0, 10))
        
        # Password field  
        pass_frame = ttk.Frame(input_frame)
        pass_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(pass_frame, text="비밀번호:", width=12).pack(side='left')
        self.pass_var = tk.StringVar()
        pass_entry = ttk.Entry(pass_frame, textvariable=self.pass_var, show='*', width=25)
        pass_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Security note
        security_frame = ttk.Frame(main_frame)
        security_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(security_frame,
                 text="🔒 비밀번호는 안전하게 암호화되어 저장됩니다",
                 foreground='#2E86AB',
                 font=('Malgun Gothic' if self.window.tk.call('tk', 'windowingsystem') == 'win32' else 'Sans', 9)).pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, 
                  text="💾 저장", 
                  style='Primary.TButton',
                  command=self.save_login).pack(side='right', padx=(10, 0))
        
        ttk.Button(button_frame, 
                  text="취소",
                  command=self.window.destroy).pack(side='right')
        
        # Focus on appropriate field
        if current_id:
            pass_entry.focus_set()
        else:
            id_entry.focus_set()
        
    def save_login(self):
        if not self.id_var.get() or not self.pass_var.get():
            messagebox.showerror("오류", "아이디와 비밀번호를 모두 입력하세요.")
            return
            
        try:
            # Test login
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


class ReservationWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"🎫 {rail_type} 기차표 예매")
        self.window.geometry("600x800")
        self.window.resizable(False, False)
        self.window.grab_set()
        
        # Center the window
        self.center_window()
        
        # Initialize variables
        self.setup_variables()
        
        self.create_interface()
        
    def center_window(self):
        """Center the window on parent"""
        self.window.update_idletasks()
        parent_x = self.window.master.winfo_x()
        parent_y = self.window.master.winfo_y()
        parent_width = self.window.master.winfo_width()
        parent_height = self.window.master.winfo_height()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def setup_variables(self):
        """Initialize form variables with saved values"""
        from datetime import datetime, timedelta
        
        now = datetime.now() + timedelta(minutes=10)
        today = now.strftime("%Y%m%d")
        
        is_srt = self.rail_type == "SRT"
        default_departure = "수서" if is_srt else "서울"
        
        # Get saved values or defaults
        self.departure_var = tk.StringVar(value=keyring.get_password(self.rail_type, "departure") or default_departure)
        self.arrival_var = tk.StringVar(value=keyring.get_password(self.rail_type, "arrival") or "동대구")
        self.date_var = tk.StringVar(value=keyring.get_password(self.rail_type, "date") or today)
        self.time_var = tk.StringVar(value=keyring.get_password(self.rail_type, "time") or "120000")
        
        # Passenger counts
        self.adult_var = tk.IntVar(value=int(keyring.get_password(self.rail_type, "adult") or 1))
        self.child_var = tk.IntVar(value=int(keyring.get_password(self.rail_type, "child") or 0))
        self.senior_var = tk.IntVar(value=int(keyring.get_password(self.rail_type, "senior") or 0))
        self.disability1to3_var = tk.IntVar(value=int(keyring.get_password(self.rail_type, "disability1to3") or 0))
        self.disability4to6_var = tk.IntVar(value=int(keyring.get_password(self.rail_type, "disability4to6") or 0))
        
        # Seat preference
        self.seat_type_var = tk.StringVar(value="일반실 우선")
        self.auto_pay_var = tk.BooleanVar(value=False)
        
        # Status
        self.is_running = False
        
    def create_interface(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        rail_icon = "🚄" if self.rail_type == "SRT" else "🚅"
        ttk.Label(header_frame, 
                 text=f"{rail_icon} {self.rail_type} 기차표 예매", 
                 style='Title.TLabel').pack()
        
        # Route selection
        route_frame = ttk.LabelFrame(main_frame, text="🚉 여행 경로", padding=15)
        route_frame.pack(fill='x', pady=(0, 15))
        
        route_grid = ttk.Frame(route_frame)
        route_grid.pack(fill='x')
        
        # Departure station
        dep_frame = ttk.Frame(route_grid)
        dep_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Label(dep_frame, text="출발역").pack(anchor='w')
        stations, selected_stations = get_station(self.rail_type)
        dep_combo = ttk.Combobox(dep_frame, textvariable=self.departure_var, values=selected_stations, width=15)
        dep_combo.pack(fill='x', pady=(5, 0))
        
        # Arrow
        ttk.Label(route_grid, text="→", font=('Sans', 16)).pack(side='left', padx=10)
        
        # Arrival station
        arr_frame = ttk.Frame(route_grid)
        arr_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        ttk.Label(arr_frame, text="도착역").pack(anchor='w')
        arr_combo = ttk.Combobox(arr_frame, textvariable=self.arrival_var, values=selected_stations, width=15)
        arr_combo.pack(fill='x', pady=(5, 0))
        
        # Date and time
        datetime_frame = ttk.LabelFrame(main_frame, text="📅 출발 일시", padding=15)
        datetime_frame.pack(fill='x', pady=(0, 15))
        
        dt_grid = ttk.Frame(datetime_frame)
        dt_grid.pack(fill='x')
        
        # Date
        date_frame = ttk.Frame(dt_grid)
        date_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Label(date_frame, text="출발 날짜").pack(anchor='w')
        
        # Generate date choices
        from datetime import datetime, timedelta
        now = datetime.now()
        date_choices = []
        for i in range(30):
            date_obj = now + timedelta(days=i)
            date_str = date_obj.strftime("%Y-%m-%d (%a)")
            date_val = date_obj.strftime("%Y%m%d")
            date_choices.append((date_str, date_val))
        
        date_combo = ttk.Combobox(date_frame, values=[choice[0] for choice in date_choices], width=18)
        date_combo.pack(fill='x', pady=(5, 0))
        
        # Set current date
        current_date = self.date_var.get()
        for i, (display, value) in enumerate(date_choices):
            if value == current_date:
                date_combo.set(display)
                break
        else:
            date_combo.set(date_choices[0][0])
            
        # Update date_var when selection changes
        def on_date_change(event):
            selected_display = date_combo.get()
            for display, value in date_choices:
                if display == selected_display:
                    self.date_var.set(value)
                    break
        date_combo.bind('<<ComboboxSelected>>', on_date_change)
        
        # Time
        time_frame = ttk.Frame(dt_grid)
        time_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        ttk.Label(time_frame, text="출발 시각").pack(anchor='w')
        time_choices = [f"{h:02d}:00" for h in range(6, 24)]  # 06:00 ~ 23:00
        time_combo = ttk.Combobox(time_frame, values=time_choices, width=10)
        time_combo.pack(fill='x', pady=(5, 0))
        
        # Set current time
        current_time = self.time_var.get()
        current_hour = current_time[:2] if len(current_time) >= 2 else "12"
        time_display = f"{current_hour}:00"
        time_combo.set(time_display)
        
        # Update time_var when selection changes
        def on_time_change(event):
            selected_time = time_combo.get()
            hour = selected_time.split(':')[0]
            self.time_var.set(f"{hour}0000")
        time_combo.bind('<<ComboboxSelected>>', on_time_change)
        
        # Passengers
        passengers_frame = ttk.LabelFrame(main_frame, text="👥 승객 정보", padding=15)
        passengers_frame.pack(fill='x', pady=(0, 15))
        
        # Adult (always shown)
        adult_frame = ttk.Frame(passengers_frame)
        adult_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(adult_frame, text="성인:", width=12).pack(side='left')
        ttk.Spinbox(adult_frame, from_=1, to=9, textvariable=self.adult_var, width=5).pack(side='left', padx=(5, 0))
        
        # Optional passenger types based on options
        options = get_options()
        
        if "child" in options:
            child_frame = ttk.Frame(passengers_frame)
            child_frame.pack(fill='x', pady=(0, 5))
            ttk.Label(child_frame, text="어린이:", width=12).pack(side='left')
            ttk.Spinbox(child_frame, from_=0, to=9, textvariable=self.child_var, width=5).pack(side='left', padx=(5, 0))
        
        if "senior" in options:
            senior_frame = ttk.Frame(passengers_frame)  
            senior_frame.pack(fill='x', pady=(0, 5))
            ttk.Label(senior_frame, text="경로우대:", width=12).pack(side='left')
            ttk.Spinbox(senior_frame, from_=0, to=9, textvariable=self.senior_var, width=5).pack(side='left', padx=(5, 0))
        
        # Seat preferences
        seat_frame = ttk.LabelFrame(main_frame, text="💺 좌석 선택", padding=15)
        seat_frame.pack(fill='x', pady=(0, 15))
        
        seat_types = ["일반실 우선", "일반실만", "특실 우선", "특실만"]
        for i, seat_type in enumerate(seat_types):
            ttk.Radiobutton(seat_frame, text=seat_type, variable=self.seat_type_var, 
                          value=seat_type).pack(anchor='w', pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 예매 옵션", padding=15)
        options_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Checkbutton(options_frame, text="💳 예매 성공 시 자동 결제", 
                       variable=self.auto_pay_var).pack(anchor='w')
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="📊 예매 진행 상태", padding=15)
        status_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.status_text = tk.Text(status_frame, height=8, wrap='word', state='disabled',
                                  font=('Consolas' if self.window.tk.call('tk', 'windowingsystem') == 'win32' else 'Monospace', 9))
        self.status_text.pack(fill='both', expand=True)
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        self.start_button = ttk.Button(button_frame, 
                                      text="🚀 예매 시작", 
                                      style='Primary.TButton',
                                      command=self.start_booking)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, 
                                     text="⏹️ 중지",
                                     state='disabled',
                                     command=self.stop_booking)
        self.stop_button.pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="닫기",
                  command=self.window.destroy).pack(side='right')
        
    def log_message(self, message):
        """Add message to status display"""
        def update():
            self.status_text.configure(state='normal')
            self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} {message}\n")
            self.status_text.configure(state='disabled')
            self.status_text.see(tk.END)
        
        self.window.after(0, update)
        
    def start_booking(self):
        """Start the reservation process"""
        # Validate inputs
        if self.departure_var.get() == self.arrival_var.get():
            messagebox.showerror("입력 오류", "출발역과 도착역이 같습니다.")
            return
            
        total_passengers = (self.adult_var.get() + self.child_var.get() + 
                          self.senior_var.get() + self.disability1to3_var.get() + 
                          self.disability4to6_var.get())
        
        if total_passengers == 0:
            messagebox.showerror("입력 오류", "승객수는 0이 될 수 없습니다.")
            return
            
        if total_passengers >= 10:
            messagebox.showerror("입력 오류", "승객수는 10명을 초과할 수 없습니다.")
            return
        
        # Save current settings
        self.save_settings()
        
        # Update UI state
        self.is_running = True
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        
        # Clear status
        self.status_text.configure(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state='disabled')
        
        self.log_message("🚀 예매를 시작합니다...")
        self.log_message(f"🚄 {self.rail_type}: {self.departure_var.get()} → {self.arrival_var.get()}")
        self.log_message(f"👥 승객: 성인 {self.adult_var.get()}명")
        
        # Start reservation in separate thread
        import threading
        thread = threading.Thread(target=self.run_reservation, daemon=True)
        thread.start()
        
    def stop_booking(self):
        """Stop the reservation process"""
        self.is_running = False
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        self.log_message("⏹️ 예매가 중지되었습니다.")
        
    def save_settings(self):
        """Save current form values"""
        keyring.set_password(self.rail_type, "departure", self.departure_var.get())
        keyring.set_password(self.rail_type, "arrival", self.arrival_var.get())
        keyring.set_password(self.rail_type, "date", self.date_var.get())
        keyring.set_password(self.rail_type, "time", self.time_var.get())
        keyring.set_password(self.rail_type, "adult", str(self.adult_var.get()))
        keyring.set_password(self.rail_type, "child", str(self.child_var.get()))
        keyring.set_password(self.rail_type, "senior", str(self.senior_var.get()))
        keyring.set_password(self.rail_type, "disability1to3", str(self.disability1to3_var.get()))
        keyring.set_password(self.rail_type, "disability4to6", str(self.disability4to6_var.get()))
        
    def run_reservation(self):
        """Run the actual reservation logic (simplified version)"""
        try:
            # Get login credentials
            user_id = keyring.get_password(self.rail_type, "id")
            password = keyring.get_password(self.rail_type, "pass")
            
            if not user_id or not password:
                self.log_message("❌ 로그인 정보를 찾을 수 없습니다.")
                self.stop_booking()
                return
            
            self.log_message("🔐 로그인 중...")
            
            # Login
            rail_class = SRT if self.rail_type == "SRT" else Korail
            rail = rail_class(user_id, password, verbose=self.debug)
            
            self.log_message("✅ 로그인 성공!")
            
            # This is a simplified version - you would need to implement the full
            # reservation logic here similar to the CLI version
            self.log_message("🔍 열차 검색 중...")
            self.log_message("💡 실제 예매 기능은 CLI 버전에서 완전히 구현됩니다.")
            self.log_message("💡 현재 GUI는 데모 버전입니다.")
            
            # Simulate some processing time
            import time
            time.sleep(2)
            
            if self.is_running:
                self.log_message("🎫 예매 기능 구현 예정 - CLI 버전을 사용해주세요!")
                
        except Exception as e:
            self.log_message(f"❌ 오류 발생: {str(e)}")
            
        finally:
            if self.is_running:
                self.window.after(0, self.stop_booking)


class ReservationCheckWindow:
    def __init__(self, parent, rail_type, debug):
        self.rail_type = rail_type
        self.debug = debug
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"📋 {rail_type} 예매 확인")
        self.window.geometry("700x500")
        self.window.resizable(True, True)
        self.window.grab_set()
        
        # Center the window
        self.center_window()
        
        self.create_interface()
        self.load_reservations()
        
    def center_window(self):
        """Center the window on parent"""
        self.window.update_idletasks()
        parent_x = self.window.master.winfo_x()
        parent_y = self.window.master.winfo_y()
        parent_width = self.window.master.winfo_width()
        parent_height = self.window.master.winfo_height()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def create_interface(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        rail_icon = "🚄" if self.rail_type == "SRT" else "🚅"
        ttk.Label(header_frame, 
                 text=f"📋 {rail_icon} {self.rail_type} 예매 내역", 
                 style='Title.TLabel').pack()
        
        # Reservations list
        list_frame = ttk.LabelFrame(main_frame, text="예매 내역", padding=15)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Treeview for reservations
        columns = ('상태', '열차', '구간', '날짜', '시간', '좌석')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {'상태': 80, '열차': 80, '구간': 120, '날짜': 100, '시간': 80, '좌석': 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        self.tree.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, 
                  text="🔄 새로고침", 
                  command=self.load_reservations).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="💳 결제하기",
                  command=self.pay_reservation).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="❌ 취소하기",
                  command=self.cancel_reservation).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="닫기",
                  command=self.window.destroy).pack(side='right')
        
    def load_reservations(self):
        """Load reservation list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Get login credentials
            user_id = keyring.get_password(self.rail_type, "id")
            password = keyring.get_password(self.rail_type, "pass")
            
            if not user_id or not password:
                messagebox.showerror("로그인 오류", "로그인 정보를 찾을 수 없습니다.")
                return
            
            # Login and get reservations
            rail_class = SRT if self.rail_type == "SRT" else Korail
            rail = rail_class(user_id, password, verbose=self.debug)
            
            # This is a placeholder - implement actual reservation retrieval
            self.tree.insert('', 'end', values=('예약완료', 'SRT-101', '수서→부산', '2024-12-25', '10:00', '1A-2'))
            self.tree.insert('', 'end', values=('결제대기', 'KTX-201', '서울→대구', '2024-12-26', '14:30', '2B-1'))
            
            messagebox.showinfo("안내", "💡 실제 예매 내역 조회는 CLI 버전에서 완전히 구현됩니다.\n현재는 데모 데이터를 표시합니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"예매 내역 조회 실패: {str(e)}")
            
    def pay_reservation(self):
        """Pay for selected reservation"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "결제할 예매를 선택하세요.")
            return
            
        messagebox.showinfo("안내", "💳 결제 기능은 CLI 버전에서 구현됩니다.")
            
    def cancel_reservation(self):
        """Cancel selected reservation"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "취소할 예매를 선택하세요.")
            return
            
        if messagebox.askyesno("확인", "선택한 예매를 정말 취소하시겠습니까?"):
            messagebox.showinfo("안내", "❌ 취소 기능은 CLI 버전에서 구현됩니다.")


def main():
    app = SRTGoGUI()
    app.run()


if __name__ == "__main__":
    main()