import os
import subprocess

root = os.path.abspath(os.path.dirname(__file__))

python_virtual_env = os.path.join(root, '.env/bin/python')
pip_virtual_env = os.path.join(root, '.env/bin/pip')
requirements_path = os.path.join(root, 'requirements.txt')
env_path = os.path.join(root, 'ssms/.env')


def main():
    install_process = subprocess.Popen((pip_virtual_env, 'install', '-r', requirements_path))
    install_process.wait()

    with open(env_path, 'w') as file:
        file.writelines("""STORAGE_PATH={root}/static
DATABASE_URI=sqlite:///:memory:
LOGGING_LEVEL=10
DEBUG=True""".format(root=root))


if __name__ == '__main__':
    main()
