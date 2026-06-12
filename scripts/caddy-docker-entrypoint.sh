#!/bin/sh
set -e

ENVIRONMENT="${ENVIRONMENT:-local}"

case "$ENVIRONMENT" in
  local)
    CONFIG="/etc/caddy/Caddyfile.docker.local"
    echo "Caddy: local mode (tls internal) -> $CONFIG"
    ;;
  staging|production)
    if [ -z "$ACME_EMAIL" ]; then
      echo "Caddy: ACME_EMAIL is required for ENVIRONMENT=$ENVIRONMENT" >&2
      exit 1
    fi
    if [ -z "$DOMAIN" ]; then
      echo "Caddy: DOMAIN is required for ENVIRONMENT=$ENVIRONMENT" >&2
      exit 1
    fi
    CONFIG="/etc/caddy/Caddyfile.docker.prod"
    echo "Caddy: $ENVIRONMENT mode (Let's Encrypt) -> $CONFIG (DOMAIN=$DOMAIN)"
    ;;
  *)
    echo "Caddy: unknown ENVIRONMENT=$ENVIRONMENT (use local, staging, or production)" >&2
    exit 1
    ;;
esac

exec caddy run --config "$CONFIG" --adapter caddyfile
