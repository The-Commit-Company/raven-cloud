# Raven Cloud

A Push Notification Relay Server for [Raven](https://github.com/The-Commit-Company/raven) - built on the Frappe Framework.

## Overview

Raven Cloud acts as a centralized relay server that handles push notifications for multiple Raven instances. It uses Firebase Cloud Messaging (FCM) internally to deliver notifications to web and mobile clients.

Eventually, Raven Cloud can be extended for other features like Typesense search, Video calling and Raven's Marketplace.

## Frappe Cloud sites

A Raven site on Frappe Cloud sets push notifications up without keys from its owner. The site gets a 5-minute token from Frappe Cloud that names its team, and exchanges it at `raven_cloud.api.frappe_cloud.exchange_frappe_cloud_token`. Raven Cloud verifies the token against Frappe Cloud's public keys, then returns the API keys of the team's user. Every site of a team gets the same keys.

To trust Frappe Cloud, set its issuer URL in the site config:

```bash
bench --site <site> set-config frappe_cloud_issuer <frappe-cloud-url>
```

Raven Cloud refuses a token when its audience is not this site's URL, or when it is expired or is not a `team-identity` token. To rotate a team's keys, generate new keys on its user. Each site gets them again when Raven Cloud refuses the old ones. To cut a team off, disable its user.

## License

AGPL-3.0
