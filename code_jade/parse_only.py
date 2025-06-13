from parse_extract import extract_tar_file, find_xml_files, parse_articles
import os

def main():
    # Cherche le dernier .tar.gz dans legi_download
    download_dir = "code_jade/jade_download"
    files = [f for f in os.listdir(download_dir) if f.endswith(".tar.gz")]
    if not files:
        print("Aucune archive trouvée dans circu_download.")
        return
    files.sort(reverse=True)
    filepath = os.path.join(download_dir, files[0])
    extract_path = extract_tar_file(filepath)  # extraction ira dans circu_extract
    xml_files = find_xml_files(extract_path)
    print(f" {len(xml_files)} fichiers XML trouvés")
    parse_articles(xml_files, max_articles=None, output_path="data/articles_jade.json")

if __name__ == "__main__":
    main()