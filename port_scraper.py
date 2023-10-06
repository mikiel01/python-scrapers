from bs4 import BeautifulSoup
import requests
import time
import requests
from lxml import etree
from io import StringIO
from html.parser import HTMLParser

class PortUpdate:
    def __init__(self, nid_id, subject_text, date_text, priority_text, attachments_list, notice_text, notice_posted_text):
        self.subject = subject_text
        self.date = date_text
        self.priority = priority_text
        self.attachments = attachments_list
        self.notice = notice_text
        self.notice_posted = notice_posted_text
        self.nid = nid_id

def getNotices(node):
    parser = HTMLParser()
    etree.strip_tags(node, '*')
    s = parser.unescape(etree.tostring(node).decode('utf8'))
    # print(s)
    # s = node.text
    if s is None:
        s = ''
    for child in node:
        s += etree.tostring(child, encoding='unicode')
    return s

def getLinks(id_to_find, soup, get_links=False):
    strings = []
    table = soup.find(id=id_to_find)
    # print(table)
    links = table.find_all('a')

    if get_links:
        for link in links:
            if link.has_attr('href'):
                strings.append(link['href'])
    else:
        for link in links:
            strings.append(link.string)
    return strings


def walk(node, s):
    for child in node.getchildren():
        if child.text is not None:
            return walk(child, s)
    if node.text is not None:
        s = s +  node.text + " "
    return s

def getText(node, start=1):
    text = ""
    temp = node
    for i in range(start, len(node)):
        text += walk(node[i], "")


    return text

def getAttachments(node):
    attachments = []
    
    attachments_table_node = node[1][0]
    for i in range(0, len(attachments_table_node)):
        temp = attachments_table_node[i][0][0][0]
        if temp.text is not None:
            attachments.append(temp.text)

    return attachments
        
def scrape_page(url):
    port_update_request = requests.get(url)
    port_update_soup = BeautifulSoup(port_update_request.text, 'html.parser')
    port_update = port_update_soup.find(id="WebPartWPQ6")
    id_identifier = "NID="
    nid = getID(url, id_identifier)


    tree = etree.parse(StringIO(str(port_update)))
    root = tree.getroot()

    table_body = root[0][0][0][0]

    subject = table_body[0]
    subject_text = getText(subject)
    print(subject_text)
    date = table_body[1]
    date_text = getText(date)
    print(date_text)
    priority = table_body[2]
    priority_text = getText(priority)
    print(priority_text)
    attachments = table_body[3]
    attachments_text = getAttachments(attachments)
    print(attachments_text)
    notice = table_body[4][1][0][0]
    temp = notice
    notice_text = getNotices(notice)
    print(notice_text)

    notice_posted = table_body[5]
    notice_posted_text = getText(notice_posted, 0)
    print(notice_posted_text)
    port_update_info = PortUpdate(nid, subject_text, date_text, priority_text, attachments, notice_text, notice_posted_text)
    return port_update_info

def getID(url, id_string):
    index = url.find(id_string)
    i = index + len(id_string)
    s2 = ""
    while (i < len(url) and url[i] != "&"):
        s2 += url[i]
        i += 1
    return int(s2)
def run():
    req = requests.get("http://pta.ports.moranshipping.com/Pages/Notices.aspx?NID=5488&Year=2021&Month=July")
    soup = BeautifulSoup(req.text, 'html.parser')

    years = getLinks("WebPartWPQ3", soup)
    months = getLinks("WebPartWPQ4", soup)

    for year in years:
        for month in months:
            url = "http://pta.ports.moranshipping.com/Pages/Notices.aspx?NID=2&Year=" + str(year) + "&Month=" + str(month)

            req = requests.get(url)
            soup = BeautifulSoup(req.text, 'html.parser')
            port_update_links = getLinks("WebPartWPQ5", soup, True)
            for port_update_link in port_update_links:
                port_update_info = scrape_page("http://pta.ports.moranshipping.com/Pages/" + port_update_link)
                print(port_update_info.nid)
                time.sleep(1)
                # from here I would have already created a table for all info (nid, subject, date, priority, notice, and notice update)
                # I would create a separate table for the documents that maps to the nid
                # then i would just insert each port_update_info field into the database

run()