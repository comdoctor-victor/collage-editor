#!/usr/bin/env python3
"""
===============================================================================
Collage Editor & Batch WebP Converter (v12)
===============================================================================
2026 ComDoctor Inc. (https://comdoctor.ca)
- File > 설정: 저장 폴더, 워터마크 파일, 시작 기본 규격, 저장 포맷, 인터페이스 언어 영구 저장
- 구글 디스커버 공식 기준(1200x675 16:9, 1200x800 3:2), Blogger OG, PC/모바일 규격 프리셋
- 일괄 이미지 WebP 변환 시 우측 하단 50% 투명도 워터마크 일괄 적용 기능
===============================================================================
"""

import os
import io
import json
import re
import queue
import threading
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.scrolledtext as st
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps

UI_LANGUAGE = "ko"

UI_TRANSLATIONS = {
    "ComDoctor 콜라주 편집기 & 일괄 WebP 변환기 (v12)": "ComDoctor Collage Editor & Batch WebP Converter (v12)",
    "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)": "⭐ [Google Discover] 16:9 Wide (1200 × 675)",
    "⭐ [구글 디스커버 공식] 3:2 표준 (1200 × 800)": "⭐ [Google Discover] 3:2 Standard (1200 × 800)",
    "🌐 [Blogger / SNS 공유] 1.91:1 OG (1200 × 630)": "🌐 [Blogger / SNS Sharing] 1.91:1 OG (1200 × 630)",
    "💻 [PC 블로그] 본문 표준 세로 (860 × 1146)": "💻 [Desktop Blog] Standard Portrait (860 × 1146)",
    "💻 [PC 블로그] 고화질 세로형 (1200 × 1600)": "💻 [Desktop Blog] High-Quality Portrait (1200 × 1600)",
    "💻 [PC 블로그] 4:3 가로형 (1200 × 900)": "💻 [Desktop Blog] 4:3 Landscape (1200 × 900)",
    "📱 [네이버 / SNS 피드] 1:1 정방형 (1080 × 1080)": "📱 [Naver / Social Feed] 1:1 Square (1080 × 1080)",
    "📱 [모바일 블로그] 표준 세로 (720 × 960)": "📱 [Mobile Blog] Standard Portrait (720 × 960)",
    "📱 [모바일 블로그] 풀스크린 세로 (1080 × 1920)": "📱 [Mobile Blog] Full-Screen Portrait (1080 × 1920)",
    "📌 [핀터레스트] 2:3 레시피 카드 (1000 × 1500)": "📌 [Pinterest] 2:3 Recipe Card (1000 × 1500)",
    "🎬 [유튜브 / 영상] 16:9 썸네일 (1280 × 720)": "🎬 [YouTube / Video] 16:9 Thumbnail (1280 × 720)",
    "📐 Custom (사용자 지정 직접 입력)": "📐 Custom (enter dimensions)",
    "원본 비율 그대로 (Original Ratio)": "Original ratio",
    "⚙️ 설정 (File > 설정)": "⚙️ Settings",
    "❓ Guide (도움말 & 가이드)": "❓ Guide",
    "❌ 종료": "❌ Exit",
    "저장": "Save",
    "설정": "Settings",
    "설정 저장 및 적용 [OK]": "Save and Apply [OK]",
    "취소": "Cancel",
    "저장 경로:": "Save folder:",
    "📁 기본 저장 폴더 경로:": "📁 Default save folder:",
    "📁 저장 폴더 변경...": "📁 Change save folder...",
    "🖼️ 기본 워터마크(로고) 파일:": "🖼️ Default watermark (logo) file:",
    "선택 안 됨 (미지정)": "Not selected",
    "🗑️ 워터마크 해제": "🗑️ Clear watermark",
    "🖼️ 워터마크 파일 선택...": "🖼️ Select watermark file...",
    "⭐ 시작 시 기본 이미지 규격 (Default Preset):": "⭐ Default image size at startup:",
    "콜라주 저장 포맷:": "Collage output format:",
    "일괄 변환 시 50% 워터마크 기본 적용": "Apply 50% watermark to batch conversions by default",
    "⚙️ 환경설정 (새로 시작시에도 자동 보존)": "⚙️ Settings (saved for next launch)",
    "⚙️ File > 설정 (저장 폴더 · 워터마크 · 시작 기본 규격 영구 저장)": "⚙️ Settings (save folder, watermark, default size)",
    "💾 설정 저장 및 적용 [OK]": "💾 Save and Apply [OK]",
    "완료": "Done",
    "설정이 성공적으로 저장되었습니다!\n프로그램을 새로 시작해도 동일하게 적용됩니다.": "Settings saved successfully!\nYour language and settings will be used next time too.",
    "한국어": "Korean",
    "영어": "English",
    "언어 / Language:": "Language:",
    "❓ ComDoctor Collage & WebP 편집기 - 도움말 및 사용 가이드": "❓ ComDoctor Collage & WebP Editor - Help and User Guide",
    "ComDoctor Collage Editor & WebP Converter (v12) 가이드": "ComDoctor Collage Editor & WebP Converter (v12) Guide",
    "언어 / Language:": "Language:",
    "클릭: 셀선택 | 셀간 드래그: 교체": "click to select a cell | drag between cells to swap",
    "파일": "File",
    "📐 이미지 규격 (공식 기준):": "📐 Image size (official presets):",
    " 🎨 이미지 규격 및 콜라주 설정 ": " 🎨 Image size and collage settings ",
    "가로(W):": "Width:",
    "px  ×  세로(H):": "px  ×  Height:",
    "적용": "Apply",
    "⭐ 현재 규격을 기본값으로 저장": "⭐ Save current size as default",
    "그리드 레이아웃 선택:": "Choose grid layout:",
    "📁 사진 일괄 불러오기 (최대 9장)": "📁 Load photos (up to 9)",
    "📋 불러온 사진 이름 박스 (클릭하여 셀 선택):": "📋 Loaded photos (click to select a cell):",
    "저장 경로: {path}": "Save folder: {path}",
    " ✂️ 셀 편집 박스 ": " ✂️ Cell editing ",
    "📷 교체": "📷 Replace",
    "🔄 회전": "🔄 Rotate",
    "🗑️ 삭제": "🗑️ Delete",
    "선택된 셀: 없음 (미리보기/목록에서 선택)": "Selected cell: none (choose from preview or list)",
    "💡 팁: 셀 클릭 후 마우스 드래그로 위치 조절 / 다른 셀로 드래그하여 순서 교체": "💡 Tip: drag a photo to reposition it or swap it with another cell",
    "사진 확대/축소 (Zoom):": "Photo zoom:",
    "사진 편집 완료 > OK": "Finish photo editing > OK",
    " 💧 워터마크 박스 (위치 마우스 드래그) ": " 💧 Watermark (drag to reposition) ",
    "워터마크 확대/축소 (Scale):": "Watermark scale:",
    "워터마크 투명도 (Opacity):": "Watermark opacity:",
    "🎨 콜라주 생성 및 저장 (mmddhhmm.webp 자동생성)": "🎨 Create and save collage (auto-name)",
    " 🖼️ 일괄 이미지 WebP 변환기 ": " 🖼️ Batch WebP converter ",
    "변환할 비율/해상도 규격 (공식 규격 지원):": "Output aspect ratio / size:",
    "원본 비율 그대로 (Original Ratio)": "Original ratio",
    "중앙 잘라내기(Crop)": "Center crop",
    "여백 채우기(Fit)": "Fit with padding",
    "💧 워터마크 일괄 삽입 (우측 하단 · 투명도 50%)": "💧 Add watermark to batch (bottom-right · 50% opacity)",
    "📁 외부 파일 선택 ➔ 미리보기·편집·WebP 변환": "📁 Choose files ➔ preview, edit, convert",
    "⚡ 현재 콜라주 사진 ➔ 일괄 WebP 변환": "⚡ Batch-convert current collage photos",
    "Developed by ": "Developed by ",
    "📄 사용 설명서 문서 파일 저장 (collage_editor_guide_manual.md)": "📄 Save user guide document (collage_editor_guide_manual.md)",
    "닫기": "Close",
    "미리보기 화면": "Preview",
    "📁 파일 추가": "📁 Add files",
    "🗑 선택 삭제": "🗑 Remove selected",
    "전체 비우기": "Clear all",
    "※ 원본 비율 그대로 저장 (자르기를 하면 자른 영역의 비율로 저장됩니다)": "※ Saves at the original ratio (cropping changes the output ratio)",
    "파일 / 미리보기": "File / Preview",
    "출력 크기": "Output size",
    "원본 용량": "Original size",
    "WebP 용량": "WebP size",
    "↺ 왼쪽 회전": "↺ Rotate left",
    "↻ 오른쪽 회전": "↻ Rotate right",
    "✂ 자르기 해제": "✂ Clear crop",
    "⟲ 이 사진 초기화": "⟲ Reset this photo",
    "사진 위에서 드래그 = 자르기 영역 지정 / 모서리 = 크기 조절 / 안쪽 = 이동": "Drag on photo to crop / drag a corner to resize / drag inside to move",
    "WebP 품질:": "WebP quality:",
    "최대 크기:": "Max size:",
    "원본 크기 유지": "Keep original size",
    "긴 변 최대 2400px": "Max long edge 2400 px",
    "긴 변 최대 1920px": "Max long edge 1920 px",
    "긴 변 최대 1600px": "Max long edge 1600 px",
    "긴 변 최대 1200px": "Max long edge 1200 px",
    "긴 변 최대 800px": "Max long edge 800 px",
    "현재 로고: {name} (File > 설정에서 변경 가능)": "Current logo: {name} (change in File > Settings)",
    "저장 폴더:": "Save folder:",
    "폴더 변경": "Change folder",
    "🚀 전체 WebP 변환": "🚀 Convert all to WebP",
    "[📁 파일 추가]로 사진을 선택하세요": "Choose photos with [📁 Add files]",
    "오류": "Error",
    "경고": "Warning",
    "알림": "Notice",
    "저장 실패": "Save failed",
    "저장 완료": "Saved",
    "일부 파일 열기 실패": "Some files could not be opened",
    "미리보기를 불러올 수 없습니다:": "Could not load preview:",
    "저장 폴더 선택": "Choose save folder",
    "변환할 사진이 없습니다. [파일 추가]를 눌러 선택하세요.": "No photos to convert. Click [Add files] to choose photos.",
    "저장 폴더를 만들 수 없습니다:": "Could not create save folder:",
    "변환 완료": "Conversion complete",
    "모든 변환에 실패했습니다.": "All conversions failed.",
    "워터마크 이미지 선택": "Choose watermark image",
    "워터마크 로드 실패:": "Could not load watermark:",
    "기본값 저장": "Default saved",
    "⭐ 다음 규격이 프로그램 시작 시 기본값으로 저장되었습니다:\n\n{current}": "⭐ This size is now the startup default:\n\n{current}",
    "가로 및 세로 크기는 최소 100px 이상이어야 합니다.": "Width and height must each be at least 100 px.",
    "유효한 숫자를 입력해 주세요.": "Enter valid numbers.",
    "성공": "Success",
    "🎉 사용 설명서가 성공적으로 저장되었습니다!\n경로: {path}": "🎉 The user guide was saved successfully!\nPath: {path}",
    "문서 저장 실패:": "Could not save document:",
    "사진을 추가하거나 변경할 셀을 미리보기/목록에서 먼저 선택해 주세요.": "Select a cell in the preview or list before adding or replacing a photo.",
    "사진 선택": "Choose photos",
    "WebP로 변환할 사진들 선택": "Choose photos to convert to WebP",
    "슬롯 #{slot} 사진 선택": "Choose a photo for slot #{slot}",
    "이미지를 불러오는 중 문제가 발생했습니다:": "There was a problem loading the image:",
    "삭제할 사진이 들어있는 셀을 미리보기에서 선택해 주세요.": "Select a cell containing a photo to delete.",
    "변환할 사진이 콜라주 슬롯에 없습니다. 먼저 '사진 불러오기'를 진행하세요.": "There are no photos in the collage. Load photos first.",
    "슬롯 사진 변환 중 오류가 발생했습니다.": "An error occurred while converting slot photos.",
    "회전할 사진 칸(슬롯)을 먼저 선택하세요.": "Select a photo slot to rotate first.",
    "설정 저장 중 오류:": "Could not save settings:",
    "설정 불러오기 중 오류:": "Could not load settings:",
    "파일 저장 중 오류가 발생했습니다:": "An error occurred while saving the file:",
    "선택된 셀: 슬롯 #{slot}": "Selected cell: slot #{slot}",
    "슬롯 #{slot} 위치/줌 초기화 완료": "Reset position and zoom for slot #{slot}",
    "슬롯 #{slot} 편집 완료 [OK]": "Finished editing slot #{slot} [OK]",
    "슬롯 #{source} ➔ 슬롯 #{target} 이동 완료": "Moved slot #{source} ➔ slot #{target}",
    "  [셀 #{slot}] (빈 슬롯)": "  [Cell #{slot}] (empty)",
    "  [셀 #{slot}] {filename}": "  [Cell #{slot}] {filename}",
    "선택된 셀: 슬롯 #": "Selected cell: slot #",
    "슬롯 #": "Slot #",
    "[셀 #": "[Cell #",
    " (빈 슬롯)": " (empty)",
    "현재 로고:": "Current logo:",
    "파일 추가": "Add files",
    "저장 폴더:\n": "Save folder:\n",
    "생성된 파일:\n": "Created files:\n",
    "총 ": "Total ",
    "개 | 원본 ": " | original ",
    "개 사진을 WebP로 변환했습니다!": " photos converted to WebP!",
    "개 사진이 회전 설정 반영 후 ": " photos converted with rotation applied to ",
    "용량:": "Size:",
    "기본": "Default",
    "기본값": "Default",
    "회전 ": "Rotate ",
    "자르기 적용": "Crop applied",
    "워터마크(50%)": "Watermark (50%)",
    "적용:": "Applied:",
    "계산 중": "Calculating",
    "사진을 선택하세요": "Choose photos",
    "선택할 수 없습니다": "Could not select",
    "현재 콜라주 사진": "Current collage photos",
    "변환할 사진": "Photos to convert",
    "계산 중…": "Calculating…",
    "WebP 용량 계산 중…": "Calculating WebP size…",
    "원본 ": "Original ",
    "저장 위치:": "Saved to:",
    "셀 #": "Cell #",
    "위치/줌 초기화 완료": "position and zoom reset",
    "이동 완료": "moved",
    "출력 ": "Output ",
    "실패": "Failed",
    "변환 불가": "Cannot convert",
    "선택 안 됨": "Not selected",
    "슬롯 내 ": "In the slots, ",
    " WebP로 변환되었습니다!": " converted to WebP!",
    "🖼️ 일괄 WebP 변환기 - 미리보기 · 편집 · 워터마크 · 변환": "🖼️ Batch WebP Converter - Preview · Edit · Watermark · Convert",
}

