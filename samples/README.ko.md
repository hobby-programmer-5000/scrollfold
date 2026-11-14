[English](README.md) | **한국어**

# 샘플 입력 이미지

이 이미지들로 Scrollfold를 시험해 보세요. 모든 이미지는 `tools/make_samples.py`가 직접 그렸습니다(남의 사진이나 그림 없음).
이 스크립트를 실행하면 똑같이 다시 만들어지고, `tools/split_samples.py <빈 폴더>`로 한 번에 모두 분할할 수 있습니다.

| 폴더 | 무엇인가 | 추천 설정 |
|---|---|---|
| `by-format/` | 같은 1500×300 그림을 PNG, JPEG, WebP, AVIF, GIF, BMP, TIFF, TGA, JPEG 2000, QOI, PPM, PCX, ICO로 저장 | 아무거나. TIFF/TGA/JP2/QOI/PPM/PCX는 데스크톱 앱이나 로컬 웹 모드가 필요 |
| `by-shape/panorama-10x1_for-1-2.jpg` | 4000×400 | 1:2, 20장 — 넘겨 보는 큰 카드 |
| `by-shape/panorama-11x1_for-9-16.jpg` | 4000×356 | 9:16, 20장 |
| `by-shape/panorama-15x1_for-3-4.jpg` | 4000×267 | 3:4, 20장 |
| `by-shape/panorama-20x1_for-1-1.jpg` | 4000×200 | 1:1, 20장 |
| `by-shape/wide-5x3_for-1-12-slats.jpg` | 2400×1440 | 1:12, 20장 — 얇은 띠 |
| `by-shape/square-1x1.jpg`, `tall-3x4.jpg` | 정사각, 세로 사진 | 1:2 + "여백: 흐린 배경", 2장 |
| `by-type/transparent-rounded.png` | 투명한 둥근 모서리 | JPEG 결과에서 투명한 부분은 흰색 |
| `by-type/cmyk.jpg` | CMYK JPEG | RGB로 변환 |
| `by-type/grayscale.png`, `grayscale-16bit.png` | 8비트·16비트 흑백 | 16비트는 8비트로 맞춤 |
| `by-type/phone-photo-exif-rotated.jpg` | EXIF 방향 6으로 옆으로 저장된 사진 | 바로 세워져 나옴 |
| `by-type/animated.gif` | 3프레임 | 첫 프레임만 사용 |
| `by-type/too-narrow-19px.png` | 폭 19px | 20장으로는 거부됨 (너무 좁음) |
| `by-type/not-an-image.png` | 이름만 .png인 텍스트 파일 | 거부됨 |

## 라이선스: CC0 1.0 (퍼블릭 도메인)

이 이미지들은 어떤 사진이나 그림을 가공한 것이 아닙니다. `tools/make_samples.py`가 그라데이션, 도형, 무작위 별로
처음부터 그립니다. 구석의 작은 라벨은 Pillow에 기본으로 들어 있는 Aileron Regular 폰트로 썼고, 이 폰트도 CC0입니다
(https://dotcolon.net/fonts/aileron).

법이 허용하는 범위에서 저작자는 이 `samples/` 폴더의 이미지에 대한 모든 저작권을 CC0 1.0으로 포기합니다:
https://creativecommons.org/publicdomain/zero/1.0/ — 어떤 용도로든 출처 표기 없이 쓸 수 있습니다.
(이미지를 만드는 스크립트는 코드이므로 프로젝트의 MIT 라이선스를 따릅니다.)
