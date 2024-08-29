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
        full_name = f"{row['Vorname']} {row['Nachname']}"
        event.name = f"Geburtstag: {full_name}"
        
        # Setzt das Startdatum des Events auf den Geburtstag im aktuellen Jahr
        geburtstag = datetime.strptime(row['Geburtsdatum'], '%d.%m.%Y')
        geburtstag = geburtstag.replace(year=current_year)
        
        event.begin = geburtstag
        event.make_all_day()  # Als ganztägiges Ereignis
        
        # Fügt die Wiederholungsregel manuell hinzu
        event.extra.append("RRULE:FREQ=YEARLY")
        
        # Fügt eine Erinnerung um 08:00 Uhr am Geburtstag hinzu
        alarm = DisplayAlarm(trigger=timedelta(hours=8))  # 08:00 Uhr am Ereignistag
        event.alarms.append(alarm)
        
        # Kontaktinformationen und Adresse formatieren
        contact_info = ""
        
        if pd.notna(row['Tel M']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Tel M'])}\n\n"
        
        if pd.notna(row['Email']):
            contact_info += f"E-Mail: {row['Email']}\n\n"
        
        address = f"{row['Strasse']}, {row['Adresszeile 1']} {row['Adresszeile 2']}".strip()
        contact_info += f"{address}\n{row['PLZ']} {row['Ort']}"
        
        event.description = contact_info
        
        # UID und DTSTAMP hinzufügen
        event.uid = str(uuid.uuid4())  # Generiert eine eindeutige UID
        event.dtstamp = datetime.now()  # Setzt den Zeitstempel auf die aktuelle Zeit
        
        calendar.events.add(event)
    
    # Serialisiere den Kalender zu einem String und füge die RRULE hinzu
    ics_content = str(calendar)
    
    # Füge die RRULE für jedes Event manuell hinzu
    ics_lines = []
    for line in ics_content.splitlines():
        ics_lines.append(line)
        if line.startswith("BEGIN:VEVENT"):
            ics_lines.append("RRULE:FREQ=YEARLY")
    
    return "\n".join(ics_lines)

# Streamlit-App
st.title('Geburtstags-ICS-Datei Generator')

uploaded_file = st.file_uploader("Laden Sie Ihre Excel-Datei hoch", type=["xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Ihre hochgeladene Excel-Datei:")
    st.dataframe(df)
    
    if st.button('ICS-Datei generieren'):
        ics_content = create_ics_file(df)
        
        st.download_button(
            label="ICS-Datei herunterladen",
            data=ics_content,
            file_name='geburtstage.ics',
            mime='text/calendar'
        )
