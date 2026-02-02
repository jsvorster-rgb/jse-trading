"""
Sharenet EOD CSV scraper with optional login and date filtering
"""
import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def sharenet_login(session, login_url="https://www.sharenet.co.za/login"):
    """Perform login if SHARENET_USER/PASS env vars are set; return True if logged in."""
    user = os.getenv('SHARENET_USER')
    pwd = os.getenv('SHARENET_PASS')
    if not user or not pwd:
        return False
    resp = session.get(login_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    form = soup.find('form')
    if not form or not form.get('action'):
        print("Login form not found; skipping login.")
        return False
    data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input', type='hidden') if inp.get('name')}
    data['username'] = user
    data['password'] = pwd
    post_url = urljoin(login_url, form['action'])
    res = session.post(post_url, data=data)
    res.raise_for_status()
    # rudimentary success check
    if 'invalid' in res.text.lower() or res.url.rstrip('/') == login_url.rstrip('/'):
        print("Sharenet login failed; continuing anonymously.")
        return False
    print("Logged into Sharenet successfully.")
    return True

def fetch_eod_index(session, base_url="https://www.sharenet.co.za/tools/eod/"):
    """Fetch the EOD index page and return BeautifulSoup."""
    resp = session.get(base_url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def find_csv_links(soup, base_url="https://www.sharenet.co.za/tools/eod/", date_filter=None):
    """Extract CSV download links from the index page, optionally filter by date (YYYY-MM-DD)."""
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.lower().endswith('.csv'):
            continue
        full = urljoin(base_url, href)
        if date_filter and date_filter not in full:
            continue
        links.append(full)
    return links

def download_csv(session, url, dest_dir="data/raw/sharenet"):
    """Download a CSV file to the destination directory."""
    os.makedirs(dest_dir, exist_ok=True)
    filename = os.path.basename(url)
    out_path = os.path.join(dest_dir, filename)
    if os.path.exists(out_path):
        print(f"Skipping existing file: {filename}")
        return out_path
    print(f"Downloading {filename}...")
    resp = session.get(url)
    resp.raise_for_status()
    with open(out_path, 'wb') as f:
        f.write(resp.content)
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Sharenet EOD CSV scraper")
    parser.add_argument('--date', help="Filter downloads by date string (YYYY-MM-DD)")
    args = parser.parse_args()

    # Create a session with retry logic (backoff and status retries)
    session = requests.Session()
    retries = requests.adapters.Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    if sharenet_login(session):
        print("Authenticated session.")

    print("Fetching Sharenet EOD index page...")
    soup = fetch_eod_index(session)
    csv_urls = find_csv_links(soup, date_filter=args.date)
    if not csv_urls:
        print("No CSV links found on EOD page. Login may be required or page structure changed.")
        return
    for url in csv_urls:
        download_csv(session, url)

if __name__ == '__main__':
    main()

