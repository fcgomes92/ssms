import os
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Config the SSMS Application")
parser.add_argument('-e', '--env', metavar='env', type=str, help='The env path', default='./.env')

args = parser.parse_args()
env_path = args.env

root = os.path.abspath(os.path.dirname(__file__))

python_virtual_env = os.path.join(env_path, 'bin/python')
pip_virtual_env = os.path.join(env_path, 'bin/pip')
app_env_path = os.path.join(root, 'ssms/.env')
requirements_path = os.path.join(root, 'requirements.txt')


def main():
    install_process = subprocess.Popen((pip_virtual_env, 'install', '-r', requirements_path))
    install_process.wait()

    with open(app_env_path, 'w') as file:
        file.writelines("""STORAGE_PATH={root}/static
DATABASE_URI=sqlite:///:memory:
LOGGING_LEVEL=10
DEBUG=True""".format(root=root))


if __name__ == '__main__':
    main()
