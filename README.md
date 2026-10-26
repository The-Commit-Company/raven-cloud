# Raven Cloud

A Push Notification Relay Server for [Raven](https://github.com/The-Commit-Company/raven) - built on the Frappe Framework.

## Overview

Raven Cloud acts as a centralized relay server that handles push notifications for multiple Raven instances. It uses Firebase Cloud Messaging (FCM) internally to deliver notifications to web and mobile clients.

Eventually, Raven Cloud can be extended for other features like Typesense search, Video calling and Raven's Marketplace.

## Frappe Cloud sites

A Raven site on Frappe Cloud sets push notifications up without keys from its owner. The site gets a 5-minute token from Frappe Cloud that names its team and the hostnames the team serves. The site sends the token and its hostname to `raven_cloud.api.frappe_cloud.exchange_frappe_cloud_token`. Raven Cloud verifies the token against Frappe Cloud's public keys and registers the hostname for the team's user. It returns that user's API keys and the push settings. Every site of a team gets the same keys.

Only the account that registered a site can send to it or change its device tokens. A System Manager can use any site. Frappe Cloud vouches for its hostnames, so when another account registered a hostname first, the team takes the site over and the old account's device tokens are removed.

To trust Frappe Cloud, set its issuer URL in the site config:

```bash
bench --site <site> set-config frappe_cloud_issuer <frappe-cloud-url>
```

Raven Cloud refuses a token when its audience is not this site's URL, when it is expired or is not a `team-identity` token, or when it does not list the site's hostname. Set `host_name` on Raven Cloud, so its URL matches the audience that sites use. To rotate a team's keys, generate new keys on its user. Each site gets them again when Raven Cloud refuses the old ones. To cut a team off, disable its user.

## License

AGPL-3.0
