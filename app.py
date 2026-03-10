import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid

# ... (parse_date, calculate_new_age, generate_whatsapp_link bleiben gleich)

def create_ics_file(df):
    current_year = datetime.now().year
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Geburtstags-Generator//DE",
    ]

    for index, row in df.iterrows():
        full_name = f"{row['Vorname']} {row['Nachname']}"
        geburtstag = parse_date(row['Geburtsdatum'])
        if not geburtstag:
            continue

        geburtstag_in_current_year = geburtstag.replace(year=current_year)
        new_age = calculate_new_age(geburtstag)

        # Kontaktinfos aufbauen (gleiche Logik wie vorher)
        contact_info = ""
        if pd.notna(row['Feld6']):
            contact_info += f"WhatsApp: {generate_whatsapp_link(row['Feld6'])}\\n\\n"
        if pd.notna(row['Email']):
            contact_info += f"E-Mail: {row['Email']}\\n\\n"
        address = row['StrasseUndNr'] if pd.notna(row['StrasseUndNr']) else ""
        if pd.notna(row['Adresszeile1']):
            address += f", {row['Adresszeile1']}"
        if pd.notna(row['Adresszeile2']):
            address += f" {row['Adresszeile2']}"
        address = address.strip()
        contact_info += f"{address}\\n{row['PLZ']} {row['Ort']}" if address else f"{row['PLZ']} {row['Ort']}"
        contact_info += f"\\n\\nGeburtsjahr: {geburtstag.year} (wird heute {new_age})"

        date_str = geburtstag_in_current_year.strftime("%Y%m%d")
        now_str = datetime.now().strftime("%Y%m%dT%H%M%SZ")

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}",
            f"DTSTAMP:{now_str}",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"SUMMARY:Geburtstag: {full_name}",
            f"DESCRIPTION:{contact_info}",
            "RRULE:FREQ=YEARLY",
            "BEGIN:VALARM",
            "TRIGGER;RELATED=START:PT9H",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Geburtstag: {full_name}",
            "END:VALARM",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\n".join(lines)
