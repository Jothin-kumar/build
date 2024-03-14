import shutil, os, json

os.system("python3 -m pip install -r build/requirements.txt && echo 'build requirements installed'")
from bs4 import BeautifulSoup

if os.path.exists("build-output"):
    shutil.rmtree("build-output")
os.mkdir("build-output")

with open("build-config.json") as d:
    config = json.loads(d.read())
line_end = config["line-end"]

for page in config["pages"]:

    with open(f"{config['parent-dir']}/{page}") as html_file:
        html_content = html_file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        path_parent = f"{config['parent-dir']}{page}"[::-1].partition("/")[2][::-1]

        new_script = soup.new_tag("script")
        new_script.string = "\n"
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                with open(f"{path_parent}/{src}") as js_content:
                    script.decompose()
                    new_script.string += js_content.read() + "\n"
        soup.head.append(new_script)
        
        new_style = soup.new_tag("style")
        new_style.string = "\n"
        for style in soup.find_all("link"):
            if "stylesheet" not in style.get("rel"):
                continue
            href = style.get("href")
            if href:
                with open(f"{path_parent}/{href}") as css_content:
                    style.decompose()
                    new_style.string += css_content.read() + "\n"
        soup.head.append(new_style)
    
    filename = f"build-output/{page}"
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