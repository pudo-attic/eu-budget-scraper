# coding=UTF-8
from pprint import pprint
from lxml import html
from urlparse import urljoin
from csv import DictWriter
import json, os, sys, re

from webstore.client import DSN

BASE = "http://eur-lex.europa.eu/budget/data/D%s_VOL%s/EN/index.html"
MDASH =  u'—'
PREFIXEN = ['Subitem', 'Item', 'Article', 'Chapter', 'Title', 'Volume']
UNIQUE_COLUMNS = ['time', 'item_name', 'article_name', 'projection', 'flow',
                  'country', 'volume_name', 'type']

def split_title(title):
    title = title.replace(u'\xa0', ' ')
    title = title.replace(u'\u2014', '-')
    if MDASH in title: # this is mdash 
        name, label = title.split(MDASH, 1)
    if '-' in title: 
        name, label = title.split('-', 1)
    else:
        name, label = title.strip(), ''
    for prefix in PREFIXEN: 
        name = name.replace(prefix, '').strip()
    name = name.replace(' ', '.')
    #print "NAME", name
    return name.strip(), label.strip()

def load_budget(year, table):
    rows = []
    for i in range(10):
        ctx = {'budget_year': year}
        url = BASE % (year, i+1)
        try:
            for v in load_volume(url, ctx):
                rows.append(v)
                print map(lambda x: v.get(x), UNIQUE_COLUMNS)
                if len(rows) % 100 == 0:
                    table.writerows(rows, unique_columns=UNIQUE_COLUMNS)
                    rows = []
        except:
            # data protection was only established 2007:
            #if year > 2006 or i != 10:
            #    raise
            pass
    table.writerows(rows, unique_columns=UNIQUE_COLUMNS)

def load_volume(base_url, context):
    context = context.copy() 
    doc = html.parse(base_url)
    title = doc.find('//title').text
    context['volume_name'], context['volume_label'] = split_title(title)
    print "VOLUME", context['volume_name']
    for a in doc.findall('//a'):
        if 'nmc-title' in a.get('href'):
            url = urljoin(base_url, a.get('href'))
            for v in load_title(url, context):
                yield v

def load_title(base_url, context):
    context = context.copy()
    doc = html.parse(base_url)
    title = doc.find('//title').text
    context['title_name'], context['title_label'] = split_title(title)
    print " TITLE", context['title_name']
    for a in doc.findall('//a'):
        if a.get('href') and 'nmc-chapter' in a.get('href'):
            url = urljoin(base_url, a.get('href'))
            for v in load_chapter(url, context):
                yield v

def load_chapter(base_url, context):
    context = context.copy()
    doc = html.parse(base_url)
    title = doc.find('//title').text
    context['chapter_name'], context['chapter_label'] = split_title(title)
    print "  CHAPTER", context['chapter_name']
    known_articles = []
    for a in doc.findall('//a'):
        href = unicode(a.get('href')).rsplit('#', 1)[0]
        if href and 'articles' in href and not href in known_articles:
            known_articles.append(href)
            url = urljoin(base_url, href)
            for v in load_articles(url, context):
                yield v

