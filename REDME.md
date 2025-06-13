le code a rentrer dans le terminal pour faire fonctionné le projet 

python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate

pip install selenium pandas openpyxl streamlit

sudo apt-get update

sudo apt-get install -y unzip wget

wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/137.0.7151.55/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

chromedriver --version

https://echanges.dila.gouv.fr/OPENDATA/LEGI/?C=S;O=D