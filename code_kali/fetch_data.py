import os
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://echanges.dila.gouv.fr/OPENDATA/KALI/"
DOWNLOAD_DIR = "code_kali/kali_download"

def get_latest_kali_url():
    print("Récupération de la liste des fichiers disponibles...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    tar_links = sorted(
        [a["href"] for a in soup.find_all("a", href=True) if re.match(r"KALI_.*\.tar\.gz", a["href"])],
        reverse=True
    )
    if not tar_links:
        raise Exception(" Aucun fichier KALI trouvé.")
    return BASE_URL + tar_links[0], tar_links[0]



def download_file(url, filename):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        print(f" Fichier déjà présent : {filename}")
        return filepath
    print(f" Téléchargement du fichier : {filename}")
    response = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(" Fichier téléchargé")
    return filepath
