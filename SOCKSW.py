import streamlit as st
import os
import io
import base64
from PIL import Image, ImageFilter

# ==================== 頁面配置 ====================
st.set_page_config(
    page_title="Gabriel-JL Co., Ltd. | SOCKS",
    page_icon="🧦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 路徑設定 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

PRODUCT_IMAGES = {
    "product1": "product1.jpg",
    "product2": "product2.jpg",
    "product3": "product3.jpg",
    "product4": "product4.jpg",
    "product5": "product5.jpg",
}
DUCK_IMAGE = "duck.jpg"


# ==================== 鴨子圖處理（加快取） ====================
@st.cache_data(show_spinner=False)
def make_duck_clean_cached(image_path,
                           rotate_degrees=90,
                           crop_border=8,
                           line_threshold=40,
                           line_color=(0, 0, 0),
                           thicken=True,
                           thicken_passes=2):
    if not os.path.exists(image_path):
        print("Duck image NOT FOUND:", image_path)
        return None
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print("Duck image load error:", e)
        return None

    # === 0. 旋轉 ===
    if rotate_degrees == 90:
        img = img.transpose(Image.ROTATE_90)
    elif rotate_degrees == 180:
        img = img.transpose(Image.ROTATE_180)
    elif rotate_degrees == 270:
        img = img.transpose(Image.ROTATE_270)

    # === 1. 裁掉外框 ===
    if crop_border > 0:
        w, h = img.size
        img = img.crop((crop_border, crop_border, w - crop_border, h - crop_border))

    # === 2. 去黑底 ===
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []

    for r, g, b, a in datas:
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        if brightness <= line_threshold:
            new_data.append((line_color[0], line_color[1], line_color[2], 255))
        else:
            new_data.append((0, 0, 0, 0))

    img.putdata(new_data)

    # === 3. 加粗 ===
    if thicken and thicken_passes > 0:
        alpha = img.split()[3]
        for _ in range(thicken_passes):
            alpha = alpha.filter(ImageFilter.MaxFilter(3))
        r, g, b, _ = img.split()
        img = Image.merge("RGBA", (r, g, b, alpha))

    # === 4. 轉 base64 ===
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ==================== 產品圖片讀取（加快取） ====================
@st.cache_data(show_spinner=False)
def load_local_image_cached(filename):
    path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(path):
        try:
            return Image.open(path).copy()
        except Exception as e:
            print("Image load error:", path, e)
            return None
    else:
        print("Image NOT FOUND:", path)
        return None


# ==================== 載入鴨子圖 ====================
duck_path = os.path.join(IMAGE_DIR, DUCK_IMAGE)
duck_b64 = make_duck_clean_cached(
    duck_path,
    rotate_degrees=90,     # ★ 先試 90；若腳朝上就改 270
    crop_border=8,
    line_threshold=40,
    line_color=(0, 0, 0),
    thicken=True,
    thicken_passes=2
)

if duck_b64 is not None:
    duck_src = f"data:image/png;base64,{duck_b64}"
    mother_html = f'<img src="{duck_src}" class="duck-img duck-mother" alt="mother duck">'
    duckling1_html = f'<img src="{duck_src}" class="duck-img duck-duckling d1" alt="duckling1">'
    duckling2_html = f'<img src="{duck_src}" class="duck-img duck-duckling d2" alt="duckling2">'
    duckling3_html = f'<img src="{duck_src}" class="duck-img duck-duckling d3" alt="duckling3">'
    ducks_html = mother_html + duckling1_html + duckling2_html + duckling3_html
else:
    ducks_html = ""


# ==================== 網頁瀏覽計次器 ====================
if "visit_count" not in st.session_state:
    st.session_state.visit_count = 0
st.session_state.visit_count += 1


# ==================== 自訂 CSS ====================
st.markdown(f"""
<style>
    * {{ font-family: 'Helvetica Neue', 'Microsoft YaHei', sans-serif; }}

    .header-banner {{
        position: relative;
        background: linear-gradient(135deg, #a8b8e8 0%, #b8a8e0 50%, #9fa8e0 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(168, 184, 232, 0.4);
        overflow: hidden;
        min-height: 150px;
    }}

    .header-banner .duck-img {{
        position: absolute;
        pointer-events: none;
        width: auto;
        background: transparent;
        border: none;
        outline: none;
        box-shadow: none;
    }}

    /* ★ 母鴨：慢慢走 */
    .header-banner .duck-mother {{
        height: 72px;
        top: 22px;
        right: 250px;
        animation: duckWalk 2.4s ease-in-out infinite;   /* ★ 0.6s → 2.4s */
        animation-delay: 0s;
        z-index: 10;
    }}
    /* ★ 小鴨1：慢慢走，晚一點出發 */
    .header-banner .duck-duckling.d1 {{
        height: 24px;
        top: 52px;
        right: 195px;
        animation: duckWalk 2.4s ease-in-out infinite;   /* ★ 0.6s → 2.4s */
        animation-delay: 0.6s;                           /* ★ 0.15s → 0.6s */
        z-index: 5;
    }}
    /* ★ 小鴨2：慢慢走，再晚一點 */
    .header-banner .duck-duckling.d2 {{
        height: 18px;
        top: 58px;
        right: 150px;
        animation: duckWalk 2.4s ease-in-out infinite;   /* ★ 0.6s → 2.4s */
        animation-delay: 1.2s;                           /* ★ 0.30s → 1.2s */
        z-index: 5;
    }}
    /* ★ 小鴨3：慢慢走，最晚出發 */
    .header-banner .duck-duckling.d3 {{
        height: 13px;
        top: 63px;
        right: 112px;
        animation: duckWalk 2.4s ease-in-out infinite;   /* ★ 0.6s → 2.4s */
        animation-delay: 1.8s;                           /* ★ 0.45s → 1.8s */
        z-index: 5;
    }}

    /* ★ 慢慢走：往前走三步、往後走三步 */
    @keyframes duckWalk {{
        0%   {{ transform: translateX(0); }}
        15%  {{ transform: translateX(8px); }}
        30%  {{ transform: translateX(0); }}
        45%  {{ transform: translateX(-8px); }}
        60%  {{ transform: translateX(0); }}
        100% {{ transform: translateX(0); }}
    }}

    .header-banner h1 {{
        color: #ffffff;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: 1.5px;
        position: relative;
        z-index: 20;
        padding-right: 340px;
        text-align: left;
    }}
    .header-banner p {{
        color: #ffffff;
        font-size: 1rem;
        margin-top: 0.3rem;
        font-weight: 300;
        position: relative;
        z-index: 20;
        padding-right: 340px;
        text-align: left;
    }}

    .visit-counter {{
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(255,255,255,0.85);
        border: 2px solid #1a1a1a;
        border-radius: 40px;
        padding: 0.4rem 1.2rem;
        font-family: monospace;
        font-size: 1rem;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }}
    .visit-counter .num {{
        font-weight: 700;
        font-size: 1.4rem;
        color: #000;
    }}

    .product-card {{
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
    }}
    .product-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }}
    .product-card h3 {{ color: #16213e; margin-bottom: 0.3rem; }}
    .product-card .price {{ color: #e94560; font-size: 1.3rem; font-weight: bold; }}
    .product-card .desc {{ color: #555; font-size: 0.95rem; line-height: 1.6; }}

    .contact-card {{
        background: linear-gradient(135deg, #0f3460, #16213e);
        color: #fff;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }}
    .contact-card a {{ color: #e94560; text-decoration: none; }}

    .footer {{
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #888;
        font-size: 0.85rem;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


# ==================== 雙語字典 ====================
TEXTS = {
    "en": {
        "title": "Gabriel-JL Co., Ltd.",
        "subtitle": "Premium SOCKS Manufacturer & Supplier",
        "nav_products": "🧦 Products",
        "nav_about": "ℹ️ About Us",
        "nav_contact": "📬 Contact / Message",
        "products_title": "Our SOCKS Collection",
        "products_desc": "High-quality socks for every occasion — sports, casual, business, and custom designs.",
        "about_title": "About Gabriel-JL Co., Ltd.",
        "about_text": """
**Gabriel-JL Co., Ltd.** (Contact: He YA) is a professional manufacturer and exporter of all kinds of socks.

We specialize in:
- 🏃 Sports socks (running, basketball, cycling)
- 👔 Business & dress socks
- 🧦 Casual & fashion socks
- 🏭 Custom OEM/ODM orders
- 🌿 Organic cotton & bamboo fiber socks

With years of experience in the textile industry, we are committed to providing premium quality products with competitive prices.

**Email:** hejingling51@gmail.com
""",
        "contact_title": "Send Us a Message",
        "contact_desc": "We'd love to hear from you! Leave your message below and we'll get back to you within 24 hours.",
        "form_name": "Your Name",
        "form_email": "Your Email",
        "form_message": "Your Message",
        "form_submit": "Send Message",
        "form_success": "✅ Thank you! Your message has been received. We'll contact you soon.",
        "form_error": "⚠️ Please fill in all fields.",
        "product1_name": "Sports Socks",
        "product1_desc": "Breathable, moisture-wicking, cushioned sole. Perfect for running and outdoor activities.",
        "product1_price": "$2.50 - $4.00 / pair",
        "product2_name": "Business Socks",
        "product2_desc": "Elegant design, premium cotton blend. Comfortable for all-day office wear.",
        "product2_price": "$3.00 - $5.00 / pair",
        "product3_name": "Casual Socks",
        "product3_desc": "Soft, colorful, and stylish. Great for everyday wear and gifts.",
        "product3_price": "$1.80 - $3.00 / pair",
        "product4_name": "Custom OEM Socks",
        "product4_desc": "Your logo, your design, your colors. MOQ from 500 pairs. Free sample available.",
        "product4_price": "Negotiable",
        "product5_name": "Kids Socks",
        "product5_desc": "Soft and safe for children. Various cute designs available.",
        "product5_price": "$1.50 - $2.50 / pair",
        "footer": "© 2025 Gabriel-JL Co., Ltd. All rights reserved. | Contact: He YA | hejingling51@gmail.com",
        "lang_switch": "🇨🇳 中文",
        "advantages_title": "Our Advantages",
        "advantages": [
            ("✅", "Quality Control", "Strict QC at every step"),
            ("🚚", "Fast Delivery", "Worldwide shipping"),
            ("💰", "Competitive Price", "Factory direct pricing"),
            ("🎨", "Custom Design", "OEM/ODM welcomed"),
        ],
        "no_photo": "Photo coming soon",
        "photo_hint": "Put your product photos into the `images/` folder with these names:",
    },
    "zh": {
        "title": "Gabriel-JL 有限公司",
        "subtitle": "專業襪子製造商與供應商",
        "nav_products": "🧦 產品展示",
        "nav_about": "ℹ️ 關於我們",
        "nav_contact": "📬 聯絡我們 / 留言",
        "products_title": "我們的襪子系列",
        "products_desc": "高品質襪子，適合各種場合 — 運動、休閒、商務及訂製設計。",
        "about_title": "關於 Gabriel-JL 有限公司",
        "about_text": """
**Gabriel-JL 有限公司**（聯絡人：He YA）是一家專業的襪子製造商和出口商。

我們專注於：
- 🏃 運動襪（跑步、籃球、騎行）
- 👔 商務正裝襪
- 🧦 休閒時尚襪
- 🏭 訂製 OEM/ODM 訂單
- 🌿 有機棉與竹纖維襪

憑藉多年的紡織行業經驗，我們致力於以有競爭力的價格提供優質產品。

**郵箱：** hejingling51@gmail.com
""",
        "contact_title": "給我們留言",
        "contact_desc": "歡迎聯絡我們！請在下方留言，我們會在24小時內回覆您。",
        "form_name": "您的姓名",
        "form_email": "您的郵箱",
        "form_message": "您的留言",
        "form_submit": "發送留言",
        "form_success": "✅ 感謝您！我們已收到您的留言，會盡快與您聯絡。",
        "form_error": "⚠️ 請填寫所有欄位。",
        "product1_name": "運動襪",
        "product1_desc": "透氣吸汗，加厚緩衝鞋底。適合跑步、健身及戶外運動。",
        "product1_price": "$2.50 - $4.00 / 雙",
        "product2_name": "商務襪",
        "product2_desc": "優雅設計，優質棉混紡。適合全天辦公穿著，舒適有型。",
        "product2_price": "$3.00 - $5.00 / 雙",
        "product3_name": "休閒襪",
        "product3_desc": "柔軟多彩，時尚百搭。適合日常穿著和送禮。",
        "product3_price": "$1.80 - $3.00 / 雙",
        "product4_name": "訂製 OEM 襪子",
        "product4_desc": "您的Logo、您的設計、您的顏色。起訂量500雙起，可提供免費樣品。",
        "product4_price": "面議",
        "product5_name": "兒童襪",
        "product5_desc": "柔軟安全，適合兒童。多款可愛設計可選。",
        "product5_price": "$1.50 - $2.50 / 雙",
        "footer": "© 2025 Gabriel-JL 有限公司 版權所有 | 聯絡人: He YA | hejingling51@gmail.com",
        "lang_switch": "🇬🇧 English",
        "advantages_title": "我們的優勢",
        "advantages": [
            ("✅", "品質把控", "每一步嚴格質檢"),
            ("🚚", "快速交付", "全球發貨"),
            ("💰", "價格優勢", "工廠直銷價格"),
            ("🎨", "訂製設計", "歡迎OEM/ODM"),
        ],
        "no_photo": "照片即將上傳",
        "photo_hint": "請將您的產品照片放入 `images/` 資料夾，檔名如下：",
    }
}


# ==================== Session State ====================
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "form_status" not in st.session_state:
    st.session_state.form_status = None


# ==================== 回調 ====================
def toggle_lang():
    st.session_state.lang = "zh" if st.session_state.lang == "en" else "en"

def handle_form_submit():
    name = st.session_state.get("input_name", "").strip()
    email = st.session_state.get("input_email", "").strip()
    message = st.session_state.get("input_message", "").strip()
    if not name or not email or not message:
        st.session_state.form_status = "error"
        return
    st.session_state.messages.append({"name": name, "email": email, "message": message})
    st.session_state.form_status = "success"
    st.session_state.input_name = ""
    st.session_state.input_email = ""
    st.session_state.input_message = ""


# ==================== 語言文本 ====================
T = TEXTS[st.session_state.lang]


# ==================== 頂部橫幅 ====================
st.markdown(f"""
<div class="header-banner">
    {ducks_html}
    <h1>{T['title']}</h1>
    <p>{T['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# ==================== 瀏覽計次器 ====================
st.markdown(f"""
<div class="visit-counter">
    <span>👀 瀏覽次數</span>
    <span class="num">{st.session_state.visit_count:,}</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    if st.button(T['lang_switch'], key="lang_btn"):
        toggle_lang()
        st.rerun()


# ==================== 側邊欄 ====================
with st.sidebar:
    st.markdown(f"### 🧦 {T['title']}")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [T['nav_products'], T['nav_about'], T['nav_contact']],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**📧 Email:**  \nhejingling51@gmail.com")
    st.markdown("**👤 Contact:**  \nHe YA")
    st.markdown("---")
    st.caption("Gabriel-JL Co., Ltd.")


# ==================== 產品展示 ====================
if page == T['nav_products']:
    st.markdown(f"## {T['products_title']}")
    st.markdown(f"*{T['products_desc']}*")
    st.markdown("---")

    products = [
        {"key": "product1", "name": T['product1_name'], "desc": T['product1_desc'],
         "price": T['product1_price'], "emoji": "🏃"},
        {"key": "product2", "name": T['product2_name'], "desc": T['product2_desc'],
         "price": T['product2_price'], "emoji": "👔"},
        {"key": "product3", "name": T['product3_name'], "desc": T['product3_desc'],
         "price": T['product3_price'], "emoji": "🧦"},
        {"key": "product4", "name": T['product4_name'], "desc": T['product4_desc'],
         "price": T['product4_price'], "emoji": "🎨"},
        {"key": "product5", "name": T['product5_name'], "desc": T['product5_desc'],
         "price": T['product5_price'], "emoji": "🧒"},
    ]

    cols = st.columns(2)
    for i, prod in enumerate(products):
        with cols[i % 2]:
            st.markdown(f"### {prod['emoji']} {prod['name']}")
            img = load_local_image_cached(PRODUCT_IMAGES[prod["key"]])
            if img is not None:
                st.image(img, use_container_width="stretch")
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f5f7fa, #e4e8ec);
                            border-radius: 10px; padding: 3rem; text-align: center;
                            border: 2px dashed #ccc; color: #aaa;">
                    <div style="font-size: 3rem;">{prod['emoji']}</div>
                    <p>{T['no_photo']}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="product-card">
                <p class="desc">{prod['desc']}</p>
                <p class="price">{prod['price']}</p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📁 " + T['photo_hint']):
        st.code("\n".join([f"images/{v}" for v in PRODUCT_IMAGES.values()]))


# ==================== 關於我們 ====================
elif page == T['nav_about']:
    st.markdown(f"## {T['about_title']}")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(T['about_text'])
    with col2:
        st.markdown("""
        <div class="contact-card">
            <h3>📬 Contact</h3>
            <p><strong>He YA</strong></p>
            <p><a href="mailto:hejingling51@gmail.com">hejingling51@gmail.com</a></p>
            <p style="margin-top:1rem; font-size:0.85rem; opacity:0.8;">
                Gabriel-JL Co., Ltd.<br>
                Socks Manufacturer & Exporter
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🏭 {T['advantages_title']}")
    adv_cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(T['advantages']):
        with adv_cols[i]:
            st.markdown(f"""
            <div style="text-align:center; padding:1rem;">
                <div style="font-size:2rem;">{icon}</div>
                <h4>{title}</h4>
                <p style="color:#777; font-size:0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ==================== 聯絡 / 留言 ====================
elif page == T['nav_contact']:
    st.markdown(f"## {T['contact_title']}")
    st.markdown(f"*{T['contact_desc']}*")
    st.markdown("---")
    col_form, col_info = st.columns([3, 2])
    with col_form:
        if st.session_state.form_status == "success":
            st.success(T['form_success'])
            st.balloons()
            st.session_state.form_status = None
        elif st.session_state.form_status == "error":
            st.error(T['form_error'])
            st.session_state.form_status = None

        for k in ("input_name", "input_email", "input_message"):
            if k not in st.session_state:
                st.session_state[k] = ""

        with st.form("message_form", clear_on_submit=False):
            st.text_input(T['form_name'], key="input_name", placeholder="John Doe / 張三")
            st.text_input(T['form_email'], key="input_email", placeholder="you@example.com")
            st.text_area(T['form_message'], key="input_message", placeholder="...", height=150)
            st.form_submit_button(T['form_submit'], use_container_width=True, on_click=handle_form_submit)

    with col_info:
        st.markdown("""
        <div class="contact-card">
            <h3>📬 Contact Information</h3>
            <hr style="border-color: rgba(255,255,255,0.2);">
            <p><strong>Company:</strong><br>Gabriel-JL Co., Ltd.</p>
            <p><strong>Contact Person:</strong><br>He YA</p>
            <p><strong>Email:</strong><br>
                <a href="mailto:hejingling51@gmail.com" style="color:#e94560;">
                    hejingling51@gmail.com
                </a>
            </p>
            <hr style="border-color: rgba(255,255,255,0.2);">
            <p style="font-size:0.85rem; opacity:0.8;">
                We reply within 24 hours.<br>
                我們會在24小時內回覆。
            </p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.messages:
        st.markdown("---")
        with st.expander(f"📋 Message History ({len(st.session_state.messages)})"):
            for i, msg in enumerate(reversed(st.session_state.messages)):
                st.markdown(f"**{msg['name']}** ({msg['email']})  \n*{msg['message']}*")
                if i < len(st.session_state.messages) - 1:
                    st.markdown("---")


# ==================== 頁腳 ====================
st.markdown(f"""
<div class="footer">
    {T['footer']}
</div>
""", unsafe_allow_html=True)
