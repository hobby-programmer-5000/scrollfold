[English](reference.md) | **한국어**

# 참고 자료

Scrollfold를 설계하면서 참고한 자료와, 각 자료의 라이선스가 허용하는 범위입니다.
원칙: **아이디어**만 가져옵니다. 코드나 글은 라이선스가 허용할 때만 복사하고, 그때는 여기에 출처를 남깁니다.

## 외부에서 가져온 모든 것 (색인)

이 프로젝트가 쓰거나 참고한 외부 요소 전부와 그 라이선스입니다. 자세한 내용은 아래 절과
THIRD-PARTY-NOTICES.ko.md에 있습니다. 새로 들어오는 것이 있으면 그때 이 표에 한 줄을 추가합니다.

| 무엇 | 어떻게 썼나 | 라이선스 | 위치 |
|---|---|---|---|
| Python + Tkinter (Tcl/Tk) | 실행 환경 | PSF, Tcl/Tk는 BSD 계열 | 저장소에 없음 |
| Pillow | 의존성 (이미지 읽기·쓰기) | MIT-CMU | `requirements.txt`, 저장소에 없음 |
| Aileron Regular 폰트 (dotcolon), Pillow에 내장 | `samples/` 이미지 구석 라벨 글씨 | CC0 | 저장소에 없음 (Pillow 안) |
| PyInstaller | 선택 사항인 Windows exe 빌드, 부트로더가 exe 안에 들어감 | GPL-2.0 + 부트로더 예외 | 저장소에 없음 (`build.bat`) |
| Node.js | 웹 테스트(`web/*.test.mjs`) 실행만 | MIT | 저장소에 없음, 배포물에 없음 |
| uv | 가상환경 생성 (개발 도구) | MIT / Apache-2.0 | 저장소에 없음 |
| UX 가이드: GOV.UK, Microsoft, Carbon, GNOME, NN/g (아래 "UX 가이드" 참고) | 아이디어를 우리 말로 바꿔 씀, 글·코드·에셋 복사 없음 | OGL v3 / CC BY 4.0 / © IBM / © GNOME 저자 / © NN/g | 아래 링크 |
| Chrome Modern Web Guidance | 디자인 지침을 따름, 복사 없음 | CC BY 4.0 (글) / Apache-2.0 (예제 코드) | 아래 링크 |
| Google Design, Interactive Canvas 가이드 | 일반적인 영감 | © Google / CC BY 4.0 | 아래 링크 |
| fotoner/strip-split, virtualbanana877/ImageSegmentation | 아이디어만, 코드는 읽지도 복사하지도 않음 | 없음 (모든 권리 보유) | 아래 링크 |
| X 게시물 15개 | 조각 크기·비율 측정, 내려받거나 저장하지 않음 | © 각 작성자 | 아래 링크 |
| X 이미지 제한 (긴 변 4096px, 사진당 5MB, 게시물당 20장) | 최적화 목표값 | 사실 정보, 측정한 게시물과 X 공지 기준 | `core.py` |
| 청명상하도 (청원본, 1736) | 첫 수동 테스트에만 사용 | 퍼블릭 도메인 | 저장소에 없음 |

이 프로젝트가 직접 만든 것(외부 아님): 앱 코드(MIT), 아이콘(`web/icon.svg`, 직접 그림. `web/icon.png`와 `icon.ico`는 `tools/make_icon.py`가 같은 도형으로 그림), 샘플 이미지(CC0).

## 비슷한 분할 사이트

| 사이트 | 저장소 | 라이선스 | 쓸 수 있는 범위 |
|---|---|---|---|
| 사진 세로 분할 (Photo Strip Splitter) — https://fotoner.github.io/strip-split/ | github.com/fotoner/strip-split (`index.html`, `og.png`) | **없음** (LICENSE 파일 없음, GitHub API도 라이선스 없음, 2026-11-14 확인) | 아이디어만. 기본 저작권 상태라 코드·글·이미지 복사 금지 |
| ImageSegmentation — https://virtualbanana877.github.io/ImageSegmentation/ (저장소 이름으로 추정한 주소, 열어 보지 않음) | github.com/virtualbanana877/ImageSegmentation (`index.html`) | **없음** (같은 방법으로 확인) | 아이디어만. 복사 금지 |