UI_SHORT_FRAGMENTS = {
    "총 ", "원본 ", "회전 ", "기본", "기본값", "용량:", "출력 ", "실패",
    "적용:", "셀 #", "계산 중", "저장 위치:"
}

_ORIGINAL_MESSAGEBOX = messagebox


class _LocalizedMessageBox:
    def __getattr__(self, name):
        method = getattr(_ORIGINAL_MESSAGEBOX, name)

        def show(title, message, *args, **kwargs):
            return method(
                translate_ui_text(title, UI_LANGUAGE),
                translate_ui_text(message, UI_LANGUAGE),
                *args,
                **kwargs
            )

        return show


messagebox = _LocalizedMessageBox()


def translate_ui_text(value, language):
    if not isinstance(value, str):
        return value

    def match_template(source, target):
        pattern = re.escape(source)
        pattern = re.sub(r"\\\{([A-Za-z_]\w*)\\\}", r"(?P<\1>.*?)", pattern)
        matched = re.fullmatch(pattern, value)
        if not matched:
            return None
        groups = matched.groupdict()
        for key in ("current", "preset"):
            if key in groups:
                groups[key] = translate_ui_text(groups[key], language)
        return target.format(**groups)

    if language == "ko":
        reverse = {}
        for korean, english in UI_TRANSLATIONS.items():
            reverse.setdefault(english, korean)
        exact = reverse.get(value)
        if exact is not None:
            return exact
        for english, korean in reverse.items():
            if "{" in english:
                translated = match_template(english, korean)
                if translated is not None:
                    return translated
        translated = value
        for korean, english in sorted(UI_TRANSLATIONS.items(), key=lambda item: len(item[1]), reverse=True):
            if (len(english) > 4 or korean in UI_SHORT_FRAGMENTS) and english in translated:
                translated = translated.replace(english, korean)
        return translated
    exact = UI_TRANSLATIONS.get(value)
    if exact is not None:
        return exact
    for korean, english in UI_TRANSLATIONS.items():
        if "{" in korean:
            translated = match_template(korean, english)
            if translated is not None:
                return translated
    translated = value
    for korean, english in sorted(UI_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        if (len(korean) > 4 or korean in UI_SHORT_FRAGMENTS) and korean in translated:
            translated = translated.replace(korean, english)
    return translated


def canonical_preset_name(value):
    return translate_ui_text(value, "ko")


PROGRAM_GUIDE_MANUAL_TEXT = """===============================================================================
📸 Collage Editor & Batch WebP Converter (v12)
2026 이 프로그램은 개인이 무료로 사용할 수 있게 배포합니다.
https://comdoctor.ca 블로그 관리에 필요성에 의해 만든 것입니다.
사용시 문제나 개선은 info@comdoctor.ca로 연락하세요.
===============================================================================

사용 설명서, 환경설정 및 프로그램 가이드

1. ⚙️ 설치 및 환경설정 (Installation & Environment Setup)
--------------------------------------------------------------------------------
* Python 버전: Python 3.8 이상 권장
* 운영체제: Windows, macOS, Linux 지원
* 필수 패키지 설치: pip install Pillow

2. 🌟 프로그램 주요 기능 및 v12 업데이트 안내
--------------------------------------------------------------------------------
① 📁 상단 메뉴 (File > 설정, File > Guide)
* File > 설정: 저장 포맷(WebP, PNG, AVIF), 저장 폴더, 워터마크 파일, 시작 시 기본 규격(Default), 인터페이스 언어(English/한국어) 지정
* 저장 시 프로그램 새로 시작 시에도 설정이 영구적으로 보존됩니다 (설정 자동 복원).

② 📐 공식 이미지 규격 프리셋 리스트 및 기본값(Default) 선택
* ⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675) - 구글 공식 가로 1200px 이상 & 16:9 황금 비율
* ⭐ [구글 디스커버 공식] 3:2 표준 (1200 × 800) - 가독성 높은 3:2 표준
* 🌐 [Blogger / SNS 공유] 1.91:1 OG (1200 × 630) - 오픈그래프 링크 공유 시 잘림 방지
* 💻 [PC 블로그] 본문 표준 세로 (860 × 1146)
* 💻 [PC 블로그] 고화질 세로형 (1200 × 1600)
* 💻 [PC 블로그] 4:3 가로형 (1200 × 900)
* 📱 [네이버 / SNS 피드] 1:1 정방형 (1080 × 1080)
* 📱 [모바일 블로그] 표준 세로 (720 × 960)
* 📱 [모바일 블로그] 풀스크린 세로 (1080 × 1920)
* 📌 [핀터레스트] 2:3 레시피 카드 (1000 × 1500)
* 🎬 [유튜브 / 영상] 16:9 썸네일 (1280 × 720)
* 📐 Custom (사용자 지정 직접 입력)
* [⭐ 기본값 저장] 버튼을 누르면 원하는 규격을 프로그램 시작 시 기본값으로 저장할 수 있습니다.

③ 💧 일괄 이미지 WebP 변환 시 우측 하단 50% 투명도 워터마크 자동 삽입
* 외부 파일 일괄 변환 및 콜라주 슬롯 일괄 변환 시 '워터마크 일괄 삽입' 체크 시
  모든 사진의 우측 하단에 투명도 50%로 최적화된 크기의 로고가 일괄 자동 합성됩니다.
* 변환 전 미리보기 화면에서도 워터마크 합성 상태를 실시간 확인할 수 있습니다.

④ 🎨 콜라주 설정 & 그리드 레이아웃
* 8가지 그리드 레이아웃 지원 (1x1, 1x2, 1x3, 2x1, 2x2, 3x1, 3x2, 3x3)
* 사진 일괄 불러오기 및 불러온 사진 이름 박스 목록 제공
* 셀간 사진 드래그 & 드롭 이동/교체 (Drag & Swap)
* 셀 내부 사진 마우스 드래그 이동 및 확대/축소 (Zoom)
* mmddhhmm.webp 형식 자동 파일명 생성 저장
"""

PROGRAM_GUIDE_MANUAL_TEXT_EN = """===============================================================================
📸 Collage Editor & Batch WebP Converter (v12)
2026 ComDoctor Inc. - https://comdoctor.ca
This program is free for personal use.
For questions or suggestions, contact info@comdoctor.ca.
===============================================================================

User Guide and Settings

1. Installation and setup
--------------------------------------------------------------------------------
* Python 3.8 or later is recommended.
* Supported operating systems: Windows, macOS, and Linux.
* Required package: Pillow (install with: pip install Pillow)

2. Main features
--------------------------------------------------------------------------------
* File > Settings stores the output format, save folder, watermark, startup size,
  batch watermark option, and interface language. Settings are restored at startup.
* Image presets include Google Discover sizes, Blogger/SNS sharing, desktop and
  mobile blog formats, Pinterest, YouTube, and custom dimensions.
* Save the selected image size as the startup default with the default-size button.
* Batch WebP conversion supports preview, rotation, cropping, resizing, and an
  optional 50% watermark in the bottom-right corner.
* Collages support 1x1 through 3x3 layouts, photo replacement, drag-and-drop
  repositioning, zoom, and automatic file naming.
"""

# 공식 이미지 규격 프리셋 리스트
CANVAS_SIZE_PRESETS = {
    "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)": (1200, 675),
    "⭐ [구글 디스커버 공식] 3:2 표준 (1200 × 800)": (1200, 800),
    "🌐 [Blogger / SNS 공유] 1.91:1 OG (1200 × 630)": (1200, 630),
    "💻 [PC 블로그] 본문 표준 세로 (860 × 1146)": (860, 1146),
    "💻 [PC 블로그] 고화질 세로형 (1200 × 1600)": (1200, 1600),
    "💻 [PC 블로그] 4:3 가로형 (1200 × 900)": (1200, 900),
    "📱 [네이버 / SNS 피드] 1:1 정방형 (1080 × 1080)": (1080, 1080),
    "📱 [모바일 블로그] 표준 세로 (720 × 960)": (720, 960),
    "📱 [모바일 블로그] 풀스크린 세로 (1080 × 1920)": (1080, 1920),
    "📌 [핀터레스트] 2:3 레시피 카드 (1000 × 1500)": (1000, 1500),
    "🎬 [유튜브 / 영상] 16:9 썸네일 (1280 × 720)": (1280, 720),
    "📐 Custom (사용자 지정 직접 입력)": (0, 0)
}

ORIGINAL_RATIO_LABEL = "원본 비율 그대로 (Original Ratio)"

ROT_MAP = {
    90: Image.Transpose.ROTATE_270,
    180: Image.Transpose.ROTATE_180,
    270: Image.Transpose.ROTATE_90,
}

EDGE_OPTIONS = {
    "원본 크기 유지": 0,
    "긴 변 최대 2400px": 2400,
    "긴 변 최대 1920px": 1920,
    "긴 변 최대 1600px": 1600,
    "긴 변 최대 1200px": 1200,
    "긴 변 최대 800px": 800,
}

def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/noto-cjk/NotoSansKR-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "NotoSansKR-Regular.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def fmt_size(n):
    if n is None: return "…"
    if n < 1024: return f"{n} B"
    if n < 1024 ** 2: return f"{n / 1024:.1f} KB"
    return f"{n / 1024 ** 2:.2f} MB"

def fmt_pct(est, orig):
    if est is None or not orig: return ""
    return f"{(est / orig - 1) * 100:+.0f}%"

def flatten_rgb(im):
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")

def rotate_crop_cw(c):
    x0, y0, x1, y1 = c
    return [1 - y1, x0, 1 - y0, x1]

def rotate_crop_ccw(c):
    x0, y0, x1, y1 = c
    return [y0, 1 - x1, y1, 1 - x0]

def apply_watermark_bottom_right(base_img, watermark_img, opacity=0.5, margin_ratio=0.025, scale_ratio=0.16):
    """
    일괄 변환용: 이미지의 우측 하단에 투명도 50%로 최적 비율 리사이즈하여 워터마크 합성
    """
    if not watermark_img:
        return base_img

    was_rgb = (base_img.mode != "RGBA")
    work_img = base_img.convert("RGBA")
    bw, bh = work_img.size

    # 이미지 크기에 비례한 워터마크 크기 계산
    target_wm_w = max(40, int(bw * scale_ratio))
    wm_w, wm_h = watermark_img.size
    wm_ratio = wm_w / max(1, wm_h)
    target_wm_h = max(20, int(target_wm_w / wm_ratio))

    if target_wm_h > bh * 0.25:
        target_wm_h = max(20, int(bh * 0.25))
        target_wm_w = max(40, int(target_wm_h * wm_ratio))

    resized_wm = watermark_img.resize((target_wm_w, target_wm_h), Image.Resampling.LANCZOS)
    if resized_wm.mode != "RGBA":
        resized_wm = resized_wm.convert("RGBA")

    # 투명도(기본 50%) 적용
    r, g, b, a = resized_wm.split()
    a = a.point(lambda p: int(p * opacity))
    resized_wm.putalpha(a)

    # 우측 하단 여백 계산
    margin_x = max(10, int(bw * margin_ratio))
    margin_y = max(10, int(bh * margin_ratio))

    dest_x = max(0, bw - target_wm_w - margin_x)
    dest_y = max(0, bh - target_wm_h - margin_y)

    work_img.alpha_composite(resized_wm, dest=(dest_x, dest_y))

    if was_rgb:
        return work_img.convert("RGB")
    return work_img

def process_image(path, rot=0, crop=None, max_edge=0):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    im.load()
    if im.mode not in ("RGB", "RGBA"):
        if im.mode in ("LA", "PA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")
    if rot in ROT_MAP:
        im = im.transpose(ROT_MAP[rot])
    if crop:
        W, H = im.size
        x0 = max(0, min(W - 1, int(round(crop[0] * W))))
        y0 = max(0, min(H - 1, int(round(crop[1] * H))))
        x1 = max(x0 + 1, min(W, int(round(crop[2] * W))))
        y1 = max(y0 + 1, min(H, int(round(crop[3] * H))))
        im = im.crop((x0, y0, x1, y1))
    if max_edge and max(im.size) > max_edge:
        r = max_edge / max(im.size)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.Resampling.LANCZOS)
    return im

