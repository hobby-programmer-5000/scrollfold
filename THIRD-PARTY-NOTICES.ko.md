[English](THIRD-PARTY-NOTICES.md) | **한국어**

# 서드파티 고지

Scrollfold는 아래 서드파티 소프트웨어를 사용합니다. 빌드한 실행 파일에는 이것들이 함께 들어갑니다.

| 구성 요소 | 라이선스 | 링크 |
|---|---|---|
| Python (Tkinter, Tcl/Tk 포함) | PSF 라이선스, Tcl/Tk는 BSD 계열 | https://docs.python.org/3/license.html |
| Pillow | MIT-CMU | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| PyInstaller 부트로더 (선택 사항인 Windows exe에만 포함) | GPL-2.0 + 부트로더 예외 (빌드한 exe는 어떤 라이선스로든 배포 가능) | https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt |

Pillow 휠에는 libjpeg-turbo, libpng, zlib, libwebp, libtiff, FreeType 등도 각자의 관대한 라이선스로 들어 있습니다.
전체 목록은 Pillow의 LICENSE 파일을 보세요.

샘플 이미지(`samples/`, CC0)의 작은 라벨 글씨는 Pillow에 기본으로 들어 있는 **Aileron Regular** 폰트(dotcolon, CC0)로
그렸습니다: https://dotcolon.net/fonts/aileron

웹 UI(`web/`)는 외부 코드, 폰트, 아이콘을 쓰지 않습니다. 아이콘(`web/icon.svg`, `web/icon.png`, `icon.ico`)은 이 프로젝트용으로 직접 그렸습니다.
디자인 참고(내용 복사 없음): Chrome Modern Web Guidance, CC BY 4.0 — reference.ko.md 참고.
