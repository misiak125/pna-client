import keyring

APP_NAME = "PNA" 

try:
    keyring.delete_password(APP_NAME, "api_key")
    print("\n[SUKCES] Zły klucz API został usunięty z pamięci systemu!")
    print("Możesz teraz uruchomić aplikację główną, by wpisać go ponownie.\n")
except keyring.errors.PasswordDeleteError:
    print("\n[INFO] Nie znaleziono żadnego zapisanego klucza. Pamięć jest już pusta.\n")