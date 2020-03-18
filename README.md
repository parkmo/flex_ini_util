# flex_ini_util
Flexible utility with INI file using python.

* Usage
<pre>
# ./server_util.py -h
Usage: server_util.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c CMD, --cmd=CMD     set command in [config] section
  -s SERVERNAME, --server=SERVERNAME
                        set setver name in [xxx] section
  -v, --verbosity       verbose
  -C FILE, --config=FILE
                        config ini filename
</pre>

* serverlst.ini
  * Files encrypted via vim are supported.
* Structure of serverlst.ini
  * item of [config] Section : CMD
  * other sections : SEVERNAME

* Example1
<pre>
# ./server_util.py -s example -c test.info
Enter Password:
Example 192.168.1.101 myID myPASS
</pre>

* Example2
<pre>
# ./server_util.py -c show.parent -s example
Enter Password:
Parent desc [Test Server], Child desc [Example]
</pre>
