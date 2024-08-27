import streamlit as st
import requests
from icalendar import Calendar, Event
from datetime import datetime
from io import BytesIO

# Titel der App
st.title("Kunden Geburtstags-ICS Datei Generator")

# Button zur Auslösung des Prozesses
if st.button('Geburtstagsdaten aktualisieren und ICS-Datei generieren'):
    # Beispiel-API-URL und Header (passen Sie diese an Ihre API an)
    api_url = "https://api.tarif590.ch/kunden"  # Beispiel-URL
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}  # Ersetzen Sie dies mit Ihrem API-Token
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        kontakte_liste = response.json()  # Annahme: JSON-Antwort mit den Kundendaten
        
        # ICS Datei erstellen
        cal = Calendar()

        for kontakt in kontakte_liste:
            event = Event()
            event.add('summary', f"Geburtstag von {kontakt['name']}")
            event.add('dtstart', datetime.strptime(kontakt['geburtsdatum'], '%Y-%m-%d'))
            event.add('description', f"Kontaktdetails: {kontakt['email']}, {kontakt['telefonnummer']}")
            event.add('rrule', {'freq': 'yearly'})

            cal.add_component(event)

        # ICS-Datei als Download bereitstellen
        ics_file = BytesIO(cal.to_ical())
        ics_file_name = "geburtstage.ics"
        st.download_button(
            label="ICS-Datei herunterladen",
            data=ics_file,
            file_name=ics_file_name,
            mime="text/calendar"
        )
    else:
        st.error(f"API Anfrage fehlgeschlagen: {response.status_code}")
