# SimproToTTM
 Simpro To Telstra Track and Monitor(TTM), Syncs data from TTM to Simpro

# How it works
 1. Connects to Simpro and enumerates all specified companies.
    1. Finds all trackable `plant_types` based on `SIMPRO_SERIAL` & `SIMPRO_LAST_KNOWN_LOCATION`
        1. _If a `plant_type` has both these fields its considered **trackable**_
    1. _If no companies are specified it enumerates the whole tenant._
 2. Connects to Telstra Track Monitor and retrieves all trackers with a friendly name.
 3. Iterates over each `plant` and tries to find a match in the ttm data. 
    1. If a match is found, it then appends that tracker with match info to a list.
 4. The match list is then iterated over.
    1. A map url is made and patched to the `plant` if the location has changed.

## Requirements
 - Telstra Track Monitor
    - Trackers
    - OAuth2 grant
 - Simpro
    - OAuth2 grant
    - User account
    - Tenant

## Installing
1. Download the Repo and place it on your docker host.
1. Create a new file next to the "docker-compose.yml" called ".env" enter in all the required [docker environment variables](#docker-environment-variables)
1. `docker-compose up --build`
   1. Don't add the `-d` flag so you can see if any errors occur on startup.\
   If it starts successfully then stop and start the container again in detached mode.

## Docker environment variables
- SIMPRO_SERVER ***Required**
   - URL of the simpro build i.e "https://**mybuild**.simprocloud.com"
- SIMPRO_CLIENT_ID ***Required**
   - OAuth2 Client ID
- SIMPRO_CLIENT_SECRET ***Required**
   - OAuth2 Secret ID
- SIMPRO_USERNAME ***Required**
   - Username of an account on the Simpro build
- SIMPRO_PASSWORD ***Required**
   - Password of an account on the Simpro build
- SIMPRO_SERIAL ***Required**
   - Name of a `plant_type` `custom_field` **Case Sensitive**
   - This field will be matched against the Telstra track and monitor `serialNumber`
- SIMPRO_LAST_KNOWN_LOCATION ***Required**
   - Name of a `plant_type` `custom_field` **Case Sensitive**
   - This field will be populated with a maps url.
   - _This only occurs if a match to a tracker is found_
- SIMPRO_SAVE_LOCATION
   - File path plus file name to save temp token information
   - i.e simpro_token.json
   - i.e /app/storage/simpro_token.json
- SIMPRO_TARGET_COMPANIES
   - `List` of companies to target
      - _Defined by either `ID` or `Name`; not case sensitive_
   - i.e "['Contoso - HeadOffice',55,9000,'Osotnoc - backoffice']"
- TTM_SERVER ***Required**
   - URL to Telstra track and monitor api
- TTM_CLIENT_ID ***Required**
   - OAuth2 Client ID
- TTM_CLIENT_SECRET ***Required**
   - OAuth2 Secret ID
- TTM_SAVE_LOCATION
   - File path plus file name to save temp token information
   - i.e ttm_token.json
   - i.e /app/storage/ttm_token.json
- TZ
   - Time zone for the docker container
   - i.e `Australia/Sydney`
- LOG_SAVE_LOCATION
   - File path plus file name to save the logs to
   - i.e simpro_to_ttm.logs
   - i.e /app/storage/simpro_to_ttm.logs
- SCHEDULE_RUN_EVERY_MINUTES
   - How often to run a sync; in minute(s)
   - _default is 30_
## Dockerfile
Slightly modified version of the dockerfile layed out [here](https://www.kevin-messer.net/how-to-create-a-small-and-secure-container-for-your-python-applications/)
