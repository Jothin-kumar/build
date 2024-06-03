import shutil, os, json

os.system("python3 -m pip install -r build/requirements.txt && echo 'build requirements installed'")
from bs4 import BeautifulSoup, Tag
import requests

if os.path.exists("build-output"):
    shutil.rmtree("build-output")
os.mkdir("build-output")

with open("build-config.json") as d:
    config = json.loads(d.read())
line_end = config["line-end"]

for page in config["pages"]:
    if type(page) == str:
        page_path = page
        page_prefetches = []
    else:
        page_path = page["path"]
        page_prefetches = page["prefetches"]

    with open(f"{config['parent-dir']}/{page_path}") as html_file:
        html_content = html_file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    path_parent = f"{config['parent-dir']}{page_path}"[::-1].partition("/")[2][::-1]

    for prefetch in page_prefetches:
        tag = Tag(soup, name="link")
        tag["rel"] = "prefetch"
        tag["href"] = prefetch
        soup.head.append(tag)

    for script in soup.find_all("script"):
        src = script.get("src")
        if src:
            tag = Tag(soup, name="script")
            if src.startswith("https://"):
                r = requests.get(src)
                assert r.status_code == 200
                tag.string = f"\n// Source: {src}\n{r.text}\n"
            else:
                with open(f"{path_parent}/{src}") as js_content:
                    tag.string = f"\n// Source: {path_parent}/{src}\n{js_content.read()}\n"
            script.replace_with(tag)

    new_style = soup.new_tag("style")
    new_style.string = "\n* {-webkit-tap-highlight-color: transparent; outline: none;} /* Inserted by build */\n"
    for style in soup.find_all("link"):
        if "stylesheet" not in style.get("rel"):
            continue
        href = style.get("href")
        if href:
            if href.startswith("https://"):
                r = requests.get(href)
                assert r.status_code == 200
                new_style.string += f"/* */\n/* Source: {href} */\n{r.text}\n"
            else:
                with open(f"{path_parent}/{href}") as css_content:
                    new_style.string += f"/* */\n/* Source: {path_parent}/{href} */\n{css_content.read()}\n"
            style.decompose()
    soup.head.append(new_style)
    
    filename = f"build-output/{page_path}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as out:
        result = str(soup)
        while "\n\n" in result:
            result = result.replace("\n\n", "\n")
        lines = result.split("\n")
        result = ""
        for line in lines:
            result += line.strip() + line_end
        for var in config["vars"]:
            result = result.replace(var["replaceFrom"], var["replaceWith"])
        out.write(result)