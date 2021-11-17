# popup_content

Currently this is a proof-of-concept
to create content that can be embedded in a popup 
in an ArcGIS web map.

```bash
conda create -n flask_popup python flask flask-bootstrap flask-debugtoolbar autopep8 -c conda-forge
conda activate flask_popup
FLASK_APP=app.py flask run
```

The launch.json is set up to allow running the app inside VSCode,
select the flask_popup Python environment (you might have to restart VSCode),
select Python:Flask in the debugger and then F5 and stand back.



