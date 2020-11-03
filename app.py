import logging
from flask import Flask
from controller import routes
import conf
from pprint import pformat

app = Flask(__name__, template_folder=conf.TEMPLATES_DIR, static_folder=conf.STATIC_DIR)
app.register_blueprint(routes.routes)

logger = logging.getLogger('app')

# run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=conf.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')
    
    # Write all upper-case keys with string values in conf to log file
    logger.debug('conf = {}'.format(pformat({key: value 
                          for key, value in conf.__dict__.items() 
                          if key == key.upper()
                          and type(value) == str}
                          )))

    # run the Flask app
    app.run(debug=conf.DEBUG, threaded=True, use_reloader=False)