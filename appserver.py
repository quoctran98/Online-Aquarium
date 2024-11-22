import eventlet
eventlet.monkey_patch()

from server.__init__ import create_app

if __name__ == '__main__':
    print("🧪 Starting in development mode")
    app = create_app()
    app.run()
else:
    print("🦄 Starting in not development mode using gunicorn")
    gunicorn_app = create_app()