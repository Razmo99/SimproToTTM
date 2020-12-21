# SimproToTTM
 Simpro To Telstra Track and Monitor(TTM), Syncs data from TTM to Simpro

# How it works
 1. Connects to Simpro and enumerates all specified companies.
    1. Finds all trackable `plant_types` based on `SIMPRO_SERIAL` & `SIMPRO_LAST_KNOWN_LOCATION`
        1. _If a `plant_type` has both these fields its considered **trackable**_
    1. _If no companies are specified it enumerates the whole tenant_
 2. Connects to Telstra Track Monitor and retrieves all trackers with a friendly name.
 3. Iterates over each plant item and tries to find a match in the ttm data. 
    1. If a match is found, it then appends that tracker with match info to a list.
 4. The match list is then iterated over.
    1. A maps url is generated and patched to the plant item if the url has changed

## Requirements
 - Telstra Track Monitor
    - Trackers
    - OAuth2 Grant
 - Simpro
    - O2Auth Grant
    - User Account
    - Tenant

## Installing
1. Download the Repo and place it on your docker host.
1. Create a new file next to the "docker-compose.yml" called ".env" enter in all the required [docker environment variables](#docker-environment-variables)
1. `docker-compose up --build`
   1. Don't add the `-d` flag so you can see if any errors occur on startup.\
   If it starts successfully then stop and start the container again in detached mode.

## Docker environment variables
~~~
LOG_SAVE_LOCATION #dir to save logs to
SCHEDULE_RUN_EVERY_MINUTES # x minutes to run sync
SIMPRO_SERVER # URL of a Simpro Build
SIMPRO_CLIENT_ID # Client ID for a Simpro Build
SIMPRO_CLIENT_SECRET # API Secret for a Simpro Build
SIMPRO_USERNAME # Username for a Simpro Build
SIMPRO_PASSWORD # Pass for a Simpro Build
SIMPRO_SERIAL # Custom field under a plant_type that is matched against the TTM serial
SIMPRO_LAST_KNOWN_LOCATION # Custom field under a plant_type that is populated with TTM Lat & long data
SIMPRO_SAVE_LOCATION # Dir to save temp token auth to
SIMPRO_TARGET_COMPANIES # Companies to specify if any
TTM_SERVER # URL of Telstra Track Monitor API gateway
TTM_CLIENT_ID # API Client ID 
TTM_CLIENT_SECRET # API Client Secret
TTM_SAVE_LOCATION # Dir to save temp token auth to
TZ # Timezone
~~~