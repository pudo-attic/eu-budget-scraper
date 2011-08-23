#coding: utf-8
import sys
from csv import DictReader, DictWriter, field_size_limit
from pprint import pprint

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
    "United Kingdom": "UK"
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
    "UK": "#062170"
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

def for_row(row):
    sys.stdout.write(".")
    sys.stdout.flush()
    for col in CODE_FIELDS:
        row[col] = expand_code(row[col])
    row['volume_color'] = VOLUME_COLORS.get(row['volume_name'])
    row['volume_name'] = VOLUME_NAMES.get(row['volume_name'])
    row['country_code'] = EU27.get(row['country'])
    row['country_color'] = EU_COLORS.get(row['country_code'])
    return row

def process_file(infile, outfile):
    field_size_limit(100000000)
    infile = open(infile, 'rb')
    outfile = open(outfile, 'wb')
    incsv = DictReader(infile)
    headers = list(incsv.fieldnames) + EXTRA_FIELDS
    outcsv = DictWriter(outfile, headers)
    outcsv.writerow(dict(zip(headers, headers)))
    print headers
    for row in incsv:
         outcsv.writerow(for_row(row))
    outfile.close()
    infile.close()

if __name__ == '__main__':
    assert len(sys.argv)==3, "Need 2 arguments: infile, outfile!"
    process_file(sys.argv[1], sys.argv[2])
