import json
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from code_legi.utils import load_articles, filter_articles
import os
import time
import subprocess
import sys
import shutil


# --- CONFIGURATION DE L’APPLICATION ---


st.set_page_config(page_title="Consultation Code Législatif", layout="wide")
st.title("📚 Articles de Loi")
st.title("Base de donnée sur les dernières modifications législative française")



# --- STYLE PERSONNALISÉ POUR LA SIDEBAR ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 380px;
            max-width: 400px;
            width: 23vw;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- INITIALISATION DES VARIABLES DE SESSION ---

if "visible_count" not in st.session_state:
    st.session_state.visible_count = 20

for key in ["title_filter", "article_number_filter", "text_search"]:
    if key not in st.session_state:
        st.session_state[key] = ""

for key in ["date_debut_min", "date_debut_max"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- FILTRES UTILISATEUR ---

st.sidebar.header("🔎 Filtres")
st.sidebar.markdown("**Filtrer par plage de date de début :**")

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut_min = st.date_input("De", value=st.session_state.date_debut_min, key="start_date")
with col2:
    date_debut_max = st.date_input("À", value=st.session_state.date_debut_max, key="end_date")

# --- CHAMP DE RECHERCHE GLOBAL ---


search_all = st.sidebar.text_input(
    "Recherche (titre, texte, numéro d’article, code)",
    value=st.session_state.get("search_all", ""),
    key="search_all_input"
)

if st.sidebar.button("Appliquer la recherche"):
    st.session_state.search_all = search_all
    st.session_state.date_debut_min = date_debut_min
    st.session_state.date_debut_max = date_debut_max
    st.session_state.visible_count = 20

show_only_vigueur = st.sidebar.checkbox("Afficher uniquement les lois en vigueur")


# === CHARGEMENT DES ARTICLES ===


# --- LEGI ---


legi_db_path = "data/articles_legi.json"
legi_db_exists = os.path.exists(legi_db_path)
legi_articles = load_articles(legi_db_path) if legi_db_exists else []
legi_nb_articles = len(legi_articles)
legi_db_size = os.path.getsize(legi_db_path) if legi_db_exists else 0
legi_db_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(legi_db_path))) if legi_db_exists else "N/A"


# --- KALI ---


kali_db_path = "data/articles_kali.json"
kali_db_exists = os.path.exists(kali_db_path)
kali_articles = []
if kali_db_exists:
    try:
        with open(kali_db_path, encoding="utf-8") as f:
            kali_articles = json.load(f)
    except Exception:
        kali_articles = []
kali_nb_articles = len(kali_articles)
kali_db_size = os.path.getsize(kali_db_path) if kali_db_exists else 0
kali_db_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(kali_db_path))) if kali_db_exists else "N/A"

# --- JORF ---


jorf_db_path = "data/articles_jorf.json"
jorf_db_exists = os.path.exists(jorf_db_path)
jorf_articles = []
if jorf_db_exists:
    try:
        with open(jorf_db_path, encoding="utf-8") as f:
            jorf_articles = json.load(f)
    except Exception:
        jorf_articles = []
jorf_nb_articles = len(jorf_articles)
jorf_db_size = os.path.getsize(jorf_db_path) if jorf_db_exists else 0
jorf_db_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(jorf_db_path))) if jorf_db_exists else "N/A"


# --- JADE ---

jade_db_path = "data/articles_jade.json"
jade_db_exists = os.path.exists(jade_db_path)
jade_articles = []
if jade_db_exists:
    try:
        with open(jade_db_path, encoding="utf-8") as f:
            jade_articles = json.load(f)
    except Exception:
        jade_articles = []
jade_nb_articles = len(jade_articles)
jade_db_size = os.path.getsize(jade_db_path) if jade_db_exists else 0
jade_db_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(jade_db_path))) if jade_db_exists else "N/A"

# --- CASS ---

cass_db_path = "data/articles_cass.json"
cass_db_exists = os.path.exists(cass_db_path)
cass_articles = []
if cass_db_exists:
    try:
        with open(cass_db_path, encoding="utf-8") as f:
            cass_articles = json.load(f)
    except Exception:
        cass_articles = []
cass_nb_articles = len(cass_articles)
cass_db_size = os.path.getsize(cass_db_path) if cass_db_exists else 0
cass_db_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(cass_db_path))) if cass_db_exists else "N/A"



