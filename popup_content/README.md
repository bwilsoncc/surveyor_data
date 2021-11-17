# popup_content

Currently this is a proof-of-concept
to create content that can be embedded in a popup 
in an ArcGIS web map.

It will run just fine as a standalone flask app, on Windows or Linux. You'd start it this way.

```bash
conda create -n flask_popup python flask flask-bootstrap flask-debugtoolbar autopep8 -c conda-forge
conda activate flask_popup
FLASK_APP=app.py flask run
```

However! It is not usable in ArcGIS popups unless it's running on an HTTPS URL. 
So there is a Docker deployment option; this allows me to run it behind a proxy server.

## Development

The launch.json is set up to allow running the app inside VSCode,
select the flask_popup Python environment (you might have to restart VSCode),
select Python:Flask in the debugger and then F5 and stand back.

## Docker deployment

Set the environment for your site and then start it with

```bash
docker-compose up -d
```