두 사이트의 코드는 읽지 않았으므로 Scrollfold는 독립적으로 작성했습니다.

## 디자인·웹 가이드

| 출처 | 라이선스 (페이지 하단에서 확인 필요) | 쓰는 방식 |
|---|---|---|
| Chrome — Modern Web Guidance: https://developer.chrome.com/docs/modern-web-guidance/guides?hl=ko | Google 개발자 문서는 보통 글은 CC BY 4.0, 예제 코드는 Apache-2.0 | 지침을 따름. 예제 코드를 복사하면 Apache-2.0 고지를 남기고 여기에 출처 기록 |
| Google Design: https://design.google/ | 글은 © Google, 재사용 라이선스 없음 | 영감만 (명세가 아니라 글 목록) |
| Interactive Canvas 디자인 가이드: https://developers.google.com/assistant/interactivecanvas/design?hl=ko | 위 Google 개발자 문서와 같음 | 일반 원칙만 (어시스턴트·스마트 디스플레이용) |

쓰지 않는 것: Google 로고나 제품 이름을 브랜딩에 쓰는 것.

## 스톡 에셋 규칙 (아이콘, 폰트, 이미지, 소리)

- **상업적 이용이 가능한** 오픈소스만 씁니다: MIT, Apache-2.0, OFL-1.1, CC0, CC BY 등.
  금지: CC BY-NC / ND, "개인 용도만 무료", 라이선스가 불분명하거나 없는 것.
- 모든 에셋은 **반드시 크레딧**을 남깁니다: 이름, 만든 사람, 출처 URL, 라이선스를 THIRD-PARTY-NOTICES와
  앱 안 크레딧 화면(데스크톱·웹)에 적습니다. CC0처럼 표기가 필요 없는 라이선스라도 남깁니다.
- 에셋은 라이선스 파일과 함께 저장소에 넣고, 실행 중에 CDN에서 불러오지 않습니다.

### 가져온 원칙

- 시스템의 라이트·다크 모드를 따르고, 스크롤바와 입력 요소도 맞추며, 고대비·강제 색상 모드를 존중합니다.
- 고정 구간 대신 유동 크기(rem, `clamp()`), Grid/Flexbox, 컨테이너 쿼리를 써서 폰부터 데스크톱, 세로·가로 화면까지 대응합니다.
- 스크롤 칸은 내용이 더 있는 쪽에만 흐림이나 그림자를 보여 줍니다.
- 긴 파일 이름은 한 줄에서 말줄임합니다.
- 마우스, 터치, 키보드로 같은 기능을 쓸 수 있고 포커스가 보입니다.
- 오류는 사용자가 행동한 뒤에, 예측 가능한 한 곳에 나옵니다.
- 무거운 작업(분할, 내보내기)은 작게 나눠서 페이지가 멈추지 않게 합니다.
- 이미지는 브라우저 안에서만 처리하고, 파일 이름은 텍스트로 넣으며(`innerHTML` 안 씀), 콘텐츠 보안 정책(CSP)을 둡니다.
- UI는 깔끔하게: 컨트롤은 적게, 작은 화면에서 중요한 컨트롤을 맨 아래에 두지 않습니다.

## UX 가이드 (2026-11-14 확인)

아이디어만 우리 말로 바꿔 쓰고, 글·코드·아이콘 등 에셋은 복사하지 않습니다.
"라이선스"는 각 사이트 글의 라이선스로, 페이지·하단·원본 저장소에서 확인했습니다.

