## Intro
Script to bulk-download slides (pdf) from indico using the official [API](https://docs.getindico.io/en/stable/http-api/).

## Setup 
Create an API key in your indico instance here: https://indico.cern.ch/user/api/

Create a file named `api.secret` containing your HTTP API key `Token` in the first line and the `Secret` in the second.

## Use
Specify the url containing the category id, a regex matching the event title of all events that should be fetched and the name for an output dir for the slides to be downloaded into.

General usage:
```
python indicoscraper.py [url] [regex] [out_dir]
```

Example usage:
```
python indicoscraper.py indico.cern.ch/category/3285/ "Run 3.*Analysis Meeting" out_dir
```

The downloaded pdf's will have a klickable (but invisible) link to their original url (the 'contribution' on the indico page) in the upper left corner of each page.
