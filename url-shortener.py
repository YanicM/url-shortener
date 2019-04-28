from flask import Flask, request, redirect
from urllib.parse import urlparse
import json, os
import random, string
import datetime, dateutil.parser

app = Flask(__name__)

site_root = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(site_root, "data", "urls.json")
letters_digits = string.ascii_letters + string.digits


@app.route('/', methods=['GET'])
def input_page():
    """Either start creating a new shortcut or redirect to another page."""
    urls = json.load(open(json_url))

    #  Redirect to the corresponding URL if the ID was found.
    url_key = request.args.get('i')
    if url_key in urls.keys():
        return redirect(urls[url_key]["url"], code=302)

    return str(type(urls)) + '''<form method="POST">
                   <input name="url">
                    <input type="submit" value="Create Link">
                </form>'''


@app.route('/', methods=['POST'])
def get_url():
    """This process creates the new shortcut and adds it to the DB."""

    #  Retrieve the URL from the original input field.
    input_url = request.form['url']

    # IMPLEMENT LOGIC TO VALIDATE URL!
    if all([c in letters_digits for c in input_url]):
        try:
            valid_url = urlparse(input_url)
            if all([valid_url.scheme, valid_url.netloc, valid_url.path]):
                input_url = valid_url.geturl()
        except:
            pass
    else:
        return 'This is not a valid URL.'
    if input_url.startswith(("http://", "https://")) != True:
        input_url = "http://{}".format(input_url)

    #  Generate a shortcut/ID for the URL.
    shortcut = ''.join(random.choice(letters_digits) for c in range(6))
    shortcut = str(shortcut).lower()

    #  Load the database.
    urls = json.load(open(json_url))

    #  Add the current time.
    now = datetime.datetime.now()
    #current_date = "{}-{}-{}".format(now.year, now.month, now.day)
    current_date = str(now)
    urls[shortcut] = {"url": input_url, "time": current_date}

    #  Delete IDs that are older than 30 days.
    old_ids = []
    for url_id in urls:
        time_since = now - dateutil.parser.parse(urls[url_id]["time"],
                                                 ignoretz=True)
        if time_since.days > 30:
            try:
                old_ids.append(url_id)
            except KeyError:
                pass
    for old_id in old_ids:
        del urls[old_id]

    #  Add the new URL to the JSON.
    with open(json_url, mode='w') as f:
        json.dump(urls, f, sort_keys=True, indent=2)

    #  Create a link to display.
    new_link = request.url + "?i=" + shortcut
    return '<a href="' + new_link + '">' + new_link + '</a> ' \
                            'is your new link for {}'.format(input_url)


if __name__ == '__main__':
    app.run()
