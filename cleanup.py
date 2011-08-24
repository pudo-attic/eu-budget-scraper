#coding: utf-8
import sys
from csv import DictReader, DictWriter, field_size_limit
from pprint import pprint

from webstore.client import URL as WebStore

EXTRA_FIELDS = ['volume_color', 'country_code', 'country_color']

CODE_FIELDS = ['title_name', 'subitem_name', 'item_name',
               'article_name', 'chapter_name']

EU27 = {
    "Belgium": "BE",
    "France": "FR",
    "Austria": "AT",
    "Bulgaria": "BG",
    "Italy": "IT",
    "Poland": "PL",
    "Czech Republic": "CZ",
    "Cyprus": "CY",
    "Portugal": "PT",
    "Denmark": "DK",
    "Latvia": "LV",
    "Romania": "RO",
    "Germany": "DE",
    "Lithuania": "LT",
    "Slovenia": "SI",
    "Estonia": "EE",
    "Luxembourg": "LU",
    "Slovakia": "SK",
    "Ireland": "IE",
    "Hungary": "HU",
    "Finland": "FI",
    "Greece": "EL",
    "Malta": "MT",
    "Sweden": "SE",
    "Spain": "ES",
    "Netherlands": "NL",
    "United Kingdom": "UK",
    "European Union": "EU"
}

EU_COLORS = {
    "BE": "#FFCC00",
    "FR": "#2E16B1",
    "AT": "#A2000C",
    "BG": "#FF9140",
    "IT": "#228D00",
    "PL": "#A0000F",
    "CZ": "#472B83",
    "CY": "#006B53",
    "PT": "#FF6200",
    "DK": "#9D0019",
    "LV": "#268E00",
    "RO": "#4AA329",
    "DE": "#A63F00",
    "LT": "#009E8E",
    "SI": "#5DCFC3",
    "EE": "#FF9140",
    "LU": "#FF9A00",
    "SK": "#B52D43",
    "IE": "#268E00",
    "HU": "#A66400",
    "FI": "#3BDA00",
    "EL": "#259433",
    "MT": "#A60800",
    "SE": "#FFA900",
    "ES": "#0969A2",
    "NL": "#FF6F00",
    "UK": "#062170",
    "EU": "#003399"
}

VOLUME_NAMES = {
        'SECTION.V': 'Section 5', 
        'Section.VOL7': 'Section 6', 
        'SECTION.VII': 'Section 7', 
        'SECTION.IV': 'Section 4',
        'SECTION.VIII': 'Section 8',
        '1': 'Section 0', 
        '4.(section.3)': 'Section 3', 
        'SECTION.II': 'Section 2', 
        'SECTION.IX': 'Section 9', 
        'SECTION.I': 'Section 1'
        }

VOLUME_COLORS = {
        'SECTION.V': '#015367', 
        'Section.VOL7': '#A60400', 
        'SECTION.VII': '#39E444', 
        'SECTION.IV': '#04819E',
        'SECTION.VIII': '#770060',
        '1': '#A65F00', 
        '4.(section.3)': '#003399', 
        'SECTION.II': '#008500', 
        'SECTION.IX': '#48036F', 
        'SECTION.I': '#FF8C00'
        }

def expand_code(code):
    return ".".join([p.zfill(2) for p in code.split('.')])

def dependent_column(table, src_column, dst_column, lookup):
    print "SRC", src_column, "DST", dst_column
    for src_value in table.distinct(src_column):
        value = src_value.get(src_column)
        dst_value = lookup(value)
        row = {dst_column: dst_value,
               src_column: value}
        pprint(row)
        table.writerow(row, unique_columns=[src_column])

def extend_budget(url):
    db, table = WebStore(url, "raw")
    fun = lambda i: VOLUME_COLORS.get(i)
    dependent_column(table, 'volume_name', 
                     'volume_color', fun)
    fun = lambda i: VOLUME_NAMES.get(i)
    dependent_column(table, 'volume_name', 
                     'volume_normalized_name', fun)
    fun = lambda i: EU27.get(i)
    dependent_column(table, 'country', 
                     'country_code', fun)
    fun = lambda i: EU_COLORS.get(i)
    dependent_column(table, 'country_code', 
                     'country_color', fun)
    for col in CODE_FIELDS:
        dependent_column(table, col, col + '_expanded', 
                         expand_code)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    #process_file(sys.argv[1], sys.argv[2])
    extend_budget(sys.argv[1])
