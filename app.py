import io
from PIL import Image
import qrcode
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Pro QR Studio", page_icon="📱", layout="centered")

# Custom CSS for perfect balanced width and modern spacing
st.markdown(
    """
    <style>
    /* App ki max width set karke overall structure clean aur focused banana */
    .block-container {
        max-width: 850px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
    }
    
    /* Input Fields ki styling & margin adjust karna */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.8rem;
    }

    /* Preview Card Container */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.title("📱 Pro QR Code Studio")
st.caption("Convert your links or text into a QR code and add a custom logo.")
st.markdown("---")

# Balanced 2-Column Grid with comfortable gap
col_controls, col_preview = st.columns([1.1, 0.9], gap="large")

with col_controls:
    st.markdown("##### ⚙️ Settings")

    # 1. Text / Link Input
    data = st.text_input(
        "Website URL / Text:",
        value="https://google.com",
        help="Enter the link you want to create a QR code for here.",
    )

    # 2. Colors Selection
    c1, c2 = st.columns(2)
    with c1:
        fill_color = st.color_picker("QR Color", value="#0F172A")
    with c2:
        back_color = st.color_picker("Background", value="#FFFFFF")

    # 3. Logo Upload
    uploaded_logo = st.file_uploader(
        "Center Logo (Optional):", type=["png", "jpg", "jpeg"]
    )

    logo_size_percent = 20
    if uploaded_logo is not None:
        logo_size_percent = st.slider(
            "Logo Size (%):",
            min_value=10,
            max_value=30,
            value=20,
            help="20% ideal size hota hai easy scanning ke liye.",
        )

    # 4. File Format
    file_format = st.selectbox("Download Format:", ["PNG", "JPEG"])


# QR Code Generator Function
def generate_qr_with_logo(text, fg, bg, logo_file, logo_percent):
    if not text.strip():
        text = " "

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fg, back_color=bg).convert("RGBA")

    if logo_file is not None:
        logo = Image.open(logo_file).convert("RGBA")

        qr_width, qr_height = qr_img.size
        logo_max_size = int(qr_width * (logo_percent / 100))

        logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

        logo_w, logo_h = logo.size
        pos = ((qr_width - logo_w) // 2, (qr_height - logo_h) // 2)

        padding = 5
        bg_box = Image.new(
            "RGBA", (logo_w + padding * 2, logo_h + padding * 2), bg
        )
        bg_pos = (
            (qr_width - bg_box.width) // 2,
            (qr_height - bg_box.height) // 2,
        )

        qr_img.paste(bg_box, bg_pos)
        qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

    return qr_img.convert("RGB")


# Generate QR
qr_img = generate_qr_with_logo(
    data, fill_color, back_color, uploaded_logo, logo_size_percent
)

# Right Panel: Live Preview Card
with col_preview:
    st.markdown("##### 💁 Live Preview")

    # Image Preview
    st.image(
        qr_img,
        caption="Your Generated QR Code",
        use_container_width=True,
    )

    # Buffer for Download
    buffer = io.BytesIO()
    fmt = "PNG" if file_format == "PNG" else "JPEG"
    qr_img.save(buffer, format=fmt)
    img_bytes = buffer.getvalue()

    # Download Button
    st.download_button(
        label=f"💾 Download ({file_format})",
        data=img_bytes,
        file_name=f"qr_code.{file_format.lower()}",
        mime=f"image/{file_format.lower()}",
        use_container_width=True,
    )