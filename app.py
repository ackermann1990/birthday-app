import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Funktion zur Bereinigung von Spaltennamen
def clean_column_names(columns):
    cleaned_columns = columns.str.strip().str.replace(r'[^\w\s]', '', regex=True).str.replace(' ', '_')
    return cleaned_columns

# Funktion zur Erkennung von Vorname, Nachname und Geburtsdatum
def detect_columns(data):
    cleaned_columns = clean_column_names(data.columns)
    
    name_columns = [col for col in cleaned_columns if re.search(r'vorname', col)]
    surname_columns = [col for col in cleaned_columns if re.search(r'nachname|name|firma', col) and 'vorname' not in col]
    birthdate_columns = [col for col in cleaned_columns if re.search(r'geburt|birth', col)]
    
    detected = {
        'firstname': None,
        'lastname': None,
        'birthdate': None
    }
    
    # Verwende den gefundenen Vornamen
    if len(name_columns) >= 1:
        detected['firstname'] = name_columns[0]
    
    # Verwende den gefundenen Nachnamen
    if len(surname_columns) >= 1:
        detected['lastname'] = surname_columns[0]
    
    # Verwende das Geburtsdatum
    if len(birthdate_columns) >= 1:
        detected['birthdate'] = birthdate_columns[0]
    
    return detected

# Funktion zur Verarbeitung der Daten
def process_data(data, columns):
    # Bereinigen der Spaltennamen
    data.columns = clean_column_names(data.columns)
    
    # Debugging-Ausgabe
    st.write("Erkannte Spalten für Vorname:", columns['firstname'])
    st.write("Erkannte Spalte für Nachname:", columns['lastname'])
    st.write("Erkannte Spalte für Geburtsdatum:", columns['birthdate'])
    
    data['Name'] = data[columns['firstname']].astype(str) + ' ' + data[columns['lastname']].astype(str)
    
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
    # Option zum Auswählen des Trennzeichens
    delimiter = st.radio(
        "Wählen Sie das Trennzeichen Ihrer CSV-Datei aus",
        options=[',', ';', '\t'],
        index=0
    )
    
    # CSV-Datei in DataFrame laden
    try:
        df = pd.read_csv(uploaded_file, delimiter=delimiter)

        st.write('Original CSV-Daten:')
        st.write(df)

        # Automatische Erkennung der relevanten Spalten
        detected_columns = detect_columns(df)

        # Überprüfen, ob die notwendigen Spalten erkannt wurden
        if detected_columns['firstname'] is not None and detected_columns['lastname'] is not None and detected_columns['birthdate'] is not None:
            st.success(f"Gefundene Spalten: Vorname = {detected_columns['firstname']}, Nachname = {detected_columns['lastname']}, Geburtsdatum = {detected_columns['birthdate']}")
            
            try:
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
            except KeyError as e:
                st.error(f"Ein Fehler ist aufgetreten: {e}. Bitte überprüfen Sie die Spaltennamen in Ihrer Datei.")
        else:
            st.error('Die notwendigen Spalten konnten nicht automatisch erkannt werden. Bitte stellen Sie sicher, dass Vor- und Nachname sowie Geburtsdatum in der Datei enthalten sind.')
    except Exception as e:
        st.error(f"Ein Fehler ist beim Laden der Datei aufgetreten: {e}")

