# TODO - Release 1

* code architecture and description for each part of the code

* create UserGuide

* apply python style-code

* re-think in code/folders organization

* **[ALMOST]** MailBox (from IntelMQ reporitory)
    * split by specific keys
    * template(subject/message) configurable with variables
    * use 'abuse contact' field to ge the email to send ('abuse contact' was filled by ContactDB)
    * CSV Format
    * Events that MailBox will send must be stored in a specific Database to get again all events if mailer crash or wtv

* Remove field values like 'mauro.silva@fccn.pt' :D and some other values in Portuguese. :)

* Use "Expire Documents after a Certain Number of Seconds" mechanism described in http://docs.mongodb.org/manual/tutorial/expire-data/

* The system is configurated to periodically (5min to 5min) send the events that happend within those 5 minutes, therefore not repeating the events already sent in the previous periods.
```
Configuration needs to have:
- 'start datetime' [Format: dd-mm-yyyy hh:mm:ss Z] (ex: 01-07-2014 00:00:00 UTC)
- 'time interval'  [Format: y+:m+:d+:h+:m+:s+] (ex: yearly - 1:0:0:0:0:0)

Algorithm:
- start sending data at 01-07-2014 00:00:00 and in the end save a state file with the that datetime
- crontab will call the script again and script will get the last datetime from state file and add 'time interval' value to have the next 'start datetime'.

```


* implement logging. (catch traceback, count number of reports sent and number of events for each report)

* internal: in begging we should send all reports with CC to a specific email to monitor the behavior

# TODO - Release 2

Plugins to attach in:
    * STIX Format
    * IODEF Format
    * HTML Format for quick visualization

* In the end MailBox must send a summary of sent reports
* web interface to manage reports, customize and execute them - check code from Modern Honey Project
* RTIR Output Bot

