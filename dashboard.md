# AB BLE Gateway Dashboard

Here's a sample Markdown Dashboard card you can add to your Home Assistant dashboard to clean up failed AB BLE Gateway entries.

## Markdown Card Content:

```yaml
type: markdown
content: >
  ## AB BLE Gateway Maintenance

  Use the button below to clean up failed AB BLE Gateway entries. This will remove all
  failed integration entries from your configuration.

  **Warning**: Home Assistant will need to be restarted after cleaning up entries.

  <ha-call-service-button
    hass="[[hass]]"
    domain="ab_ble_gateway"
    service="clean_failed_entries"
    service-data="{\"dry_run\": false}"
    class="btn"
    style="background-color: #03a9f4; color: white; font-weight: 500; margin: 8px 0px; width: 100%;"
  >
    Clean Failed Entries
  </ha-call-service-button>

  <ha-call-service-button
    hass="[[hass]]"
    domain="ab_ble_gateway"
    service="clean_failed_entries"
    service-data="{\"dry_run\": true}"
    class="btn"
    style="background-color: #4CAF50; color: white; font-weight: 500; margin: 8px 0px; width: 100%;"
  >
    Dry Run (No Changes)
  </ha-call-service-button>

  <ha-call-service-button
    hass="[[hass]]"
    domain="homeassistant"
    service="restart"
    class="btn"
    style="background-color: #F44336; color: white; font-weight: 500; margin: 8px 0px; width: 100%;"
  >
    Restart Home Assistant
  </ha-call-service-button>
```

## Instructions

1. Go to your dashboard and add a new card.
2. Choose "Manual" card.
3. Paste the YAML content above.
4. Save the card.

You can now use the buttons to:
- Run a dry run (no changes, just log what would be done)
- Clean up failed entries 
- Restart Home Assistant after cleaning up entries