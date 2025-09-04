# 백신 프로그램 오탐지 관련 안내

## 문제 상황
PyInstaller로 생성된 실행 파일이 일부 백신 프로그램(Norton, Windows Defender 등)에서 악성코드로 잘못 탐지될 수 있습니다.

## 원인
- **False Positive**: PyInstaller가 Python 런타임을 압축하여 포함시키는 과정에서 발생
- **새로운 파일**: 백신 프로그램이 처음 보는 실행 파일에 대한 보수적 접근
- **동적 로딩**: Python 모듈의 동적 로딩 패턴이 의심스러운 행동으로 인식

## 해결 방법

### 1. 백신 프로그램에서 예외 처리
**Norton의 경우:**
1. Norton 보안 → 설정 → 바이러스 및 스파이웨어 보호
2. 신뢰할 수 있는 파일 → 추가
3. `SRTGo-GUI.exe` 파일 선택

**Windows Defender의 경우:**
1. Windows 보안 → 바이러스 및 위협 방지
2. 설정 관리 → 제외 항목 추가 또는 제거
3. 파일 또는 폴더 제외 → `SRTGo-GUI.exe` 추가

### 2. 소스코드 직접 실행 (권장)
더 안전한 방법으로 Python을 직접 설치하고 소스코드를 실행:

```bash
# Python 설치 후
pip install srtgo
srtgo-gui  # GUI 실행
srtgo      # CLI 실행
```

### 3. 백신 프로그램에 신고
- Norton: "잘못된 탐지 보고" 버튼 클릭
- 해당 파일이 안전하다고 신고하여 데이터베이스 개선에 기여

## 보안 확인 방법

### VirusTotal 검사
1. https://www.virustotal.com 방문
2. 실행 파일 업로드하여 다중 백신 엔진으로 검사
3. 대부분의 엔진에서 깨끗하게 나오는지 확인

### 소스코드 검증
- 모든 소스코드가 GitHub에 공개되어 있음: https://github.com/lapis42/srtgo
- 투명한 빌드 과정: GitHub Actions를 통한 자동 빌드
- 악성 코드가 없음을 직접 확인 가능

## 주의사항
- 신뢰할 수 있는 소스(공식 GitHub Release)에서만 다운로드
- 실행 전 파일 무결성 확인
- 의심스러운 경우 소스코드 직접 실행 권장

## 문의
백신 오탐지 관련 문의는 GitHub Issues에 등록해주세요.