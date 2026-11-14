# Scrollfold

이 프로젝트는 `small-app-harness` 스킬의 공통 규칙을 따른다. 아래는 이 프로젝트에만 해당하는 내용이다.
개인 정보(계정, 로컬 경로)는 `CLAUDE.local.md`, 진행 상태는 `PROGRESS.md`에 있다 (둘 다 gitignore).
이 파일은 공개 저장소에 올라가도 괜찮은 내용만 쓴다.

## 무엇인가

이미지 하나를 X 여러 장 게시물용 세로 띠 N개(기본 20, 최대 20)로 자르고, 게시물에서 어떻게 이어져 보일지 미리 보여 주는 크로스플랫폼 데스크톱 앱.

## 명령 (Windows 기준, macOS/Linux는 `.venv/bin/python`)

| 할 일 | 명령 |
|---|---|
| 환경 | `uv venv --python 3.14 .venv` → `uv pip install --python .venv\Scripts\python.exe -r requirements.txt` |
| 테스트 | `.venv\Scripts\python.exe -X utf8 test_core.py` |
| 소스로 실행 | `.venv\Scripts\python.exe app.py [이미지]` |
| 로컬 웹 모드 | `.venv\Scripts\python.exe server.py` → http://127.0.0.1:8765/ |
| 웹 로직 테스트 | `node --test web/split.test.mjs` |
| 포맷·크기·비율 매트릭스 | `.venv\Scripts\python.exe -X utf8 tools/format_matrix.py [--heavy]` (60개, --heavy는 62개·RAM 2GB) |
| 샘플 다시 만들기 | `.venv\Scripts\python.exe -X utf8 tools/make_samples.py` |
| 샘플 일괄 분할 (output/ 밖으로) | `.venv\Scripts\python.exe -X utf8 tools/split_samples.py <빈 폴더>` |
| UI 테스트 (데스크톱·문구) | `.venv\Scripts\python.exe -X utf8 test_app.py`, `test_i18n.py`, `node --test web/i18n.test.mjs` |
| 웹 UI 셀프 테스트 (브라우저) | `.venv\Scripts\python.exe -X utf8 tools/web_selftest.py [--static]` → 제목이 PASS n/n |
| 서버 테스트 | `.venv\Scripts\python.exe -X utf8 test_server.py` |
| 아이콘 다시 만들기 | `.venv\Scripts\python.exe -X utf8 tools/make_icon.py` → `web/icon.png`, `icon.ico` (`web/icon.svg`와 같은 그림) |
| 웹 최소 배포 파일 | `web/`의 index.html, app.css, app.js, split.js, i18n.js, icon.svg, icon.png. `file://`로는 ES 모듈이 막히므로 HTTP로 제공 |
| 빌드 (선택, Windows만) | `build.bat` → `dist\Scrollfold.exe` — 기본 사용·시험 경로가 아님 |

## 데이터

- 결과: 앱 옆 `output/<입력 파일 이름>/01.png …` (gitignore). 쓰기 불가면 OS별 사용자 데이터 폴더의 `Scrollfold/output`.

## 이 프로젝트의 불변 조건

- `core.py`는 tkinter를 import하지 않는다. 외부 패키지는 Pillow 하나뿐이다.
- `web/split.js`는 `core.py`와 같은 계산을 한다. 한쪽을 바꾸면 다른 쪽과 두 테스트를 같이 바꾼다.
- 웹은 외부 스크립트·폰트·CDN 없이 동작한다 (CSP `default-src 'self'`). 이미지는 업로드하지 않는다.
- `server.py`는 127.0.0.1에만 바인딩하고, 쓰기는 토큰 헤더 + Host 검사를 통과해야 한다. 파일 이름은 `NN.png|jpg`만 받는다.
- 기존 출력 폴더는 절대 덮어쓰지 않는다 (`name_2`, `name_3` …).
- 모든 조각은 같은 너비다. 남는 픽셀은 양 끝에서 고르게 잘라 낸다.
- X 최적화 결과는 긴 변 4096px 이하, 5MB 이하 JPEG다 (`test_core.Optimize`).
- OS 전용 호출은 `core.open_in_file_manager`와 `app.enable_high_dpi`에만 둔다. 전역 설정·레지스트리는 건드리지 않는다.

## UI 에셋 (아이콘, 폰트, 이미지)

- 상업적 이용이 가능한 오픈소스만 쓴다 (MIT, Apache-2.0, OFL-1.1, CC0, CC BY 등). NC·ND·개인용 한정·라이선스 불명은 금지.
- 쓸 때마다 반드시 크레딧을 남긴다: THIRD-PARTY-NOTICES.md와 앱 안 크레딧 화면(데스크톱·웹 모두). CC0라도 남긴다.
- 에셋은 라이선스 파일과 함께 저장소에 넣고, 실행 중 CDN에서 불러오지 않는다.
- **외부에서 가져다 쓴 것(의존성, 폰트, 도구, 문서, 참고 게시물, 이미지, 수치)은 전부 `reference.md` 맨 위 색인 표에 라이선스와 함께 남긴다.** 새로 들어오면 그때 행을 추가한다. 라이선스 없는 남의 코드(비슷한 분할 사이트 등)는 복사하지 않는다.

## 문서

- 사용자 문서는 영어가 기본이고 한국어판을 함께 둔다: `X.md` + `X.ko.md`, 맨 위에 언어 전환 링크. 한쪽을 고치면 다른 쪽도 고친다.
- UI는 시스템 언어(OS·브라우저)를 따라 시작한다.

## 하지 말 것

- X에 직접 업로드하는 기능을 넣지 않는다 (API·약관).
- 저작권이 있는 이미지를 `samples/`나 문서 이미지로 넣지 않는다. 직접 만든 것이나 퍼블릭 도메인만.
