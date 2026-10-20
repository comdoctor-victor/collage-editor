import streamlit as st
from PIL import Image
import io
import math

st.set_page_config(page_title="ComDoctor Media & Collage Editor", page_icon="🎨", layout="wide")

# ==========================================
# 1. 상단 타이틀 영역
# ==========================================
st.title("🎨 올인원 웹 미디어 편집 및 WebP 최적화 툴")
st.markdown("설치 없이 웹에서 사진 회전·편집, 목적별 기기 최적화 및 고효율 WebP 용량 압축을 한 번에 해결하세요.")
st.markdown("---")

# ==========================================
# 2. 메인 상단: 화면 비율 및 콜라주 배치 방식 적용 영역
# ==========================================
st.subheader("⚙️ 1단계: 화면 비율 및 콜라주 배치 방식 선택")

col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    aspect_ratio = st.selectbox(
        "📐 화면 비율 선택", 
        ["원본 비율 유지", "정방형 (1:1 - 인스타그램/프로필용)", "가로형 (16:9 - 블로그/유튜브용)", "세로형 (9:16 - 숏폼/모바일용)"]
    )

with col_opt2:
    layout_choice = st.selectbox(
        "🧩 콜라주 배치 방식 (Max 3x3)", 
        [
            "➡️ 가로 나란히 (Row)", 
            "⬇️ 세로 나란히 (Column)", 
            "🔲 2x2 격자 배열 (Grid)", 
            "🎛️ 3x3 격자 배열 (Grid)"
        ]
    )

# 사이드바 (기타 세부 설정: 용량 압축 품질 및 기기별 최대 너비)
st.sidebar.header("⚙️ 출력 및 압축 세부 설정")
device_mode = st.sidebar.selectbox(
    "📱 사용 목적 (기기별 최적 크기)", 
    ["PC 웹용 (가장 선명함)", "Tablet 태블릿용", "Mobile 모바일용 (최적화)", "사용자 직접 지정"]
)

if device_mode == "PC 웹용 (가장 선명함)":
    default_width = 1200
elif device_mode == "Tablet 태블릿용":
    default_width = 800
elif device_mode == "Mobile 모바일용 (최적화)":
    default_width = 500
else:
    default_width = 1000

max_width = st.sidebar.slider("출력 이미지 최대 너비 (Width, px)", 300, 2500, default_width, step=50)
quality = st.sidebar.slider("WebP 압축 품질 (Quality)", 10, 100, 85, help="낮을수록 용량이 작아집니다 (이메일/웹용 추천: 75~85)")

st.markdown("---")

# ==========================================
# 3. 메인 중단: 이미지 파일 업로드 및 개별 편집 영역
# ==========================================
st.subheader("🖼️ 2단계: 이미지 파일 업로드 및 개별 회전 편집")
uploaded_files = st.file_uploader("편집 및 변환할 이미지 파일들을 선택하세요 (PNG, JPG, WEBP)", type=["jpg", "png", "webp"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("---")
    
    # 좌측: 개별 편집 / 우측 상단: 실시간 미리보기 2단 분할
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.write("### ✂️ 업로드된 이미지 개별 회전")
        processed_images = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            
            sub_c1, sub_c2 = st.columns([1, 2])
            with sub_c1:
                st.image(image, caption=f"{uploaded_file.name}\n({image.size[0]}x{image.size[1]}px)", use_container_width=True)
            with sub_c2:
                st.write(f"**#{i+1} 파일:** {uploaded_file.name}")
                rotate_angle = st.selectbox(f"방향 회전 - #{i+1}", [0, 90, 180, 270], key=f"rotate_{i}")
                
                if rotate_angle > 0:
                    image = image.rotate(-rotate_angle, expand=True)
                
                processed_images.append(image)

    # ==========================================
    # 4. 우측 상단: 실시간 결과물 미리보기 및 다운로드
    # ==========================================
    with col_right:
        st.subheader("📺 우측 상단 미리보기 화면")
        st.markdown("상단에서 선택한 비율과 배치 방식에 따라 실시간 반영됩니다.")
        
        # 이미지 비율 사전 크롭 처리
        cropped_images = []
        for img in processed_images:
            w, h = img.size
            if aspect_ratio == "정방형 (1:1 - 인스타그램/프로필용)":
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                img = img.crop((left, top, left + side, top + side))
            elif aspect_ratio == "가로형 (16:9 - 블로그/유튜브용)":
                target_h = int(w * 9 / 16)
                if h > target_h:
                    top = (h - target_h) // 2
                    img = img.crop((0, top, w, top + target_h))
            elif aspect_ratio == "세로형 (9:16 - 숏폼/모바일용)":
                target_w = int(h * 9 / 16)
                if w > target_w:
                    left = (w - target_w) // 2
                    img = img.crop((left, 0, left + target_w, h))
            cropped_images.append(img)

        # 레이아웃 배치 로직
        widths, heights = zip(*(img.size for img in cropped_images))
        
        if "가로 나란히" in layout_choice:
            total_width = sum(widths)
            max_height = max(heights)
            new_im = Image.new('RGB', (total_width, max_height), (255, 255, 255))
            x_offset = 0
            for im in cropped_images:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]
                
        elif "세로 나란히" in layout_choice:
            max_w = max(widths)
            total_height = sum(heights)
            new_im = Image.new('RGB', (max_w, total_height), (255, 255, 255))
            y_offset = 0
            for im in cropped_images:
                new_im.paste(im, (0, y_offset))
                y_offset += im.size[1]
                
        elif "2x2 격자" in layout_choice or "3x3 격자" in layout_choice:
            cols = 2 if "2x2" in layout_choice else 3
            cell_w = max(widths)
            cell_h = max(heights)
            
            rows = math.ceil(len(cropped_images) / cols)
            
            new_im = Image.new('RGB', (cell_w * cols, cell_h * rows), (255, 255, 255))
            for idx, im in enumerate(cropped_images):
                r = idx // cols
                c = idx % cols
                resized_cell = im.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
                new_im.paste(resized_cell, (c * cell_w, r * cell_h))

        # 최종 최대 너비 기준 리사이즈
        if new_im.width > max_width:
            ratio = max_width / float(new_im.width)
            new_height = int(float(new_im.height) * ratio)
            new_im = new_im.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # WebP 바이트 변환
        buf = io.BytesIO()
        new_im.save(buf, format="WEBP", quality=quality)
        byte_im = buf.getvalue()
        file_size_kb = len(byte_im) / 1024

        # 결과 출력
        st.image(new_im, caption=f"최종 결과물 미리보기", use_container_width=True)
        st.info(f"📊 **해상도:** `{new_im.width} x {new_im.height} px` | **예상 용량:** `{file_size_kb:.1f} KB`")
        
        st.download_button(
            label="💾 최적화된 WebP 이미지 다운로드",
            data=byte_im,
            file_name="comdoctor_optimized_collage.webp",
            mime="image/webp",
            type="primary"
        )