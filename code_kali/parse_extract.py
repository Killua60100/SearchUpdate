import os
import json
import xml.etree.ElementTree as ET
import tarfile
import subprocess
import sys

EXTRACT_DIR = "code_kali/kali_extract"

def extract_tar_file(filepath):
    folder_name = os.path.splitext(os.path.splitext(os.path.basename(filepath))[0])[0]
    extract_path = os.path.join(EXTRACT_DIR, folder_name)
    if os.path.exists(extract_path):
        print(f" Dossier déjà extrait : {extract_path}")
        return extract_path
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    with tarfile.open(filepath, "r:gz") as tar:
        tar.extractall(path=extract_path)
    print(f" Extraction terminée dans le dossier : {extract_path}")
    return extract_path


def find_xml_files(folder):
    xml_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".xml"):
                xml_files.append(os.path.join(root, file))
    return xml_files


def parse_articles(xml_files, max_articles=999999, output_path="data/articles_kali.json"):
    articles = []
    count = 0

    for xml_file in xml_files:
        if max_articles is not None and count >= max_articles:
            break
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Champs de base
            numero = root.findtext(".//META_ARTICLE/NUM", default="Inconnu")
            titre_code = root.findtext(".//TITRE_TXT", default="Code inconnu")
            date_debut = root.findtext(".//META_ARTICLE/DATE_DEBUT", default="")
            date_fin = root.findtext(".//META_ARTICLE/DATE_FIN", default="")
            cid = root.findtext(".//META/CID", default="")
            id_article = root.findtext(".//ID", default="")
            etat = root.findtext(".//META/ETAT", default="")

            # Structure législative
            titre = root.findtext(".//META_TITRE", default="")
            sous_titre = root.findtext(".//META_SOUS_TITRE", default="")
            division = root.findtext(".//META_DIVISION", default="")
            section = root.findtext(".//META_SECTION", default="")
            parent = root.findtext(".//META_ARTICLE/PARENT", default="")

            # Texte
            bloc = root.find(".//BLOC_TEXTUEL/CONTENU")
            texte = "".join(bloc.itertext()).strip() if bloc is not None else ""

            if id_article and numero:
                texte_indexe = (
                    f"{titre_code} {numero} {titre} {sous_titre} {division} {section} {texte}".lower()
                    if texte else ""
                )

                articles.append({
                    "code": titre_code,
                    "article": numero,
                    "titre": titre,
                    "sous_titre": sous_titre,
                    "division": division,
                    "section": section,
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                    "etat": etat,
                    "cid": cid,
                    "id_article": id_article,
                    "parent": parent,
                    "texte": texte,
                    "texte_indexe": texte_indexe,
                    "source": xml_file
                })
                count += 1

        except Exception as e:
            print(f"Erreur sur {xml_file}: {e}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"{len(articles)} articles enregistrés dans {output_path}")