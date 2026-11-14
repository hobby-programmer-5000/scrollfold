[English](README.md) | **한국어**

# Scrollfold

가로로 긴 이미지 하나를 X(트위터) 여러 장 게시물용 세로 띠 최대 20개로 자르고, 올리기 전에 어떻게 이어져 보일지 미리 보여 주는 앱입니다.

## 만든 이유

X가 게시물 하나에 사진 20장을 허용하면서 그림 한 장을 20조각으로 잘라 올리는 게 유행했습니다. 손으로 자르기는 번거롭고, 올리기 전에는 결과를 볼 수 없었습니다.

## 기능

- 조각 수 1~20. **자동**을 누르면 고른 조각 비율에 가장 잘 맞는 조각 수를 정합니다.
- **조각 비율**은 실제 X 게시물을 측정해 고른 프리셋입니다([reference.ko.md](reference.ko.md)): **1:2**(기본, 가장 큰 카드), 9:16, 3:4, 1:1, **1:12**(얇은 띠), 원본.
- **비율이 안 맞으면**: 자르기(가운데를 남기고, 남는 비율을 상태 줄에 표시) 또는 흐린 배경·검정·흰색 여백 채우기. 그림을 늘리지는 않습니다.
- 스크롤되는 두 칸: 빨간 분할선이 그려진 원본, 그리고 틈을 두고 나란히 놓은 조각들. 배율: 맞춤, 10~200%.
- **X 게시물 최적화**: 각 조각을 긴 변 4096px 이하, 5MB 이하 JPEG로 만듭니다. 끄면 무손실 PNG.
- 결과는 `output/<입력 파일 이름>/01.png …`에 저장합니다. 기존 폴더는 덮어쓰지 않습니다 (`이름_2`, `이름_3` …).
- "결과 폴더 열기"로 탐색기, Finder, 리눅스 파일 관리자에서 바로 엽니다.
- 명확한 안내: 파일을 고르기 전에 지원 포맷을 보여 주고, 문제(지원 안 함, 빈 파일, 너무 큼, 너무 좁음)마다 해결 방법이 담긴 메시지를 화면 안에 보여 줍니다. 저장 중에는 "조각 3/20"처럼 진행을 보여 주고 취소(버튼 또는 Esc)할 수 있으며, 이미 만든 조각은 남겨 둡니다.
- 영어/한국어 UI. 처음에는 시스템(OS·브라우저) 언어를 따르고, 버튼으로 바꿀 수 있습니다. 단축키: Ctrl+O 열기, Ctrl+S 분할·저장, Ctrl+E 폴더 열기. 휠은 세로, Shift+휠은 가로 스크롤.

### 샘플 이미지

`samples/`에 바로 넣어 볼 수 있는 입력 이미지가 있습니다. 포맷별, 모양별(비율 프리셋마다 하나), 까다로운 유형별(투명, CMYK, 16비트, EXIF 회전, 움직이는 GIF, 잘못된 파일)로 나눠 두었습니다. [samples/README.ko.md](samples/README.ko.md)를 참고하세요.

### 지원 포맷

| 포맷 | 데스크톱 앱 | 로컬 웹 모드 (`server.py`) | 브라우저 전용 웹 |
|---|:-:|:-:|:-:|
| PNG, JPEG, WebP, GIF(첫 프레임), BMP | ✓ | ✓ | ✓ |
| AVIF, ICO | ✓ | ✓ | ✓ (최신 브라우저) |
| TIFF, TGA, JPEG 2000, QOI, PPM, PCX | ✓ | ✓ (서버가 대신 읽음) | ✗ 브라우저가 못 읽음 |
| HEIC/HEIF(아이폰), RAW, PSD, SVG | ✗ | ✗ | ✗ — JPEG/PNG로 내보낸 뒤 사용 |

모든 모드에서 휴대폰 사진은 EXIF 방향대로 세우고 투명도도 처리합니다. 데스크톱과 로컬 모드는 CMYK, 16비트도 처리합니다.
최적화(JPEG) 결과에서 투명한 부분은 흰색이 됩니다.

### 주의 사항

- **아주 큰 이미지는 쓰지 마세요.** 이미지는 메모리에 압축 없이 올라갑니다(픽셀당 약 4바이트). 여기에 작업용 사본이 더해져서
  1억 픽셀이면 사본 하나에 약 0.4GB입니다. 큰 스캔본은 먼저 줄이세요. X는 조각 하나를 최대 4096px로만 보여 줍니다.
- 움직이는 GIF/WebP는 첫 프레임만 씁니다.
- 자르기는 그림 일부를 버립니다. 남는 비율이 상태 줄에 나옵니다. 여백 모드는 전부 남깁니다.
- 그림을 늘리지는 않습니다.

### 큰 이미지 안전장치 (와 그 한계)

| 안전장치 | 데스크톱 / 로컬 모드 | 브라우저 전용 웹 |
|---|---|---|
| 1억 픽셀 초과 경고 | ✓ 상태 줄 | ✓ 상태 줄 |
| 4억 픽셀 초과 거부 | ✓ 이미지를 풀기 **전에** 파일 헤더로 검사 | ✓ 단, 브라우저가 이미지를 **다 푼 뒤에** 검사 |
| 미리보기 크기 상한 | 긴 변 20,000px | 긴 변 16,000px |
| 디코딩용 업로드 상한 (`/api/decode`) | 300MB | — |
| 결과 크기 | "X 최적화" 시 조각당 4096px·5MB 이하 | 같음 |

