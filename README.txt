Deployment & other animals


How to Deploy :
    Before deployment - in local development :

        After suitable testing and merging.

        (env) .../SuffolkCycleRide:$ manifest create # Ignores /media, /static
        (env) .../SuffolkCycleRide:$ git add manifest.txt
        (env) .../SuffolkCycleRide:$ git commit -m 'Something appropriate here'
        (env) .../SuffolkCycleRide:$ git push

    staging testing :
        In a new terminal window :
        cd ~/Development/python/SuffolkCycleStaging/SuffolkCycleDjango
        ../SuffolkCycleDjango $ source env/bin/activate
        (env) ../SuffolkCycleDjango:$ git pull
        (env) ../SuffolkCycleDjango:$ manifest check

        ** Resolve any issues **

    In Browser : navigate to www.pythonanywhere.com and Login
    Open Bash console :

        $ workon suffolkcycle
        (master)$ cd SuffolkCycleDjango/
        ~/SuffolkCycleDjango (master)$ git pull         # Fetch latest github repository
        ~/SuffolkCycleDjango (master)$ manifest check
        ~/SuffolkCycleDjango (master)$ python manage.py migrate     # Execute migrations
        ~/SuffolkCycleDjango (master)$ python manage.py collectstatic

    On Python Anywhere Dashboard

        Reload application

    Test all main pages


How to clear logs

    In Bash Console
        $ workon suffolkcycle
        (master)$ truncate -s 0 /var/log/suffolkcycleride.pythonanywhere.com.access.log
        (master)$ truncate -s 0 /var/log/suffolkcycleride.pythonanywhere.com.error.log
        (master)$ truncate -s 0 /var/log/suffolkcycleride.pythonanywhere.com.server.log


Dependencies
    python = 2.7                                    # Basic project depedency
    django >= 1.9.1                                 # Basic project depedency
    django-ipware >= 1.1.3                          # Required by stats app
    django-markitup >= 2.3.1                        # Required by blog app
    Pillow > 3.1.1                                  # Required by dashboard
    markdown >= 2.6.5                               # Required by blog app
    BeautifulSoup4 >= 4.00                          # Required for testing
    htm5lib                                         # Required for testing
    manifest-checker > 0.0.2rc3                     # Required for deployment check