# --- CHECKBOX BASES DE DONNÉES ---

show_legi = st.sidebar.checkbox("Afficher LEGI", value=True)
show_kali = st.sidebar.checkbox("Afficher KALI", value=True)
show_jorf = st.sidebar.checkbox("Afficher JORF", value=True)
show_jade = st.sidebar.checkbox("Afficher JADE", value=True)
show_cass = st.sidebar.checkbox("Afficher CASS", value=True)


# === CONSTRUCTION DE LA LISTE À AFFICHER ===

articles_to_display = []
if show_legi:
    articles_to_display += legi_articles
if show_kali:
    articles_to_display += kali_articles
if show_jorf:
    articles_to_display += jorf_articles
if show_jade:
    articles_to_display += jade_articles
if show_cass:
    articles_to_display += cass_articles
    

# --- FILTRAGE ---

# ... puis après le filtrage principal :
filtered_articles = filter_articles(
    articles_to_display,
    search_all=st.session_state.get("search_all", ""),
    date_debut_min=st.session_state.date_debut_min,
    date_debut_max=st.session_state.date_debut_max
)
if show_only_vigueur:
    filtered_articles = [a for a in filtered_articles if a.get("date_fin") == "2999-01-01"]


# --- TOTAL ---


total_articles = legi_nb_articles + kali_nb_articles + jorf_nb_articles + jade_nb_articles + cass_nb_articles
st.sidebar.success(f"✅ Total articles trouvés : {total_articles}")


# === CONSTRUCTION DE LA LISTE À AFFICHER ===
    

articles_to_display = []
if show_legi:
    articles_to_display += legi_articles
if show_kali:
    articles_to_display += kali_articles
if show_jorf:
    articles_to_display += jorf_articles
if show_jade:
    articles_to_display += jade_articles
if show_cass:
    articles_to_display += cass_articles

# --- FILTRAGE ---


filtered_articles = filter_articles(
    articles_to_display,
    search_all=st.session_state.get("search_all", ""),
    date_debut_min=st.session_state.date_debut_min,
    date_debut_max=st.session_state.date_debut_max
)
if show_only_vigueur:
    filtered_articles = [a for a in filtered_articles if a.get("date_fin") == "2999-01-01"]

# --- EXPORT XLSX ---