def convert_image_to_uniform_webp(img_input, target_w, target_h, fit_mode="crop", rotation=0, quality=90):
    if isinstance(img_input, str):
        raw_img = Image.open(img_input).convert("RGBA")
    else:
        raw_img = img_input.copy().convert("RGBA")

    if rotation == 90:
        raw_img = raw_img.transpose(Image.ROTATE_270)
    elif rotation == 180:
        raw_img = raw_img.transpose(Image.ROTATE_180)
    elif rotation == 270:
        raw_img = raw_img.transpose(Image.ROTATE_90)

    orig_w, orig_h = raw_img.size

    if target_w == 0 or target_h == 0 or target_w is None:
        return raw_img.convert("RGB")

    img_ratio = orig_w / orig_h
    target_ratio = target_w / target_h

    if fit_mode == "crop":
        if img_ratio > target_ratio:
            base_h = target_h
            base_w = int(target_h * img_ratio)
        else:
            base_w = target_w
            base_h = int(target_w / img_ratio)

        resized = raw_img.resize((base_w, base_h), Image.Resampling.LANCZOS)
        crop_x = (base_w - target_w) // 2
        crop_y = (base_h - target_h) // 2

        out_img = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
        out_img.paste(resized, (-crop_x, -crop_y))
    else:
        if img_ratio > target_ratio:
            fit_w = target_w
            fit_h = int(target_w / img_ratio)
        else:
            fit_h = target_h
            fit_w = int(target_w / img_ratio)

        resized = raw_img.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
        out_img = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
        offset_x = (target_w - fit_w) // 2
        offset_y = (target_h - fit_h) // 2
        out_img.paste(resized, (offset_x, offset_y))

    return out_img.convert("RGB")

