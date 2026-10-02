# Method 3: Most Update Web Scraping Technique
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sqlite3



# Extract PubMed ID through GSEID
##Enter GSEID as string
def gse_pmid(soup_gse):
    import requests
    from bs4 import BeautifulSoup
    meta_info = soup_gse.find_all("span", class_="pubmed_id", attrs={})[0].text
    return meta_info

# Generate PMID List
def pmid_ls(gse_list):
    id_ls = []
    for i in gse_list:
        pmid = gse_pmid(i)
        # If GSE has more than 1 PMID, save the first PMID to list
        if "," in pmid:
            first_pmid = pmid.split(",")[0]
            id_ls.append(first_pmid)
        else:
            id_ls.append(pmid)
    return id_ls


# Generate dictionary for GSEID:PMID
def id_dic(gse_list):
    dic = {}
    for gse in gse_list:
        pmid = gse_pmid(gse)
        # If GSE has more than 1 PMID, save the first PMID to list
        if "," in pmid:
            first_pmid = pmid.split(",")[0]
            dic[gse] = first_pmid
        else:
            dic[gse] = pmid
    return dic


# Generate dictionary for PMID:GSEID
def pmid_dic(dic):
    dic_new = {}
    for k, v in dic.items():
        dic_new.update({v: k})
    return dic_new


# Extract PudMed ID
def pubmed_id(soup):
    meta_info = soup.find_all("meta", attrs={'name': 'citation_pmid'})
    pm_id = str(meta_info[0]).split('"')[1]
    return pm_id


def author_name(soup,author_index):
    affiliation = soup.find_all('span', class_='authors-list-item')
    sub_layer1 = list(affiliation)[author_index]
    sub_layer2 = list(sub_layer1.children)
    author = list(sub_layer2[0].children)[0]
    return author

# Author Name List
def name_full_list(soup,num_author):
    name = []
    for i in range(num_author):
        name.append(author_name(soup,i))
    return name


## Author name list for pmid that already exist in database
def name_full_list_db(pmid):
    conn = sqlite3.connect("recom_sys.db")
    cur = conn.cursor()
    cur.execute(f'''select contact,GROUP_CONCAT(first_name||' '||last_name)
    FROM author_publication ap
    JOIN author au
    ON au.author_id = ap.author_id
    WHERE pmid={pmid};''')
    fetch_author_tuple = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    fetch_author_ls=fetch_author_tuple[0][1].split(",")
    return fetch_author_ls

def test_name_full_list_db(pmid):
    if not pmid or pd.isna(pmid):
        return [""]
    else:
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        cur.execute(f'''select contact,GROUP_CONCAT(first_name||' '||last_name)
        FROM author_publication ap
        JOIN author au
        ON au.author_id = ap.author_id
        WHERE pmid={pmid};''')
        fetch_author_tuple = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        fetch_author_ls=fetch_author_tuple[0][1].split(",")
        return fetch_author_ls


# Author first and last name dictionary
def first_last(author_list, ls_index):
    first_last_dic = {}
    name_list = author_list[ls_index].split(' ')
    if len(name_list) < 2:
        first_last_dic['FIRST_NAME'] = name_list[0]
        first_last_dic['LAST_NAME'] = ''
    elif len(name_list) < 3:
        first_last_dic['FIRST_NAME'] = name_list[0]
        first_last_dic['LAST_NAME'] = name_list[1]
    else:
        first_middle = name_list[0] + ' ' + name_list[1]
        first_last_dic['FIRST_NAME'] = first_middle
        first_last_dic['LAST_NAME'] = name_list[2]
    return first_last_dic

def first_last_contact(name):
    first_last_dic = {}
    name_list = name.split(' ')
    if len(name_list) < 2:
        first_last_dic['FIRST_NAME'] = name_list[0]
        first_last_dic['LAST_NAME'] = ''
    elif len(name_list) < 3:
        first_last_dic['FIRST_NAME'] = name_list[0]
        first_last_dic['LAST_NAME'] = name_list[1]
    else:
        first_middle = name_list[0] + ' ' + name_list[1]
        first_last_dic['FIRST_NAME'] = first_middle
        first_last_dic['LAST_NAME'] = name_list[2]
    return first_last_dic

# Count how many authors in this publication
def author_count(soup):
    affiliation = soup.find_all('span', class_='authors-list-item')
    search_text = "data-ga-label"
    list_match = re.findall(search_text, str(affiliation))
    num_author = len(list_match) / 2
    return num_author

def test_author_count(soup):
    author_ls_soup=soup.find(class_="authors-list")
    data_label_ls=re.findall("data-ga-label", str(author_ls_soup))
    num_author=len(data_label_ls)
    return num_author

# Find Affiliation New Version
##Drop footnote
def drop_footnote(str):
    str_ls = str.split(" ")
    for i in str_ls:
        if "]" in i:
            str_ls.remove(i)
    str_new = ' '.join(str_ls)
    return str_new


