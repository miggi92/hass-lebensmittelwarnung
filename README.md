# hass-lebensmittelwarnung

[![Static Badge](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/miggi92/hass-lebensmittelwarnung/total?style=for-the-badge)
![GitHub Release](https://img.shields.io/github/v/release/miggi92/hass-lebensmittelwarnung?style=for-the-badge)
![GitHub License](https://img.shields.io/github/license/miggi92/hass-lebensmittelwarnung?style=for-the-badge)
![GitHub Repo stars](https://img.shields.io/github/stars/miggi92/hass-lebensmittelwarnung?style=for-the-badge)

> Home assistant integration for [lebensmittelwarnung.de](https://www.lebensmittelwarnung.de/)

![Logo](https://www.lebensmittelwarnung.de/SiteGlobals/Frontend/Images/images/logo-inverted.svg?__blob=normal&v=1)

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=miggi92&repository=hass-lebensmittelwarnung&category=Integration)

### HACS (recommended)

1. Open HACS
2. add this repository as a custom repository
3. search for "Lebensmittelwarnung" in the HACS store
4. install the integration
5. restart Home Assistant

### Manual

Copy the `custom_components/lebensmittelwarnung` folder to your Home Assistant `custom_components` folder. Then restart Home Assistant.


## Configuration

1. Open the Home Assistant UI
2. Go to `Configuration` > `Integrations`
3. Click on `+ Add Integration`
4. Search for `Lebensmittelwarnung`
5. Enter the relevant information for the integration (e.g. your location or preferences as required by the integration)
6. Click on `Submit`

### Watchlist

Open the integration entry and click `Configure` to set up a watchlist:

- **Keywords**: searched for in the product, manufacturer and reason of each
  warning (case-insensitive, partial words match, so `Käse` also finds
  `Weinbauernkäse`).
- **Product list (optional)**: an entity whose attribute contains a list of
  products, e.g. your [Grocy](https://github.com/custom-components/grocy)
  stock (`sensor.grocy_stock`, attribute `products`, field `name`). A product
  matches if all of its words with at least 4 characters appear in the
  warning, so `Bio Wildheidelbeeren TK` also finds
  `EDEKA Bio Wildheidelbeeren tiefgefroren`.

The binary sensor `Watchlist Match` is on while a warning from the last 7 days
matches. Each new warning additionally fires the `New Warning` event, whose
`watchlist_treffer` attribute lists all matches (keywords and products) and
`watchlist_produkte` only the matches from the product list.

## Example automation: notify on watchlist matches

Sends a push notification for every new warning that matches your watchlist.
The event entity fires exactly once per new warning – not on restarts, reloads
or when the feed is temporarily unavailable – which makes it the right trigger
for notifications.

Replace the entity ID (it depends on your federal state and your Home
Assistant language, e.g. `event.lebensmittelwarnung_bayern_new_warning` in
English) and the notify service with your own.

```yaml
alias: Lebensmittelwarnung – Watchlist-Treffer
description: Benachrichtigt bei neuen Warnungen, die auf die Watchlist passen.
mode: queued
triggers:
  - trigger: state
    entity_id: event.lebensmittelwarnung_bayern_neue_meldung
    # Ignore the entity becoming available again after a restart or reload.
    not_from:
      - unavailable
    not_to:
      - unavailable
conditions:
  - condition: template
    value_template: >
      {{ trigger.to_state.attributes.watchlist_treffer | default([]) | length > 0 }}
actions:
  - action: notify.mobile_app_mein_handy
    data:
      title: "⚠️ Rückruf: {{ trigger.to_state.attributes.titel }}"
      message: >
        Treffer: {{ trigger.to_state.attributes.watchlist_treffer | join(', ') }}
        {%- if trigger.to_state.attributes.watchlist_produkte %}
        (aus deinem Vorrat){% endif %}

        Grund: {{ trigger.to_state.attributes.grund }}

        Hersteller: {{ trigger.to_state.attributes.hersteller }}
      data:
        url: "{{ trigger.to_state.attributes.link }}"
        clickAction: "{{ trigger.to_state.attributes.link }}"
```

`url` opens the warning on iOS, `clickAction` on Android when tapping the
notification.

## Screenshots

![Screenshot Integration Screen](https://github.com/miggi92/hass-lebensmittelwarnung/blob/main/assets/screenshots/integration_screen.png)

## Sponsors

![Sponsors](https://github.com/miggi92/static/blob/master/sponsors.svg)