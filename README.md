# SimproToTTM
 Simpro To Telstra Track and Monitor(TTM), Syncs data from TTM to Simpro

# Docker Enviroment Variables
~~~

LOG_SAVE_LOCATION #dir to save logs to
SCHEDULE_RUN_EVERY_MINUTES # x minutes to run sync
SIMPRO_SERVER # URL of a Simpro Build
SIMPRO_CLIENT_ID # Client ID for a Simpro Build
SIMPRO_CLIENT_SECRET # API Secret for a Simpro Build
SIMPRO_USERNAME # Username for a Simpro Build
SIMPRO_PASSWORD # Pass for a Simpro Build
SIMPRO_SERIAL # Custom field under a plant_type that is matched against TTM's serial
SIMPRO_LAST_KNOWN_LOCATION # Custom field under a plant_type that is populated with TTM Lat & long data
SIMPRO_SAVE_LOCATION # Dir to save temp token auth to
TTM_SERVER # URL of Telstra Track Monitor API gateway
TTM_CLIENT_ID # API Client ID 
TTM_CLIENT_SECRET # API Client Secret
TTM_SAVE_LOCATION # Dir to save temp token auth to
TZ # Timezone

~~~