def affiliation(soup,num_author):
    affiliation = soup.find_all('span',class_='authors-list-item')
    if 'affiliation-link' in str(affiliation[num_author]):
        af1 = list(affiliation[num_author].children)[1]
        if len(af1) < 2:
            return ''
        else:
            af2 = list(af1.children)[1]
            import re
            rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
            search_rs = re.findall(rule_aff, str(af2))
            affiliation = search_rs[0].split("=")
            search_character = "@"
            match_index = re.search(search_character, affiliation[1])
            rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
            if match_index:
                affiliation = re.sub(rule, '', affiliation[1])
                affiliation = str(affiliation)
                return affiliation
            else:
                affiliation = drop_footnote(affiliation[1])
                return affiliation
    else:
        return ""



# Email New version
def email(soup,author_index,affiliation):
    email = soup.find_all('span', class_='authors-list-item')
    if affiliation == "":
        return '[]'
    elif '@' in str(email):
        e1 = list(email[author_index].children)[1]
        e2 = list(e1.children)[1]

        rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
        search_rs = re.findall(rule_aff, str(e2))
        affiliation_text = search_rs[0].split("=")
        search_character = "@"
        match_index = re.search(search_character, affiliation_text[1])
        rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
        if match_index:
            address = re.findall(rule, affiliation_text[1])
            return str(address[0])
        else:
            return '[]'
    else:
        return '[]'

#Email New version Alternation
def email_alter(affiliation):
    aff=str(affiliation)
    if  aff == "":
        return '[]'
    elif '@' in aff:
        import re
        search_character="@"
        match_index=re.search(search_character,aff)
        rule = "[a-zA-Z0-9+_.-]*\s*@\s*[a-zA-Z0-9+_.-]*\w"
        if match_index:
            address = re.findall(rule, aff)
            return str(address[0])
        else:
            return '[]'
    else:
        return '[]'


# Co_Author

def co_author(author_list,pmid,a_loc,author_id,max_id):
    if not pmid or pd.isna(pmid) :
        return []

    elif author_id<max_id:
        author_list_db=name_full_list_db(pmid)
        author_index=a_loc-1 # Minus 1 because author_location from database start from 1 but python start from 0
        co_a_ls = []
        for n in range(len(author_list_db)):
            name_list = author_list_db[n].split(' ')
            if len(name_list) < 2:
                co_a = (str(''), str(name_list[0]))
                co_a_ls.append(co_a)
            elif len(name_list) < 3:
                co_a = (str(name_list[1]), str(name_list[0]))
                co_a_ls.append(co_a)
            else:
                first_middle = name_list[0] + ' ' + name_list[1]
                co_a = (str(name_list[2]), str(first_middle))
                co_a_ls.append(co_a)
        co_a_ls.pop(author_index)
        return co_a_ls
    else:
        author_index = a_loc - 1
        co_a_ls = []
        for n in range(len(author_list)):
            name_list = author_list[n].split(' ')
            if len(name_list) < 2:
                co_a = (str(''), str(name_list[0]))
                co_a_ls.append(co_a)
            elif len(name_list) < 3:
                co_a = (str(name_list[1]), str(name_list[0]))
                co_a_ls.append(co_a)
            else:
                first_middle = name_list[0] + ' ' + name_list[1]
                co_a = (str(name_list[2]), str(first_middle))
                co_a_ls.append(co_a)
        co_a_ls.pop(author_index)
        return co_a_ls

def co_author(author_list,pmid,a_loc,author_id,max_id):
    if not pmid:
        return []

    elif author_id<max_id:
        author_list_db=test_name_full_list_db(pmid)
        author_index=a_loc-1 # Minus 1 because author_location from database start from 1 but python start from 0
        co_a_ls = []
        for n in range(len(author_list_db)):
            name_list = author_list_db[n].split(' ')
            if len(name_list) < 2:
                co_a = (str(''), str(name_list[0]))
                co_a_ls.append(co_a)
            elif len(name_list) < 3:
                co_a = (str(name_list[1]), str(name_list[0]))
                co_a_ls.append(co_a)
            else:
                first_middle = name_list[0] + ' ' + name_list[1]
                co_a = (str(name_list[2]), str(first_middle))
                co_a_ls.append(co_a)
        co_a_ls.pop(author_index)
        return co_a_ls
    else:
        author_index = a_loc - 1
        co_a_ls = []
        for n in range(len(author_list)):
            name_list = author_list[n].split(' ')
            if len(name_list) < 2:
                co_a = (str(''), str(name_list[0]))
                co_a_ls.append(co_a)
            elif len(name_list) < 3:
                co_a = (str(name_list[1]), str(name_list[0]))
                co_a_ls.append(co_a)
            else:
                first_middle = name_list[0] + ' ' + name_list[1]
                co_a = (str(name_list[2]), str(first_middle))
                co_a_ls.append(co_a)
        co_a_ls.pop(author_index)
        return co_a_ls


