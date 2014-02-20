# NEW_APP_TODO

## Installation

```
git clone --recursive git@github.com:shoptime/{{ basename }}

cd {{ basename }}

virtualenv -p python2.7 .
source bin/activate

# TODO - CODE TO INSTALL DELS

cd app/
cp local.ini.dist local.ini
vim local.ini
```

## Running

You probably want to make sure you have the less-watcher running in a terminal

```
app watch_static
```

To run the site in debug-mode, simply:

```
app
```
