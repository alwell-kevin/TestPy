from django.conf.urls import url
from django.db import connection


def show_user(request, username):
    with connection.cursor() as cursor:
    # BAD -- Using string formatting
        cursor.execute("SELECT * FROM users WHERE username = '%s'" % username)
        user = cursor.fetchone()

        # GOOD -- Using parameters
        cursor.execute("SELECT * FROM users WHERE username = %s", username)
        user = cursor.fetchone()

        # BAD -- Manually quoting placeholder (%s)
        cursor.execute("SELECT * FROM users WHERE username = '%s'", username)
        user = cursor.fetchone()
        
        cursor.execute("SELECT admin FROM users WHERE username = '" + username + '");
        user = cursor.fetchone()

        cursor.execute("SELECT admin FROM users WHERE username = '%s' % username);
        user = cursor.fetchone()

        cursor.execute("SELECT admin FROM users WHERE username = '{}'".format(username));
        user = cursor.fetchone()

        #cursor.execute(f"SELECT admin FROM users WHERE username = '{username}'");
        #user = cursor.fetchone()

urlpatterns = [url(r'^users/(?P<username>[^/]+)$', show_user)]
