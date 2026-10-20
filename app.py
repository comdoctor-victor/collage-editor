import streamlit as st
from PIL import Image
import io
import math

st.set_page_config(page_title="ComDoctor Media & Collage Editor", page_icon="🎨", layout="wide")

# ==========================================
# 1. 상단 타이틀 및 설명
# ==========================================
st.title("🎨 올인원 웹 미디어 편집 및 WebP 최적화 툴")
st.markdown("설치 없이 웹에서 사진 회전·편집, 목적별 기기 최적화 및 고효율 WebP 용량 압축을 한 번에 해결하세요.")
st.markdown("---")

# ==========================================
# 2. 사이드바: 출력 및 압축 세부 설정
# ==========================================
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

st.sidebar.markdown("---")
st.sidebar.info("💡 **팁:** 대용량 사진도 자동으로 경량화되어 메모리 과부하 없이 원활하게 편집할 수 있습니다.")

# ==========================================
# 3. 세션 상태 초기화
# ==========================================
if 'image_states' not in st.session_state:
    st.session_state['image_states'] = []

# ==========================================
# 4. 메인 상단: 비율 및 격자 배치 방식 선택
# ==========================================
col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    aspect_ratio = st.selectbox(
        "📐 화면 비율 선택", 
        ["원본 비율 유지", "정방형 (1:1 - 인스타그램/프로필용)", "가로형 (16:9 - 블로그/유튜브용)", "세로형 (9:16 - 숏폼/모바일용)"]
    )

with col_opt2:
    layout_choice = st.selectbox(
        "🧩 콜라주 배치 방식 (Max 3x3)", 
        ["1x1", "1x2", "1x3", "2x1", "2x2", "2x3", "3x1", "3x2", "3x3"]
    )

st.markdown("---")

# ==========================================
# 5. 이미지 파일 업로드 및 메모리 최적화 로딩
# ==========================================
st.subheader("🖼️ 이미지 파일 선택 및 편집")
uploaded_files = st.file_uploader("편집할 이미지 파일들을 선택하세요 (PNG, JPG, WEBP)", type=["jpg", "png", "webp"], accept_multiple_files=True)

if uploaded_files:
    current_names = [f.name for f in uploaded_files]
    existing_names = [s["name"] for s in st.session_state['image_states']]
    
    if current_names != existing_names and len(uploaded_files) > 0:
        new_states = []
        for f in uploaded_files:
            # 메모리 보호를 위해 업로드된 원본을 가벼운 Pillow 객체로 로드 후 바이트로 보관
            img = Image.open(f)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 과도한 메모리 사용 방지를 위해 긴 축이 1200px을 넘으면 사전 축소
            max_dim = 1200
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='JPEG', quality=90)
            
            new_states.append({
                "bytes": byte_arr.getvalue(),
                "name": f.name,
                "rotate": 0,
                "scale": 100
            })
        st.session_state['image_states'] = new_states

# ==========================================
# 6. 레이아웃 분할 (좌측: 개별 편집 / 우측 상단 고정: 미리보기)
# ==========================================
if not st.session_state['image_states']:
    st.info("📂 선택된 이미지가 없습니다. 위에서 이미지 파일을 업로드해 주세요.")
