from intellisense.syntax.utils import (
    DBArgument,
    DBDialect,
    DBFunction,
    Driver,
    get_amazon_links,
    get_contents_between,
)


class SNOWFLAKEscraper(DBDialect):
    def __init__(
        self,
    ):
        super().__init__(name="snowflake", functions=[], keywords=[])

    def scrape_keywords(self):
        soup = self.driver.scrape(
            "https://docs.snowflake.com/en/sql-reference/reserved-keywords"
        )
        tbl = soup.find("tbody")
        for row in tbl.find_all("tr"):
            cells = row.find_all("td")
            if (
                cells[-1].get_text() != ""
            ):  # removes header rows within table that are not real keywords
                self.keywords.append(cells[0].get_text())

    def scrape_functions(self):
        # Navigate to the website you want to scrape
        url = "https://docs.snowflake.com/en/sql-reference/functions-all"
        soup = self.driver.scrape(url)

        for row in soup.find("table").find_all("tr"):
            td = row.find("td")
            if not td:
                continue
            a = td.find("a")
            if not a:
                continue
            func_name = a.text
            func_url = "https://docs.snowflake.com/en/sql-reference/" + a["href"]
            func_it = DBFunction(name=func_name, link=func_url, arguments=[])

            # get info about function
            func_soup = self.driver.scrape(func_url)
            try:
                parent_div = func_soup.find(
                    "div",
                    attrs={
                        "class": "section",
                        "id": func_name.lower().replace("_", "-"),
                    },
                )
            except:
                continue

            # get syntax
            try:
                syntax = [
                    pre.get_text().strip()
                    for pre in parent_div.find(
                        "div", class_="section", id="syntax"
                    ).find_all("pre")
                ]
                func_it.syntax = "\n".join(syntax)
            except:
                pass

            # get description
            try:
                divs_to_remove = parent_div.find_all(
                    "div", class_="section"
                )  # remove all other sections to help isolate the description
                for div in divs_to_remove:
                    div.decompose()
                parent_div.find("h1").decompose()
                func_it.description = parent_div.text.strip()
            except:
                pass

            self.functions.append(func_it)


class BIGQUERYscraper(DBDialect):
    def __init__(
        self,
    ):
        super().__init__(name="bigquery", functions=[], keywords=[])

    def scrape_keywords(self):
        soup = self.driver.scrape(
            "https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical"
        )
        header = soup.find("h2", id="reserved_keywords")
        keyword_string = header.find_next("table").get_text()
        self.keywords = [i for i in keyword_string.split("\n") if i != ""]

    def scrape_functions(self):
        page_prefix = "https://cloud.google.com/bigquery/docs/reference/standard-sql/"
        bq_pages = [
            "aead_encryption_functions",
            "aggregate_functions",
            "approximate_aggregate_functions",
            "array_functions",
            "bit_functions",
            "table-functions-built-in",
            "conversion_functions",
            "date_functions",
            "datetime_functions",
            "debugging_functions",
            "aggregate-dp-functions",
            "federated_query_functions",
            "dlp_functions",
            "geography_functions",
            "hash_functions",
            "hll_functions",
            "interval_functions",
            "json_functions",
            "mathematical_functions",
            "navigation_functions",
            "net_functions",
            "numbering_functions",
            "search_functions",
            "security_functions",
            "statistical_aggregate_functions",
            "string_functions",
            "time_functions",
            "timestamp_functions",
            "utility-functions",
        ]
        for page in bq_pages:
            try:
                soup = self.driver.scrape(page_prefix + page)
                table = soup.find("h3", id="function_list").find_next("table")
            except:
                continue
            for row in table.find("tbody").find_all("tr"):
                try:
                    link = row.find("td").find("a").get("href")
                    header = soup.find(
                        "h3", id=link.lower().replace("#", "").replace(".", "")
                    )
                    func_it = DBFunction(
                        name=header.get_text(), link=page_prefix + page + link
                    )

                    # get syntax
                    func_it.syntax = header.find_next("pre").get_text()

                    # get description
                    start = header.find_next("p", string="Description")
                    end = start.find_next("strong").find_next(
                        "strong"
                    )  # this finds the next strong tag after the current
                    raw_description = get_contents_between(start, end, "p", strip=False)
                    func_it.description = "\n".join(
                        raw_description.splitlines()[:-1]
                    )  # above strategy catches one extra line for the next strong tag. This removes it
                    self.functions.append(func_it)
                except:
                    continue


