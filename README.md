chimera
=======

Website editor for Jekyll sites

## Development environment setup
1. Install virtualenv and virtualenvwrapper

  ```
  pip install virtualenv virtualenvwrapper
  ```

2. Add the following lines to your `.bashrc` or `.zshrc`, then restart your shell

  ```
  export WORKON_HOME=$HOME/.venvs
  source /usr/local/bin/virtualenvwrapper.sh
  ```
  **Note:** location of virtualenvwrapper.sh depends on your distribution, it might also be in `/usr/bin`.

3. Create a virtualenv for the project

  ```
  mkvirtualenv -p /usr/bin/python2.7 chimera
  ```

4. When working on the project, don't forget to run `workon chimera`, and when leaving, run `deactivate` to restore your normal Python setup.
5. Run `pip install -r requirements.txt` to install all needed Python modules.
6. Copy `instance/application.cfg.example` to `instance/application.cfg` and edit as needed.
7. Install CouchDB. Ensure it is running.
8. Run the application with `python run.py` (while in the virtualenv). The database should be initialized automatically.
9. To generate site previews, you will also need a Ruby version 1.9.3 or higher and the 'jekyll' gem. On Ubuntu 14.04:

  ```
  sudo apt-get install ruby2.0
  sudo gem2.0 install jekyll therubyracer
  ```
  OR

  ```
  sudo apt-get install ruby1.9.1
  sudo gem1.9.1 install jekyll therubyracer
  ```
  You may also need to install `build-essential` if your system does not already have it.

  **Note:** The `ruby1.9.1` package on Debian-based systems is actually Ruby 1.9.3.

## Deployment with Docker
1. From the root of this repository, build the Docker image:

  ```
  docker build -t deltawhy/chimera .
  ```

2. Create an instance folder. Copy `instance/application.cfg.example` to `application.cfg` in this folder and edit as needed.
3. Create a data container. This makes it easier to update the application without losing your stored data.

  ```
  docker run -d -v /path/to/your/instance:/app/instance -v /data -v /var/lib/couchdb --name chimera-data ubuntu:trusty true
  ```

4. Start the application container.

  ```
  docker run -d --volumes-from chimera-data -p 80:8080 --name chimera deltawhy/chimera
  ```

5. Finally, you'll need to give your Chimera instance commit access to your website repository.
  For GitHub, creating a dedicated account for the editor is recommended. The public key can be found in your instance folder at
  `instance/id_rsa_chimera.pub` after the application is started.
