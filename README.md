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
python indicoscraper.py https://indico.cern.ch/category/492/ "In situ*" insitu
python indicoscraper.py https://indico.cern.ch/category/492/ "Jet tagging" jettag
python indicoscraper.py https://indico.cern.ch/category/492/ "Jet/Etmiss Main Meeting" jetetmissmain
python indicoscraper.py https://indico.cern.ch/category/492/ "JetMET Coordination" jetetmisscoordination
python indicoscraper.py https://indico.cern.ch/category/3285/ "Trigger Level Analysis Meeting" tlarun2
python indicoscraper.py https://indico.cern.ch/category/3285/ "Run 3 TLA.*ISR.*DiJet Analysis Meeting" tlarun3
python indicoscraper.py https://indico.cern.ch/category/3286/ ".*(JDM|JMX).*" jmx
```

Since indico does not save who uploaded the material in a contribution and some contributions (e.g. roundtables) can have a long list of speakers the speaker name that goes into the file name is determined like so:
* The first page of the pdf (usually title slide) is converted to text
* If one of the words matches any of the first or last names of one of the contribution speakers on indico it is considered to be the name

Once a file would be downloaded that already exists in the `out_dir` the script exits. This allows to quickly updating just the new contributions in a particular category / meeting.

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

Once a file would be downloaded that already exists it is skipped. Note that this is different from the behaviour of `indicoscraper` which exits under that condition.

## ATLAS Figures
Often one wants to download all pdfs on a given web page.
E.g. when one wants to get all figures associated to an ATLAS publication. 
On the [ATLAS public results page](https://twiki.cern.ch/twiki/bin/view/AtlasPublic) there is a 'Documents' link for each publication that points to a web page with all figures.

Downloading them can be achieved via regex and wget.
To download all pdfs from the given url use:

```
url="https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/STDM-2018-41/"

for fig in $( grep -Po 'href="\K[^"]+pdf(?=")' <(curl $url) ); do
  wget -O $fig $url$fig
done
```
