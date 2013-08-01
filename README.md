# Bang at UChicago

## General Description

This is the official code repository of [Bang at UChicago](http://bangatuchicago.com) (BaUC), a [Bang with Friends](http://bangwithfriends.com)-esque web service that is aimed toward the [University of Chicago](http://uchicago.edu) community. BaUC utilizes the public University of Chicago LDAP server in order to allow UChicagoans to search for each other. Users who indicate a mutual interest in "banging" each other are notified by email.

**NOTE:** Bang at UChicago is not affiliated with Bang with Friends or with the University of Chicago.

## License
Bang at UChicago is licensed under the terms of the GPL v3 - see [LICENSE](LICENSE).

## Technical Description

Behind the scenes, Bang at UChicago is powered by [Python](http://www.python.org) and [Django](https://www.djangoproject.com/‎) and makes liberal use of [Django REST Framework](http://django-rest-framework.org/).
The frontend is written in mostly-compliant HTML5 and CSS3, and uses [AngularJS](http://angularjs.org) for UI and business logic. Matching is performed asynchronously using a
[Celery](http://www.celeryproject.org/) task queue that's connected to [RabbitMQ](http://www.rabbitmq.com/). Persistent data is stored in a [SQLite](http://www.sqlite.org) database.

## Want to Bang, but not at UChicago?

If you're interested in banging at your school/institution/college/university/workplace we highly encourage you to fork the BaUC repo and modify it as appropriate. The UChicago-specific LDAP query code residing in `app/main/users.py` will have to be customized for your specific environment, of course.






