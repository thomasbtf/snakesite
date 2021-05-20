# Snakesite - Websites for Snakemake

![Status](https://img.shields.io/badge/-under%20development-yellow?style=flat-square)

Snakesite enables interactive execution of Snakemake workflows via a web interface. Users can register, start, monitor workflows and inspect the results of their (and others') executions.

## Start-up

1. Start the message broker via `rabbitmq-server`.
2. Start the distributed task queue via `celery -A snakesite worker -l INFO`.
3. Start the website via `python manage.py runserver`.


## Thanks

This project wouldn't be possible without several open source libraries!

- [Bootstrap](https://getbootstrap.com/) "Builds fast, responsive sites"
- [Celery](https://docs.celeryproject.org/) "Distributed Task Queue"
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/) "Forms have never been this crispy"
- [Django](https://www.djangoproject.com/) "The Web framework for perfectionists with deadlines"
- [RabbitMQ](https://www.rabbitmq.com/) "Messaging that just works"
- [Snakemake](https://snakemake.readthedocs.io/en/stable/) "The workflow management system for reproducible and scalable data analyses."
