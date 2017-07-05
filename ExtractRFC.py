#  RFC_Library - Access to every RFC
#
# Copyright (c) <2017> <Larz60+>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Credits: All RFC data comes from: https://www.rfc-editor.org
# 
# also see: https://www.rfc-editor.org/search/rfc_search.php
#           self.text_url_base = 'https://www.rfc-editor.org/rfc/rfc10.txt'
#           self.pdf_url_base = 'https://www.rfc-editor.org/rfc/pdfrfc/rfc10.txt.pdf'
#           self.official_internet_Protocol_Standards = 'https://www.rfc-editor.org/standards'
#
import requests
from bs4 import BeautifulSoup
import socket
import sys
import json
import os.path


class ExtractRFC:
    def __init__(self, local=False):
        self.internet_available = self.has_internet()
        self.index_loaded = False
        self.fname = os.path.abspath('data\\rfc_index.json')
        if local:
            if os.path.isfile(self.fname):
                with open(self.fname) as f:
                    self.rfc_index = json.load(f)
                    self.index_loaded = True
        else:
            self.xurl = 'https://www.rfc-editor.org/rfc-index.xml'
            self.x = None
            self.soup = None
            self.rfc_entries = []
            self.tag_list = {}
            self.make_soup()
            self.get_tag_list()
            self.new_entry = False
            self.doc_id = None
            self.rfc_index = {}
            self.index_loaded = True

    def has_internet(self):
        return socket.gethostbyname(socket.gethostname()) != '127.0.0.1'

    def make_soup(self):
        if self.has_internet():
            with open('data\\rfc-index.xml', 'wb') as f:
                self.x = requests.get(self.xurl, stream=True).text
                f.write(self.x.encode(sys.stdout.encoding, errors='replace'))
            # This is a hack to get around MS utf-8 missing 5 utf-8 characters crude but works
            # see http://www.i18nqa.com/debug/bug-double-conversion.html for more information
            with open('data\\rfc-index.xml') as f:
                self.x = f.read()
        self.soup = BeautifulSoup(self.x, 'lxml')
        self.rfc_entries = self.soup.select('rfc-entry')

    def get_tag_list(self):
        for one_entry in self.rfc_entries:
            doc_id = one_entry.select('doc-id')[0].text
            tags = [tag.name for tag in one_entry.find_all()]
            for tag in tags:
                if tag not in self.tag_list:
                    self.tag_list[tag] = doc_id

    def extract_rfc(self, find_doc_id):
        for entry_num in range(len(self.rfc_entries)):
            rfc_entry = self.rfc_entries[entry_num]
            self.doc_id = rfc_entry.select('doc-id')[0].text
            if self.doc_id == find_doc_id:
                return rfc_entry
        return None

    @staticmethod
    def capitalize(word):
        return word[0].upper() + word[1:]

    def fetch_field(self, rfc_entry, field):
        for n, value in enumerate(rfc_entry.select(field)):
            if value.parent.name != 'rfc-entry':
                continue
            if self.new_entry and field == 'doc-id':
                self.doc_id = value.text
                self.rfc_index[self.doc_id] = {}
                self.new_entry = False
            subfields = value.find_all()
            slen = len(subfields)
            if slen:
                first_entry = True
                for sfield in subfields:
                    if sfield.name != 'p':
                        # Following is wrong, doesn't account for multiple entries like two (or more) authors
                        if field not in self.rfc_index[self.doc_id]:
                                self.rfc_index[self.doc_id][field] = {}
                        self.rfc_index[self.doc_id][field] = sfield.text
            else:
                self.rfc_index[self.doc_id][field] = value.text


def main():
    er = ExtractRFC(local=True)
    if er.index_loaded:
        print(er.rfc_index)
    else:
        if er.internet_available:
            er = ExtractRFC(local=False)
            print(er.rfc_index)
        else:
            print('No json file available and internet unavailable')

if __name__ == '__main__':
    main()
