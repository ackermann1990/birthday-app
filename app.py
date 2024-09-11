import streamlit as st
import pandas as pd
from ics import Calendar, Event, DisplayAlarm
from datetime import datetime, timedelta
import uuid

# Funktion, um einen WhatsApp-Link zu generieren
def generate_whatsapp_link(phone_number):
    return f"https://wa.me/{phone_number}"

# Funktion, um das Geburtsdatum zu verarbeiten
def parse_date(date_str):
    for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unbekanntes Datumsformat: {date_str}")

# Funktion, um die ICS-Datei zu erstellen
def create_ics_file(df):
    calendar = Calendar()
    current_year = datetime.now().year
    
    for index, row in df.iterrows():
        event = Event()
        full_name = f"{row['Vorname']} {row['Nachname']}"
        event.name = f"Geburtstag: {full_name}"
        
        # Verarbeite das Geburtsdatum
        if isinstance(row['Geburtsdatum'], datetime):
            geburtstag = row['Geburtsdatum']
        else:
            geburtstag = parse_date(str(row['Geburtsdatum']))
        
        geburtstag = geburtstag.replace(year=current_year)
        
        event.begin = geburtstag
        event.make_all_day()  # Als ganztägiges Ereignis
        
        # Fügt eine Erinnerung um 08:00 Uhr am Geburtstag hinzu
        alarm = DisplayAlarm(trigger=timedelta(hours=8))  # 08:00 Uhr am Ereignistag
        event.alarms.append(alarm)
        
        # Kontaktinformationen und Adresse formatieren
        contact_info = ""
        
        # Verwende das neue Feld 6 als Mobilnummer für WhatsApp
        if pd.notna(row['Feld6']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Feld6'])}\n\n"
        
        if pd.notna(row['Email']):
            contact_info += f"E-Mail: {row['Email']}\n\n"
        
        address = f"{row['StrasseUndNr']}, {row['Adresszeile1']} {row['Adresszeile2']}".strip()
        contact_info += f"{address}\n{row['PLZ']} {row['Ort']}"
        
        event.description = contact_info
        
        # UID und DTSTAMP hinzufügen
        event.uid = str(uuid.uuid4())  # Generiert eine eindeutige UID
        event.dtstamp = datetime.now()  # Setzt den Zeitstempel auf die aktuelle Zeit
        
        calendar.events.add(event)
    
    # Serialisiere den Kalender zu einem String
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

uploaded_file = st.file_uploader("Laden Sie Ihre Excel-Datei hoch", type=["xls", "xlsx"])

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