| 출처 | 글의 라이선스 | 쓸 수 있는 범위 |
|---|---|---|
| GOV.UK 디자인 시스템, 파일 업로드 — https://design-system.service.gov.uk/components/file-upload/ | Open Government Licence v3.0, © Crown copyright (사이트 하단) | 출처를 밝히면 글도 재사용 가능, 여기서는 아이디어만 |
| Microsoft, Windows 앱 디자인 — https://learn.microsoft.com/en-us/windows/apps/design/ | CC BY 4.0 (원본 저장소 MicrosoftDocs/windows-dev-docs, GitHub API: CC-BY-4.0) | 출처를 밝히면 재사용 가능, 여기서는 아이디어만 |
| IBM Carbon, 파일 업로더 사용법 — https://carbondesignsystem.com/components/file-uploader/usage/ | 문서: "Copyright © 2026 IBM", 공개 라이선스 없음. Carbon *코드*는 Apache-2.0 | 아이디어만 |
| GNOME HIG, 진행 표시줄 / 대화상자 — https://developer.gnome.org/hig/patterns/feedback/progress-bars.html, https://developer.gnome.org/hig/patterns/feedback/dialogs.html | 라이선스를 찾지 못함 (저장소 Teams/Websites/developer.gnome.org-hig에는 파일별 저자 표기만, "© 2021 Allan Day") → 모든 권리 보유로 취급 | 아이디어만 |
| Nielsen Norman Group, 사용성 휴리스틱 10가지 — https://www.nngroup.com/articles/ten-usability-heuristics/ | "Copyright © Jakob Nielsen", 모든 권리 보유. 출처와 링크를 밝히면 인용 가능 | 아이디어만, 출처 표기 |
| Material Design 3, 진행 표시기 — https://m3.material.io/components/progress-indicators/guidelines | 확인 못 함 (JavaScript 없이는 페이지가 열리지 않음) | 쓰지 않음 |
| Apple Human Interface Guidelines | © Apple, 모든 권리 보유. 디자인 리소스는 Apple 플랫폼 시안용으로만 허용 | 쓰지 않음 |

### 가져온 아이디어

- 파일을 고르기 전에, 놓는 곳 옆에 지원 포맷과 크기 상한을 보여 줍니다. (GOV.UK)
- 실패마다 구체적인 오류 하나: 지원 안 하는 포맷(목록 제시), 너무 큼(상한 제시), 너무 좁음, 빈 파일·깨진 파일. 해결 방법도 알려 줍니다. (GOV.UK, Carbon, NN/g 9번)
- 드래그 앤 드롭 옆에 진짜 "파일 선택" 버튼을 둡니다. 드래그 앤 드롭만으로는 부족합니다. (GOV.UK)
- 파일 선택 창을 연 버튼으로 포커스를 돌려줍니다. 긴 파일 이름은 말줄임하고 마우스를 올리면 전체를 보여 줍니다. (Carbon)
- 작업 옆에 단위가 있는 진행 표시("조각 3/20")를 두고, 오래 걸리는 작업에는 취소를 제공합니다. (GNOME, NN/g 1·3번)
- 확인 대화상자보다 되돌리기를 선호하고, 오류 팝업 대신 화면 안에 오류를 보여 줍니다. (GNOME)
- 화면마다 주요 버튼은 하나, 같은 이미지를 다시 고르지 않고 설정만 바꿔 다시 자를 수 있게 합니다. (Carbon, GOV.UK)
- 자주 쓰는 동작에 단축키를 두고 화면에 표시합니다. (NN/g 7번, Microsoft)

## 조사한 X 게시물 (2026-11-14 측정)

X가 게시물당 이미지를 20장까지 허용한 뒤, X 검색("20 images", "20枚", min_faves)으로 찾았습니다.
조각 크기는 저장된 원본(`name=orig`) 기준이고, "표시"는 데스크톱 웹(창 폭 768px)에서 보이는 카드 크기입니다.
비율을 정하려고 본 것이며, 이미지를 복사하거나 저장하지 않았습니다.