이 장치들은 위험을 줄일 뿐 없애지는 못합니다. 메모리 사용량은 컴퓨터 사양, 다른 프로그램, 브라우저에 따라 달라집니다.
4억 픽셀 미만이어도 메모리가 적은 컴퓨터에서는 부족할 수 있고, 브라우저 전용 모드에서는 Scrollfold가 검사하기 전에
브라우저가 먼저 이미지를 풀기 때문에 너무 큰 이미지는 탭을 멈추거나 닫히게 할 수 있습니다.

**사용 책임은 사용자에게 있습니다.** Scrollfold는 MIT 라이선스로 "있는 그대로" 제공되는 오픈소스이며 어떤 보증도 하지 않습니다.
큰 이미지를 열어서 앱, 브라우저, 시스템의 메모리가 부족해지거나 느려지거나 멈추는 일이 생기면 그 책임은 사용자에게 있습니다.
다른 작업은 미리 저장하고, 이미지는 적당한 크기로 쓰세요.

팁: 1:2 조각 20장이면 원본이 10:1 파노라마여야 하고, 1:12면 약 5:3입니다. 세로 사진은 1~4장이 자연스럽습니다.

## 세 가지 사용 방법

| 모드 | 방법 | 결과 위치 |
|---|---|---|
| **웹, 브라우저만** | 정적 호스팅(GitHub Pages 등)에서 `web/index.html` 열기 | `.zip` 다운로드, 크롬 계열은 "폴더에 저장…"도 가능 |
| **웹, 로컬** | `python server.py` → `http://127.0.0.1:8765/`가 열림 | `output/<파일 이름>/`, "결과 폴더 열기" 지원 |
| **데스크톱** | `python app.py` | `output/<파일 이름>/` |

두 웹 모드 모두 이미지는 브라우저 안에서 처리되고 업로드되지 않습니다. 로컬 서버는 127.0.0.1에서만 열리고,
자기 페이지에서 온 요청만 파일을 쓸 수 있습니다(실행마다 바뀌는 토큰, Host 검사).

## 소스로 실행 (Windows, macOS, Linux)

빌드는 필요 없습니다. 프로젝트 폴더에 가상환경을 만들고, 거기에 Pillow를 설치한 뒤 실행하면 됩니다.
시스템 전체에는 아무것도 설치되지 않습니다. Python 3.10 이상이 필요하고, 데스크톱 앱은 Tkinter도 필요합니다.

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py        # 데스크톱
.venv\Scripts\python server.py     # 로컬 웹 모드
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py            # 데스크톱
.venv/bin/python server.py         # 로컬 웹 모드
```

- 리눅스: `import tkinter`가 실패하면 배포판의 Tk 패키지를 설치하세요 (예: `sudo apt install python3-tk`).
- macOS: python.org 설치본에는 Tk가 들어 있습니다. Homebrew Python이면 `brew install python-tk`가 필요할 수 있습니다.
- 브라우저 전용 모드는 Python이 없어도 됩니다. `web/` 폴더를 정적 호스팅에 올리면 됩니다.

### 브라우저 전용 웹: 최소 파일

웹 버전만 올리려면 `web/`에서 다음 7개만 복사하면 됩니다:
`index.html`, `app.css`, `app.js`, `split.js`, `i18n.js`, `icon.svg`, `icon.png`.
테스트 파일(`*.test.mjs`, `selftest.*`)은 필요 없습니다.

`index.html`을 디스크에서 바로(`file://`) 열면 **동작하지 않습니다**. 브라우저가 거기서는 ES 모듈을 막습니다.
HTTP로 제공하세요: 정적 호스팅(GitHub Pages, Netlify 등), `python server.py`, 잠깐 볼 때는
`python -m http.server -d web`.

## 선택: Windows exe

`build.bat`이 테스트를 돌리고 PyInstaller로 `dist\Scrollfold.exe`를 만듭니다. 필수가 아니고 평소 테스트 대상도 아닙니다.
모든 OS에서 기본 사용 방법은 소스로 실행하는 것입니다. exe와 데스크톱 창은 `icon.ico` / `web/icon.png`를 씁니다.
`web/icon.svg`를 바꾸면 `python tools/make_icon.py`로 둘 다 다시 만드세요.

## 프로젝트 구조

```
app.py        데스크톱 UI (Tkinter)
server.py     로컬 웹 모드 (표준 라이브러리만)
core.py       분할, X 최적화, 출력 폴더 (GUI import 없음)
i18n.py       데스크톱 UI 문자열 (en, ko)
web/          웹 UI: index.html, app.css, app.js, split.js(로직), i18n.js, icon.svg, icon.png
samples/      샘플 입력 이미지 (CC0), samples/README.ko.md 참고
test_*.py     Python 테스트: core, 서버, 데스크톱 UI, UI 문구
web/*.test.mjs  Node 테스트: 웹 로직, UI 문구
web/selftest.html  브라우저에서 도는 웹 UI 셀프 테스트 (tools/web_selftest.py)
icon.ico      exe 아이콘 (tools/make_icon.py가 web/icon.svg와 같은 그림으로 생성)
reference.md  참고 자료와 라이선스 (한국어: reference.ko.md)
build.bat     전체 테스트 → 빌드 → 스모크 테스트 (Windows)
tools/        스모크 테스트, 포맷 매트릭스, 샘플·아이콘 생성, 셀프 테스트 실행기
```

## 만든 사람

- hobby-programmer-5000 — 아이디어, 요구사항, X 실사용 테스트
- Claude (Anthropic) — 구현, 테스트, 문서

## 라이선스

- 코드: MIT ([LICENSE](LICENSE)).
- `samples/`의 샘플 이미지: CC0 1.0, 퍼블릭 도메인 — [samples/README.ko.md](samples/README.ko.md) 참고.
- 서드파티 라이선스: [THIRD-PARTY-NOTICES.ko.md](THIRD-PARTY-NOTICES.ko.md).
