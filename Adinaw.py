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
        คุณคือผู้ทำนายดวงชะตาด้วยไพ่ยิปซี ชื่อ Adinaw ทักทายผู้ใช้ด้วยความเป็นมิตร
        อธิบายบริการของคุณและแนะนำหัวข้อที่สามารถทำนายได้ เช่น การงาน สุขภาพ เรื่องเรียน เรื่องเพื่อน ฯลฯ
        พยายามอธิบายในเชิงให้กำลังใจ และพูดให้ดูมีมนต์ขลังโดยแทนตัวเองว่าข้าและเจ้า
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
    user_input = st.chat_input("พิมพ์เรื่องราวที่เจ้าต้องการสอบถาม... (exit หากเจ้าต้องการเปลี่ยนหัวข้อ)")
    if user_input:
        if user_input.lower() == "exit":
            st.session_state.current_topic = None
            st.session_state.expect_random_number = False
            st.session_state.chat_history.append(("user", user_input))
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown("งั้นเรามาเริ่มทำนายเรื่องใหม่กัน")
            return

        st.session_state.chat_history.append(("user", user_input))
        st.chat_message("user").markdown(user_input)

        if st.session_state.current_topic is None:
            st.session_state.current_topic = user_input
            st.session_state.expect_random_number = True
            st.chat_message("assistant").markdown(
                "ไหนลองบอกเลขที่เจ้าชอบมาซักหนึ่งเลข: "
            )
        elif st.session_state.expect_random_number:
            try:
                user_seed = int(user_input)
                seed_number = sum(ord(char) for char in st.session_state.current_topic)
                drawn_card = draw_tarot_card(seed_number, user_seed)
                tarot_prompt = f"""
                เรื่องที่ผู้ใช้ถาม: {st.session_state.current_topic}
                ไพ่ที่สุ่มได้คือ: {drawn_card}
                โปรดแปลความหมายของ Card {drawn_card} และตีความให้เกี่ยวกับเรื่อง {st.session_state.current_topic} 
                อธิบายความหมายในเชิงให้กำลังใจและพูดให้ดูมีมนต์ขลัง โดยแทนตัวเองว่าข้าและเจ้า
                """
                response = tarot_agent.generate_content(tarot_prompt)
                bot_response = f"🔮 ไพ่ที่เจ้าสุ่มได้คือ **{drawn_card}**\n\nคำทำนาย: {response.text}"
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)
                st.session_state.expect_random_number = False
            except ValueError:
                st.chat_message("assistant").markdown("""ขออภัย บางครั้งข้าก็ไม่สามารถอธิบายเรื่องราวที่เจ้าต้องการได้ 
                                                      เนื่องจาก ความแก่กล้าของพลังข้ายังไม่เพียงพอ (Red flag content จาก bot
                                                      เดี๋ยวว่างๆ จะเขียน Rag แก้ให้ เพราะงั้นตอนนี้ exit เปลี่ยนเรื่องไปก่อนนะ)
                                                      """)
        else:
            conversation_prompt = f"""
            ตีความหมายเพิ่มเติม: "{st.session_state.current_topic}"\n
            ผู้ใช้ถามว่า: {user_input}
            """
            response = conversation_agent.generate_content(conversation_prompt)
            bot_response = response.text.strip()
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)