# =============================================================================
# Batch WebP Editor Dialog (외부 파일 선택 > 미리보기 > 회전/자르기 > 워터마크 > 변환)
# =============================================================================
class BatchWebPDialog:
    THUMB_SIZE = 56
    HANDLE = 10
    MIN_CROP = 0.02

    def __init__(self, app, initial_paths=None):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("🖼️ 일괄 WebP 변환기 - 미리보기 · 편집 · 워터마크 · 변환")
        self.win.geometry("1220x800")
        self.win.minsize(1000, 660)
        self.win.transient(app.root)

        self.items = {}
        self.counter = 0
        self.current = None
        self.cur_src = None
        self.pending = set()
        self.est_after = None
        self.result_q = queue.Queue()
        self.closed = False

        self.quality_var = app.batch_quality_var
        self.edge_var = tk.StringVar(value="원본 크기 유지")
        self.save_dir = app.save_dir
        self.apply_wm_var = tk.BooleanVar(value=app.batch_apply_wm_var.get())

        self.drag_mode = None
        self.drag_start = (0, 0)
        self.drag_crop0 = None
        self.disp_img = self.disp_dim = self.tk_prev = None
        self.disp_off = (0, 0)

        self.build_ui()
        app._translate_widget_tree(self.win, set())
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.poll_results()

        if initial_paths:
            self.add_files(initial_paths)
        else:
            self.win.after(150, self.add_files_dialog)

    def build_ui(self):
        w = self.win
        bold = ("Arial", 9, "bold")

        top = tk.Frame(w, padx=8, pady=6)
        top.pack(fill=tk.X)
        tk.Button(top, text="📁 파일 추가", command=self.add_files_dialog, bg="#0056b3", fg="white", font=bold).pack(side=tk.LEFT)
        tk.Button(top, text="🗑 선택 삭제", command=self.remove_selected, font=("Arial", 9)).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="전체 비우기", command=self.clear_all, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(top, text="※ 원본 비율 그대로 저장 (자르기를 하면 자른 영역의 비율로 저장됩니다)", fg="#6c757d", font=("Arial", 9)).pack(side=tk.LEFT, padx=12)

        body = tk.PanedWindow(w, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        body.pack(fill=tk.BOTH, expand=True, padx=8)

        # 왼쪽: 파일 목록 (Treeview)
        left = tk.Frame(body)
        style = ttk.Style()
        style.configure("Batch.Treeview", rowheight=self.THUMB_SIZE + 6)
        cols = ("dim", "orig", "webp")
        self.tree = ttk.Treeview(left, columns=cols, style="Batch.Treeview", selectmode="extended")
        self.tree.heading("#0", text="파일 / 미리보기")
        self.tree.heading("dim", text="출력 크기")
        self.tree.heading("orig", text="원본 용량")
        self.tree.heading("webp", text="WebP 용량")
        self.tree.column("#0", width=210, minwidth=140)
        self.tree.column("dim", width=90, anchor="center")
        self.tree.column("orig", width=80, anchor="e")
        self.tree.column("webp", width=115, anchor="e")
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Delete>", lambda e: self.remove_selected())
        body.add(left, width=520, minsize=380)

        # 오른쪽: 편집 미리보기
        right = tk.Frame(body)
        tb = tk.Frame(right)
        tb.pack(fill=tk.X, pady=(0, 4))
        tk.Button(tb, text="↺ 왼쪽 회전", command=lambda: self.rotate(False), font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Button(tb, text="↻ 오른쪽 회전", command=lambda: self.rotate(True), font=("Arial", 9)).pack(side=tk.LEFT, padx=4)
        tk.Button(tb, text="✂ 자르기 해제", command=self.reset_crop, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Button(tb, text="⟲ 이 사진 초기화", command=self.reset_all, font=("Arial", 9)).pack(side=tk.LEFT, padx=4)
        tk.Label(tb, text="사진 위에서 드래그 = 자르기 영역 지정 / 모서리 = 크기 조절 / 안쪽 = 이동", fg="#6c757d", font=("Arial", 8)).pack(side=tk.LEFT, padx=8)

        self.canvas = tk.Canvas(right, bg="#2b2b2b", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.render_preview())
        self.canvas.bind("<ButtonPress-1>", self.on_down)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_up)
        self.canvas.bind("<Motion>", self.on_hover)

        self.info_name = tk.Label(right, text="", anchor="w", justify="left", font=("Arial", 9), fg="#495057")
        self.info_name.pack(fill=tk.X, pady=(4, 0))
        self.info_size = tk.Label(right, text="", anchor="w", justify="left", font=("Arial", 11, "bold"))
        self.info_size.pack(fill=tk.X)
        body.add(right, minsize=420)

        # 하단: 옵션 + 워터마크 + 변환
        bottom = tk.Frame(w, padx=8, pady=6)
        bottom.pack(fill=tk.X)

        opt1 = tk.Frame(bottom)
        opt1.pack(fill=tk.X)
        tk.Label(opt1, text="WebP 품질:", font=bold).pack(side=tk.LEFT)
        self.q_label = tk.Label(opt1, text=str(self.quality_var.get()), width=3, font=bold)
        self.q_label.pack(side=tk.LEFT)
        tk.Scale(opt1, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, showvalue=False, length=180, command=self.on_quality_change).pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(opt1, text="최대 크기:", font=bold).pack(side=tk.LEFT)
        cb = ttk.Combobox(opt1, textvariable=self.edge_var, values=list(EDGE_OPTIONS.keys()), state="readonly", width=18)
        cb.pack(side=tk.LEFT, padx=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self.request_estimate(delay=200))

        self.total_label = tk.Label(opt1, text="", font=("Arial", 10, "bold"), fg="#0056b3")
        self.total_label.pack(side=tk.RIGHT)

        # 워터마크 옵션 바
        wm_bar = tk.Frame(bottom, bg="#eef5ff", padx=6, pady=4, relief="groove", bd=1)
        wm_bar.pack(fill=tk.X, pady=(4, 4))

        self.wm_check = tk.Checkbutton(
            wm_bar,
            text="💧 워터마크 일괄 삽입 (우측 하단 · 투명도 50%)",
            variable=self.apply_wm_var,
            font=("Arial", 9, "bold"),
            fg="#0056b3",
            bg="#eef5ff",
            command=self.on_wm_toggle
        )
        self.wm_check.pack(side=tk.LEFT)

        wm_name = os.path.basename(self.app.watermark_path) if self.app.watermark_path else "선택 안 됨"
        self.wm_note_label = tk.Label(
            wm_bar,
            text=f"현재 로고: {wm_name} (File > 설정에서 변경 가능)",
            font=("Arial", 8),
            fg="#28a745" if self.app.watermark_img else "#dc3545",
            bg="#eef5ff"
        )
        self.wm_note_label.pack(side=tk.LEFT, padx=10)

        # 실행 버튼 바
        run = tk.Frame(bottom)
        run.pack(fill=tk.X, pady=(2, 0))
        tk.Label(run, text="저장 폴더:", font=bold).pack(side=tk.LEFT)
        self.dir_label = tk.Label(run, text=self.save_dir, fg="#495057", anchor="w")
        self.dir_label.pack(side=tk.LEFT, padx=4)
        tk.Button(run, text="폴더 변경", command=self.change_dir, font=("Arial", 9)).pack(side=tk.LEFT)
        self.convert_btn = tk.Button(run, text="🚀 전체 WebP 변환", command=self.convert_all, bg="#28a745", fg="white", font=("Arial", 11, "bold"), padx=14)
        self.convert_btn.pack(side=tk.RIGHT)
        self.progress = ttk.Progressbar(run, length=180, mode="determinate")
        self.progress.pack(side=tk.RIGHT, padx=10)

        self.draw_empty_hint()

    def on_wm_toggle(self):
        self.app.batch_apply_wm_var.set(self.apply_wm_var.get())
        self.app.save_config(silent=True)
        self.render_preview()
        self.request_estimate(delay=150)

    def add_files_dialog(self):
        if self.closed: return
        paths = filedialog.askopenfilenames(
            parent=self.win,
            title=translate_ui_text("WebP로 변환할 사진들 선택", self.app.language),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.gif"), ("All Files", "*.*")],
        )
        if paths:
            self.add_files(paths)

    def add_files(self, paths):
        existing = {it["path"] for it in self.items.values()}
        new_ids, failed = [], []
        for p in paths:
            if p in existing: continue
            try:
                thumb = self.make_thumb(p)
                orig = os.path.getsize(p)
            except Exception as e:
                failed.append(f"{os.path.basename(p)} ({e})")
                continue
            self.counter += 1
            iid = f"i{self.counter}"
            self.items[iid] = {"path": p, "rot": 0, "crop": None, "orig": orig, "thumb": thumb,
                               "out": None, "est": None, "ver": 0, "err": None}
            self.tree.insert("", "end", iid=iid, text="  " + os.path.basename(p), image=thumb,
                             values=("…", fmt_size(orig), "계산 중…"))
            new_ids.append(iid)

        if failed:
            messagebox.showwarning("일부 파일 열기 실패", "\n".join(failed[:8]), parent=self.win)
        if new_ids:
            if self.current is None:
                self.tree.selection_set(new_ids[0])
            self.request_estimate(new_ids, delay=50)

    def make_thumb(self, path):
        im = Image.open(path)
        try:
            im.draft("RGB", (self.THUMB_SIZE * 2, self.THUMB_SIZE * 2))
        except Exception:
            pass
        im = flatten_rgb(ImageOps.exif_transpose(im))
        im.thumbnail((self.THUMB_SIZE, self.THUMB_SIZE), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(im)

    def remove_selected(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)
            self.items.pop(iid, None)
            self.pending.discard(iid)
        self.after_list_change()

    def clear_all(self):
        for iid in list(self.items):
            self.tree.delete(iid)
        self.items.clear()
        self.pending.clear()
        self.after_list_change()

    def after_list_change(self):
        if self.current not in self.items:
            self.current = None
            self.cur_src = None
            children = self.tree.get_children()
            if children:
                self.tree.selection_set(children[0])
            else:
                self.render_preview()
                self.update_info()
        self.update_totals()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel or sel[0] == self.current or sel[0] not in self.items:
            return
        iid = sel[0]
        try:
            im = ImageOps.exif_transpose(Image.open(self.items[iid]["path"]))
            im.load()
            src = flatten_rgb(im)
            src.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        except Exception as e:
            messagebox.showerror("오류", f"미리보기를 불러올 수 없습니다:\n{e}", parent=self.win)
            return
        self.current = iid
        self.cur_src = src
        self.render_preview()
        self.update_info()

    def change_dir(self):
        d = filedialog.askdirectory(parent=self.win, title=translate_ui_text("저장 폴더 선택", self.app.language), initialdir=self.save_dir)
        if d:
            self.save_dir = d
            self.dir_label.config(text=d)
            self.app.save_dir = d
            try:
                self.app.dir_label.config(text=f"저장 경로: {d}")
                self.app.save_config(silent=True)
            except Exception:
                pass

    def draw_empty_hint(self):
        self.canvas.delete("all")
        cw, ch = max(self.canvas.winfo_width(), 100), max(self.canvas.winfo_height(), 100)
        hint = "[📁 파일 추가]로 사진을 선택하세요"
        self.canvas.create_text(cw // 2, ch // 2, text=translate_ui_text(hint, self.app.language), fill="#adb5bd", font=("Arial", 13))

    def rotated_src(self):
        rot = self.items[self.current]["rot"]
        return self.cur_src.transpose(ROT_MAP[rot]) if rot in ROT_MAP else self.cur_src

    def render_preview(self):
        if not self.current or self.cur_src is None:
            self.draw_empty_hint()
            return
        src = self.rotated_src()
        cw, ch = max(self.canvas.winfo_width(), 100), max(self.canvas.winfo_height(), 100)
        s = min((cw - 20) / src.width, (ch - 20) / src.height)
        dw, dh = max(1, int(src.width * s)), max(1, int(src.height * s))
        self.disp_img = src.resize((dw, dh), Image.Resampling.BILINEAR)
        self.disp_dim = Image.blend(self.disp_img, Image.new("RGB", (dw, dh), (0, 0, 0)), 0.55)
        self.disp_off = ((cw - dw) // 2, (ch - dh) // 2)
        self.redraw_canvas()

    def crop_px(self, crop):
        dw, dh = self.disp_img.size
        return [crop[0] * dw, crop[1] * dh, crop[2] * dw, crop[3] * dh]

    def redraw_canvas(self):
        if not self.current or self.disp_img is None:
            return
        c = self.canvas
        c.delete("all")
        ox, oy = self.disp_off
        crop = self.items[self.current]["crop"]
        if crop:
            x0, y0, x1, y1 = [int(round(v)) for v in self.crop_px(crop)]
            comp = self.disp_dim.copy()
            if x1 > x0 and y1 > y0:
                cropped = self.disp_img.crop((x0, y0, x1, y1))
                # 워터마크 활성화 시 미리보기에 50% 투명도로 표시
                if self.apply_wm_var.get() and self.app.watermark_img:
                    cropped = apply_watermark_bottom_right(cropped, self.app.watermark_img, opacity=0.5)
                comp.paste(cropped, (x0, y0))
        else:
            comp = self.disp_img.copy()
            if self.apply_wm_var.get() and self.app.watermark_img:
                comp = apply_watermark_bottom_right(comp, self.app.watermark_img, opacity=0.5)

        self.tk_prev = ImageTk.PhotoImage(comp)
        c.create_image(ox, oy, image=self.tk_prev, anchor="nw")
        if crop:
            x0, y0, x1, y1 = self.crop_px(crop)
            c.create_rectangle(ox + x0, oy + y0, ox + x1, oy + y1, outline="#00d1ff", width=2)
            for hx, hy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                c.create_rectangle(ox + hx - 4, oy + hy - 4, ox + hx + 4, oy + hy + 4, fill="#00d1ff", outline="white")

    def to_norm(self, x, y):
        dw, dh = self.disp_img.size
        ox, oy = self.disp_off
        return (min(1.0, max(0.0, (x - ox) / dw)), min(1.0, max(0.0, (y - oy) / dh)))

    def hit_test(self, x, y):
        if not self.current or self.disp_img is None: return None
        crop = self.items[self.current]["crop"]
        if not crop: return None
        ox, oy = self.disp_off
        x0, y0, x1, y1 = self.crop_px(crop)
        x0, x1, y0, y1 = x0 + ox, x1 + ox, y0 + oy, y1 + oy
        h = self.HANDLE
        for name, (cx, cy) in {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}.items():
            if abs(x - cx) <= h and abs(y - cy) <= h:
                return name
        if x0 < x < x1 and y0 < y < y1:
            return "move"
        return None

    def on_hover(self, event):
        mode = self.hit_test(event.x, event.y)
        cur = {"move": "fleur", "nw": "size_nw_se", "se": "size_nw_se", "ne": "size_ne_sw", "sw": "size_ne_sw"}.get(mode, "crosshair")
        try: self.canvas.config(cursor=cur)
        except tk.TclError: self.canvas.config(cursor="crosshair")

    def on_down(self, event):
        if not self.current or self.disp_img is None: return
        it = self.items[self.current]
        mode = self.hit_test(event.x, event.y) or "new"
        self.drag_mode = mode
        self.drag_start = self.to_norm(event.x, event.y)
        self.drag_crop0 = list(it["crop"]) if it["crop"] else None

    def on_drag(self, event):
        if not self.drag_mode or not self.current: return
        it = self.items[self.current]
        nx, ny = self.to_norm(event.x, event.y)
        sx, sy = self.drag_start
        c0 = self.drag_crop0
        mode = self.drag_mode
        if mode == "new":
            it["crop"] = [min(sx, nx), min(sy, ny), max(sx, nx), max(sy, ny)]
        elif mode == "move" and c0:
            w, h = c0[2] - c0[0], c0[3] - c0[1]
            x0 = min(max(0.0, c0[0] + nx - sx), 1 - w)
            y0 = min(max(0.0, c0[1] + ny - sy), 1 - h)
            it["crop"] = [x0, y0, x0 + w, y0 + h]
        elif c0:
            ax = c0[2] if "w" in mode else c0[0]
            ay = c0[3] if "n" in mode else c0[1]
            it["crop"] = [min(ax, nx), min(ay, ny), max(ax, nx), max(ay, ny)]
        self.redraw_canvas()

    def on_up(self, event):
        if not self.drag_mode or not self.current: return
        it = self.items[self.current]
        c = it["crop"]
        if c and ((c[2] - c[0]) < self.MIN_CROP or (c[3] - c[1]) < self.MIN_CROP):
            it["crop"] = None
        if it["crop"] and it["crop"] == [0.0, 0.0, 1.0, 1.0]:
            it["crop"] = None
        self.drag_mode = None
        self.redraw_canvas()
        if it["crop"] != self.drag_crop0:
            self.request_estimate([self.current])
        self.update_info()

    def rotate(self, clockwise=True):
        if not self.current: return
        it = self.items[self.current]
        if clockwise:
            it["rot"] = (it["rot"] + 90) % 360
            if it["crop"]: it["crop"] = rotate_crop_cw(it["crop"])
        else:
            it["rot"] = (it["rot"] - 90) % 360
            if it["crop"]: it["crop"] = rotate_crop_ccw(it["crop"])
        self.render_preview()
        self.request_estimate([self.current])
        self.update_info()

    def reset_crop(self):
        if self.current and self.items[self.current]["crop"]:
            self.items[self.current]["crop"] = None
            self.redraw_canvas()
            self.request_estimate([self.current])
            self.update_info()

    def reset_all(self):
        if self.current:
            it = self.items[self.current]
            it["rot"], it["crop"] = 0, None
            self.render_preview()
            self.request_estimate([self.current])
            self.update_info()

    def edge_value(self):
        return EDGE_OPTIONS.get(canonical_preset_name(self.edge_var.get()), 0)

    def on_quality_change(self, val):
        self.q_label.config(text=str(int(float(val))))
        self.request_estimate(delay=500)

    def request_estimate(self, iids=None, delay=300):
        for iid in (iids if iids is not None else list(self.items)):
            it = self.items.get(iid)
            if not it: continue
            it["ver"] += 1
            it["est"] = None
            it["err"] = None
            self.tree.set(iid, "webp", "계산 중…")
            self.pending.add(iid)
        if self.current in self.items:
            self.update_info()
        if self.est_after:
            self.win.after_cancel(self.est_after)
        self.est_after = self.win.after(delay, self.launch_estimate)

    def launch_estimate(self):
        self.est_after = None
        ids = [i for i in self.pending if i in self.items]
        self.pending.clear()
        if not ids: return
        ids.sort(key=lambda i: 0 if i == self.current else 1)
        jobs = []
        for iid in ids:
            it = self.items[iid]
            jobs.append((iid, it["path"], it["rot"], tuple(it["crop"]) if it["crop"] else None, it["ver"]))
        apply_wm = self.apply_wm_var.get() and (self.app.watermark_img is not None)
        threading.Thread(target=self._worker, args=(jobs, int(self.quality_var.get()), self.edge_value(), apply_wm), daemon=True).start()

    def _worker(self, jobs, quality, max_edge, apply_wm):
        for iid, path, rot, crop, ver in jobs:
            it = self.items.get(iid)
            if self.closed or not it or it["ver"] != ver: continue
            try:
                im = process_image(path, rot, crop, max_edge)
                if apply_wm and self.app.watermark_img:
                    im = apply_watermark_bottom_right(im, self.app.watermark_img, opacity=0.5)
                buf = io.BytesIO()
                im.save(buf, "WEBP", quality=quality, method=4)
                self.result_q.put((iid, ver, im.size, buf.tell(), None))
            except Exception as e:
                self.result_q.put((iid, ver, None, None, str(e)))

    def poll_results(self):
        if self.closed: return
        try:
            while True:
                iid, ver, size, nbytes, err = self.result_q.get_nowait()
                it = self.items.get(iid)
                if not it or it["ver"] != ver: continue
                it["out"], it["est"], it["err"] = size, nbytes, err
                self.refresh_row(iid)
                if iid == self.current: self.update_info()
        except queue.Empty: pass
        self.update_totals()
        self.win.after(120, self.poll_results)

    def refresh_row(self, iid):
        it = self.items[iid]
        if it["err"]:
            self.tree.item(iid, values=(
                translate_ui_text("오류", self.app.language),
                fmt_size(it["orig"]),
                translate_ui_text("변환 불가", self.app.language)
            ))
            return
        dim = f"{it['out'][0]}×{it['out'][1]}" if it["out"] else "…"
        webp = "계산 중…" if it["est"] is None else f"{fmt_size(it['est'])} ({fmt_pct(it['est'], it['orig'])})"
        self.tree.item(iid, values=(dim, fmt_size(it["orig"]), webp))

    def update_info(self):
        if not self.current or self.current not in self.items:
            self.info_name.config(text="")
            self.info_size.config(text="")
            return
        it = self.items[self.current]
        edits = []
        if it["rot"]: edits.append(f"회전 {it['rot']}°")
        if it["crop"]: edits.append("자르기 적용")
        if self.apply_wm_var.get() and self.app.watermark_img:
            edits.append("워터마크(50%)")
        info_name = f"📄 {os.path.basename(it['path'])}   |   적용: {', '.join(edits) if edits else '기본'}"
        self.info_name.config(text=translate_ui_text(info_name, self.app.language))
        if it["err"]:
            self.info_size.config(text=translate_ui_text(f"⚠ {it['err']}", self.app.language), fg="#dc3545")
        elif it["est"] is None:
            self.info_size.config(text=translate_ui_text("WebP 용량 계산 중…", self.app.language), fg="#6c757d")
        else:
            w, h = it["out"]
            color = "#28a745" if it["est"] <= it["orig"] else "#dc3545"
            self.info_size.config(
                text=translate_ui_text(f"원본 {fmt_size(it['orig'])}  ➔  WebP {fmt_size(it['est'])} ({fmt_pct(it['est'], it['orig'])})   |   출력 {w}×{h}px", self.app.language),
                fg=color)

    def update_totals(self):
        if not self.items:
            self.total_label.config(text="")
            return
        done = [it for it in self.items.values() if it["est"] is not None]
        orig_all = sum(it["orig"] for it in self.items.values())
        pending = len(self.items) - len(done)
        txt = f"총 {len(self.items)}개 | 원본 {fmt_size(orig_all)}"
        if done:
            est_all = sum(it["est"] for it in done)
            orig_done = sum(it["orig"] for it in done)
            txt += f" ➔ WebP {fmt_size(est_all)} ({fmt_pct(est_all, orig_done)})"
        if pending: txt += f"  (계산 중 {pending}개)"
        self.total_label.config(text=translate_ui_text(txt, self.app.language))

    @staticmethod
    def unique_path(folder, base):
        p = os.path.join(folder, f"{base}.webp")
        n = 1
        while os.path.exists(p):
            p = os.path.join(folder, f"{base}_{n}.webp")
            n += 1
        return p

    def convert_all(self):
        if not self.items:
            messagebox.showwarning("경고", "변환할 사진이 없습니다. [파일 추가]를 눌러 선택하세요.", parent=self.win)
            return
        try:
            os.makedirs(self.save_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("오류", f"저장 폴더를 만들 수 없습니다:\n{e}", parent=self.win)
            return

        quality, max_edge = int(self.quality_var.get()), self.edge_value()
        apply_wm = self.apply_wm_var.get() and (self.app.watermark_img is not None)
        ids = list(self.tree.get_children())
        self.convert_btn.config(state=tk.DISABLED)
        self.progress.config(maximum=len(ids), value=0)

        ok, failed, total_out, total_orig, names = 0, [], 0, 0, []
        for n, iid in enumerate(ids, 1):
            it = self.items[iid]
            try:
                im = process_image(it["path"], it["rot"], it["crop"], max_edge)
                if apply_wm:
                    im = apply_watermark_bottom_right(im, self.app.watermark_img, opacity=0.5)
                base = os.path.splitext(os.path.basename(it["path"]))[0]
                out_path = self.unique_path(self.save_dir, base)
                im.save(out_path, "WEBP", quality=quality, method=4)
                total_out += os.path.getsize(out_path)
                total_orig += it["orig"]
                names.append(os.path.basename(out_path))
                ok += 1
            except Exception as e:
                failed.append(f"{os.path.basename(it['path'])}: {e}")
            self.progress.config(value=n)
            self.win.update()
        self.convert_btn.config(state=tk.NORMAL)
        self.app.save_config(silent=True)

        if ok:
            wm_text = " (우측 하단 50% 워터마크 적용)" if apply_wm else ""
            listing = "\n".join(names[:5]) + (f"\n... 외 {len(names) - 5}개" if len(names) > 5 else "")
            msg = (f"🎉 {ok}개 사진을 WebP로 변환했습니다!{wm_text}\n\n"
                   f"용량: {fmt_size(total_orig)} ➔ {fmt_size(total_out)} ({fmt_pct(total_out, total_orig)})\n"
                   f"저장 폴더:\n{self.save_dir}\n\n생성된 파일:\n{listing}")
            if failed:
                msg += f"\n\n⚠ 실패 {len(failed)}개:\n" + "\n".join(failed[:5])
            messagebox.showinfo("변환 완료", msg, parent=self.win)
        else:
            messagebox.showerror("오류", "모든 변환에 실패했습니다.\n" + "\n".join(failed[:5]), parent=self.win)

    def on_close(self):
        self.closed = True
        if self.est_after:
            self.win.after_cancel(self.est_after)
        self.app.batch_dialog = None
        self.win.destroy()

# =============================================================================
# Main GUI Class
# =============================================================================
class CollageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ComDoctor Collage Editor & Batch WebP Converter (v12)")
        self.root.geometry("1420x940")

        # 설정 파일 경로 (스크립트 폴더 내 collage_config.json)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        self.config_file = os.path.join(base_dir, "collage_config.json")
        self.language = "ko"

        self.is_initializing = True  # 초기화 중 자동 저장 방지 플래그

        # 그리드 레이아웃 구조 (행, 열, 최대 사진 수)
        self.layout_grid_configs = {
            "1x1": (1, 1, 1),
            "1x2": (1, 2, 2),
            "1x3": (1, 3, 3),
            "2x1": (2, 1, 2),
            "2x2": (2, 2, 4),
            "3x1": (3, 1, 3),
            "3x2": (3, 2, 6),
            "3x3": (3, 3, 9)
        }

        # 기본 선택 변수 초기화
        self.layout_var = tk.StringVar(value="2x2")
        self.default_preset = "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)"
        self.canvas_preset_var = tk.StringVar(value=self.default_preset)
        self.custom_w_var = tk.StringVar(value="1200")
        self.custom_h_var = tk.StringVar(value="675")

        self.format_var = tk.StringVar(value="WebP")
        self.save_dir = os.getcwd()

        # 일괄 변환 옵션 변수
        self.batch_aspect_var = tk.StringVar(value="⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)")
        self.batch_fit_var = tk.StringVar(value="crop")
        self.batch_quality_var = tk.IntVar(value=90)
        self.batch_apply_wm_var = tk.BooleanVar(value=True)  # 기본 50% 워터마크 체크
        self.batch_dialog = None

        self.images = [None] * 9  
        self.image_filenames = [None] * 9
        self.slot_transforms = [{'zoom': 1.0, 'ox': 0.0, 'oy': 0.0, 'rotation': 0} for _ in range(9)]
        self.selected_slot = None

        self.watermark_path = None
        self.watermark_img = None
        self.wm_x, self.wm_y = 50.0, 50.0  
        self.wm_scale, self.wm_opacity = 0.5, 1.0  

        self.is_dragging_wm, self.is_dragging_photo = False, False
        self.drag_start_x, self.drag_start_y = 0.0, 0.0
        self.drag_start_slot = None

        # 1. 이전 저장 설정 불러오기 (영구성 보장)
        self.load_config(silent=True)

        # 2. UI 및 메뉴바 생성
        self.setup_menu_bar()
        self.create_widgets()

        # 3. 초기화 완료 플래그 활성화
        self.is_initializing = False
        self.apply_language()

    def setup_menu_bar(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="⚙️ 설정 (File > 설정)", command=self.open_settings_dialog)
        file_menu.add_command(label="❓ Guide (도움말 & 가이드)", command=self.show_help_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="❌ 종료", command=self.root.quit)

        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def apply_language(self):
        global UI_LANGUAGE
        UI_LANGUAGE = self.language
        visited = set()
        self._translate_widget_tree(self.root, visited)
        menu_name = self.root.cget("menu")
        if menu_name:
            self._translate_widget_tree(self.root.nametowidget(menu_name), visited)
        self.root.title(translate_ui_text("ComDoctor 콜라주 편집기 & 일괄 WebP 변환기 (v12)", self.language))

    def _translate_widget_tree(self, widget, visited):
        widget_name = str(widget)
        if widget_name in visited:
            return
        visited.add(widget_name)
        if isinstance(widget, (tk.Tk, tk.Toplevel)):
            title = widget.title()
            translated_title = translate_ui_text(title, self.language)
            if title != translated_title:
                widget.title(translated_title)
        if widget.winfo_class() == "Menu":
            last_entry = widget.index("end")
            if last_entry is not None:
                for index in range(last_entry + 1):
                    if widget.type(index) == "command":
                        label = widget.entrycget(index, "label")
                        widget.entryconfigure(index, label=translate_ui_text(label, self.language))
                    elif widget.type(index) == "cascade":
                        label = widget.entrycget(index, "label")
                        widget.entryconfigure(index, label=translate_ui_text(label, self.language))
                        child_menu = widget.nametowidget(widget.entrycget(index, "menu"))
                        self._translate_widget_tree(child_menu, visited)
        elif widget.winfo_class() == "Treeview":
            for column, label in (("#0", "파일 / 미리보기"), ("dim", "출력 크기"),
                                  ("orig", "원본 용량"), ("webp", "WebP 용량")):
                widget.heading(column, text=translate_ui_text(label, self.language))
            for item in widget.get_children():
                values = widget.item(item, "values")
                widget.item(item, values=tuple(translate_ui_text(value, self.language) for value in values))
        elif isinstance(widget, tk.Listbox):
            items = [widget.get(index) for index in range(widget.size())]
            selected = widget.curselection()
            if items:
                widget.delete(0, tk.END)
                for index, item in enumerate(items):
                    widget.insert(tk.END, translate_ui_text(item, self.language))
                    if index in selected:
                        widget.selection_set(index)
        elif isinstance(widget, ttk.Combobox):
            values = widget.cget("values")
            if isinstance(values, str):
                values = widget.tk.splitlist(values)
            canonical_values = [canonical_preset_name(value) for value in values]
            current_value = canonical_preset_name(widget.get())
            widget.configure(values=tuple(translate_ui_text(value, self.language) for value in canonical_values))
            if current_value:
                widget.set(translate_ui_text(current_value, self.language))
        elif isinstance(widget, tk.Canvas):
            for item in widget.find_all():
                if widget.type(item) != "text":
                    continue
                text = widget.itemcget(item, "text")
                if text:
                    widget.itemconfigure(item, text=translate_ui_text(text, self.language))
        elif isinstance(widget, st.ScrolledText):
            content = widget.get("1.0", tk.END).strip()
            if "사용 설명서" in content or "User Guide" in content:
                replacement = PROGRAM_GUIDE_MANUAL_TEXT_EN if self.language == "en" else PROGRAM_GUIDE_MANUAL_TEXT
                widget.configure(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
                widget.insert(tk.INSERT, replacement)
                widget.configure(state=tk.DISABLED)
        else:
            try:
                text = widget.cget("text")
            except tk.TclError:
                text = None
            if text:
                try:
                    widget.configure(text=translate_ui_text(text, self.language))
                except tk.TclError:
                    pass

        for child in widget.winfo_children():
            self._translate_widget_tree(child, visited)

    def manual_text(self):
        return PROGRAM_GUIDE_MANUAL_TEXT_EN if self.language == "en" else PROGRAM_GUIDE_MANUAL_TEXT

    def open_settings_dialog(self):
        """File > 설정 다이얼로그 (저장 폴더, 워터마크, 기본 규격 영구 저장)"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("⚙️ File > 설정 (저장 폴더 · 워터마크 · 시작 기본 규격 영구 저장)")
        settings_win.geometry("560x530")
        settings_win.configure(bg="#f8f9fa")
        settings_win.grab_set()

        tk.Label(settings_win, text="⚙️ 환경설정 (새로 시작시에도 자동 보존)", font=("Arial", 12, "bold"), bg="#f8f9fa", fg="#212529").pack(anchor="w", padx=20, pady=(15, 10))

        # 1. 기본 저장 폴더 경로
        dir_frame = tk.Frame(settings_win, bg="#f8f9fa")
        dir_frame.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(dir_frame, text="📁 기본 저장 폴더 경로:", font=("Arial", 9, "bold"), bg="#f8f9fa").pack(anchor="w")
        dir_val_label = tk.Label(dir_frame, text=self.save_dir, bg="#ffffff", fg="#495057", relief="sunken", anchor="w", padx=5, pady=3, wraplength=500)
        dir_val_label.pack(fill=tk.X, pady=3)

        def change_dir_action():
            selected_dir = filedialog.askdirectory(
                initialdir=self.save_dir,
                parent=settings_win,
                title=translate_ui_text("저장 폴더 선택", self.language)
            )
            if selected_dir:
                dir_val_label.config(text=selected_dir)

        tk.Button(dir_frame, text="📁 저장 폴더 변경...", command=change_dir_action, bg="#e2e6ea", font=("Arial", 9)).pack(anchor="e")

        # 2. 워터마크 이미지 파일
        wm_frame = tk.Frame(settings_win, bg="#f8f9fa")
        wm_frame.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(wm_frame, text="🖼️ 기본 워터마크(로고) 파일:", font=("Arial", 9, "bold"), bg="#f8f9fa").pack(anchor="w")
        unselected_watermark = translate_ui_text("선택 안 됨 (미지정)", self.language)
        wm_val_label = tk.Label(wm_frame, text=self.watermark_path if self.watermark_path else unselected_watermark, bg="#ffffff", fg="#495057", relief="sunken", anchor="w", padx=5, pady=3, wraplength=500)
        wm_val_label.pack(fill=tk.X, pady=3)

        wm_btn_row = tk.Frame(wm_frame, bg="#f8f9fa")
        wm_btn_row.pack(anchor="e")

        def clear_wm_action():
            wm_val_label.config(text=translate_ui_text("선택 안 됨 (미지정)", self.language))

        def change_wm_action():
            path = filedialog.askopenfilename(parent=settings_win, title=translate_ui_text("워터마크 이미지 선택", self.language), filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")])
            if path:
                wm_val_label.config(text=path)

        tk.Button(wm_btn_row, text="🗑️ 워터마크 해제", command=clear_wm_action, bg="#f8d7da", fg="#721c24", font=("Arial", 9)).pack(side=tk.LEFT, padx=4)
        tk.Button(wm_btn_row, text="🖼️ 워터마크 파일 선택...", command=change_wm_action, bg="#e2e6ea", font=("Arial", 9)).pack(side=tk.LEFT)

        # 3. 프로그램 시작 시 기본 이미지 규격 (Default Preset)
        preset_frame = tk.Frame(settings_win, bg="#f8f9fa")
        preset_frame.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(preset_frame, text="⭐ 시작 시 기본 이미지 규격 (Default Preset):", font=("Arial", 9, "bold"), bg="#f8f9fa", fg="#0056b3").pack(anchor="w")
        default_preset_var = tk.StringVar(value=self.default_preset)
        default_preset_cb = ttk.Combobox(preset_frame, textvariable=default_preset_var, values=list(CANVAS_SIZE_PRESETS.keys()), state="readonly")
        default_preset_cb.pack(fill=tk.X, pady=3)

        # 4. 저장 포맷 및 일괄 워터마크 옵션
        opt_frame = tk.Frame(settings_win, bg="#f8f9fa")
        opt_frame.pack(fill=tk.X, padx=20, pady=6)
        
        tk.Label(opt_frame, text="콜라주 저장 포맷:", font=("Arial", 9, "bold"), bg="#f8f9fa").pack(side=tk.LEFT)
        temp_fmt_var = tk.StringVar(value=self.format_var.get())
        fmt_cb = ttk.Combobox(opt_frame, textvariable=temp_fmt_var, values=["WebP", "PNG", "AVIF"], state="readonly", width=10)
        fmt_cb.pack(side=tk.LEFT, padx=10)

        temp_batch_wm_var = tk.BooleanVar(value=self.batch_apply_wm_var.get())
        tk.Checkbutton(opt_frame, text="일괄 변환 시 50% 워터마크 기본 적용", variable=temp_batch_wm_var, bg="#f8f9fa", font=("Arial", 9)).pack(side=tk.RIGHT)

        language_frame = tk.Frame(settings_win, bg="#f8f9fa")
        language_frame.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(language_frame, text="언어 / Language:", font=("Arial", 9, "bold"), bg="#f8f9fa").pack(side=tk.LEFT)
        temp_language_var = tk.StringVar(value="English" if self.language == "en" else "한국어")
        ttk.Combobox(
            language_frame,
            textvariable=temp_language_var,
            values=["English", "한국어"],
            state="readonly",
            width=12
        ).pack(side=tk.LEFT, padx=10)

        def save_settings_action():
            previous_language = self.language
            self.language = "en" if temp_language_var.get() == translate_ui_text("English", previous_language) else "ko"
            self.format_var.set(temp_fmt_var.get())
            new_dir = dir_val_label.cget("text")
            if new_dir and os.path.exists(new_dir):
                self.save_dir = new_dir
                self.dir_label.config(text=f"저장 경로: {self.save_dir}")

            new_wm_path = wm_val_label.cget("text")
            if new_wm_path and new_wm_path not in (
                "선택 안 됨 (미지정)",
                translate_ui_text("선택 안 됨 (미지정)", self.language)
            ) and os.path.exists(new_wm_path):
                self.watermark_path = new_wm_path
                try:
                    raw_wm = Image.open(new_wm_path)
                    self.watermark_img = self.remove_white_background(raw_wm)
                except Exception as e:
                    messagebox.showerror("오류", f"워터마크 로드 실패: {e}", parent=settings_win)
            else:
                self.watermark_path = None
                self.watermark_img = None

            self.default_preset = canonical_preset_name(default_preset_var.get())
            self.batch_apply_wm_var.set(temp_batch_wm_var.get())

            self.clamp_watermark_position()
            if not self.save_config(silent=False):
                self.language = previous_language
                return
            self.apply_language()
            self.redraw_preview()
            messagebox.showinfo("완료", "설정이 성공적으로 저장되었습니다!\n프로그램을 새로 시작해도 동일하게 적용됩니다.", parent=settings_win)
            settings_win.destroy()

        btn_bar = tk.Frame(settings_win, bg="#f8f9fa")
        btn_bar.pack(fill=tk.X, padx=20, pady=18)
        tk.Button(btn_bar, text="💾 설정 저장 및 적용 [OK]", command=save_settings_action, bg="#28a745", fg="white", font=("Arial", 10, "bold"), padx=15, pady=6).pack(side=tk.RIGHT)
        tk.Button(btn_bar, text="취소", command=settings_win.destroy, bg="#6c757d", fg="white", font=("Arial", 10), padx=10, pady=6).pack(side=tk.RIGHT, padx=5)
        self._translate_widget_tree(settings_win, set())

    def set_current_as_default_preset(self):
        """현재 선택된 이미지 규격을 시작 시 기본값으로 저장"""
        current = canonical_preset_name(self.canvas_preset_var.get())
        self.default_preset = current
        self.save_config(silent=True)
        messagebox.showinfo("기본값 저장", f"⭐ 다음 규격이 프로그램 시작 시 기본값으로 저장되었습니다:\n\n{current}")

    def create_widgets(self):
        left_container = tk.Frame(self.root, width=470, bg="#f8f9fa")
        left_container.pack(side=tk.LEFT, fill=tk.Y)

        canvas_scroll = tk.Canvas(left_container, width=450, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas_scroll.yview)
        control_frame = tk.Frame(canvas_scroll, padx=12, pady=10, bg="#f8f9fa")

        control_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        canvas_scroll.create_window((0, 0), window=control_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------------------------------------------------------------------
        # 1. 공식 이미지 규격 및 콜라주 설정
        # ---------------------------------------------------------------------
        collage_set_frame = tk.LabelFrame(control_frame, text=" 🎨 이미지 규격 및 콜라주 설정 ", font=("Arial", 11, "bold"), bg="#f8f9fa", fg="#2C3523", padx=8, pady=8)
        collage_set_frame.pack(fill=tk.X, pady=(0, 8))

        # 1-A. 공식 이미지 규격 드롭다운 + 기본값 저장 버튼
        preset_hdr = tk.Frame(collage_set_frame, bg="#f8f9fa")
        preset_hdr.pack(fill=tk.X, pady=(2, 2))
        tk.Label(preset_hdr, text="📐 이미지 규격 (공식 기준):", bg="#f8f9fa", font=("Arial", 9, "bold"), fg="#0056b3").pack(side=tk.LEFT)
        tk.Button(preset_hdr, text="⭐ 현재 규격을 기본값으로 저장", command=self.set_current_as_default_preset, bg="#ffc107", fg="#212529", font=("Arial", 8, "bold"), padx=4).pack(side=tk.RIGHT)

        preset_cb = ttk.Combobox(collage_set_frame, textvariable=self.canvas_preset_var, values=list(CANVAS_SIZE_PRESETS.keys()), state="readonly", font=("Arial", 9))
        preset_cb.pack(fill=tk.X, pady=3)
        preset_cb.bind("<<ComboboxSelected>>", self.on_preset_change)

        # Custom 입력을 위한 UI 프레임
        self.custom_size_frame = tk.Frame(collage_set_frame, bg="#e9ecef", padx=6, pady=4, relief="groove", bd=1)
        tk.Label(self.custom_size_frame, text="가로(W):", bg="#e9ecef", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        tk.Entry(self.custom_size_frame, textvariable=self.custom_w_var, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Label(self.custom_size_frame, text="px  ×  세로(H):", bg="#e9ecef", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        tk.Entry(self.custom_size_frame, textvariable=self.custom_h_var, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Label(self.custom_size_frame, text="px", bg="#e9ecef", font=("Arial", 8)).pack(side=tk.LEFT)
        tk.Button(self.custom_size_frame, text="적용", command=self.apply_custom_canvas_size, bg="#007bff", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=2)

        # 1-B. 그리드 레이아웃
        tk.Label(collage_set_frame, text="그리드 레이아웃 선택:", bg="#f8f9fa", font=("Arial", 9)).pack(anchor="w", pady=(6, 2))
        layout_cb = ttk.Combobox(collage_set_frame, textvariable=self.layout_var, values=list(self.layout_grid_configs.keys()), state="readonly")
        layout_cb.pack(fill=tk.X, pady=2)
        layout_cb.bind("<<ComboboxSelected>>", self.on_layout_change)

        tk.Button(collage_set_frame, text="📁 사진 일괄 불러오기 (최대 9장)", command=self.load_images, bg="#007bff", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=5)

        tk.Label(collage_set_frame, text="📋 불러온 사진 이름 박스 (클릭하여 셀 선택):", bg="#f8f9fa", font=("Arial", 9)).pack(anchor="w", pady=(4, 2))
        
        list_frame = tk.Frame(collage_set_frame, bg="#ffffff")
        list_frame.pack(fill=tk.X, pady=2)

        self.photo_listbox = tk.Listbox(list_frame, height=4, font=("Consolas", 8), bg="#ffffff", fg="#212529", selectbackground="#007bff", selectforeground="white")
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.photo_listbox.yview)
        self.photo_listbox.configure(yscrollcommand=list_scroll.set)

        self.photo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.photo_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.dir_label = tk.Label(collage_set_frame, text=f"저장 경로: {self.save_dir}", wraplength=410, justify="left", bg="#f8f9fa", fg="#6c757d", font=("Arial", 8))
        self.dir_label.pack(anchor="w", pady=(4, 0))

        # ---------------------------------------------------------------------
        # 2. 셀 편집 박스
        # ---------------------------------------------------------------------
        cell_edit_frame = tk.LabelFrame(control_frame, text=" ✂️ 셀 편집 박스 ", font=("Arial", 11, "bold"), bg="#f8f9fa", fg="#0056b3", padx=8, pady=8)
        cell_edit_frame.pack(fill=tk.X, pady=(0, 8))

        line1_frame = tk.Frame(cell_edit_frame, bg="#f8f9fa")
        line1_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Button(line1_frame, text="📷 교체", command=self.add_photo_to_selected_slot, bg="#007bff", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(line1_frame, text="🔄 회전", command=self.rotate_selected_photo, bg="#6c757d", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(line1_frame, text="🗑️ 삭제", command=self.delete_selected_photo, bg="#dc3545", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        line23_frame = tk.Frame(cell_edit_frame, bg="#ffffff", relief="groove", bd=1, padx=6, pady=4)
        line23_frame.pack(fill=tk.X, pady=4)

        self.slot_info_label = tk.Label(line23_frame, text="선택된 셀: 없음 (미리보기/목록에서 선택)", bg="#ffffff", fg="#dc3545", font=("Arial", 9, "bold"))
        self.slot_info_label.pack(anchor="w")

        tk.Label(line23_frame, text="💡 팁: 셀 클릭 후 마우스 드래그로 위치 조절 / 다른 셀로 드래그하여 순서 교체", bg="#ffffff", fg="#495057", font=("Arial", 8)).pack(anchor="w")

        line4_frame = tk.Frame(cell_edit_frame, bg="#f8f9fa")
        line4_frame.pack(fill=tk.X, pady=(4, 0))

        tk.Label(line4_frame, text="사진 확대/축소 (Zoom):", bg="#f8f9fa", font=("Arial", 8, "bold")).pack(anchor="w")
        self.photo_zoom_slider = tk.Scale(line4_frame, from_=0.5, to=3.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#f8f9fa", command=self.on_photo_zoom_change)
        self.photo_zoom_slider.set(1.0)
        self.photo_zoom_slider.pack(fill=tk.X, pady=(0, 4))

        btn_row4 = tk.Frame(line4_frame, bg="#f8f9fa")
        btn_row4.pack(fill=tk.X)

        tk.Button(btn_row4, text="🔄 Refresh", command=self.refresh_photo_edit, bg="#17a2b8", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        tk.Button(btn_row4, text="사진 편집 완료 > OK", command=self.finish_photo_edit, bg="#28a745", fg="white", font=("Arial", 9, "bold")).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # ---------------------------------------------------------------------
        # 3. 워터마크 박스
        # ---------------------------------------------------------------------
        wm_box_frame = tk.LabelFrame(control_frame, text=" 💧 워터마크 박스 (위치 마우스 드래그) ", font=("Arial", 11, "bold"), bg="#f8f9fa", fg="#17a2b8", padx=8, pady=8)
        wm_box_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(wm_box_frame, text="워터마크 확대/축소 (Scale):", bg="#f8f9fa", font=("Arial", 8, "bold")).pack(anchor="w")
        self.scale_slider = tk.Scale(wm_box_frame, from_=0.1, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#f8f9fa", command=self.on_scale_change)
        self.scale_slider.set(self.wm_scale)
        self.scale_slider.pack(fill=tk.X, pady=(0, 4))

        tk.Label(wm_box_frame, text="워터마크 투명도 (Opacity):", bg="#f8f9fa", font=("Arial", 8, "bold")).pack(anchor="w")
        self.opacity_slider = tk.Scale(wm_box_frame, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg="#f8f9fa", command=self.on_opacity_change)
        self.opacity_slider.set(self.wm_opacity)
        self.opacity_slider.pack(fill=tk.X)

        # ---------------------------------------------------------------------
        # 4. 콜라주 생성 및 저장
        # ---------------------------------------------------------------------
        tk.Button(control_frame, text="🎨 콜라주 생성 및 저장 (mmddhhmm.webp 자동생성)", command=self.save_collage, bg="#28a745", fg="white", font=("Arial", 11, "bold"), pady=8).pack(fill=tk.X, pady=(4, 10))

        # ---------------------------------------------------------------------
        # 5. 일괄 변환 패널
        # ---------------------------------------------------------------------
        batch_frame = tk.LabelFrame(control_frame, text=" 🖼️ 일괄 이미지 WebP 변환기 ", bg="#f8f9fa", padx=8, pady=6, fg="#6c757d", font=("Arial", 10, "bold"))
        batch_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(batch_frame, text="변환할 비율/해상도 규격 (공식 규격 지원):", bg="#f8f9fa", font=("Arial", 8, "bold")).pack(anchor="w")
        batch_aspect_options_list = [ORIGINAL_RATIO_LABEL] + list(CANVAS_SIZE_PRESETS.keys())
        aspect_cb = ttk.Combobox(batch_frame, textvariable=self.batch_aspect_var, values=batch_aspect_options_list, state="readonly", font=("Arial", 8))
        aspect_cb.pack(fill=tk.X, pady=2)

        fit_frame = tk.Frame(batch_frame, bg="#f8f9fa")
        fit_frame.pack(fill=tk.X, pady=2)
        tk.Radiobutton(fit_frame, text="중앙 잘라내기(Crop)", variable=self.batch_fit_var, value="crop", bg="#f8f9fa", font=("Arial", 8)).pack(side=tk.LEFT)
        tk.Radiobutton(fit_frame, text="여백 채우기(Fit)", variable=self.batch_fit_var, value="fit", bg="#f8f9fa", font=("Arial", 8)).pack(side=tk.LEFT)

        # 일괄 워터마크 체크박스 (50% 투명도)
        self.slot_wm_check = tk.Checkbutton(
            batch_frame,
            text="💧 워터마크 일괄 삽입 (우측 하단 · 투명도 50%)",
            variable=self.batch_apply_wm_var,
            bg="#f8f9fa",
            font=("Arial", 8, "bold"),
            fg="#0056b3",
            command=lambda: self.save_config(silent=True)
        )
        self.slot_wm_check.pack(anchor="w", pady=2)

        tk.Button(batch_frame, text="📁 외부 파일 선택 ➔ 미리보기·편집·WebP 변환", command=self.batch_convert_external_files, bg="#0056b3", fg="white", font=("Arial", 8, "bold")).pack(fill=tk.X, pady=2)
        tk.Button(batch_frame, text="⚡ 현재 콜라주 사진 ➔ 일괄 WebP 변환", command=self.batch_convert_current_slots, bg="#17a2b8", fg="white", font=("Arial", 8, "bold")).pack(fill=tk.X, pady=2)

        # ---------------------------------------------------------------------
        # 6. 하단 푸터
        # ---------------------------------------------------------------------
        footer_frame = tk.Frame(control_frame, bg="#f8f9fa", pady=10)
        footer_frame.pack(fill=tk.X)

        tk.Label(footer_frame, text="Developed by ", font=("Arial", 9), bg="#f8f9fa", fg="#495057").pack(side=tk.LEFT)
        link_site = tk.Label(footer_frame, text="comdoctor.ca", font=("Arial", 9, "bold", "underline"), bg="#f8f9fa", fg="#007bff", cursor="hand2")
        link_site.pack(side=tk.LEFT)
        link_site.bind("<Button-1>", lambda e: webbrowser.open("https://comdoctor.ca"))

        tk.Label(footer_frame, text="  |  ", font=("Arial", 9), bg="#f8f9fa", fg="#adb5bd").pack(side=tk.LEFT)

        link_email = tk.Label(footer_frame, text="info@comdoctor.ca", font=("Arial", 9, "underline"), bg="#f8f9fa", fg="#007bff", cursor="hand2")
        link_email.pack(side=tk.LEFT)
        link_email.bind("<Button-1>", lambda e: webbrowser.open("mailto:info@comdoctor.ca"))

        # 우측 미리보기 영역
        preview_frame = tk.Frame(self.root, bg="#ffffff")
        preview_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        preview_header_frame = tk.Frame(preview_frame, bg="white")
        preview_header_frame.pack(fill=tk.X, pady=5)

        self.preview_title_label = tk.Label(preview_header_frame, text="미리보기 화면", font=("Arial", 10, "bold"), bg="white")
        self.preview_title_label.pack(side=tk.LEFT)
        
        self.canvas = tk.Canvas(preview_frame, bg="#e9ecef", width=620, height=760)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.on_preset_change()

    def get_layout_info(self):
        preset_name = canonical_preset_name(self.canvas_preset_var.get())
        if preset_name == "📐 Custom (사용자 지정 직접 입력)":
            try:
                total_w = max(100, int(self.custom_w_var.get()))
                total_h = max(100, int(self.custom_h_var.get()))
            except ValueError:
                total_w, total_h = 1200, 675
        else:
            total_w, total_h = CANVAS_SIZE_PRESETS.get(preset_name, (1200, 675))

        layout_key = self.layout_var.get()
        rows, cols, max_count = self.layout_grid_configs.get(layout_key, (2, 2, 4))

        return total_w, total_h, rows, cols, max_count

    def on_preset_change(self, event=None):
        preset_name = canonical_preset_name(self.canvas_preset_var.get())
        if preset_name == "📐 Custom (사용자 지정 직접 입력)":
            self.custom_size_frame.pack(fill=tk.X, pady=4, after=self.canvas_preset_var)
        else:
            self.custom_size_frame.pack_forget()
            w, h = CANVAS_SIZE_PRESETS.get(preset_name, (1200, 675))
            self.custom_w_var.set(str(w))
            self.custom_h_var.set(str(h))

        tw, th, _, _, _ = self.get_layout_info()
        is_def = " [기본값]" if preset_name == self.default_preset else ""
        preview_title = f"미리보기 화면 [{tw} × {th} px]{is_def} (클릭: 셀선택 | 셀간 드래그: 교체)"
        self.preview_title_label.config(text=translate_ui_text(preview_title, self.language))
        self.clamp_watermark_position()
        self.redraw_preview()
        self.save_config(silent=True)

    def apply_custom_canvas_size(self):
        try:
            w = int(self.custom_w_var.get())
            h = int(self.custom_h_var.get())
            if w < 100 or h < 100:
                messagebox.showwarning("경고", "가로 및 세로 크기는 최소 100px 이상이어야 합니다.")
                return
        except ValueError:
            messagebox.showerror("오류", "유효한 숫자를 입력해 주세요.")
            return

        self.on_preset_change()

    def clamp_watermark_position(self):
        if self.watermark_img:
            total_w, total_h, _, _, _ = self.get_layout_info()
            wm_w = self.watermark_img.width * self.wm_scale
            wm_h = self.watermark_img.height * self.wm_scale

            max_x = max(0.0, float(total_w - wm_w))
            max_y = max(0.0, float(total_h - wm_h))

            self.wm_x = max(0.0, min(float(self.wm_x), max_x))
            self.wm_y = max(0.0, min(float(self.wm_y), max_y))

    def update_photo_listbox(self):
        self.photo_listbox.delete(0, tk.END)
        _, _, _, _, max_count = self.get_layout_info()

        for i in range(max_count):
            if i < len(self.images) and self.images[i] is not None:
                fname = self.image_filenames[i] if self.image_filenames[i] else f"사진_{i+1}.png"
                self.photo_listbox.insert(tk.END, translate_ui_text(f"  [셀 #{i+1}] {fname}", self.language))
            else:
                self.photo_listbox.insert(tk.END, translate_ui_text(f"  [셀 #{i+1}] (빈 슬롯)", self.language))

        if self.selected_slot is not None and self.selected_slot < max_count:
            self.photo_listbox.selection_clear(0, tk.END)
            self.photo_listbox.selection_set(self.selected_slot)
            self.photo_listbox.see(self.selected_slot)

    def on_listbox_select(self, event):
        sel = self.photo_listbox.curselection()
        if sel:
            idx = sel[0]
            self.selected_slot = idx
            self.slot_info_label.config(text=translate_ui_text(f"선택된 셀: 슬롯 #{idx+1}", self.language), fg="#007bff")
            if self.images[idx] is not None:
                self.photo_zoom_slider.set(self.slot_transforms[idx]['zoom'])
            self.redraw_preview()

    def refresh_photo_edit(self):
        if self.selected_slot is not None and self.images[self.selected_slot] is not None:
            self.slot_transforms[self.selected_slot] = {'zoom': 1.0, 'ox': 0.0, 'oy': 0.0, 'rotation': 0}
            self.photo_zoom_slider.set(1.0)
            self.slot_info_label.config(text=translate_ui_text(f"슬롯 #{self.selected_slot+1} 위치/줌 초기화 완료", self.language), fg="#17a2b8")
            self.redraw_preview()
            self.save_config(silent=True)
        else:
            self.redraw_preview()

    def show_help_dialog(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("❓ ComDoctor Collage & WebP 편집기 - 도움말 및 사용 가이드")
        help_win.geometry("820x700")
        help_win.configure(bg="#f8f9fa")

        top_bar = tk.Frame(help_win, bg="#556B2F", padx=15, pady=10)
        top_bar.pack(fill=tk.X)

        tk.Label(top_bar, text="ComDoctor Collage Editor & WebP Converter (v12) Guide", font=("Arial", 12, "bold"), fg="white", bg="#556B2F").pack(side=tk.LEFT)

        text_area = st.ScrolledText(help_win, wrap=tk.WORD, font=("Consolas", 10), bg="#ffffff", fg="#2c3523", padx=15, pady=15)
        text_area.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)

        text_area.insert(tk.INSERT, self.manual_text())
        text_area.config(state=tk.DISABLED)

        bottom_bar = tk.Frame(help_win, bg="#f8f9fa", padx=15, pady=10)
        bottom_bar.pack(fill=tk.X)

        def save_doc_action():
            doc_path = os.path.join(self.save_dir, "collage_editor_guide_manual.md")
            try:
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(self.manual_text())
                messagebox.showinfo("성공", f"🎉 사용 설명서가 성공적으로 저장되었습니다!\n경로: {doc_path}")
            except Exception as e:
                messagebox.showerror("오류", f"문서 저장 실패: {e}")

        tk.Button(bottom_bar, text="📄 사용 설명서 문서 파일 저장 (collage_editor_guide_manual.md)", command=save_doc_action, bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Button(bottom_bar, text="닫기", command=help_win.destroy, bg="#6c757d", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT)
        self._translate_widget_tree(help_win, set())

    def add_photo_to_selected_slot(self):
        if self.selected_slot is None:
            messagebox.showinfo("알림", "사진을 추가하거나 변경할 셀을 미리보기/목록에서 먼저 선택해 주세요.")
            return
        
        file_path = filedialog.askopenfilename(
            title=translate_ui_text(f"슬롯 #{self.selected_slot + 1} 사진 선택", self.language),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff")]
        )
        if file_path:
            try:
                self.images[self.selected_slot] = Image.open(file_path).convert("RGBA")
                self.image_filenames[self.selected_slot] = os.path.basename(file_path)
                self.slot_transforms[self.selected_slot] = {'zoom': 1.0, 'ox': 0.0, 'oy': 0.0, 'rotation': 0}
                self.update_photo_listbox()
                self.redraw_preview()
                self.save_config(silent=True)
                self.slot_info_label.config(text=translate_ui_text(f"슬롯 #{self.selected_slot + 1} 사진 변경 완료", self.language), fg="#28a745")
            except Exception as e:
                messagebox.showerror("오류", f"이미지를 불러오는 중 문제가 발생했습니다: {e}")

    def delete_selected_photo(self):
        if self.selected_slot is not None and self.images[self.selected_slot] is not None:
            self.images[self.selected_slot] = None
            self.image_filenames[self.selected_slot] = None
            self.slot_transforms[self.selected_slot] = {'zoom': 1.0, 'ox': 0.0, 'oy': 0.0, 'rotation': 0}
            self.update_photo_listbox()
            self.redraw_preview()
            self.save_config(silent=True)
            self.slot_info_label.config(text=translate_ui_text(f"슬롯 #{self.selected_slot + 1} 사진 삭제됨", self.language), fg="#dc3545")
        else:
            messagebox.showinfo("알림", "삭제할 사진이 들어있는 셀을 미리보기에서 선택해 주세요.")

    def batch_convert_external_files(self):
        if self.batch_dialog is not None and self.batch_dialog.win.winfo_exists():
            self.batch_dialog.win.lift()
            self.batch_dialog.add_files_dialog()
            return
        self.batch_dialog = BatchWebPDialog(self)

    def batch_convert_current_slots(self):
        valid_slots = [(i, img) for i, img in enumerate(self.images) if img is not None]
        if not valid_slots:
            messagebox.showwarning("경고", "변환할 사진이 콜라주 슬롯에 없습니다. 먼저 '사진 불러오기'를 진행하세요.")
            return

        aspect_preset = canonical_preset_name(self.batch_aspect_var.get())
        if aspect_preset == "원본 비율 그대로 (Original Ratio)":
            target_w, target_h = 0, 0
        else:
            target_w, target_h = CANVAS_SIZE_PRESETS.get(aspect_preset, (0, 0))

        fit_mode = self.batch_fit_var.get()
        quality = self.batch_quality_var.get()
        apply_wm = self.batch_apply_wm_var.get() and (self.watermark_img is not None)

        converted_count = 0
        saved_paths = []

        for slot_idx, img in valid_slots:
            try:
                rotation = self.slot_transforms[slot_idx].get('rotation', 0)
                out_img = convert_image_to_uniform_webp(img, target_w, target_h, fit_mode=fit_mode, rotation=rotation, quality=quality)
                
                # 워터마크 우측 하단 50% 투명도 적용
                if apply_wm:
                    out_img = apply_watermark_bottom_right(out_img, self.watermark_img, opacity=0.5)

                if target_w == 0 or target_h == 0:
                    out_filename = f"collage_slot_{slot_idx+1}_original.webp"
                else:
                    out_filename = f"collage_slot_{slot_idx+1}_{target_w}x{target_h}.webp"

                out_path = os.path.join(self.save_dir, out_filename)
                out_img.save(out_path, "WEBP", quality=quality)
                converted_count += 1
                saved_paths.append(out_filename)
            except Exception as e:
                print(f"슬롯 {slot_idx+1} 변환 실패: {e}")

        if converted_count > 0:
            preview_list = "\n".join(saved_paths)
            spec_str = "원본 비율 유지" if (target_w == 0 or target_h == 0) else f"{target_w}x{target_h}"
            wm_msg = " (우측 하단 50% 워터마크 포함)" if apply_wm else ""
            messagebox.showinfo(
                "성공",
                f"🎉 슬롯 내 {converted_count}개 사진이 회전 설정 반영 후 {spec_str} WebP로 변환되었습니다!{wm_msg}\n\n"
                f"저장 폴더:\n{self.save_dir}\n\n"
                f"생성된 파일:\n{preview_list}"
            )
        else:
            messagebox.showerror("오류", "슬롯 사진 변환 중 오류가 발생했습니다.")

    def on_layout_change(self, event=None):
        self.selected_slot = None
        self.slot_info_label.config(text=translate_ui_text("선택된 셀: 없음 (미리보기/목록에서 선택)", self.language), fg="#dc3545")
        self.update_photo_listbox()
        self.clamp_watermark_position()
        self.redraw_preview()
        self.save_config(silent=True)

    def load_images(self):
        _, _, _, _, max_count = self.get_layout_info()
        file_paths = filedialog.askopenfilenames(
            title=translate_ui_text("사진 선택", self.language),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
        )
        if file_paths:
            for i, path in enumerate(file_paths[:max_count]):
                try:
                    self.images[i] = Image.open(path).convert("RGBA")
                    self.image_filenames[i] = os.path.basename(path)
                    self.slot_transforms[i] = {'zoom': 1.0, 'ox': 0.0, 'oy': 0.0, 'rotation': 0}
                except Exception as e:
                    messagebox.showerror("오류", f"이미지를 불러오는 중 문제가 발생했습니다: {e}")
            self.update_photo_listbox()
            self.redraw_preview()

    def rotate_selected_photo(self):
        if self.selected_slot is not None and self.images[self.selected_slot] is not None:
            curr_rot = self.slot_transforms[self.selected_slot].get('rotation', 0)
            self.slot_transforms[self.selected_slot]['rotation'] = (curr_rot + 90) % 360
            self.redraw_preview()
            self.save_config(silent=True)
        else:
            messagebox.showinfo("알림", "회전할 사진 칸(슬롯)을 먼저 선택하세요.")

    def remove_white_background(self, img, threshold=200):
        img = img.convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        return img

    def on_scale_change(self, val):
        self.wm_scale = float(val)
        self.clamp_watermark_position()
        self.redraw_preview()

    def on_opacity_change(self, val):
        self.wm_opacity = float(val)
        self.redraw_preview()

    def on_photo_zoom_change(self, val):
        if self.selected_slot is not None and self.images[self.selected_slot] is not None:
            self.slot_transforms[self.selected_slot]['zoom'] = float(val)
            self.redraw_preview()

    def finish_photo_edit(self):
        if self.selected_slot is not None:
            self.slot_info_label.config(text=translate_ui_text(f"슬롯 #{self.selected_slot+1} 편집 완료 [OK]", self.language), fg="#28a745")
            self.selected_slot = None
            self.update_photo_listbox()
            self.redraw_preview()
            self.save_config(silent=True)

    def save_config(self, silent=False):
        """설정 파일 저장 (초기화 중 실행 방지)"""
        if getattr(self, "is_initializing", False):
            return

        config_data = {
            "layout": self.layout_var.get(),
            "default_preset": getattr(self, "default_preset", "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)"),
            "canvas_preset": canonical_preset_name(self.canvas_preset_var.get()),
            "custom_w": self.custom_w_var.get(),
            "custom_h": self.custom_h_var.get(),
            "format": self.format_var.get(),
            "language": self.language,
            "save_dir": self.save_dir,
            "batch_aspect": canonical_preset_name(self.batch_aspect_var.get()),
            "batch_fit": self.batch_fit_var.get(),
            "batch_quality": self.batch_quality_var.get(),
            "batch_apply_wm": self.batch_apply_wm_var.get(),
            "slot_transforms": self.slot_transforms,
            "watermark_path": self.watermark_path,
            "wm_x": self.wm_x,
            "wm_y": self.wm_y,
            "wm_scale": self.wm_scale,
            "wm_opacity": self.wm_opacity
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("오류", f"설정 저장 중 오류: {e}")
            return False

    def load_config(self, silent=True):
        """저장된 설정 불러오기 (영구성 보장)"""
        if not os.path.exists(self.config_file):
            return
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            self.language = config_data.get("language", "ko")
            if self.language not in ("en", "ko"):
                self.language = "ko"
            global UI_LANGUAGE
            UI_LANGUAGE = self.language

            # 저장 폴더 복원
            saved_dir = config_data.get("save_dir")
            if saved_dir and os.path.exists(saved_dir):
                self.save_dir = saved_dir

            # 워터마크 복원
            wm_path = config_data.get("watermark_path")
            if wm_path and os.path.exists(wm_path):
                self.watermark_path = wm_path
                try:
                    raw_wm = Image.open(wm_path)
                    self.watermark_img = self.remove_white_background(raw_wm)
                except Exception:
                    self.watermark_img = None
            else:
                self.watermark_path = None
                self.watermark_img = None

            # 기본 규격(Default) 및 현재 규격 복원
            self.default_preset = config_data.get("default_preset", "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)")
            if self.default_preset not in CANVAS_SIZE_PRESETS:
                self.default_preset = "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)"

            saved_preset = config_data.get("canvas_preset", self.default_preset)
            if saved_preset in CANVAS_SIZE_PRESETS:
                self.canvas_preset_var.set(saved_preset)
            else:
                self.canvas_preset_var.set(self.default_preset)

            self.custom_w_var.set(config_data.get("custom_w", "1200"))
            self.custom_h_var.set(config_data.get("custom_h", "675"))
            self.layout_var.set(config_data.get("layout", "2x2"))
            self.format_var.set(config_data.get("format", "WebP"))

            # 일괄 변환 옵션 복원
            self.batch_aspect_var.set(config_data.get("batch_aspect", "⭐ [구글 디스커버 공식] 16:9 와이드 (1200 × 675)"))
            self.batch_fit_var.set(config_data.get("batch_fit", "crop"))
            self.batch_quality_var.set(config_data.get("batch_quality", 90))
            self.batch_apply_wm_var.set(config_data.get("batch_apply_wm", True))

            if "slot_transforms" in config_data:
                self.slot_transforms = config_data["slot_transforms"]

            self.wm_x = config_data.get("wm_x", 50.0)
            self.wm_y = config_data.get("wm_y", 50.0)
            self.wm_scale = config_data.get("wm_scale", 0.5)
            self.wm_opacity = config_data.get("wm_opacity", 1.0)

            # 생성된 위젯이 있을 경우 값 동기화
            if hasattr(self, "dir_label"):
                self.dir_label.config(text=translate_ui_text(f"저장 경로: {self.save_dir}", self.language))
            if hasattr(self, "scale_slider"):
                self.scale_slider.set(self.wm_scale)
            if hasattr(self, "opacity_slider"):
                self.opacity_slider.set(self.wm_opacity)

            self.clamp_watermark_position()
            if hasattr(self, "canvas"):
                self.update_photo_listbox()
                self.redraw_preview()
        except Exception as e:
            if not silent:
                messagebox.showerror("오류", f"설정 불러오기 중 오류: {e}")

    def get_slots_rects(self):
        total_w, total_h, rows, cols, max_count = self.get_layout_info()
        gap = 12 if rows > 1 or cols > 1 else 0
        cell_w = (total_w - (cols - 1) * gap) // cols
        cell_h = (total_h - (rows - 1) * gap) // rows

        slots = []
        for r in range(rows):
            for c in range(cols):
                if len(slots) < max_count:
                    x = c * (cell_w + gap)
                    y = r * (cell_h + gap)
                    slots.append((x, y, cell_w, cell_h))
        return slots

    def on_mouse_down(self, event):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        orig_w, orig_h, _, _, _ = self.get_layout_info()
        
        scale_factor = min(canvas_w / orig_w, canvas_h / orig_h)
        displayed_w = orig_w * scale_factor
        displayed_h = orig_h * scale_factor
        offset_x = (canvas_w - displayed_w) / 2
        offset_y = (canvas_h - displayed_h) / 2

        orig_mouse_x = (event.x - offset_x) / scale_factor
        orig_mouse_y = (event.y - offset_y) / scale_factor

        if self.watermark_img:
            wm_w = self.watermark_img.width * self.wm_scale
            wm_h = self.watermark_img.height * self.wm_scale
            if (self.wm_x <= orig_mouse_x <= self.wm_x + wm_w) and (self.wm_y <= orig_mouse_y <= self.wm_y + wm_h):
                self.is_dragging_wm = True
                self.drag_start_x = orig_mouse_x - self.wm_x
                self.drag_start_y = orig_mouse_y - self.wm_y
                return

        slots = self.get_slots_rects()
        for i, (rx, ry, rw, rh) in enumerate(slots):
            if rx <= orig_mouse_x <= rx + rw and ry <= orig_mouse_y <= ry + rh:
                self.selected_slot = i
                self.drag_start_slot = i
                self.slot_info_label.config(text=translate_ui_text(f"선택된 셀: 슬롯 #{i+1}", self.language), fg="#007bff")
                self.update_photo_listbox()

                if self.images[i]:
                    self.photo_zoom_slider.set(self.slot_transforms[i]['zoom'])
                
                self.is_dragging_photo = True
                self.drag_start_x = orig_mouse_x
                self.drag_start_y = orig_mouse_y
                self.redraw_preview()
                return

    def on_mouse_drag(self, event):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        orig_w, orig_h, _, _, _ = self.get_layout_info()
        
        scale_factor = min(canvas_w / orig_w, canvas_h / orig_h)
        displayed_w = orig_w * scale_factor
        displayed_h = orig_h * scale_factor
        offset_x = (canvas_w - displayed_w) / 2
        offset_y = (canvas_h - displayed_h) / 2

        orig_mouse_x = (event.x - offset_x) / scale_factor
        orig_mouse_y = (event.y - offset_y) / scale_factor

        if self.is_dragging_wm:
            self.wm_x = orig_mouse_x - self.drag_start_x
            self.wm_y = orig_mouse_y - self.drag_start_y
            self.clamp_watermark_position()
            self.redraw_preview()
        elif self.is_dragging_photo and self.selected_slot is not None:
            dx = orig_mouse_x - self.drag_start_x
            dy = orig_mouse_y - self.drag_start_y
            self.drag_start_x = orig_mouse_x
            self.drag_start_y = orig_mouse_y

            self.slot_transforms[self.selected_slot]['ox'] += dx
            self.slot_transforms[self.selected_slot]['oy'] += dy
            self.redraw_preview()

    def on_mouse_up(self, event):
        if hasattr(self, 'drag_start_slot') and self.drag_start_slot is not None:
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            orig_w, orig_h, _, _, _ = self.get_layout_info()
            
            scale_factor = min(canvas_w / orig_w, canvas_h / orig_h)
            displayed_w = orig_w * scale_factor
            displayed_h = orig_h * scale_factor
            offset_x = (canvas_w - displayed_w) / 2
            offset_y = (canvas_h - displayed_h) / 2

            orig_mouse_x = (event.x - offset_x) / scale_factor
            orig_mouse_y = (event.y - offset_y) / scale_factor

            slots = self.get_slots_rects()
            target_slot = None
            for i, (rx, ry, rw, rh) in enumerate(slots):
                if rx <= orig_mouse_x <= rx + rw and ry <= orig_mouse_y <= ry + rh:
                    target_slot = i
                    break

            if target_slot is not None and target_slot != self.drag_start_slot:
                self.images[self.drag_start_slot], self.images[target_slot] = \
                    self.images[target_slot], self.images[self.drag_start_slot]
                
                self.image_filenames[self.drag_start_slot], self.image_filenames[target_slot] = \
                    self.image_filenames[target_slot], self.image_filenames[self.drag_start_slot]

                self.slot_transforms[self.drag_start_slot], self.slot_transforms[target_slot] = \
                    self.slot_transforms[target_slot], self.slot_transforms[self.drag_start_slot]
                
                self.selected_slot = target_slot
                self.slot_info_label.config(text=translate_ui_text(f"슬롯 #{self.drag_start_slot+1} ➔ 슬롯 #{target_slot+1} 이동 완료", self.language), fg="#28a745")
                self.update_photo_listbox()
                self.redraw_preview()

            self.drag_start_slot = None

        self.is_dragging_wm = False
        self.is_dragging_photo = False
        self.save_config(silent=True)

    def generate_collage_image(self):
        total_w, total_h, rows, cols, max_count = self.get_layout_info()
        base_img = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 255))
        slots = self.get_slots_rects()

        for i, rect in enumerate(slots):
            rx, ry, rw, rh = rect
            if i < len(self.images) and self.images[i]:
                img = self.images[i]
                zoom = self.slot_transforms[i]['zoom']
                ox = self.slot_transforms[i]['ox']
                oy = self.slot_transforms[i]['oy']
                rotation = self.slot_transforms[i].get('rotation', 0)

                if rotation == 90:
                    img = img.transpose(Image.ROTATE_270)
                elif rotation == 180:
                    img = img.transpose(Image.ROTATE_180)
                elif rotation == 270:
                    img = img.transpose(Image.ROTATE_90)

                img_ratio = img.width / img.height
                slot_ratio = rw / rh
                
                if img_ratio > slot_ratio:
                    base_h = rh
                    base_w = int(rh * img_ratio)
                else:
                    base_w = rw
                    base_h = int(rw / img_ratio)
                
                new_w = int(base_w * zoom)
                new_h = int(base_h * zoom)
                resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                crop_x = (new_w - rw) // 2 - int(ox)
                crop_y = (new_h - rh) // 2 - int(oy)
                
                temp_slot = Image.new("RGBA", (rw, rh), (255, 255, 255, 255))
                temp_slot.paste(resized, (-crop_x, -crop_y))
                base_img.paste(temp_slot, (rx, ry))

                if i == self.selected_slot:
                    draw = ImageDraw.Draw(base_img)
                    draw.rectangle([rx, ry, rx+rw, ry+rh], outline="#007bff", width=5)
            else:
                placeholder = Image.new("RGBA", (rw, rh), (240, 240, 240, 255))
                base_img.paste(placeholder, (rx, ry))

        if self.watermark_img:
            self.clamp_watermark_position()
            wm_w = int(self.watermark_img.width * self.wm_scale)
            wm_h = int(self.watermark_img.height * self.wm_scale)
            resized_wm = self.watermark_img.resize((wm_w, wm_h), Image.Resampling.LANCZOS)

            if self.wm_opacity < 1.0:
                alpha = resized_wm.split()[3]
                alpha = alpha.point(lambda p: int(p * self.wm_opacity))
                resized_wm.putalpha(alpha)

            base_img.alpha_composite(resized_wm, dest=(int(self.wm_x), int(self.wm_y)))

        return base_img

    def redraw_preview(self):
        collage = self.generate_collage_image()
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10: canvas_w = 620
        if canvas_h < 10: canvas_h = 760

        orig_w, orig_h, _, _, _ = self.get_layout_info()
        scale_factor = min(canvas_w / orig_w, canvas_h / orig_h)
        
        preview_w = int(orig_w * scale_factor)
        preview_h = int(orig_h * scale_factor)
        
        resized_preview = collage.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized_preview)
        
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w / 2, canvas_h / 2, image=self.tk_img, anchor=tk.CENTER)

    def save_collage(self):
        old_selected = self.selected_slot
        self.selected_slot = None
        collage = self.generate_collage_image()
        self.selected_slot = old_selected

        fmt = self.format_var.get().lower()
        if fmt == "webp":
            ext, pil_format, save_img = "webp", "WEBP", collage
        elif fmt == "png":
            ext, pil_format, save_img = "png", "PNG", collage
        else:
            ext, pil_format, save_img = "avif", "AVIF", collage.convert("RGB")

        auto_filename = datetime.now().strftime("%m%d%H%M") + f".{ext}"
        save_path = os.path.join(self.save_dir, auto_filename)

        try:
            save_img.save(save_path, format=pil_format)
            messagebox.showinfo("저장 완료", f"🎉 콜라주가 성공적으로 저장되었습니다!\n\n파일명: {auto_filename}\n저장 위치: {save_path}")
        except Exception as e:
            messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CollageEditorApp(root)
    root.mainloop()
