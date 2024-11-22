import streamlit as st
import google.generativeai as genai
import numpy as np

api_key = "AIzaSyA2eHaMYGf4-pM92oLroLYojBOfgMWlbmY"
genai.configure(api_key=api_key)

# ตั้งค่าไพ่ยิปซี
tarot_deck = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgment", "The World"
]

# ฟังก์ชันสำหรับสุ่มไพ่
def draw_tarot_card(seed_number, user_seed):
    combined_seed = seed_number + user_seed
    np.random.seed(combined_seed)
    return np.random.choice(tarot_deck)

# ฟังก์ชันตั้งค่า agent ต่าง ๆ
def configure_agent(model_name):
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Error configuring model {model_name}: {e}")
        return None

# แอปหลัก
def Adinaw():
    st.title("🔮 Adinaw Horoscopes")
    
    # การจัดการสถานะ
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "greeted" not in st.session_state:
        st.session_state.greeted = False
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "expect_random_number" not in st.session_state:
        st.session_state.expect_random_number = False

    # ตั้งค่าเอเจนต์
    tarot_agent = configure_agent("gemini-pro")
    conversation_agent = configure_agent("gemini-pro")

    if not tarot_agent or not conversation_agent:
        return

    # แสดงประวัติการสนทนา
    for role, message in st.session_state.chat_history:
        st.chat_message(role).markdown(message)

    # ทักทายผู้ใช้ครั้งแรก
    if not st.session_state.greeted:
        greeting_prompt = """
        คุณคือผู้ทำนายดวงชะตาด้วยไพ่ยิปซี ชื่อ Adinaw ทักทายผู้ใช้ด้วยคำพูดที่สร้างมนต์ขลัง อธิบายทุกอย่างให้ดูมีมนต์ขลัง
        ให้คุณใช้หลักการทางจิตวิทยาผสมผสานเข้ากับเทคนิคการพูด เพื่อสร้างความขลังและความน่าเชื่อถือ แก่ user (ไม่ต้องบอก user) 
        อธิบายบริการของคุณและแนะนำหัวข้อที่สามารถทำนายได้ เช่น การงาน สุขภาพ ความรัก ฯลฯ อธิบายให้ดูเหมือนอยู่ในโลกจอมขมังเวทย์ แทนตัวว่าข้าและเจ้า
        """
        try:
            response = tarot_agent.generate_content(greeting_prompt)
            bot_response = response.text
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)
            st.session_state.greeted = True
        except Exception as e:
            st.error(f"Error generating AI greeting: {e}")

    # รับข้อมูลจากผู้ใช้
    user_input = st.chat_input("ใส่เรื่องราวที่เจ้าสอบถาม... (exit หากเจ้าอยากเปลี่ยนเรื่องถาม)")
    if user_input:
        if user_input.lower() == "exit":
            st.session_state.current_topic = None
            st.session_state.expect_random_number = False
            st.session_state.chat_history.append(("user", user_input))
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown("เจ้าต้องการถามเรื่องนี้งั้นรึ งั้นมาลองดูกัน...")
            return

        st.session_state.chat_history.append(("user", user_input))
        st.chat_message("user").markdown(user_input)

        if st.session_state.current_topic is None:
            st.session_state.current_topic = user_input
            st.session_state.expect_random_number = True
            st.chat_message("assistant").markdown(
                "ไหนลองบอกเลขที่เจ้าชอบมาซักหนึ่งตัว อะไรก็ได้"
            )
        elif st.session_state.expect_random_number:
            try:
                user_seed = int(user_input)
                seed_number = sum(ord(char) for char in st.session_state.current_topic)
                drawn_card = draw_tarot_card(seed_number, user_seed)
                tarot_prompt = f"""
                เรื่องที่ผู้ใช้ถาม: {st.session_state.current_topic}
                ไพ่ที่สุ่มได้คือ: {drawn_card}
                โปรดแปลความหมายของไพ่นี้เพื่อทำนายเรื่องดังกล่าว แปลตามความหมายของไผ่ ให้เกี่ยวข้องกับเรื่องราวที่ user
                ต้องการสอบถาม และใช้หลักทางจิตวิทยาและการพูดเพื่อสร้างความขลังของการทำนายและสร้างความน่าเชื่อถือ
                อธิบายให้ดูเหมือนอยู่ในโลกจอมขมังเวทย์ แทนตัวเองว่าข้าและเจ้า
                """
                response = tarot_agent.generate_content(tarot_prompt)
                bot_response = f"🔮 ไพ่ที่เจ้าสุ่มได้คือ **{drawn_card}**\n\nคำทำนาย: {response.text}"
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)
                st.session_state.expect_random_number = False
            except ValueError:
                st.chat_message("assistant").markdown("ข้าต้องการแค่ตัวเลขเท่านั้น")
        else:
            conversation_prompt = f"""
            ตีความหมายเพิ่มเติม: "{st.session_state.current_topic}"\n
            ผู้ใช้ถามว่า: {user_input}
            โปรดขยายความเพิ่มเติม โดยใช้หลักทางจิตวิทยาและการพูดเพื่อสร้างความขลังของการทำนายและสร้างความน่าเชื่อถือ
            อธิบายให้ดูเหมือนอยู่ในโลกจอมขมังเวทย์ แทนตัวเองว่าข้าและเจ้า
            """
            response = conversation_agent.generate_content(conversation_prompt)
            bot_response = response.text.strip()
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)