# packtpub_grabber
This is a system to grab free packtpub ebooks everyday and keep a log of grabbed books. 

To use this, create an account here, https://www.packtpub.com/register.

Copy config_example.json as config.json. 
On Linux or Mac use `cp config_example.json config.json`. Not sure on windows. 
After you copy this file, enter the appropriate into in config.json.

Then run main.py `python main.py`. 

I am running this on centos 7.1 and needed to do the following:
* `yum install gcc`
* `yum install python-devel`
* `yum install libffi-devel`
* `yum install openssl-devel`

Working on making this a running daemon.
