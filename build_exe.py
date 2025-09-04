#!/usr/bin/env python3
"""
SRTGo GUI 실행 파일 빌드 스크립트

사용법:
    python build_exe.py

빌드된 exe 파일은 dist/SRTGo-GUI.exe에 생성됩니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """필요한 의존성 확인"""
    try:
        import subprocess
        result = subprocess.run(['/home/jaegu/.local/bin/pyinstaller', '--version'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PyInstaller 설치됨")
        else:
            raise ImportError
    except (ImportError, FileNotFoundError):
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install pyinstaller")
        return False
    
    try:
        import tkinter
        print("✓ tkinter 사용 가능")
    except ImportError:
        print("❌ tkinter가 설치되지 않았습니다.")
        print("GUI를 위해 tkinter가 필요합니다.")
        if sys.platform.startswith('linux'):
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("CentOS/RHEL: sudo yum install tkinter")
        return False
    
    # srtgo 모듈 확인
    try:
        from srtgo import gui
        print("✓ srtgo 모듈 사용 가능")
    except ImportError:
        print("❌ srtgo 모듈을 찾을 수 없습니다.")
        print("현재 디렉토리에서 실행하거나 패키지를 설치하세요.")
        return False
    
    return True


def clean_build():
    """이전 빌드 결과물 정리"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 {dir_name} 디렉토리 정리 중...")
            shutil.rmtree(dir_name)


def build_exe():
    """PyInstaller로 실행 파일 빌드"""
    print("🔨 GUI 실행 파일 빌드 시작...")
    
    # PyInstaller 실행 - spec 파일 사용 시에는 spec 파일만 지정
    cmd = [
        '/home/jaegu/.local/bin/pyinstaller',
        'build_gui.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 빌드 성공!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        print(f"에러 출력: {e.stderr}")
        return False


def create_simple_spec():
    """간단한 spec 파일 생성 (build_gui.spec가 없는 경우)"""
    if not os.path.exists('build_gui.spec'):
        print("📝 간단한 spec 파일 생성...")
        
        # 간단한 PyInstaller 명령어로 대체
        cmd = [
            '/home/jaegu/.local/bin/pyinstaller',
            '--onefile',
            '--windowed',
            '--name=SRTGo-GUI',
            'srtgo/gui.py'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 간단 빌드 실패: {e}")
            return False
    
    return True


def main():
    """메인 함수"""
    print("🚄 SRTGo GUI 실행 파일 빌더")
    print("=" * 40)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 이전 빌드 정리
    clean_build()
    
    # 실행 파일 빌드
    success = False
    
    if os.path.exists('build_gui.spec'):
        print("📋 spec 파일을 사용하여 빌드...")
        success = build_exe()
    else:
        print("📋 spec 파일이 없습니다. 간단 빌드 시도...")
        success = create_simple_spec()
    
    if success:
        exe_path = Path('dist/SRTGo-GUI.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"🎉 빌드 완료!")
            print(f"📁 실행 파일 위치: {exe_path.absolute()}")
            print(f"📏 파일 크기: {size_mb:.1f} MB")
            
            # 실행 방법 안내
            print("\n실행 방법:")
            print(f"  - Windows: {exe_path.absolute()}")
            print(f"  - 또는 dist 폴더의 SRTGo-GUI.exe 더블클릭")
            
        else:
            print("❌ 실행 파일이 생성되지 않았습니다.")
            print("dist 폴더를 확인해보세요.")
    else:
        print("❌ 빌드에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()