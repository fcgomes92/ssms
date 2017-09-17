import subprocess
import os

root = os.path.abspath(os.path.dirname(__file__))

gunicorn_virtual_env = os.path.join(root, '.env/bin/gunicorn')


def main():
    try:
        print('Starting server with: {}'.format(gunicorn_virtual_env))
        p = subprocess.Popen((gunicorn_virtual_env, '--reload', 'ssms.app:create_app()'))
        p.wait()
    except KeyboardInterrupt:
        try:
            p.terminate()
        except OSError:
            pass
        p.wait()


if __name__ == '__main__':
    main()
