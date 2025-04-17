import streamlit as st
import sqlite3
import requests
from datetime import datetime

# === DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def create_user_chat_table(username):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS chat_{username} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    question TEXT,
                    answer TEXT
                )''')
    conn.commit()
    conn.close()

def save_chat(username, question, answer):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(f"INSERT INTO chat_{username} (timestamp, question, answer) VALUES (?, ?, ?)",
              (timestamp, question, answer))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute(f"SELECT timestamp, question, answer FROM chat_{username} ORDER BY id DESC LIMIT 20")
    history = c.fetchall()
    conn.close()
    return history[::-1]  # show oldest at top

# === STREAMLIT SESSION STATE ===
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# === LOGIN + REGISTER PAGE ===
def login_page():
    st.title("🔐 Login or Register")
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                create_user_chat_table(username)
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    elif menu == "Register":
        st.subheader("Register New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        if st.button("Register"):
            if new_password != confirm_password:
                st.warning("Passwords do not match")
            elif register_user(new_username, new_password):
                st.success("Account created. You can now login.")
            else:
                st.error("Username already exists")

# === PDF CHATBOT DASHBOARD ===
def chatbot_page():
    st.title("📄 Ollama PDF Chatbot 🤖")
    username = st.session_state['username']
    st.success(f"Welcome, {username}!")

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()

    # SIDEBAR CHAT HISTORY
    st.sidebar.markdown("## 🕘 Chat History")
    history = get_chat_history(username)
    if history:
        for time, q, a in history:
            with st.sidebar.expander(f"🗨️ {q}", expanded=False):
                st.markdown(f"**🕒 {time}**")
                st.markdown(f"{a}")
    else:
        st.sidebar.info("No chat history yet.")

    st.write("Upload a PDF and start asking questions!")

    backend_url = "http://localhost:8000"  # Adjust this as needed

    # Upload PDF
    file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if file:
        with st.spinner("Uploading and processing PDF..."):
            response = requests.post(f"{backend_url}/upload_pdf/", files={"file": file.getvalue()})
            if response.status_code == 200:
                st.success("✅ PDF processed! Ask your question.")
            else:
                st.error("❌ Failed to process PDF.")
                st.error(response.json())

    # Ask a question
    user_input = st.chat_input("Ask a question about the PDF...")
    if user_input:
        st.write(f"**You:** {user_input}")
        with st.spinner("Thinking..."):
            response = requests.post(f"{backend_url}/ask/", data={"question": user_input})
            if response.status_code == 200:
                bot_reply = response.json()["response"]
                st.write(f"**Bot:** {bot_reply}")
                save_chat(username, user_input, bot_reply)  # Save to DB
            else:
                st.error("❌ Error in getting response.")
                st.error(response.json())

# === MAIN ===
init_db()
if st.session_state["authenticated"]:
    chatbot_page()
else:
    login_page()
