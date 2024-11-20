from server.__init__ import create_app

import eventlet
eventlet.monkey_patch()

if __name__ == '__main__':
    create_app = create_app()
    create_app.run()
else:
    gunicorn_app = create_app()