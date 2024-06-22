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
python indicoscraper.py https://indico.cern.ch/category/492/ "Jet/Etmiss Main Meeting" jetetmissmain
python indicoscraper.py https://indico.cern.ch/category/3285/ "Trigger Level Analysis Meeting" tlarun2
python indicoscraper.py https://indico.cern.ch/category/3285/ "Run 3 TLA.*ISR.*DiJet Analysis Meeting" tlarun3
```

Since indico does not save who uploaded the material in a contribution and some contributions (e.g. roundtables) can have a long list of speakers the speaker name that goes into the file name is determined like so:
* The first page of the pdf (usually title slide) is converted to text
* If one of the words matches any of the first or last names of one of the contribution speakers on indico it is considered to be the name

# CDS
## Setup
So far none. Non-public files that require access are not supported yet.

## Usage
Specify the RSS feed URL as well as an output dir.

General usage:
```
python cdsscraper.py [url] [regex] [out_dir]
```

Example usage:
```
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+Papers" ".*PAPER.*pdf" papers
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+Conference+Notes" ".*CONF.*pdf" confnotes
python cdsscraper.py "https://cds.cern.ch/rss?cc=ATLAS+PUB+Notes" ".*PUB.*pdf" pubnotes
```
