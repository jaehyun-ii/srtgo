# SRTGo GUI 실행 파일 빌드 가이드

## 개요

SRTGo GUI를 Windows용 exe 파일로 빌드하는 방법을 설명합니다.

## 사전 요구사항

### 1. Python 환경
- Python 3.10 이상
- tkinter 모듈 (GUI용)

### 2. 필요한 패키지 설치
```bash
# 기본 의존성 설치
pip install -e .

# 빌드 도구 설치
pip install pyinstaller

# 또는 옵션 의존성으로 설치
pip install -e .[build]
```

### 3. tkinter 설치 (Linux의 경우)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Fedora
sudo dnf install python3-tkinter
```

## 빌드 방법

### 방법 1: 자동 빌드 스크립트 사용
```bash
python build_exe.py
```

이 스크립트는:
- 의존성을 자동으로 확인
- 이전 빌드 결과물을 정리
- PyInstaller로 실행 파일 빌드
- 빌드 결과를 보고

### 방법 2: PyInstaller 직접 사용
```bash
# spec 파일 사용
pyinstaller build_gui.spec

# 또는 간단한 명령어
pyinstaller --onefile --windowed --name=SRTGo-GUI srtgo/gui.py
```

### 방법 3: 수동 빌드
```bash
# 1. spec 파일 생성
pyi-makespec --onefile --windowed --name=SRTGo-GUI srtgo/gui.py

# 2. spec 파일 수정 (필요시)
# 생성된 SRTGo-GUI.spec 파일을 편집

# 3. 빌드 실행
pyinstaller SRTGo-GUI.spec
```

## 빌드 옵션 설명

### PyInstaller 주요 옵션
- `--onefile`: 단일 실행 파일 생성
- `--windowed`: GUI 모드 (콘솔 창 숨김)
- `--noconsole`: 콘솔 창 완전히 숨김
- `--icon=icon.ico`: 아이콘 파일 지정
- `--add-data`: 추가 데이터 파일 포함

### spec 파일 커스터마이징
`build_gui.spec` 파일에서:
- `hiddenimports`: 숨겨진 import 모듈 지정
- `datas`: 포함할 데이터 파일
- `excludes`: 제외할 모듈
- `console=False`: GUI 모드 설정

## 결과물

빌드가 성공하면:
- `dist/SRTGo-GUI.exe`: 실행 파일 생성
- `build/`: 빌드 임시 파일들
- 파일 크기: 약 50-100MB

## 실행 방법

### Windows에서
1. `dist/SRTGo-GUI.exe` 더블클릭
2. 또는 명령어: `SRTGo-GUI.exe`

### 배포시 주의사항
- 실행 파일은 독립적으로 실행 가능
- Python 설치 불필요
- Windows Defender 등 백신에서 차단될 수 있음

## 트러블슈팅

### 일반적인 문제들

#### 1. ModuleNotFoundError
```
해결방법: spec 파일의 hiddenimports에 누락된 모듈 추가
```

#### 2. tkinter 관련 오류
```
해결방법: 
- Windows: Python 재설치 (tkinter 포함)
- Linux: python3-tk 패키지 설치
```

#### 3. 키링(keyring) 오류
```
해결방법: spec 파일에 keyring 백엔드 모듈들 추가
hiddenimports에 포함:
- keyring.backends.Windows
- keyring.backends.macOS
- keyring.backends.SecretService
```

#### 4. 파일 크기가 너무 큼
```
해결방법:
- --exclude-module로 불필요한 모듈 제외
- UPX 압축 사용 (--upx-dir)
```

#### 5. 실행 속도가 느림
```
원인: 실행 파일이 임시 디렉토리에 압축 해제하는 시간
해결방법: --onedir 옵션 사용 (여러 파일로 배포)
```

## 고급 설정

### 아이콘 추가
1. .ico 파일 준비
2. spec 파일에서 `icon='path/to/icon.ico'` 설정

### 버전 정보 추가
```python
# spec 파일에 추가
version_file = 'version.txt'
exe = EXE(...
    version='version.txt',
    ...
)
```

### 디지털 서명 (Windows)
```bash
# 서명 도구 사용
signtool sign /f certificate.pfx /p password SRTGo-GUI.exe
```

## 자동화된 빌드 (CI/CD)

### GitHub Actions 예시
```yaml
name: Build GUI
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -e .[build]
    - name: Build exe
      run: python build_exe.py
    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: SRTGo-GUI
        path: dist/SRTGo-GUI.exe
```

이 가이드를 따라하면 SRTGo GUI를 독립 실행 가능한 exe 파일로 만들 수 있습니다.