class DATABRICKSscraper(DBDialect):
    def __init__(
        self,
    ):
        super().__init__(
            name="databricks",
            functions=[],
            keywords=[],
        )

    def scrape_keywords(self):
        soup = self.driver.scrape(
            "https://docs.databricks.com/en/sql/language-manual/sql-ref-reserved-words.html"
        )
        self.keywords.extend(
            [i.get_text() for i in soup.find("div", id="reserved-words").find_all("li")]
        )
        for id_ in [
            "reserved-words",
            "special-words-in-expressions",
            "reserved-schema-names",
            "ansi-reserved-words",
        ]:
            for i in soup.find("div", id=id_).find_all("li"):
                for j in i.find_all("p"):
                    txt = j.get_text()
                    if txt.isupper() and len(txt) > 1:
                        for k in txt.split(
                            ","
                        ):  # handles situation where row is a list of keywords instead of an individual keywor
                            self.keywords.append(k)

    def scrape_functions(self):
        # Navigate to the website you want to scrape
        url = "https://docs.databricks.com/en/sql/language-manual/sql-ref-functions-builtin-alpha.html"
        soup = self.driver.scrape(url)
        a_tags = soup.find_all("a", href=lambda href: href and "functions/" in href)

        url = (
            "https://docs.databricks.com/en/sql/language-manual/sql-ref-datatypes.html"
        )
        soup = self.driver.scrape(url)
        db_types = [
            i.text.split("\n")[0].split(" ")[0].split("(")[0].replace("`", "")
            for i in soup.find("tbody").find_all("tr")
        ]

        # Print the found links
        for a_tag in a_tags:
            func_name = a_tag["href"].split("/")[-1].replace(".html", "")
            func_url = (
                "https://docs.databricks.com/en/sql/language-manual/" + a_tag["href"]
            )
            func_it = DBFunction(name=func_name, link=func_url, arguments=[])

            ## get info about function
            soup = self.driver.scrape(func_it.link)

            ### get description
            try:
                func_it.description = (
                    soup.find(
                        lambda tag: tag.name == "p"
                        and tag.find("strong", string="Applies to:")
                    )
                    .find_next("p")
                    .text.strip()
                )
            except:
                pass

            ### get syntax
            try:
                func_it.syntax = (
                    soup.find("div", attrs={"id": "syntax"})
                    .find_next("pre")
                    .text.strip()
                )
            except:
                pass

            ### get arguments
            func_it.arguments = []
            try:
                raw_arguments = [
                    i.text
                    for i in soup.find("div", attrs={"id": "arguments"})
                    .find_next("ul")
                    .find_all("li")
                ]
            except:
                pass

            if raw_arguments:
                for arg in raw_arguments:
                    try:
                        arg_name = arg.split(":")[0]
                        arg_description = arg.split(":")[1].strip()
                        arg_it = DBArgument(name=arg_name, description=arg_description)
                        description_words = arg_description.split(" ")
                        all_caps = [
                            i
                            for i in description_words
                            if i.isupper() and any(j in i for j in db_types)
                        ]
                        if len(all_caps) > 0:
                            arg_it.type = "|".join(all_caps)
                        arg_it.optional = "optional" in arg_description
                        func_it.arguments.append(arg_it)

                    except:
                        pass

            self.functions.append(func_it)


class REDSHIFTscraper(DBDialect):
    driver: Driver

    def __init__(
        self,
    ):
        super().__init__(name="redshift", functions=[], keywords=[])
        self.driver = Driver()

    def scrape_keywords(self):
        soup = self.driver.scrape(
            "https://docs.aws.amazon.com/redshift/latest/dg/r_pg_keywords.html"
        )
        keyword_string = soup.find("pre").get_text()
        self.keywords = [i for i in keyword_string.split("\n") if i != ""]
        print(self.keywords)

    def scrape_functions(self):
        soup = self.driver.scrape(
            "https://docs.aws.amazon.com/redshift/latest/dg/c_SQL_functions.html"
        )
        pages = get_amazon_links(soup)
        for page in pages:
            soup_page = self.driver.scrape(page)
            try:
                func_links = get_amazon_links(soup_page)
            except:
                continue
            for link in func_links:
                func_soup = self.driver.scrape(link)
                try:
                    parent_div = func_soup.find("div", attrs={"id": "main-col-body"})
                    tag_prefix = link.split("/")[-1].replace(".html", "")
                    if tag_prefix.startswith("r_"):
                        name = tag_prefix[2:]
                    else:
                        name = tag_prefix
                    func_it = DBFunction(name=name, arguments=[])
                except:
                    continue

                # get syntax
                try:
                    start = parent_div.find("h2", id=tag_prefix + "-syntax")
                    if not start:
                        start = parent_div.find(
                            "h2", id=tag_prefix + "-synopsis"
                        )  # header tag sometimes called start and sometimes called synopsis
                    end = start.find_next("h2")
                    func_it.syntax = get_contents_between(start, end, "pre")
                except:
                    pass

                # get description
                try:
                    start = parent_div.find("h1", id=tag_prefix)
                    end = start.find_next("h2")
                    raw_descriptions = get_contents_between(start, end, "p")
                    func_it.description = " ".join(
                        [i.strip() for i in raw_descriptions.splitlines()]
                    )
                except:
                    pass

                # get arguments
                try:
                    parent_div = func_soup.find("div", class_="variablelist")
                except:
                    pass
                try:
                    dl = parent_div.find("dl")
                    arg_names = [i.get_text(strip=True) for i in dl.find_all("dt")]
                    arg_descriptions = [
                        i.get_text(" ", strip=True) for i in dl.find_all("dd")
                    ]
                    for i, el in enumerate(arg_descriptions):
                        lines = el.splitlines()
                        lines = [line.strip() for line in lines]
                        arg_it = DBArgument(
                            name=arg_names[i], description=" ".join(lines)
                        )
                        func_it.arguments.append(arg_it)
                except:
                    pass

                # account for the fact that some redshift pages have multiple functions embedded and irregular page naming syntax. Tries to figure out name from function syntax instead if possible
                if not func_it.syntax:
                    continue
                try:
                    for line in func_it.syntax.splitlines():
                        if "(" not in line:
                            split_ = (
                                line.strip()
                            )  # handles case where function has no arguments
                        else:
                            split_ = line.split("(")
                        func_names = split_[0].split("|")

                        for func_name in func_names:
                            func_name = func_name.strip()
                            if func_name:
                                self.functions.append(
                                    DBFunction(
                                        name=func_name,
                                        arguments=func_it.arguments,
                                        syntax=func_name + "(" + split_[1],
                                        description=func_it.description,
                                    )
                                )
                except:
                    self.functions.append(func_it)