df_filtered = pd.DataFrame(filtered_articles)
if not df_filtered.empty:
    output_filtered = io.BytesIO()
    with pd.ExcelWriter(output_filtered, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="Articles")
        worksheet = writer.sheets["Articles"]
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 5, 60)  # 60 = largeur max
        output_filtered.seek(0)
        st.download_button(
            label="📥 Télécharger les articles affichés (.xlsx)",
            data=output_filtered,
            file_name="articles_filtres.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.info(f"🔎 {len(filtered_articles)} article(s) trouvé(s) avec les filtres actuels.")

# === AFFICHAGE DES ARTICLES ===


st.markdown("---")
visible_articles = filtered_articles[:st.session_state.visible_count]
for article in visible_articles:
    if not article.get("texte") or not article.get("code") or not article.get("article"):
        continue
    with st.expander(f"📘 {article['code']} - Article {article['article']}"):
        st.markdown(f"**Dates** : {article['date_debut']} ➡ {article['date_fin']}")
        st.markdown(article["texte"])

if st.session_state.visible_count < len(filtered_articles):
    if st.button("📄 Voir plus"):
        st.session_state.visible_count += 20



st.sidebar.markdown("---")


# --- Informations sur la base de données LEGI ---



st.sidebar.markdown("### 📦 Informations sur la base de données LEGI")


if legi_db_exists:
    articles = json.load(open(legi_db_path, encoding="utf-8"))
    nb_articles = len(articles)

    st.sidebar.write(f"**Fichier :** `{legi_db_path}`")
    st.sidebar.write(f"**Taille :** {legi_db_size/1024:.1f} Ko")
    st.sidebar.write(f"**Dernière modification :** {legi_db_mtime}")
    st.sidebar.write(f"**Nombre d'articles :** {nb_articles}")
else:
    st.sidebar.warning("❌ Le fichier JSON de LEGI est introuvable.")


extract_dir = "code_legi/legi_extract"
if not os.path.exists(extract_dir) or not any(os.path.isdir(os.path.join(extract_dir, d)) for d in os.listdir(extract_dir)):
    st.sidebar.warning("❌ Aucun dossier LégiFrance dézippé trouvé.")

download_dir = "code_legi/legi_download"
if not os.path.exists(download_dir) or not any(f.endswith(".tar.gz") for f in os.listdir(download_dir)):
    st.sidebar.warning("❌ Aucune archive LegiFrance téléchargée trouvée.")


if st.sidebar.button("🗑️ Supprimer le fichier JSON legi extrait", key="btn_delete_json_legi"):
    try:
        if os.path.exists(legi_db_path):
            os.remove(legi_db_path)

            legi_extract_dir = "code_legi/legi_extract"
            if os.path.exists(legi_extract_dir):

                folders = [os.path.join(legi_extract_dir, d) for d in os.listdir(legi_extract_dir) if os.path.isdir(os.path.join(legi_extract_dir, d))]
                if folders:
                    last_folder = max(folders, key=os.path.getmtime)
                    shutil.rmtree(last_folder)
            st.sidebar.success("Fichier JSON LEGI et dossier extrait supprimés.")
        else:
            st.sidebar.warning("Aucun fichier JSON LEGI à supprimer.")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression fichier JSON LEGI/dossier extrait : {e}")


if st.sidebar.button("🗑️ Supprimer la BDD LégiFrance installée", key="btn_delete_legi_extract"):
    try:
        files = [f for f in os.listdir(download_dir) if f.endswith(".tar.gz")]
        if not files:
            st.sidebar.warning("Aucune archive à supprimer.")
        else:
            files.sort(reverse=True)
            last_file = files[0]
            last_file_path = os.path.join(download_dir, last_file)
            os.remove(last_file_path)

            folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
            extracted_folder = os.path.join(extract_dir, folder_name)
            if os.path.isdir(extracted_folder):
                shutil.rmtree(extracted_folder)
                st.sidebar.success(f"Archive et dossier extrait supprimés : {last_file}, {folder_name}")
            else:
                st.sidebar.success(f"Archive supprimée : {last_file} (pas de dossier extrait trouvé)")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression archive/dossier : {e}")


if st.sidebar.button("⬇️ Télécharger la dernière BDD LegiFrance", key="btn_download_legi"):
    try:
        result = subprocess.run(
            [sys.executable, "code_legi/fetch_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Archive téléchargée avec succès.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du téléchargement :\n{e.stderr}")


if st.sidebar.button("🛠️ Générer le fichier JSON depuis la BDD", key="btn_parse_legi"):
    try:
        result = subprocess.run(
            [sys.executable, "code_legi/parse_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Fichier JSON généré. Recharge la page.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du parsing :\n{e.stderr}")




# --- Informations sur la base de données KALI ---



st.sidebar.markdown("### 📦 Informations sur la base de données KALI")

if kali_db_exists:
    st.sidebar.write(f"**Fichier :** `{kali_db_path}`")
    st.sidebar.write(f"**Taille :** {kali_db_size/1024:.1f} Ko")
    st.sidebar.write(f"**Dernière modification :** {kali_db_mtime}")
    st.sidebar.write(f"**Nombre d'articles :** {kali_nb_articles}")
else:
    st.sidebar.warning("❌ Le fichier JSON de KALI est introuvable.")


kali_extract_dir = "code_kali/kali_extract"
if not os.path.exists(kali_extract_dir) or not any(os.path.isdir(os.path.join(kali_extract_dir, d)) for d in os.listdir(kali_extract_dir)):
    st.sidebar.warning("❌ Aucun dossier KALI dézippé trouvé.")


kali_download_dir = "code_kali/kali_download"
if not os.path.exists(kali_download_dir) or not any(f.endswith(".tar.gz") for f in os.listdir(kali_download_dir)):
    st.sidebar.warning("❌ Aucune archive KALI téléchargée trouvée.")


if st.sidebar.button("⬇️ Télécharger la dernière archive KALI", key="btn_download_kali"):
    try:
        result = subprocess.run(
            [sys.executable, "code_kali/fetch_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Archive KALI téléchargée avec succès.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du téléchargement KALI :\n{e.stderr}")


if st.sidebar.button("🛠️ Générer le fichier JSON KALI depuis la BDD" ,key="btn_parse_kali"):
    try:
        result = subprocess.run(
            [sys.executable, "code_kali/parse_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Fichier JSON KALI généré. Recharge la page.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du parsing KALI :\n{e.stderr}")


if st.sidebar.button("🗑️ Supprimer le fichier JSON KALI extrait", key="btn_delete_json_kali"):
    try:

        if os.path.exists(kali_db_path):
            os.remove(kali_db_path)

            kali_extract_dir = "code_kali/kali_extract"
            if os.path.exists(kali_extract_dir):

                folders = [os.path.join(kali_extract_dir, d) for d in os.listdir(kali_extract_dir) if os.path.isdir(os.path.join(kali_extract_dir, d))]
                if folders:
                    last_folder = max(folders, key=os.path.getmtime)
                    shutil.rmtree(last_folder)
            st.sidebar.success("Fichier JSON KALI et dossier extrait supprimés.")
        else:
            st.sidebar.warning("Aucun fichier JSON KALI à supprimer.")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression fichier JSON KALI/dossier extrait : {e}")


if st.sidebar.button("🗑️ Supprimer la dernière archive KALI (zippé + dézippé)" , key="btn_delete_kali_extract"):
    try:
        files = [f for f in os.listdir(kali_download_dir) if f.endswith(".tar.gz")]
        if not files:
            st.sidebar.warning("Aucune archive KALI à supprimer.")
        else:
            files.sort(reverse=True)
            last_file = files[0]
            last_file_path = os.path.join(kali_download_dir, last_file)
            os.remove(last_file_path)
            folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
            extracted_folder = os.path.join(kali_extract_dir, folder_name)
            if os.path.isdir(extracted_folder):
                shutil.rmtree(extracted_folder)
                st.sidebar.success(f"Archive et dossier extrait KALI supprimés : {last_file}, {folder_name}")
            else:
                st.sidebar.success(f"Archive KALI supprimée : {last_file} (pas de dossier extrait trouvé)")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression archive/dossier KALI : {e}")



# --- Informations sur la base de données JORF ---



st.sidebar.markdown("### 📦 Informations sur la base de données JORF")

if jorf_db_exists:
    st.sidebar.write(f"**Fichier :** `{jorf_db_path}`")
    st.sidebar.write(f"**Taille :** {jorf_db_size/1024:.1f} Ko")
    st.sidebar.write(f"**Dernière modification :** {jorf_db_mtime}")
    st.sidebar.write(f"**Nombre d'articles :** {jorf_nb_articles}")
else:
    st.sidebar.warning("❌ Le fichier JSON de JORF est introuvable.")


JORF_extract_dir = "code_jorf/jorf_extract"
if not os.path.exists(JORF_extract_dir) or not any(os.path.isdir(os.path.join(JORF_extract_dir, d)) for d in os.listdir(JORF_extract_dir)):
    st.sidebar.warning("❌ Aucun dossier JORF dézippé trouvé.")


JORF_download_dir = "code_jorf/jorf_download"
if not os.path.exists(JORF_download_dir) or not any(f.endswith(".tar.gz") for f in os.listdir(JORF_download_dir)):
    st.sidebar.warning("❌ Aucune archive JORF téléchargée trouvée.")


if st.sidebar.button("⬇️ Télécharger la dernière archive JORF", key="btn_download_jorf"):
    try:
        result = subprocess.run(
            [sys.executable, "code_jorf/fetch_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Archive JORF téléchargée avec succès.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du téléchargement JORF :\n{e.stderr}")



if st.sidebar.button("🛠️ Générer le fichier JSON JORF depuis la BDD"):
    try:
        result = subprocess.run(
            [sys.executable, "code_jorf/parse_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Fichier JSON JORF généré. Recharge la page.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du parsing JORF :\n{e.stderr}")



if st.sidebar.button("🗑️ Supprimer le fichier JSON JORF extrait", key="btn_delete_json_jorf"):
    try:

        if os.path.exists(jorf_db_path):
            os.remove(jorf_db_path)

            jorf_extract_dir = "code_jorf/jorf_extract"
            if os.path.exists(jorf_extract_dir):

                folders = [os.path.join(jorf_extract_dir, d) for d in os.listdir(jorf_extract_dir) if os.path.isdir(os.path.join(jorf_extract_dir, d))]
                if folders:
                    last_folder = max(folders, key=os.path.getmtime)
                    shutil.rmtree(last_folder)
            st.sidebar.success("Fichier JSON JORF et dossier extrait supprimés.")
        else:
            st.sidebar.warning("Aucun fichier JSON JORF à supprimer.")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression fichier JSON JORF/dossier extrait : {e}")



if st.sidebar.button("🗑️ Supprimer la dernière archive JORF (zippé + dézippé)"):
    try:
        files = [f for f in os.listdir(JORF_download_dir) if f.endswith(".tar.gz")]
        if not files:
            st.sidebar.warning("Aucune archive JORF à supprimer.")
        else:
            files.sort(reverse=True)
            last_file = files[0]
            last_file_path = os.path.join(JORF_download_dir, last_file)
            os.remove(last_file_path)
            folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
            extracted_folder = os.path.join(JORF_extract_dir, folder_name)
            if os.path.isdir(extracted_folder):
                shutil.rmtree(extracted_folder)
                st.sidebar.success(f"Archive et dossier extrait JORF supprimés : {last_file}, {folder_name}")
            else:
                st.sidebar.success(f"Archive JORF supprimée : {last_file} (pas de dossier extrait trouvé)")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression archive/dossier JORF : {e}")



# --- Informations sur la base de données JADE ---



st.sidebar.markdown("### 📦 Informations sur la base de données JADE")

if jade_db_exists:
    st.sidebar.write(f"**Fichier :** `{jade_db_path}`")
    st.sidebar.write(f"**Taille :** {jade_db_size/1024:.1f} Ko")
    st.sidebar.write(f"**Dernière modification :** {jade_db_mtime}")
    st.sidebar.write(f"**Nombre d'articles :** {jade_nb_articles}")
else:
    st.sidebar.warning("❌ Le fichier JSON de JADE est introuvable.")


jade_extract_dir = "code_jade/jade_extract"
if not os.path.exists(jade_extract_dir) or not any(os.path.isdir(os.path.join(jade_extract_dir, d)) for d in os.listdir(jade_extract_dir)):
    st.sidebar.warning("❌ Aucun dossier JADE dézippé trouvé.")


jade_download_dir = "code_jade/jade_download"
if not os.path.exists(jade_download_dir) or not any(f.endswith(".tar.gz") for f in os.listdir(jade_download_dir)):
    st.sidebar.warning("❌ Aucune archive jade téléchargée trouvée.")


if st.sidebar.button("⬇️ Télécharger la dernière archive jade", key="btn_download_jade"):
    try:
        result = subprocess.run(
            [sys.executable, "code_jade/fetch_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Archive JADE téléchargée avec succès.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du téléchargement JADE :\n{e.stderr}")



if st.sidebar.button("🛠️ Générer le fichier JSON JADE depuis la BDD"):
    try:
        result = subprocess.run(
            [sys.executable, "code_jade/parse_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Fichier JSON JADE généré. Recharge la page.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du parsing JADE :\n{e.stderr}")



if st.sidebar.button("🗑️ Supprimer le fichier JSON JADE extrait", key="btn_delete_json_JADE"):
    try:

        if os.path.exists(jade_db_path):
            os.remove(jade_db_path)

            jade_extract_dir = "code_jade/jade_extract"
            if os.path.exists(jade_extract_dir):

                folders = [os.path.join(jade_extract_dir, d) for d in os.listdir(jade_extract_dir) if os.path.isdir(os.path.join(jade_extract_dir, d))]
                if folders:
                    last_folder = max(folders, key=os.path.getmtime)
                    shutil.rmtree(last_folder)
            st.sidebar.success("Fichier JSON jade et dossier extrait supprimés.")
        else:
            st.sidebar.warning("Aucun fichier JSON jade à supprimer.")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression fichier JSON jade/dossier extrait : {e}")



if st.sidebar.button("🗑️ Supprimer la dernière archive jade (zippé + dézippé)"):
    try:
        files = [f for f in os.listdir(jade_download_dir) if f.endswith(".tar.gz")]
        if not files:
            st.sidebar.warning("Aucune archive jade à supprimer.")
        else:
            files.sort(reverse=True)
            last_file = files[0]
            last_file_path = os.path.join(jade_download_dir, last_file)
            os.remove(last_file_path)
            folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
            extracted_folder = os.path.join(jade_extract_dir, folder_name)
            if os.path.isdir(extracted_folder):
                shutil.rmtree(extracted_folder)
                st.sidebar.success(f"Archive et dossier extrait jade supprimés : {last_file}, {folder_name}")
            else:
                st.sidebar.success(f"Archive jade supprimée : {last_file} (pas de dossier extrait trouvé)")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression archive/dossier jade : {e}")



        # --- Informations sur la base de données CASS ---



st.sidebar.markdown("### 📦 Informations sur la base de données CASS")

if cass_db_exists:
    st.sidebar.write(f"**Fichier :** `{cass_db_path}`")
    st.sidebar.write(f"**Taille :** {cass_db_size/1024:.1f} Ko")
    st.sidebar.write(f"**Dernière modification :** {cass_db_mtime}")
    st.sidebar.write(f"**Nombre d'articles :** {cass_nb_articles}")
else:
    st.sidebar.warning("❌ Le fichier JSON de CASS est introuvable.")


CASS_extract_dir = "code_cass/cass_extract"
if not os.path.exists(CASS_extract_dir) or not any(os.path.isdir(os.path.join(CASS_extract_dir, d)) for d in os.listdir(CASS_extract_dir)):
    st.sidebar.warning("❌ Aucun dossier CASS dézippé trouvé.")


CASS_download_dir = "code_cass/cass_download"
if not os.path.exists(CASS_download_dir) or not any(f.endswith(".tar.gz") for f in os.listdir(CASS_download_dir)):
    st.sidebar.warning("❌ Aucune archive CASS téléchargée trouvée.")


if st.sidebar.button("⬇️ Télécharger la dernière archive CASS", key="btn_download_cass"):
    try:
        result = subprocess.run(
            [sys.executable, "code_cass/fetch_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Archive CASS téléchargée avec succès.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du téléchargement CASS :\n{e.stderr}")



if st.sidebar.button("🛠️ Générer le fichier JSON CASS depuis la BDD"):
    try:
        result = subprocess.run(
            [sys.executable, "code_cass/parse_only.py"],
            capture_output=True, text=True, check=True
        )
        st.sidebar.success("Fichier JSON CASS généré. Recharge la page.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Erreur lors du parsing CASS :\n{e.stderr}")



if st.sidebar.button("🗑️ Supprimer le fichier JSON CASS extrait", key="btn_delete_json_cass"):
    try:

        if os.path.exists(cass_db_path):
            os.remove(cass_db_path)

            cass_extract_dir = "code_cass/cass_extract"
            if os.path.exists(cass_extract_dir):

                folders = [os.path.join(cass_extract_dir, d) for d in os.listdir(cass_extract_dir) if os.path.isdir(os.path.join(cass_extract_dir, d))]
                if folders:
                    last_folder = max(folders, key=os.path.getmtime)
                    shutil.rmtree(last_folder)
            st.sidebar.success("Fichier JSON CASS et dossier extrait supprimés.")
        else:
            st.sidebar.warning("Aucun fichier JSON CASS à supprimer.")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression fichier JSON CASS/dossier extrait : {e}")



if st.sidebar.button("🗑️ Supprimer la dernière archive CASS (zippé + dézippé)"):
    try:
        files = [f for f in os.listdir(CASS_download_dir) if f.endswith(".tar.gz")]
        if not files:
            st.sidebar.warning("Aucune archive CASS à supprimer.")
        else:
            files.sort(reverse=True)
            last_file = files[0]
            last_file_path = os.path.join(CASS_download_dir, last_file)
            os.remove(last_file_path)
            folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
            extracted_folder = os.path.join(CASS_extract_dir, folder_name)
            if os.path.isdir(extracted_folder):
                shutil.rmtree(extracted_folder)
                st.sidebar.success(f"Archive et dossier extrait CASS supprimés : {last_file}, {folder_name}")
            else:
                st.sidebar.success(f"Archive CASS supprimée : {last_file} (pas de dossier extrait trouvé)")
    except Exception as e:
        st.sidebar.error(f"Erreur suppression archive/dossier CASS : {e}")
