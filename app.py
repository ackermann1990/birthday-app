import streamlit as st
import pandas as pd
from ics import Calendar, Event, DisplayAlarm
from datetime import datetime, timedelta
import uuid

# Funktion, um einen WhatsApp-Link zu generieren
def generate_whatsapp_link(phone_number):
    return f"https://wa.me/{phone_number}"

# Funktion, um das Geburtsdatum zu verarbeiten
def parse_date(date_value):
    if isinstance(date_value, datetime):
        # Falls das Datum bereits als datetime-Objekt vorliegt, direkt zurückgeben
        return date_value
    try:
        # Entferne den Zeitanteil (falls vorhanden) und verarbeite nur das Datum
        return datetime.strptime(str(date_value).split()[0], '%Y-%m-%d')
    except ValueError:
        return None  # Geburtsdatum ist ungültig, None zurückgeben

# Funktion, um die ICS-Datei zu erstellen
def create_ics_file(df):
    calendar = Calendar()
    current_year = datetime.now().year
    
    for index, row in df.iterrows():
        event = Event()
        full_name = f"{row['Vorname']} {row['Nachname']}"
        event.name = f"Geburtstag: {full_name}"
        
        # Verarbeite das Geburtsdatum
        geburtstag = parse_date(row['Geburtsdatum'])
        if not geburtstag:
            # Wenn das Geburtsdatum nicht verarbeitet werden kann, überspringe diesen Eintrag
            continue
        
        geburtstag = geburtstag.replace(year=current_year)  # Setze das Jahr auf das aktuelle Jahr
        
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
        
        # Adresse formatieren und nur gültige Teile einfügen
        address = row['StrasseUndNr'] if pd.notna(row['StrasseUndNr']) else ""
        if pd.notna(row['Adresszeile1']):
            address += f", {row['Adresszeile1']}"
        if pd.notna(row['Adresszeile2']):
            address += f" {row['Adresszeile2']}"

        address = address.strip()  # Entferne mögliche führende oder abschließende Leerzeichen
        contact_info += f"{address}\n{row['PLZ']} {row['Ort']}" if address else f"{row['PLZ']} {row['Ort']}"

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

uploaded_file = st.file_uploader("Laden Sie Ihre Excel-Datei hoch", type=["xlsx"])

if uploaded_file is not None:
    # Lese die Excel-Datei mit der Engine 'openpyxl' für .xlsx-Dateien
    df = pd.read_excel(uploaded_file, engine='openpyxl')
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
