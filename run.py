import subprocess
import os
import argparse

root = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser(description="Config the SSMS Application")
parser.add_argument('-e', '--env', metavar='env', type=str, help='The env path', default='./.env')

args = parser.parse_args()
env_path = args.env

gunicorn_virtual_env = os.path.join(env_path, 'bin/gunicorn')


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