def load_articles(base_url, context):
    context = context.copy()
    doc = html.parse(base_url)
    print "   URL", base_url
    current_article = None
    current_item = None
    current_subitem = None
    current_meta = None
    article_metas = {}
    item_metas = {}
    subitem_metas = {}
    values = None
    has_table = False

    def _emit():
        ctx = context.copy() 
        def apply_metas(m, prefix): 
            ctx[prefix + '_legal_basis'] = []
            ctx[prefix + '_description'] = ''
            for section, nodes in m.items():
                if section is None:
                    continue
                elif section == 'legal':
                    ctx[prefix + '_legal_basis'] = [n.text_content().strip() for n in nodes]
                elif section == 'remarks':
                    ctx[prefix + '_description'] = "\n".join([html.tostring(n) for n in nodes])
            ctx[prefix + '_legal_basis'] = '\n\n'.join(ctx[prefix + '_legal_basis'])
        ctx['article_name'], ctx['article_label'] = split_title(current_article)
        print "    ARTICLE", ctx['article_name']
        apply_metas(article_metas, 'article')
        
        if current_item:
            ctx['item_name'], ctx['item_label'] = split_title(current_item)
            print "     ITEM", ctx['item_name']
        else:
            ctx['item_name'], ctx['item_label'] = None, None
        apply_metas(item_metas, 'item')
        
        if current_subitem:
            ctx['subitem_name'], ctx['subitem_label'] = split_title(current_subitem)
            print "     SUBITEM", ctx['subitem_name']
        else:
            ctx['subitem_name'], ctx['subitem_label'] = None, None
        apply_metas(subitem_metas, 'subitem')
        
        #print ctx.get('article_name')
        for value in values: 
            value.update(ctx)
            if not 'country' in value:
                value['country'] = 'European Union'
            #if value.get('subitem_name'):
            #    pprint(value)
            if value.get('amount') is not None:
                yield value

    for node in doc.find('//body').iterchildren():
        if node.get('class') == 'nmc-article':
            if current_article is not None:
                for v in _emit():
                    yield v
            has_table = False
            current_item = None
            current_subitem = None
            current_article = node.text
            item_metas = {}
            subitem_metas = {}
            article_metas = {}
        elif node.get('class') == 'nmc-item': 
            if current_item is not None:
                for v in _emit():
                    yield v
            has_table = False
            current_subitem = None
            item_metas = {}
            subitem_metas = {}
            current_item = node.text
        elif node.get('class') == 'nmc-subitem':
            if current_subitem is not None:
                for v in _emit():
                    yield v
            has_table = False
            subitem_metas = {}
            current_subitem = node.text_content()
        elif node.tag == 'table' and not has_table:
            values = handle_table(node)    
            has_table = True
        elif node.get('class') == 'bud-remarks':
            current_meta = 'remarks'
        elif node.get('class') == 'bud-legal':
            current_meta = 'legal'
        elif isinstance(node, html.HtmlComment): 
            comment = node.text_content()
            if 'eurlexfooter' in comment.lower():
                break
        elif node.tag == 'table' and \
            'Member State' in node.text_content():
            values = handle_members(node, values)
        #elif node.tag == 'table':
        #    print html.tostring(node)
        else:
            if current_subitem is not None: 
                cur = subitem_metas.get(current_meta, [])
                cur.append(node)
                subitem_metas[current_meta] = cur
            elif current_item is not None:
                cur = item_metas.get(current_meta, [])
                cur.append(node)
                item_metas[current_meta] = cur
            else:
                cur = article_metas.get(current_meta, [])
                cur.append(node)
                article_metas[current_meta] = cur
    if current_article or current_item or current_subitem:
        for v in _emit():
            yield v

def handle_number(c):
    try: 
        cell_value = c.text_content().strip()
        #print "NUM", cell_value
        cell_value = re.sub("\(.*\)", "", cell_value)
        cell_value = ''.join([c for c in cell_value if c in "-0123456789,"])
        value = cell_value.replace(",", ".")
        #print "VAL", value
        return float(value)
    except ValueError:
        return None


def handle_members(table, values):
    members = []
    for row in table.findall('.//tr'):
        member = {}
        for col, value in zip(row.findall('.//td'), [None] + values):
            if value is None:
                member['country'] = col.text_content().strip()
            else:
                val = value.copy()
                val.update(member)
                val['amount'] = handle_number(col)
                if not 'Total' in val['country']:
                    members.append(val)
    return members
            

def handle_table(table):
    values = []
    headers = [{}] * len(table.find('.//tbody/tr').findall('./td'))
    i = 0
    for header in table.findall('.//thead/tr/th'):
        header_text = header.text_content().strip()
        if 'Item Subitem' in header_text: 
            return {}
        
        for colnum in range(int(header.get('colspan', '1'))):
            c = i % len(headers)
            if ('Appropriations' in header_text or \
                'Outturn' in header_text or \
                'Budget' in header_text):
                type_, year = header_text.strip().split(' ', 1)
                headers[c] = {}
                headers[c]['time'] = int(year)
                headers[c]['type'] = type_.lower()
                headers[c]['projection'] = type_ != 'Outturn'
                if type_ == 'Appropriations':
                    flow = 'spending'
                elif type_ == 'Budget': 
                    flow = 'revenue'
                headers[c]['flow'] = flow
            
            if 'Commitments' in header_text:
                headers[c]['commitment'] = True
            elif 'Payments' in header_text:
                headers[c]['commitment'] = False
            else:
                headers[c]['commitment'] = True
            i += 1
    #print "HEADER", headers
    for row in table.findall('.//tbody/tr'):
        flow = None
        for i, c in enumerate(row.findall('td')):
            if int(c.get('colspan', '1')) > 1: 
                continue
            cell = headers[i].copy()
            cell['amount'] = handle_number(c)
            values.append(cell)
            #print i, cell
    return values


if __name__ == "__main__":
    db = DSN("eubudget")
    table = db['raw']
    #table.delete()
    for y in [2010, 2009, 2008, 2007, 2006, 2005]:
        load_budget(y, table)
