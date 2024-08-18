# Guacamole

Apache Guacamole allows you via your web browser to connect to devices, specifically in this plugin we use it to connect via SSH. These connections will be proxy'd from the guacamole service you are connected to, meaning the source IP address will be that of the guacamole, not your IP.

This optional service has several requirements.

- An active Guacamole service
- Nautobot Configuration for:
    - guac_url - This is the url used from Nautobot to connect to the device.
    - guac_frontend_url - This is the URL your web client will use to connect to Guacamole, which is especially helpful in docker environments where the connection is different than your client.
    - guac_user - This is the guacamole service username, which is guacadmin by default.
    - guac_pass - This is the guacamole service username, which is guacadmin by default.
    - guac_data_source - The [guacmole datasource](https://github.com/apache/guacamole-client/blob/fff7ba41225586501869194b46db8a36ea910cb1/guacamole-docker/bin/initdb.sh#L57-L65) that is being used, one of postgresql, mysql, or sqlserver.

## Guacamole Connections

The connection options can be found on the `Containerlab Topologies` detail view, in the `Connection Portal` panel. When you click on the link, backend API calls are made to guacamole to ensure that the Guacamole connections are there, followed by a redirect to the appropriate URL in a new tab for your link.

The connection will prefer the primary_ip if provided (though untested at time of this writing) and then use the device name as the name. 

There is a presumption that device_name is unique.

> Note: In the future should create a job that populates all of the connections so they are there if you were to go direct to the guacamole service.

> Note: This will show regardless if you have Guacamole set or not, should remove in the future.

## Current Shortcomings

The docker configuration currently creates a separate postgres instance. A the creation of the feature it was easier than getting multiple databases setup in the db service.

The Docker configuration configures guacamole-preperation to get around a chicken and egg issue in which you need an sql file to be generated, which is then required by the database, which is then required by the guacamole service. There is likely a way around this, but not found at the time of this writing.

The Docker environment variables are can be cleaned up for the gucamole and db-guac services at a future date.

The `MYSQL_DATABASE` environment variable was unset since it conflicts with the [guacamole startup script](https://github.com/padarom/guacamole-common-js/blob/d631c05d7c33ae99ab017c82dfcf2ef45101332c/guacamole-docker/bin/start.sh#L171-L177) that prefers any environment with the `MYSQL_DATABASE` set.

Password for guacamole is set in nautobot_config.py and not via secrets.

## Lessons Learned

- Guacamole requires you to handle the initial SQL creation of the database of your choice, via the initdb.sh script, likely found in `/opt/guacamole/bin/initdb.sh`.
- Guacamole API will 500 or 404 if you have the wrong API data POST'd.
- It is often easier to get the API via the GUI, by using the developer tool and finding the API call being made
    - Do note that the token auth for API is generally via appending `?token=<your_token>`, with at least one notable exception which is to get the token.
