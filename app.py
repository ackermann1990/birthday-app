import streamlit as st

st.title("Meine erste Streamlit Webapp")
st.write("Willkommen zu meiner Streamlit-App!")

name = st.text_input("Gib deinen Namen ein:")
if name:
    st.write(f"Hallo, {name}!")
