# Uni Roomplan

## About

Built for a better viewing experience of the [University of Würzburg](https://www.uni-wuerzburg.de) room plans.

The plan is currently hosted at [plan.thunderray-studios.de](http://plan.thunderray-studios.de).

The project was built to run on CentOS 7.0 with Nginx, Python 3.6, Flask and uWSGI, but can probably easily be adjusted to work on other plattforms with other universities and organisations.

The server side setup was mainly based on [this](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-centos-7) tutorial.

## File Structure

- `plan.conf` should be placed in `/etc/nginx/sites-available/` and be symlinked to `/etc/nginx/sites-enabled/`
- `plan.service` sould be placed in `/etc/systemd/system/`
- the `plan` folder should be placed in your home (`~`) directory

- `/plan/sync.py` is on this server run every night at 04:00, due to lower traffic and hopfully noone trying to view the plan, which might then be broken, at this time.