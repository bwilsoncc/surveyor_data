import os
from webapp import create_app
from version import version

env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())

if __name__ == '__main__':
    print("version:", version)
    app.run()
