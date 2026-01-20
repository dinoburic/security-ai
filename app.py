import streamlit as st
import os
from groq import Groq

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="cveorg",
    page_icon="",
    layout="wide"
)

# --- SIDEBAR (POSTAVKE) ---
with st.sidebar:
    st.title("⚙️ Konfiguracija")
    # Vratio sam ovo na input polje zbog sigurnosti. 
    # NEMOJ hardkodirati ključ u fajl ako ćeš ga dijeliti ili slikati!
    if "GROQ_API_KEY" in st.secrets:
        st.success("API Key učitan iz secrets fajla! 🔒")
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        # Ako nema fajla, traži ručni unos
        api_key = st.text_input("Unesi Groq API Key:", type="password")
    
    # Model koji si koristio u svom kodu
    model_option = st.selectbox(
        "Odaberi Model:",
        ("llama-3.3-70b-versatile", "mixtral-8x7b-32768") 
    )
    st.info("Ovaj asistent je specijalizovan za Kali Linux, Nmap analizu i CVE remedijaciju.")

# --- INICIJALIZACIJA KLIJENTA ---
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Greška pri konekciji: {e}")
        st.stop()
else:
    st.warning("Molimo unesi API ključ da bi započeo.")
    st.stop()

# --- SYSTEM PROMPT ---
system_prompt = """
Ti si iskusni Senior Penetration Tester i Security Engineer. Tvoje okruženje je isključivo Kali Linux.
Tvoj zadatak je da pomažeš korisniku u etičkom hakiranju i osiguravanju sistema.

Tvoje ključne kompetencije su:
1.  Kali Linux & Networking: Znaš sve komande za konfiguraciju mreže.
2.  Nmap Ekspertiza: Znaš interpretirati kompleksne Nmap ispise.
3.  Vulnerability Assessment: Identificiraš CVE na osnovu verzija servisa.
4.  Remedijacija: Za svaku ranjivost daješ konkretan način kako je popraviti.

Pravila:
- Budi tehnički precizan.
- Koristi markdown blokove za kod.
- Odbij ilegalne zahtjeve.
"""

# --- CHAT HISTORIJA ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Zdravo! Ja sam tvoj Pentest asistent. Pošalji mi Nmap scan output ili me pitaj o konfiguraciji Kali Linuxa."}
    ]

# --- PRIKAZ PORUKA ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- POMOĆNA FUNKCIJA ZA STREAMING ---
# Ovo je ključni dio koji popravlja tvoj problem sa JSON ispisom
def generate_chat_responses(stream_response):
    for chunk in stream_response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- OBRADA UNOSA KORISNIKA ---
if prompt := st.chat_input("Unesi komandu, Nmap output ili pitanje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            temperature=0.5,
            max_tokens=2048
        )
        
        # Ovdje koristimo pomoćnu funkciju da izvučemo samo tekst
        response = st.write_stream(generate_chat_responses(stream))
    

    st.session_state.messages.append({"role": "assistant", "content": response})
