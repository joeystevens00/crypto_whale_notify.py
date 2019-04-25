# crypto_whale_notify.py  
notify2 whale-alert.io alerts. Configure config.json or just set the environment variable WHALE_ALERT_API_KEY with your API KEY and use default values. 
Uses redis to cache notification history and prevent duplicate alerts. 

## Install in cron 
```
*/2 * * * * python3 /path/to/crypto_whale_notify.pl
```

## requirements
redis, notify2

## Config.json fields 
| Field        | Description                                      | Default                     |
| -------------|:------------------------------------------------:| ---------------------------:|
| api_key      | whale-alert.io API KEY                           | WHALE_ALERT_API_KEY env var |
| seek_seconds | search historical data up to seconds old         | 1500                        |
| notify_delay | delay between notifications in seconds           | 15                          |
| min_dollars  | only return transactions exceeding dollar amount | 500000                      |
| redis        | redis connection details (container object)      | {}                          |
| redis.host   | redis host to connect to                         | localhost                   | 
| redis.port   | redis port to connect to                         | 6379                        |
| redis.db     | redis db to connect to                           | 0                           | 
