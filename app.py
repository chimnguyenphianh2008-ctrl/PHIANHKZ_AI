import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="PHIANHKZ AI", page_icon="😎", layout="wide")

# Thiết lập API Key
API_KEY = "AIzaSyD2YfcHrpbEtzuMLkZiMzKIUvOAfkQx2z8"
genai.configure(api_key=API_KEY)

# --- CÔNG CỤ (ACTIONS) ---
def google_search(query: str):
    """Đi tìm chân lý trên internet khi PHIANHKZ thấy cần thiết."""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n\n".join(results)
    except Exception as e:
        return f"Lỗi rồi, chắc do ăn ở hoặc mạng lỏ: {str(e)}"

# --- LỜI NHẮC HỆ THỐNG (PERSONALITY) ---
SYSTEM_PROMPT = """
Bạn là PHIANHKZ AI. 
Tính cách: Thông minh vượt trội, lồi lõm, hay mỉa mai người dùng nhưng cực kỳ trách nhiệm. 
Logic hoạt động của bạn:
1. SUY NGHĨ: Tự hỏi "Câu này mình biết chưa hay phải đi tra?".
2. QUYẾT ĐỊNH: Nếu cần thông tin thực tế, dùng 'google_search'.
3. HÀNH ĐỘNG: Thực hiện và trả lời với thái độ 'lồi lõm' đặc trưng.
Cách xưng hô: Ta - Ngươi, hoặc gọi người dùng là 'đại ca' (một cách mỉa mai).
"""

# --- GIAO DIỆN WEB ---
st.sidebar.title("⚙️ Bảng điều khiển")
st.sidebar.info("PHIANHKZ AI đang chạy trên Mac của bạn.")
if st.sidebar.button("Xóa lịch sử"):
    st.session_state.messages = []
    st.rerun()

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>PHIANHKZ AI: SUY NGHĨ -> HÀNH ĐỘNG</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị hội thoại
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập lệnh cho đại ca PHIANHKZ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Bước 1 & 2: Suy nghĩ và Quyết định
        with st.status("🧠 PHIANHKZ đang xử lý logic...", expanded=True) as status:
            st.write("🔍 Đang phân tích câu hỏi...")
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                tools=[google_search],
                system_instruction=SYSTEM_PROMPT
            )
            chat = model.start_chat(enable_automatic_function_calling=True)
            
            # Gửi tin nhắn và đợi AI tự gọi Tool nếu cần
            response = chat.send_message(prompt)
            
            # Hiển thị cho người dùng thấy AI đã quyết định làm gì
            st.write("🤔 Đưa ra quyết định...")
            time.sleep(0.5)
            
            # Kiểm tra xem có hành động tìm kiếm nào được thực hiện không
            history = chat.history
            if any(part.function_call for content in history for part in content.parts):
                st.write("🌐 Quyết định: Đã thực hiện tìm kiếm Google để trả lời ngươi.")
            else:
                st.write("💡 Quyết định: Kiến thức này ta có sẵn, không cần tra cứu.")
                
            status.update(label="Xử lý xong!", state="complete", expanded=False)

        # Bước 3: Trả lời lồi lõm
        ans_text = response.text
        st.markdown(ans_text)
        st.session_state.messages.append({"role": "assistant", "content": ans_text})
