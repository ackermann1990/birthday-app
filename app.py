import streamlit as st
import pandas as pd
from ics import Calendar, Event
from datetime import datetime
from urllib.parse import quote

# Funktion, um einen WhatsApp-Link zu generieren
def generate_whatsapp_link(phone_number):
    return f"https://wa.me/{phone_number}"

# Funktion, um die ICS-Datei zu erstellen
def create_ics_file(df):
    calendar = Calendar()
    
    for index, row in df.iterrows():
        event = Event()
        full_name = f"{row['Vorname']} {row['Name']}"
        event.name = f"Geburtstag: {full_name}"
        
        # Setzt das Startdatum des Events auf den Geburtstag
        geburtstag = datetime.strptime(row['Geburtsdatum'], '%d.%m.%Y')
        event.begin = geburtstag.replace(hour=8, minute=0)
        event.make_all_day()
        
        # Fügt eine Erinnerung um 08:00 Uhr am Geburtstag hinzu
        event.alarms.append('-PT0H0M')
        
        # Adresse und Kontaktlink
        address = f"{row['PLZ']} {row['Ort']}"
        contact_info = f"Adresse: {address}\n"
        
        if pd.notna(row['Mobilnummer']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Mobilnummer'])}"
        elif pd.notna(row['Emailadresse']):
            contact_info += f"E-Mail: {row['Emailadresse']}"
        
        event.description = contact_info
        
        calendar.events.add(event)
    
    return calendar

# Streamlit-App
st.title('Geburtstags-ICS-Datei Generator')

uploaded_file = st.file_uploader("Laden Sie Ihre CSV-Datei hoch", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=';')
    st.write("Ihre hochgeladene CSV-Datei:")
    st.dataframe(df)
    
    if st.button('ICS-Datei generieren'):
        calendar = create_ics_file(df)
        ics_content = str(calendar)
        
        st.download_button(
            label="ICS-Datei herunterladen",
            data=ics_content,
            file_name='geburtstage.ics',
            mime='text/calendar'
        )
