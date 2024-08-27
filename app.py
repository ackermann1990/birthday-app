import streamlit as st
import pandas as pd
from datetime import datetime

# Funktion zum Erstellen einer Outlook-kompatiblen CSV für Geburtstage
def create_outlook_birthday_csv(data):
    # Erstellen eines DataFrames für die Outlook-kompatible CSV-Datei
    outlook_df = pd.DataFrame()

    outlook_df['Subject'] = data['Name'] + ' Geburtstag'
    outlook_df['Start Date'] = data['Geburtsdatum'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
    outlook_df['Start Time'] = '08:00 AM'
    outlook_df['End Date'] = data['Geburtsdatum'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
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

    # Annahme: Die CSV-Datei enthält mindestens die Spalten 'Name' und 'Geburtsdatum'
    st.write('Original CSV-Daten:')
    st.write(df)

    # Überprüfen, ob die notwendigen Spalten vorhanden sind
    if 'Name' in df.columns and 'Geburtsdatum' in df.columns:
        # Outlook-kompatible CSV erstellen
        outlook_df = create_outlook_birthday_csv(df)

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
        st.error('Die CSV-Datei muss mindestens die Spalten "Name" und "Geburtsdatum" enthalten.')

