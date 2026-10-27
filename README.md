# Secunda test

Asynchronous service of payment processing

## Deployment

1. Create .env in the root directory

Here is the full list of variables (mostly self-explanatory):
- RabbitMQ
    - RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_VHOST
- Postgresql
    - POSTGRESQL_HOST, POSTGRESQL_PORT, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_DB
- Redis
    - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
- Gateway
    - GATEWAY_PORT - port for api http requests
    - API_KEY - X-Apy-Key header for autherization

2. Run in terminal the command "docker compose up -d"

## Notes

RabbitMQ-management image is used only for monitoring purpose to see how retry mechanics works. For production it should use regular rabbitmq image.
