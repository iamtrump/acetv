# AceTV #

* This is a docker image building instructions to run AceStreamTV with web-interface. More than 500 channels including HD channels.
* Ability to run custom acestream ID.

### Quick start ###

* Clone this repo
* Build image: 
```
docker build -t acetv .
```

* Run container: 
```
docker run -d -p 80:5000 --name acetv acetv
```
* Open [http://localhost/](http://localhost/).

### AceTV behind nginx reverse proxy
Example config:
```
location /ace/ {
  proxy_pass http://127.0.0.1:80/;
  proxy_set_header ACETV_URL $scheme://$host:$server_port/ace;
}
```
### UI/UX:

To show the menu place cursor to the right screen border or use shortcut - Alt + left-arrow and Alt + right-arrow for close it up.