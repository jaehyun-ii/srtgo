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
        
        # Configure fonts with Korean support
        import sys
        if sys.platform.startswith('win'):
            # Windows Korean fonts
            default_font = ('Malgun Gothic', 9)
            title_font = ('Malgun Gothic', 16, 'bold')
            heading_font = ('Malgun Gothic', 12, 'bold')
        else:
            # Linux/macOS fonts
            default_font = ('Sans', 9)
            title_font = ('Sans', 16, 'bold') 
            heading_font = ('Sans', 12, 'bold')
        
        # Configure colors and fonts
        style.configure('Title.TLabel', font=title_font)
        style.configure('Heading.TLabel', font=heading_font)
        style.configure('Success.TLabel', foreground='green', font=default_font)
        style.configure('Error.TLabel', foreground='red', font=default_font)
        
        # Set default font for all widgets
        self.root.option_add('*Font', default_font)
        
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
        messagebox.showinfo("안내", "예매 기능은 CLI 버전에서 사용하세요.\n이 GUI는 설정 관리용입니다.")
        
    def check_reservations(self):
        messagebox.showinfo("안내", "예매 확인은 CLI 버전에서 사용하세요.\n이 GUI는 설정 관리용입니다.")
        
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


def main():
    app = SRTGoGUI()
    app.run()


if __name__ == "__main__":
    main()