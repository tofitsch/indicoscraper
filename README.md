Script to bulk-download PDFs from indico and CDS using the official [indico API](https://docs.getindico.io/en/stable/http-api/) or [CDS RSS feeds](https://cds.cern.ch/rss).

The downloaded pdf's will have a klickable (but invisible) link to their original url in the upper left corner of each page.

# Indico
## Setup
Create an API key in your indico instance here: https://indico.cern.ch/user/api/

Create a file named `api.secret` containing your HTTP API key `Token` in the first line and the `Secret` in the second.

## Usage
Specify the url containing the category id, a regex matching the event title of all events that should be fetched and the name for an output dir for the slides to be downloaded into.

General usage:
```
python indicoscraper.py [url] [regex] [out_dir]
```

Example usage:
```
python indicoscraper.py https://indico.cern.ch/category/492/ "Jet Definitions.*MC.*" jetdef
```

# CDS
## Setup
So far none. Non-public files that require access are not supported yet.

## Usage
Specify the RSS feed URL as well as an output dir.

General usage:
```
python cdsscraper.py [url] [out_dir]
```

Example usage:
```
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+Papers" papers
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+Conference+Notes" confnotes
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+PUB+Notes" pubnotes
```