# Pair Match Authors information,generate gold standard and remove duplicated rows
## Cross match for table pull from SQL database.
def pair_sql(df):
    import pandas as pd
    df = df.rename(columns={'Unnamed: 0': 'index'})
    df['key'] = 1
    df_cross = pd.merge(df, df, on="key")

    # remove matches for name space more than 1 author
    ## Geneate a list that needs to remove duplicated match;
    group_counts = df.groupby('key').size()
    clean_ns_ls = []
    for n in range(1, group_counts.shape[0] + 1):
        if group_counts.loc[n] > 1:
            clean_ns_ls.append(n)

    ## removing duplication

    match_ls = []  ##Generate a list "Match_ls" that includes row indices that already paired
    df_index_only = df_cross[["AUTHOR_ID_x", "AUTHOR_ID_y"]]
    row_count = df_index_only.shape[0]
    for i in range(df_index_only.shape[0]):
        row1 = sorted(df_index_only.loc[i])
        for n in range(i, row_count):
            row2 = sorted(df_index_only.loc[n])
            if row1 == row2 and i != n:
                match_ls.append(n)
                break

    for i in range(df_cross.shape[0]):
        if (df_cross.loc[i, "key"] in clean_ns_ls) and (
                df_cross.loc[i, "AUTHOR_ID_x"] == df_cross.loc[i, "AUTHOR_ID_y"] or \
                i in match_ls):
            df_cross = df_cross.drop(i)

    df_cross = df_cross.sort_index(axis=1)

    return df_cross


# Special function: extract all pubmed_id from search page.
def batch_id(soup,source):
    import requests
    from bs4 import BeautifulSoup
    meta = soup.find_all("meta", {"name": "log_displayeduids"})
    id_ls = meta[0]["content"].split(",")
    return id_ls


# Generate author_info_name_adjusted_name_space.csv,author_info_name_adjusted_cross_match.csv,
# and author_info_name_adjusted_name_spaces_count.csv
def main(gse_list):
    import pandas as pd
    import time
    start = time.time()
    df = author_csv_second(gse_list)
    # df = pd.read_csv("author_info.csv")
    name_space_tbl = name_space(df)
    pair_tbl = pair(name_space_tbl)
    ns_count(name_space_tbl)
    end = time.time()
    total_time = end - start
    print("EXECUTION TIME = {:.2f} s".format(total_time))




# Convert into class
class author_local:
    def __init__(self,gseid,gse_file,pmid_file):
        self.gseid=gseid
        self.gse_file=gse_file
        self.pmid_file=pmid_file
        with open(self.pmid_file, encoding="utf-8") as fp:
            self.soup = BeautifulSoup(fp, 'html.parser')

    # Extract PubMed ID through GSEID
    ##Enter GSEID as string
    def gse_pmid(self):
        with open(self.gse_file, encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        meta_info = soup.find_all("span", class_="pubmed_id", attrs={})[0].text
        return meta_info

    # Extract PudMed ID
    def pubmed_id(self):
        meta_info = self.soup.find_all("meta", attrs={'name': 'citation_pmid'})
        pm_id = str(meta_info[0]).split('"')[1]
        return pm_id

    def author_name(self, author_index):
        affiliation = self.soup.find_all('span', class_='authors-list-item')
        sub_layer1 = list(affiliation)[author_index]
        sub_layer2 = list(sub_layer1.children)
        author = list(sub_layer2[0].children)[0]
        return author


    # Count how many authors in this publication
    def author_count(self):
        affiliation = self.soup.find_all('span', class_='authors-list-item')
        search_text = "data-ga-label"
        list_match = re.findall(search_text, str(affiliation))
        num_author = _author = len(list_match) / 2
        return num_author

    def affiliation(self, num_author):
        affiliation = self.soup.find_all('span', class_='authors-list-item')
        if 'affiliation-link' in str(affiliation[num_author]):
            af1 = list(affiliation[num_author].children)[1]
            if len(af1) < 2:
                self.affiliation=""
                return self.affiliation
            else:
                af2 = list(af1.children)[1]
                import re
                rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
                search_rs = re.findall(rule_aff, str(af2))
                affiliation = search_rs[0].split("=")
                search_character = "@"
                match_index = re.search(search_character, affiliation[1])
                rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
                if match_index:
                    self.affiliation = re.sub(rule, '', affiliation[1])
                    self.affiliation = str(self.affiliation)
                    return self.affiliation
                else:
                    self.affiliation=drop_footnote(affiliation[1])
                    return self.affiliation
        else:
            self.affiliation = ""
            return self.affiliation

    # Email New version
    def email(self, author_index):
        email = self.soup.find_all('span', class_='authors-list-item')
        if self.affiliation == "":
            return '[]'
        elif '@' in str(email):
            e1 = list(email[author_index].children)[1]
            e2 = list(e1.children)[1]
            import re
            rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
            search_rs = re.findall(rule_aff, str(e2))
            affiliation_text = search_rs[0].split("=")
            search_character = "@"
            match_index = re.search(search_character, affiliation_text[1])
            rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
            if match_index:
                address = re.findall(rule, affiliation_text[1])
                return str(address[0])
            else:
                return '[]'
        else:
            return '[]'








# Limitation
# for author having more than 1 affiliation, only first will be selected
# For GSE that associated with more than 1 PMID, always use 1st choice.






