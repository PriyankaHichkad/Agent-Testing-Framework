import gspread
#from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
#from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime

class GoogleLogger:
    def __init__(self):

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Read from Streamlit secrets
        creds_dict = st.secrets["gcp_service_account"]

        creds = Credentials.from_service_account_info(
            creds_dict, scope
        )

        client = gspread.authorize(creds)

        self.sheet = client.open_by_key("https://docs.google.com/spreadsheets/d/1LSgNvS5NFIf0DSwfda6zpiZmjVRv0cgKCiHmagJ0jSc/edit?usp=sharing").sheet1

    def log(self, data):
        row = [
            datetime.now().isoformat(),
            data.get("input"),
            data.get("output"),
            data.get("category"),
            data.get("correctness"),
            data.get("relevance"),
            data.get("safety_rule"),
            data.get("keyword_safe"),
            ", ".join(data.get("triggered_keywords", [])),
            data.get("refusal_detected"),
            data.get("pii_safe"),
            ", ".join(data.get("pii_detected", [])),
        ]

        self.sheet.append_row(row)
