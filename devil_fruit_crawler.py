import requests
from bs4 import BeautifulSoup, NavigableString
import re
import time
import json

BASE_URL = "https://onepiece.fandom.com"
CATEGORY_URL = f"{BASE_URL}/wiki/Category:Devil_Fruits"
#CATEGORY_URL = f"{BASE_URL}/wiki/Category:Shown_Devil_Fruits"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def clean_text(text):
    text = re.sub(r"\[\[.*?\]\]", "", text)   # Remove double-wrapped wiki links
    text = re.sub(r"\[.*?\]", "", text)          # Remove [x] references
    text = re.sub(r"[\s\xa0]+", " ", text).strip()  # Replace multiple spaces
    return text.replace("\u00a0", " ").strip()


#def extract_fruit_links():
#    soup = get_soup(CATEGORY_URL)
#    container = soup.find("div", class_="category-page__members")
#    links = container.find_all("a", href=True)
#    fruit_links = [BASE_URL + a['href'] for a in links if "/wiki/" in a['href'] and "Non-Canon" not in a['href']]
#    return list(set(fruit_links))  # remove duplicates


def get_fruit_links_from_navibox():
    soup = get_soup(CATEGORY_URL)
    navibox = soup.find("table", class_="navibox")
    if not navibox:
        raise RuntimeError("Navibox not found on category page")

    links = []
    related_articles_parent = None
    for subtable in navibox.find_all("table", class_="collapsible"):
        tbody = subtable.find("tbody")
        if tbody: tr = tbody.find("tr")
        if tr: th = tr.find("th", string=re.compile("Related Articles"))
        if th:
            related_articles_parent = tbody
            break  # Only one expected

    for tr in navibox.find_all("tr", class_="navibox-row"):
        if related_articles_parent and tr.find_parent("tbody") == related_articles_parent:
            continue  # Skip rows inside Related Articles
        hlists = tr.find_all("div", class_="hlist")
        for div in hlists:
            for a in div.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/wiki/"):
                    links.append(BASE_URL + href)
    return list(set(links))  # remove duplicates


def extract_fruit_data(url):
    soup = get_soup(url)
    name = soup.find("div", class_="page-header__title-wrapper").get_text(strip=True)

    content_div = soup.find("div", class_="mw-content-ltr mw-parser-output")
    if not content_div:
        return None

    paragraphs = content_div.find_all("p")
    description = ""
    user = "Unknown"

    for p in paragraphs:
        text_fragments = []
        prev_fragment = None  # To track last appended fragment
        for elem in p.descendants:
            if isinstance(elem, NavigableString):
                fragment = str(elem)
            elif elem.name == 'a':
                fragment = ' ' + elem.get_text()
            elif elem.name == 'span':
                continue
            else:
                fragment = elem.get_text()

            # Only append if different from previous fragment
            if fragment != prev_fragment:
                text_fragments.append(fragment)
                prev_fragment = fragment.strip()

        full_text = ''.join(text_fragments)
        clean = clean_text(full_text)

        if len(clean) > 40: 
            description = clean
            break

    user_container = soup.find("div", class_="pi-item pi-data pi-item-spacing pi-border-color", attrs={"data-source": "user"})
    if user_container:
        user_value = user_container.find("div", class_="pi-data-value pi-font")
        if user_value:
            a = user_value.find("a")
            if a: user = a.get_text(strip=True)

    image = soup.find("img", class_="pi-image-thumbnail")
    img_url = image["src"] if image else ""

    return {
        "name": name,
        "user": user,
        "power": description,
        "img_url": img_url,
        "sum_ranks": 0,
        "times_picked": 0
    }

def crawl_and_save_all():
    fruits = []
    fruit_links = get_fruit_links_from_navibox()
    print(f"Found {len(fruit_links)} fruit pages.")

    for idx, url in enumerate(fruit_links):
        try:
            print(f"Processing ({idx+1}/{len(fruit_links)}): {url}")
            fruit = extract_fruit_data(url)
            if fruit:
                fruits.append(fruit)
            time.sleep(0.5)  # Respectful delay
        except Exception as e:
            print(f"Error processing {url}: {e}")

    with open("devil_fruits.json", "w", encoding="utf-8") as f:
        json.dump(fruits, f, indent=2, ensure_ascii=False)
    print("✅ Saved devil_fruits.json")


if __name__ == "__main__":
    crawl_and_save_all()