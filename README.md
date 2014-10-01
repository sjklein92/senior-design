chimera
=======

Website editor for Jekyll sites

# Environment setup
1. Install virtualenv and virtualenvwrapper

  ```
  pip install virtualenv virtualenvwrapper
  ```

2. Add the following lines to your `.bashrc` or `.zshrc`, then restart your shell

  ```
  export WORKON_HOME=$HOME/.venvs
  source /usr/bin/virtualenvwrapper.sh
  ```

3. Create a virtualenv for the project

  ```
  mkvirtualenv -p /usr/bin/python2.7 chimera
  ```
  
4. When working on the project, don't forget to run `workon chimera`, and when leaving, run `deactivate` to restore your normal Python setup.