else:
    st.markdown("---")
    col_edit, col_preview = st.columns([1.1, 0.9])
    
    with col_edit:
        st.subheader("✂️ 개별 사진 순서·교체·회전·확대/축소")
        
        for idx, state in enumerate(st.session_state['image_states']):
            with st.container(border=True):
                img_obj = Image.open(io.BytesIO(state["bytes"]))
                
                c_thumb, c_controls = st.columns([1, 2])
                with c_thumb:
                    st.image(img_obj, caption=f"#{idx+1} {state['name']}", use_container_width=True)
                
                with c_controls:
                    st.write(f"**사진 #{idx+1}**: {state['name']}")
                    
                    # 1. 순서 바꾸기 (위/아래)
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if idx > 0:
                            if st.button("⬆️ 앞으로", key=f"up_{idx}"):
                                st.session_state['image_states'][idx], st.session_state['image_states'][idx-1] = \
                                    st.session_state['image_states'][idx-1], st.session_state['image_states'][idx]
                                st.rerun()
                    with c_b2:
                        if idx < len(st.session_state['image_states']) - 1:
                            if st.button("⬇️ 뒤로", key=f"down_{idx}"):
                                st.session_state['image_states'][idx], st.session_state['image_states'][idx+1] = \
                                    st.session_state['image_states'][idx+1], st.session_state['image_states'][idx]
                                st.rerun()

                    # 2. 다른 사진으로 교체
                    new_single_file = st.file_uploader(f"다른 사진 교체 (#{idx+1})", type=["jpg", "png", "webp"], key=f"replace_{idx}")
                    if new_single_file is not None:
                        new_img = Image.open(new_single_file).convert('RGB')
                        if max(new_img.size) > 1200:
                            new_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                        b_arr = io.BytesIO()
                        new_img.save(b_arr, format='JPEG', quality=90)
                        
                        st.session_state['image_states'][idx]["bytes"] = b_arr.getvalue()
                        st.session_state['image_states'][idx]["name"] = new_single_file.name
                        st.rerun()

                    # 3. 회전 설정
                    rot_option = st.selectbox(
                        "회전 (Rotation)", 
                        [0, 90, 180, 270], 
                        index=[0, 90, 180, 270].index(state["rotate"]) if state["rotate"] in [0, 90, 180, 270] else 0,
                        key=f"rot_{idx}"
                    )
                    state["rotate"] = rot_option

                    # 4. 확대/축소 스케일
                    scale_option = st.slider(
                        "확대/축소 (Scale %)", 
                        50, 200, state["scale"], step=10,
                        key=f"scale_{idx}"
                    )
                    state["scale"] = scale_option

    # ==========================================
    # 7. 우측 상단: 실시간 미리보기 및 용량 표시
    # ==========================================
    with col_preview:
        st.subheader("📺 우측 상단 미리보기 화면")
        
        processed_images = []
        for state in st.session_state['image_states']:
            img = Image.open(io.BytesIO(state["bytes"]))
            
            if state["rotate"] > 0:
                img = img.rotate(-state["rotate"], expand=True)
                
            if state["scale"] != 100:
                new_w = int(img.width * (state["scale"] / 100.0))
                new_h = int(img.height * (state["scale"] / 100.0))
                img = img.resize((max(1, new_w), max(1, new_h)), Image.Resampling.LANCZOS)
                
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
                    
            processed_images.append(img)

        gap = 2  # 사진과 사진 사이 2pt 간격
        cols_cnt = int(layout_choice[0])
        rows_cnt = int(layout_choice[2])
        total_slots = cols_cnt * rows_cnt

        if processed_images:
            cell_w = max([img.width for img in processed_images])
            cell_h = max([img.height for img in processed_images])

            grid_w = (cell_w * cols_cnt) + (gap * (cols_cnt - 1))
            grid_h = (cell_h * rows_cnt) + (gap * (rows_cnt - 1))

            new_im = Image.new('RGB', (grid_w, grid_h), (255, 255, 255))

            for idx in range(total_slots):
                r = idx // cols_cnt
                c = idx % cols_cnt
                
                x_pos = c * (cell_w + gap)
                y_pos = r * (cell_h + gap)

                if idx < len(processed_images):
                    im_to_paste = processed_images[idx].resize((cell_w, cell_h), Image.Resampling.LANCZOS)
                    new_im.paste(im_to_paste, (x_pos, y_pos))
                else:
                    blank_cell = Image.new('RGB', (cell_w, cell_h), (255, 255, 255))
                    new_im.paste(blank_cell, (x_pos, y_pos))

            # 최종 최대 너비 적용
            if new_im.width > max_width:
                ratio = max_width / float(new_im.width)
                new_height = int(float(new_im.height) * ratio)
                new_im = new_im.resize((max_width, new_height), Image.Resampling.LANCZOS)

            buf = io.BytesIO()
            new_im.save(buf, format="WEBP", quality=quality)
            byte_im = buf.getvalue()
            file_size_kb = len(byte_im) / 1024

            st.image(new_im, caption="미리보기 화면", use_container_width=True)
            
            # 마지막 줄 용량 표시
            st.markdown(f"**해상도:** `{new_im.width} x {new_im.height} px` &nbsp;|&nbsp; **예상 파일 용량:** `{file_size_kb:.1f} KB`")

            st.download_button(
                label="💾 최적화된 WebP 이미지 다운로드",
                data=byte_im,
                file_name="comdoctor_optimized_collage.webp",
                mime="image/webp",
                type="primary"
            )