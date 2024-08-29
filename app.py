import streamlit as st
import pandas as pd
from ics import Calendar, Event, DisplayAlarm
from datetime import datetime, timedelta
import uuid

# Funktion, um einen WhatsApp-Link zu generieren
def generate_whatsapp_link(phone_number):
    return f"https://wa.me/{phone_number}"

# Funktion, um die ICS-Datei zu erstellen
def create_ics_file(df):
    calendar = Calendar()
    current_year = datetime.now().year
    
    for index, row in df.iterrows():
        event = Event()
        full_name = f"{row['Vorname']} {row['Name']}"
        event.name = f"Geburtstag: {full_name}"
        
        # Setzt das Startdatum des Events auf den Geburtstag im aktuellen Jahr
        geburtstag = datetime.strptime(row['Geburtsdatum'], '%d.%m.%Y')
        geburtstag = geburtstag.replace(year=current_year)
        
        event.begin = geburtstag
        event.make_all_day()  # Als ganztägiges Ereignis
        
        # Jährlich wiederkehrend
        event.recurrence = 'FREQ=YEARLY'
        
        # Fügt eine Erinnerung um 08:00 Uhr am Geburtstag hinzu
        alarm = DisplayAlarm(trigger=timedelta(hours=8))  # 08:00 Uhr am Ereignistag
        event.alarms.append(alarm)
        
        # Adresse und Kontaktlink
        address = f"{row['PLZ']} {row['Ort']}"
        contact_info = f"Adresse: {address}\n"
        
        if pd.notna(row['Mobilnummer']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Mobilnummer'])}\n"
        
        if pd.notna(row['Emailadresse']):
            contact_info += f"E-Mail: {row['Emailadresse']}"
        
        event.description = contact_info
        
        # UID und DTSTAMP hinzufügen
        event.uid = str(uuid.uuid4())  # Generiert eine eindeutige UID
        event.dtstamp = datetime.now()  # Setzt den Zeitstempel auf die aktuelle Zeit
        
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
