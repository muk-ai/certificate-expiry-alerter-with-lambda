## configure environment

SLACK_URL: incomming webhook url
DAYS: threshold

## CloudWatch Events

### Event Source

create schdule event

### Targets
configure input

- Constant (JSON text)

```
{
  "fqdn_list": [
    "www.google.com",
    "www.amazon.com",
    "www.apple.com",
    "www.microsoft.com"
  ]
}
```
