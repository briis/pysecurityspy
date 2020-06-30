# Python Wrapper for the SecuritySpy API
This module communicates with a [SecuritySpy Video Server](https://www.bensoftware.com/securityspy/) and can retrieve and set data for:

* Cameras
* Motion Sensors
* Motion Events

It will require the Webserver component activated on SecuritySpy, and a Username, Password, IP Address and Port number for the Webserver.

See `test_client.py` for examples on how to use this wrapper. And before doing so, create a file in the same directory as `test_client.py` called `settings.json` and copy the below to that file:

````
{
    "connection": {
        "host": "WEBSERVER_IP_ADDRESS",
        "port": "WEBSERVER_PORT_NUMBER",
        "username": "WEBSERVER_USERNAME",
        "password": "WEBSERVER_PASSWORD",
        "use_ssl": "True or False"
    }
}
````
Change all the items in CAPITAL letters to your personal settings.
