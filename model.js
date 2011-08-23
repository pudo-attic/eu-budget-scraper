{
  "dataset": {
    "model_rev": 1,
    "name": "eu",
    "label": "Budget of the European Union", 
    "description": "Budget of the European Union, including both revenue and expediture. Derived via scraping from [Budget online](http://eur-lex.europa.eu/budget/www/index-en.htm).",
    "currency": "EUR",
    "unique_keys": ["flow", "to.label", "country.name", "article.name", "item.name", "subitem.name", "time.unparsed"],
    "temporal_granularity": "year"
  },
  "mapping": {
    "amount": {
      "type": "value",
      "label": "Amount",
      "description": "",
      "column": "amount",
      "datatype": "float"
    },
    "time": {
      "type": "value",
      "label": "Year",
      "description": "",
      "column": "time",
      "datatype": "date"
    },
    "budget_year": {
      "type": "value",
      "label": "Budgeting Year",
      "description": "Reporting year for this figure",
      "column": "budget_year",
      "datatype": "string"
    },
    "projection": {
      "type": "value",
      "label": "Projection",
      "description": "Projected or outturn figures.",
	  "facet": true,
      "column": "projected",
      "datatype": "string"
    },
    "type": {
      "type": "value",
      "label": "Type",
      "description": "Type of Expenditure/Revenue",
	  "facet": true,
      "column": "type",
      "datatype": "string"
    },
    "flow": {
      "type": "value",
      "label": "Flow Direction",
      "description": "Expenditure or income",
	  "facet": false,
      "column": "flow",
      "datatype": "string"
    },
    "from": {
      "label": "Spender",
      "type": "entity",
      "facet": false,
      "description": "zugeordnete Verwaltungseinheit",
      "fields": [
        {"constant": "EU Budget", "name": "label", "datatype": "constant"}
      ]
    },
    "to": {
      "label": "Recipient",
      "type": "entity",
      "facet": true,
      "fields": [
        {"column": "volume_name", "name": "name", "datatype": "string"},
        {"column": "volume_label", "name": "label", "datatype": "string"},
		{"column": "volume_color", "name": "color", "datatype": "string"},
		{"constant": "true", "name": "eu_volume", "datatype": "constant"}
      ]
    },
    "country": {
      "label": "Country",
      "type": "entity",
      "facet": true,
      "fields": [
        {"column": "country_code", "name": "name", "datatype": "string"},
        {"column": "country", "name": "label", "datatype": "string"},
		{"column": "country_color", "name": "color", "datatype": "string"},
		{"constant": "true", "name": "eu_member_state", "datatype": "constant"}
      ]
    },
    "title": {
      "label": "Title",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "Level 2 of EU Budget Hierarchy",
      "facet": true,
      "fields": [
        {"column": "title_name", "name": "name", "datatype": "string"},
        {"column": "title_label", "name": "label", "datatype": "string"},
		{"column": "title_color", "name": "color", "datatype": "string"},
		{"constant": "title", "name": "level_name", "datatype": "constant"}
      ]
    },
    "chapter": {
      "label": "Chapter",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "Level 3 of EU Budget Hierarchy",
      "facet": false,
      "fields": [
        {"column": "chapter_name", "name": "name", "datatype": "string"},
        {"column": "chapter_label", "name": "label", "datatype": "string"},
		{"column": "chapter_color", "name": "color", "datatype": "string"},
		{"constant": "chapter", "name": "level_name", "datatype": "constant"}
      ]
    },
    "article": {
      "label": "Article",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "Level 4 of EU Budget Hierarchy",
      "facet": false,
      "fields": [
        {"column": "article_name", "name": "name", "datatype": "string"},
        {"column": "article_label", "name": "label", "datatype": "string"},
		{"column": "article_color", "name": "color", "datatype": "string"},
		{"column": "article_description", "name": "description", "datatype": "string"},
		{"column": "article_legal_basis", "name": "legal_basis", "datatype": "string"},
		{"constant": "article", "name": "level_name", "datatype": "constant"}
      ]
    },
    "item": {
      "label": "Item",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "Level 5 of EU Budget Hierarchy",
      "facet": false,
      "fields": [
        {"column": "item_name", "name": "name", "datatype": "string"},
        {"column": "item_label", "name": "label", "datatype": "string"},
		{"column": "item_color", "name": "color", "datatype": "string"},
		{"column": "item_description", "name": "description", "datatype": "string"},
		{"column": "item_legal_basis", "name": "legal_basis", "datatype": "string"},
		{"constant": "item", "name": "level_name", "datatype": "constant"}
      ]
    },
    "subitem": {
      "label": "Sub-Item",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "Level 4 of EU Budget Hierarchy",
      "facet": false,
      "fields": [
        {"column": "subitem_name", "name": "name", "datatype": "string"},
        {"column": "subitem_label", "name": "label", "datatype": "string"},
		{"column": "subitem_color", "name": "color", "datatype": "string"},
		{"column": "subitem_description", "name": "description", "datatype": "string"},
		{"column": "subitem_legal_basis", "name": "legal_basis", "datatype": "string"},
		{"constant": "subitem", "name": "level_name", "datatype": "constant"}
      ]
    }
  },
  "views": [
      {
          "entity": "dataset",
          "label": "Expenditure per Volume",
          "name": "default",
          "dimension": "dataset",
          "breakdown": "to",
          "filters": {"name": "eu"},
          "view_filters": {"flow": "spending"}
      },	
      {
          "entity": "dataset",
          "label": "Revenue per Country",
          "name": "countries",
          "dimension": "dataset",
          "breakdown": "country",
          "filters": {"name": "eu"},
          "view_filters": {"flow": "revenue"}
      },	
      {
          "entity": "entity",
          "label": "Expenditure per Title",
          "name": "default",
          "dimension": "to",
          "breakdown": "title",
          "filters": {"eu_volume": "true"},
          "view_filters": {"flow": "spending"}
      },	
      {
          "entity": "classifier",
          "label": "Expenditure per Chapter",
          "name": "default",
          "dimension": "title",
          "breakdown": "chapter",
          "filters": {"taxonomy": "eu", "level_name": "title"},
          "view_filters": {"flow": "spending"}
      },	
      {
          "entity": "classifier",
          "label": "Expenditure per Article",
          "name": "default",
          "dimension": "chapter",
          "breakdown": "article",
          "filters": {"taxonomy": "eu", "level_name": "chapter"},
          "view_filters": {"flow": "spending"}
      },	
      {
          "entity": "classifier",
          "label": "Expenditure per Item",
          "name": "default",
          "dimension": "article",
          "breakdown": "item",
          "filters": {"taxonomy": "eu", "level_name": "article"},
          "view_filters": {"flow": "spending"}
      },
      {
          "entity": "classifier",
          "label": "Expenditure per Sub-Item",
          "name": "default",
          "dimension": "item",
          "breakdown": "subitem",
          "filters": {"taxonomy": "eu", "level_name": "item"},
          "view_filters": {"flow": "spending"}
      },	
      {
          "entity": "entity",
          "label": "Revenue per Title",
          "name": "default",
          "dimension": "country",
          "breakdown": "title",
          "filters": {"eu_member_state": "true"},
          "view_filters": {"flow": "revenue"}
      }	
  ]
}


