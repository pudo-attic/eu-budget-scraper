
European Budget Scraper and OpenSpending Mapping
================================================

CAVEAT: The scripts in this repository are subject to quality constraints: 

* Loss of precision due to screen-scraping of the data from relatively unstructured sources. The scraper is known to not extract all available information and some of the handling of scraped items is questionable. 

* Lack of understanding of the EU budgeting process and document on the part of the author, combined with the relative complexity of the document.


Basic structure
---------------

The EU budget has the following levels:

* Volume (Commission, Parliament and "small stuff")
* Title
* Chapter
* Article
* Item
* Sub-Item

Each level is identified with a two-digit (or 'XX') identifier, 
yielding IDs of the form: Volume 4, 06.02.01.03. 

The breakdown at the item and sub-item levels is not made in each part 
of the budget. 

Additonally, some items and sub-items are broken down on a per-country
basis. This is mostly true for the EU's revenue, i.e. Own Resources.


Running it
----------

Run "scrape.py" to get basic CSV files. Then, use cleanup.py on each of 
them to do some cleansing. To import into OpenSpending, the following 
command line is needed: 

paster --plugin=wdmmg csvimport -c $CONFIG --model=file:model.js eu-2010.csv.cleaned

License
-------

Any copyrights - if present - are to be treated under the terms of the 
Open Data Commons ODbL (Share-Alike for Databases).

http://www.opendatacommons.org/licenses/odbl/


