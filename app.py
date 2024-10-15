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
    if pd.isna(date_value) or date_value == '':
        return None
    if isinstance(date_value, datetime):
        return date_value
    try:
        return datetime.strptime(str(date_value).split()[0], '%Y-%m-%d')
    except ValueError:
        return None

# Funktion, um das Alter zu berechnen
def calculate_age(birthdate):
    today = datetime.now()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Funktion, um die ICS-Datei zu erstellen
def create_ics_file(df):
    calendar = Calendar()
    current_year = datetime.now().year
    
    for index, row in df.iterrows():
        event = Event()
        full_name = f"{row['Vorname']} {row['Nachname']}"
        
        # Verarbeite das Geburtsdatum
        geburtstag = parse_date(row['Geburtsdatum'])
        if not geburtstag:
            continue  # Überspringe diesen Eintrag, falls das Geburtsdatum ungültig ist
        
        geburtstag_in_current_year = geburtstag.replace(year=current_year)
        age = calculate_age(geburtstag)
        
        event.name = f"Geburtstag: {full_name}"
        
        event.begin = geburtstag_in_current_year
        event.make_all_day()  # Als ganztägiges Ereignis
        
        # Fügt eine Erinnerung um 09:00 Uhr am Geburtstag hinzu
        alarm = DisplayAlarm(trigger=timedelta(hours=9))
        event.alarms.append(alarm)
        
        # Kontaktinformationen und Adresse formatieren
        contact_info = ""
        
        if pd.notna(row['Feld6']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Feld6'])}\n\n"
        
        if pd.notna(row['Email']):
            contact_info += f"E-Mail: {row['Email']}\n\n"
        
        address = row['StrasseUndNr'] if pd.notna(row['StrasseUndNr']) else ""
        if pd.notna(row['Adresszeile1']):
            address += f", {row['Adresszeile1']}"
        if pd.notna(row['Adresszeile2']):
            address += f" {row['Adresszeile2']}"

        address = address.strip()
        contact_info += f"{address}\n{row['PLZ']} {row['Ort']}" if address else f"{row['PLZ']} {row['Ort']}"

        # Geburtsjahr und aktuelles Alter hinzufügen
        contact_info += f"\n\nGeburtsjahr: {geburtstag.year}\nAktuelles Alter: {age} Jahre"
        
        event.description = contact_info
        
        # UID und DTSTAMP hinzufügen
        event.uid = str(uuid.uuid4())
        event.dtstamp = datetime.now()
        
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