| 게시물 | 장수 | 조각 크기 | 비율 | 표시 | 스타일 |
|---|---|---|---|---|---|
| https://x.com/Crain1Art/status/2121009306233438440 | 20 | 272×4096 | 1:15 | 45×703 | 얇은 띠, 빨간 배경 실루엣 |
| https://x.com/torious_0/status/2121059712892571839 | 20 | 285×3840 | 1:13.5 | 51×703 | 얇은 띠, 일러스트 |
| https://x.com/ExploreFranceJP/status/2121078745440354653 | 20 | 220×2975 | 1:13.5 | 51×703 | 얇은 띠, 사진 |
| https://x.com/Artistreccs/status/2121057006656393629 | 20 | 102×1152 | 1:11 | 61×703 | 얇은 띠 |
| https://x.com/miku_emori/status/2121095856665555156 | 20 | 113×1133 | 1:10 | 69×703 | 얇은 띠 |
| https://x.com/NousResearch/status/2121348238100062408 | 20 | 140×1198 | 1:8.6 | 81×703 | 띠, 어두운 사진 |
| https://x.com/doganuraldesign/status/2120971278165414385 | 8 | 2048×4096 | 1:2 | 335×672 | "16K" 넘겨 보는 파노라마 |
| https://x.com/conspiracyslyr/status/2121248257896816768 | 20 | 881×1790 | 1:2.03 | 335×683 | 넘겨 보는 파노라마 (아폴로 17) |
| https://x.com/GoogleIndia/status/2121250042485129613 | 20 | 1005×1920 | 1:1.91 | 335×642 | 넘겨 보기, 로고 |
| https://x.com/japan_nobunaga/status/2121268348780421426 | 20 | 675×1200 | 9:16 | 335×597 | 넘겨 보기, "넘겨 보면 알 거예요" |
| https://x.com/ito_pro_illust/status/2121124737581830230 | 약 20 | 약 1536×2048 | 3:4 | 335×447 | 각각 다른 일러스트 (분할 아님) |
| https://x.com/HazoZOYAKU/status/2121117502340247653 | 8 | 240–1056 × 3200 | 제각각 | 51×703 | 조각 폭을 **일부러 다르게**, 예술적 |
| https://x.com/someki_noi/status/2121119561026253021 | 11 | 3300×2500 | 4:3 | 452×384 | 연속 프레임 넘겨 보기 (분할 아님) |
| https://x.com/Ayumu_japan_art/status/2121093853470159030, https://x.com/elle_piyo/status/2121175053056549308, https://x.com/hdrnssr/status/2121324659346125030 | — | 제각각 | 제각각 | — | 서로 다른 이미지 모음 (분할 아님) |

### 측정 결과가 말해 주는 것

- X는 이미지를 원래 비율대로 보여 줍니다. 카드는 최대 약 **폭 335px, 높이 약 700px**(데스크톱 웹)이고,
  카드 사이 간격은 **6px**입니다.
- 그래서 **1:2**(약 335×670)가 가장 큰 카드입니다. 넘겨 보는 두꺼운 조각이에요(Google India, 아폴로 17, 16K 게시물).
- **1:8~1:15**는 다른 인기 스타일입니다. 폭 45~80px의 얇은 띠로, 블라인드처럼 10장 넘게 한 번에 보입니다.
- 인기 게시물은 긴 변을 X 최대치인 **4096px**로 올립니다. 이보다 작은 조각은 열어 보면 흐릿합니다.
- 아직 만들지 않은 아이디어: 조각 폭을 다르게 자르기(HazoZOYAKU), 연속 프레임 넘겨 보기(someki_noi).

→ 프리셋: 원본(기본, 이미지를 그대로 자름), 1:2, 9:16, 3:4, 1:1, 1:12.

## 샘플 이미지

- 청명상하도 (청원본, 1736) — Wikimedia Commons,
  https://commons.wikimedia.org/wiki/File:Along_the_River_7-119-3.jpg — 퍼블릭 도메인(미술 작품). 저장소에 넣지 않음.
