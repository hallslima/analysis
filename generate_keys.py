# generate_keys.py
import streamlit_authenticator as stauth

# Lista de senhas que você quer "hashear"
passwords_to_hash = ["sua_senha_123", "outra_senha_abc"]

hashed_passwords = stauth.Hasher(passwords_to_hash).generate()

print(hashed_passwords)