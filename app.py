import streamlit as st
import re
from agent_core import classify_intent, get_clarifying_question, recommend_tiered, get_order_status, SHOP_PHONE

st.set_page_config(page_title="AI Sales Agent — Demo", page_icon="🛠️", layout="centered")
st.title("🛠️ AI Sales Agent — Demo (χωρίς εξάρτηση από το live site)")
st.caption("Τοπικό demo πάνω στο curated Products_AI dataset (422 προϊόντα, 187 κατηγορίες) + fallback στον πλήρη κατάλογο (1.027 προϊόντα).")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_need" not in st.session_state:
    st.session_state.pending_need = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("products"):
            st.write(msg["content"])
            for p in msg["products"]:
                cols = st.columns([1, 2])
                with cols[0]:
                    if p.get("image"):
                        try:
                            st.image(p["image"], width=120)
                        except Exception:
                            pass
                with cols[1]:
                    st.markdown(f"**{p['tier']}**")
                    st.markdown(f"{p['name']}")
                    st.markdown(f"💶 **€{p['price']:.2f}** (με ΦΠΑ) — {p['stock_status']}")
                    if p.get("url"):
                        st.markdown(f"[Δες το προϊόν]({p['url']})")
        else:
            st.write(msg["content"])

user_input = st.chat_input("Γράψε το μήνυμά σου σαν πελάτης...")

NO_MATCH_MSG = f"Δεν έχω αυτή τη στιγμή ακριβή πρόταση για αυτή την ανάγκη. Μπορείς να καλέσεις το μαγαζί στο **{SHOP_PHONE}** — θα σε βοηθήσουν να βρεις ακριβώς αυτό που ψάχνεις. 📞"

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.pending_need:
        combined_query = f"{st.session_state.pending_need} {user_input}"
        st.session_state.pending_need = None
        result = recommend_tiered(combined_query)
        if result["products"]:
            note = " (από τον πλήρη κατάλογο)" if result.get("source") == "full_catalog" else ""
            reply_text = f"Βάσει αυτού που μου είπες, να τι προτείνω από την κατηγορία **{result['category']}**{note}:"
            st.session_state.messages.append({"role": "assistant", "content": reply_text, "products": result["products"]})
        else:
            st.session_state.messages.append({"role": "assistant", "content": NO_MATCH_MSG})

    else:
        intent = classify_intent(user_input)

        if intent == "order_status":
            m = re.search(r"\d{4,}", user_input)
            if not m:
                reply = "Πες μου τον αριθμό παραγγελίας σου για να ελέγξω την κατάσταση."
            else:
                order = get_order_status(m.group())
                if order:
                    reply = f"Η παραγγελία σου είναι: **{order['status']}**."
                    if order.get("tracking"):
                        reply += f" Courier: {order['courier']}, tracking: `{order['tracking']}`"
                else:
                    reply = "Δεν βρήκα παραγγελία με αυτόν τον αριθμό. Επιβεβαίωσε τον αριθμό ή δώσε μου το email της παραγγελίας."
            st.session_state.messages.append({"role": "assistant", "content": reply})

        elif intent == "consultative":
            question = get_clarifying_question(user_input)
            st.session_state.pending_need = user_input
            st.session_state.messages.append({"role": "assistant", "content": question})

        else:
            result = recommend_tiered(user_input)
            if result["products"]:
                note = " (από τον πλήρη κατάλογο)" if result.get("source") == "full_catalog" else ""
                reply_text = f"Να τι προτείνω από την κατηγορία **{result['category']}**{note}:"
                st.session_state.messages.append({"role": "assistant", "content": reply_text, "products": result["products"]})
            else:
                # Weak match on direct product query — offer phone number
                st.session_state.messages.append({"role": "assistant", "content": NO_MATCH_MSG})

    st.rerun()

with st.sidebar:
    st.header("Δοκιμαστικά queries")
    st.code("θέλω ένα δράπανο")
    st.code("θέλω να κόψω έναν τοίχο από μπετόν")
    st.code("ψάχνω γεννήτρια βενζίνης")
    st.code("πού είναι η παραγγελία μου 12345;")
    st.code("θέλω να τρίψω τοίχο")
    st.divider()
    st.caption("⚠️ Το order tracking χρησιμοποιεί mock data (12345, 99999) — θα συνδεθεί με το πραγματικό Vouchers Sheet αργότερα.")
    st.caption(f"📞 Όταν δεν βρίσκεται τίποτα, ο agent δίνει το τηλέφωνο του μαγαζιού: {SHOP_PHONE}")
    if st.button("🔄 Reset conversation"):
        st.session_state.messages = []
        st.session_state.pending_need = None
        st.rerun()

