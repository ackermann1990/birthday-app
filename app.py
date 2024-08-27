import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Funktion zur Erkennung von Vorname, Nachname und Geburtsdatum
def detect_columns(data):
    columns = data.columns.str.lower()
    
    name_columns = [col for col in columns if re.search(r'vorname|nachname|name', col)]
    birthdate_columns = [col for col in columns if re.search(r'geburt|birth', col)]
    
    detected = {
        'name': None,
        'birthdate': None
    }
    
    # Kombiniere Vorname und Nachname oder verwende nur "Name"
    if len(name_columns) >= 2:
        detected['name'] = name_columns
    elif len(name_columns) == 1:
        detected['name'] = name_columns[0]
    
    # Verwende das Geburtsdatum
    if len(birthdate_columns) >= 1:
        detected['birthdate'] = birthdate_columns[0]
    
    return detected

# Funktion zur Verarbeitung der Daten
def process_data(data, columns):
    if isinstance(columns['name'], list):
        data['Name'] = data[columns['name'][0]].astype(str) + ' ' + data[columns['name'][1]].astype(str)
    else:
        data['Name'] = data[columns['name']].astype(str)
    
    data['Geburtsdatum'] = pd.to_datetime(data[columns['birthdate']], errors='coerce')
    data.dropna(subset=['Geburtsdatum'], inplace=True)  # Entfernt Zeilen mit ungültigen Geburtsdaten
    
    outlook_df = pd.DataFrame()

    outlook_df['Subject'] = data['Name'] + ' Geburtstag'
    outlook_df['Start Date'] = data['Geburtsdatum'].dt.strftime('%m/%d/%Y')
    outlook_df['Start Time'] = '08:00 AM'
    outlook_df['End Date'] = data['Geburtsdatum'].dt.strftime('%m/%d/%Y')
    outlook_df['End Time'] = '08:30 AM'
    outlook_df['All Day Event'] = 'True'
    outlook_df['Reminder on/off'] = 'True'
    outlook_df['Reminder Date'] = outlook_df['Start Date']
    outlook_df['Reminder Time'] = '08:00 AM'

    return outlook_df

# Streamlit App
st.title('Outlook-Geburtstagserinnerung Webapp')

uploaded_file = st.file_uploader('Laden Sie Ihre CSV-Datei mit Kundendaten hoch', type='csv')

if uploaded_file is not None:
    # CSV-Datei in DataFrame laden
    df = pd.read_csv(uploaded_file)

    st.write('Original CSV-Daten:')
    st.write(df)

    # Automatische Erkennung der relevanten Spalten
    detected_columns = detect_columns(df)

    if detected_columns['name'] is not None and detected_columns['birthdate'] is not None:
        st.success(f"Gefundene Spalten: Name = {detected_columns['name']}, Geburtsdatum = {detected_columns['birthdate']}")
        
        # Outlook-kompatible CSV erstellen
        outlook_df = process_data(df, detected_columns)

        st.write('Outlook-kompatible CSV-Daten:')
        st.write(outlook_df)

        # Datei zum Download anbieten
        csv = outlook_df.to_csv(index=False)
        st.download_button(
            label='Download Outlook CSV',
            data=csv,
            file_name='outlook_birthdays.csv',
            mime='text/csv'
        )
    else:
        st.error('Die notwendigen Spalten konnten nicht automatisch erkannt werden. Bitte stellen Sie sicher, dass Vor- und Nachname sowie Geburtsdatum in der Datei enthalten sind.')


