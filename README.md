# packtpub_grabber
This is a system to grab free packtpub ebooks everyday and keep a log of grabbed books. 

To use this, create an account here, https://www.packtpub.com/register.

Copy config_example.json as config.json. 
On Linux or Mac use `cp config_example.json config.json`. Not sure on windows. 
**After you copy this file, enter the appropriate into in config.json.**

Then run main.py `python main.py &` to run it in the background or use something like supervisord to run it as daemon. 

I am running this on centos 7.1 and needed to do the following:
* `yum install gcc`
* `yum install python-devel`
* `yum install libffi-devel`
* `yum install openssl-devel`

# Pushover
Pushover integration has been added so that you can get a daily push notificaiton when a new book is grabbed. This will not oly allow you to make sure it is still working, but also lets you see if todays book is worth reading without having to login to PacketPub. 
