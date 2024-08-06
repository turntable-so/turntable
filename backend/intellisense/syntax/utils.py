import time
from typing import List, Optional

from bs4 import BeautifulSoup
from chromedriver_autoinstaller import install as install_chromedriver
from selenium import webdriver


class DBArgument:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        type: Optional[str] = None,
        optional: Optional[bool] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.optional = optional

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "optional": self.optional,
        }


class DBFunction:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        link: Optional[str] = None,
        syntax: Optional[str] = None,
        arguments: Optional[List[DBArgument]] = None,
    ):
        self.name = name
        self.description = description
        self.link = link
        self.syntax = syntax
        self.arguments = arguments

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "syntax": self.syntax,
            "arguments": [arg.to_dict() for arg in self.arguments]
            if self.arguments
            else None,
        }


class DBDialect:
    def __init__(
        self,
        name: str,
        functions: Optional[List[DBFunction]] = None,
        keywords: Optional[List[str]] = None,
    ):
        self.name = name
        self.functions = functions
        self.keywords = keywords
        self.driver = Driver()

    def __del__(self):
        self.driver.close()

    def to_dict(self):
        return {
            "name": self.name,
            "keywords": self.keywords,
            "functions": [func.to_dict() for func in self.functions]
            if self.functions
            else None,
        }

    def to_json(self, path):
        import json

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


class Driver:
    def __init__(self):
        install_chromedriver()

        # Create a webdriver instance
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
        self.driver = webdriver.Chrome(options=options)

    def scrape(self, url):
        self.driver.get(url)
        print(url)

        # Optional: Wait for the page to load (you can use WebDriverWait for more complex scenarios)
        time.sleep(0.5)

        # Get the page source after it has loaded
        page_source = self.driver.page_source

        # Parse the page source using BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")

        return soup

    def close(self):
        self.driver.close()


def get_amazon_links(soup):
    return [
        "https://docs.aws.amazon.com/redshift/latest/dg/" + i.find("a")["href"][2:]
        for i in soup.find("div", class_="highlights").find_all("li")
    ]


def get_contents_between(start, end, tag_name=None, sep=None, strip=True):
    content = []
    current = start

    while current != end:
        if current.name and current != start and current != end:
            content.append(current)
        current = current.find_next()

    # Create a new BeautifulSoup object with the extracted content
    if sep:
        one_string = [
            i.get_text(sep, strip=strip)
            for i in content
            if i.name == tag_name or not tag_name
        ]  # if tag_name is none, all tags are returned
    else:
        one_string = [
            i.get_text(strip=strip)
            for i in content
            if i.name == tag_name or not tag_name
        ]
    return "\n".join(one_string)
