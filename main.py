# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 02:23:11 2024

@author: codefather
"""
# builtin import
import os
os.makedirs("journal", exist_ok=True)
import sys
import re
import enum
import datetime as dt
import pickle
import base64
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.exceptions import InvalidSignature

def clear_console() -> None:
    os.system("cls" if os.name in ("nt", "dos") else "clear")

class SecureJournalEntry:
    class Mood(enum.Enum):
        SAD = 0
        OKAY = 1
        HAPPY = 2

    def __init__(self, date, mood: 'SecureJournalEntry.Mood', desc: str, key: bytes):
        self.date = date
        self.mood = mood
        self.desc = desc
        self.key = key
    
    def encrypt(self) -> bytes:
        try:
            cipher_suite = Fernet(self.key)
            serialized_entry = pickle.dumps(self)
            return cipher_suite.encrypt(serialized_entry)
        except InvalidToken as e:
            print("Error - Invalid token during encryption:", e)
            return None
        except Exception as e:
            print("Error - An unexpected error occurred during encryption:", e)
            return None
    
    @staticmethod
    def decrypt(encrypted: bytes, key: bytes) -> 'SecureJournalEntry':
        try:
            cipher_suite = Fernet(key)
            decrypted = cipher_suite.decrypt(encrypted)
            return pickle.loads(decrypted)
        except InvalidSignature as e:
            print("Error - Signature did not match digest:", e)
            return None
        except Exception as e:
            print("Error occurred during decryption:", e)
            return None

    @classmethod
    def load(cls, date: str, key: bytes) -> 'SecureJournalEntry':
        file_path = f"journal/{date}"
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        return cls.decrypt(encrypted_data, key)

    def save(self) -> None:
        with open(f"journal/{self.date}", "wb") as f:
            f.write(self.encrypt())

    def __str__(self):

        return f"{self.date}\n\n{self.mood}\n\n{self.desc}"


def app(args: list) -> None:
    
    if len(args) == 0:
        print("[Unencrypted Journal]")
    elif len(args) == 1:
        if args[0] == "-h":
            print("[Jornl Help]")
            print("New Jornl: python main.py key")
            print("Load Existing Jornl: python main.py date(01_01_2020) key")
        else:
            print("[Encrypted Journal]")
            key = args[0].encode('utf-8')
    elif len(args) == 2:
        print("=" * 32)
        print(SecureJournalEntry.load(args[0], args[1]))
        print("=" * 32)
        return None
    else:
        print("Invalid number of arguments.")
        return None
    input("Press a button to continue / Ctrl+C to exit.")
    # Date    
    while True:
        clear_console()
        date = input("Date (d_m_y): ")
        if not date:
            today = dt.date.today()
            date = today.strftime("%d_%m_%Y")
            print("[Date] -", date)
            break
        try:
            datetime_obj = dt.datetime.strptime(date, "%d_%m_%Y").date()
            print("[Date] -", date)
            break
        except ValueError:
            pass
    
    # Mood
    while True:        
        mood = input("Mood: ").upper()
        if not mood in SecureJournalEntry.Mood.__members__:
            clear_console()
            print("[Date] -", date)
            print("Invalid Entry, try again")
            for mood in SecureJournalEntry.Mood.__members__.keys():
                print("*", mood)
        else:
            break
    clear_console()
    print("[Date] -", date)
    print("[Mood] -", mood)
    
    # Description
    while True:
        desc = input("Description: ")
        if not desc:
            clear_console()
            print("[Date] -", date)
            print("[Mood] -", mood)
            print("Better if you write something...")
        else:
            break
    clear_console()
    print("[Date] -", date)
    print("[Mood] -", mood)
    print("[Description] -", desc)
    
    #Save Confirmation
    while True:
        confirm = input("Do you want to save this entry (Y/N)").upper()
        if confirm == "N":
            print("Entry Discarded.")
            break
        elif confirm == "Y":
            entry = SecureJournalEntry(date, mood, desc, key)
            entry.save()
            print(SecureJournalEntry.load(entry.date, key))
            print(SecureJournalEntry.load("06_04_2024", key))
            print("Entry Created.")
            break
        else:
            clear_console()
            print("[Date] -", date)
            print("[Mood] -", mood)
            print("[Description] -", desc)
            print("Invalid Entry, try (Y/N)")

app(sys.argv[1:]) # ignoring the first system arg ''
