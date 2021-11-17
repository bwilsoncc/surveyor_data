from logging import DEBUG
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """ 
Load configuration from environment. 

In PRODUCTION conda sets up the environment,
so look in ~/.conda/envs/covid/etc/conda/activate.d/env_vars.sh
to see how it is set up. 
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or "24681012"
 
    pass

class ProdConfig(Config):
    DEBUG = False

class DevConfig(Config):
    DEBUG = True

if __name__ == "__main__":

    pass

# That's all!
