from fetch_data import get_latest_jade_url, download_file

def main():
    url, filename = get_latest_jade_url()
    filepath = download_file(url, filename)
    print(f" Archive téléchargée : {filepath}")

if __name__ == "__main__":
    main()

    