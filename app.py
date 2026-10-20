import streamlit as st
from PIL import Image, ImageOps
import io

# 페이지 설정
st.set_page_config(
    page_title="Collage Editor", 
    page_icon="🎨", 
    layout="wide"
)

st.title("🎨 Collage Editor & WebP Converter")
st.markdown("여러 장의 이미지를 업로드하여 **콜라주(조합)** 형태로 만들고, 최적화된 **WebP 포맷**으로 로컬 PC에 저장하세요.")

# 사이드바 설정 (콜라주 옵션)
st.sidebar.header("⚙️ 편집 및 압축 옵션")
layout_mode = st.sidebar.selectbox("콜라주 배치 방식", ["가로 나란히 (Row)", "세로 정렬 (Column)", "2열 그리드 (Grid)"])
quality_slider = st.sidebar.slider("WebP 압축 품질 (Quality)", min_value=10, max_value=100, value=85)
target_width = st.sidebar.slider("출력 이미지 최대 너비 (Width)", min_value=400, max_value=2000, value=1200, step=100)

# 파일 업로더 (다중 이미지 지원)
uploaded_files = st.file_uploader(
    "편집 및 병합할 이미지 파일들을 선택하세요 (PNG, JPG, WEBP)", 
    type=["png", "jpg", "jpeg", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("🖼️ 업로드된 이미지 목록")
    
    # 이미지 열 단위 미리보기
    cols = st.columns(min(len(uploaded_files), 4))
    images = []
    
    for idx, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGB")
        images.append(img)
        with cols[idx % len(cols)]:
            st.image(img, caption=f"{file.name} ({img.size[0]}x{img.size[1]})", use_container_width=True)

    st.markdown("---")
    
    # 콜라주 생성 및 WebP 변환 실행 버튼
    if st.button("🚀 콜라주 생성 및 WebP 변환", type="primary"):
        with st.spinner("이미지 조합 및 WebP 최적화 변환 중..."):
            
            # 1. 크기 및 레이아웃 재배치 연산 (Collage Logic)
            # 가로 폭 기준 비율 유지 리사이징
            resized_images = []
            for img in images:
                w_percent = (target_width / float(img.size[0]))
                h_size = int(float(img.size[1]) * float(w_percent))
                img_resized = img.resize((target_width, h_size), Image.Resampling.LANCZOS)
                resized_images.append(img_resized)

            # 레이아웃 모드별 병합 처리
            if layout_mode == "가로 나란히 (Row)":
                total_width = sum(img.width for img in resized_images)
                max_height = max(img.height for img in resized_images)
                combined_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))
                x_offset = 0
                for img in resized_images:
                    combined_img.paste(img, (x_offset, 0))
                    x_offset += img.width

            elif layout_mode == "세로 정렬 (Column)":
                total_width = max(img.width for img in resized_images)
                total_height = sum(img.height for img in resized_images)
                combined_img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
                y_offset = 0
                for img in resized_images:
                    combined_img.paste(img, (0, y_offset))
                    y_offset += img.height

            else:  # 2열 그리드 (Grid)
                cols_count = 2
                rows_count = (len(resized_images) + 1) // cols_count
                cell_w = target_width
                cell_h = max(img.height for img in resized_images)
                
                combined_img = Image.new("RGB", (cell_w * cols_count, cell_h * rows_count), (255, 255, 255))
                for idx, img in enumerate(resized_images):
                    r = idx // cols_count
                    c = idx % cols_count
                    combined_img.paste(img, (c * cell_w, r * cell_h))

            # 2. 결과물 WebP 포맷 버퍼 변환
            webp_buffer = io.BytesIO()
            combined_img.save(webp_buffer, format="WEBP", quality=quality_slider, method=6)
            
            st.success("🎉 콜라주 편집 및 WebP 변환 완료!")
            
            # 최종 결과물 미리보기
            st.image(combined_img, caption="최종 완성된 콜라주 미리보기", use_container_width=True)

            # 3. 방문자 로컬 PC로 WebP 다운로드 버튼 제공
            st.download_button(
                label="📦 완성된 콜라주 (.webp) 로컬 PC에 다운로드",
                data=webp_buffer.getvalue(),
                file_name="collage_output.webp",
                mime="image/webp"
            )