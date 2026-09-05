#!/usr/bin/env bash
# Sets up eduardo.greenflashusa.com on an Ubuntu/Debian server:
# nginx, the site pulled from GitHub, HTTPS from Let's Encrypt, and a
# 5-minute auto-pull so every push to main goes live on its own.
#
# Run as root:
#   curl -fsSL https://raw.githubusercontent.com/GalacticConquestRulez/eduardo/main/deploy/setup-server.sh -o setup.sh && bash setup.sh
#
# Safe to re-run: it updates the checkout and rewrites the config.
set -euo pipefail

DOMAIN="${DOMAIN:-eduardo.greenflashusa.com}"
REPO="${REPO:-https://github.com/GalacticConquestRulez/eduardo.git}"
BRANCH="${BRANCH:-main}"
WEBROOT="${WEBROOT:-/var/www/eduardo}"
CERT_EMAIL="${CERT_EMAIL:-}"   # Let's Encrypt sends renewal notices here

[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo -i, then run this again."; exit 1; }

echo "==> Installing nginx, git, certbot"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx git certbot python3-certbot-nginx >/dev/null

echo "==> Pulling the site from GitHub ($BRANCH)"
git config --global --add safe.directory "$WEBROOT" >/dev/null 2>&1 || true
if [ -d "$WEBROOT/.git" ]; then
  git -C "$WEBROOT" fetch -q --depth=1 origin "$BRANCH"
  git -C "$WEBROOT" reset -q --hard "origin/$BRANCH"
else
  rm -rf "$WEBROOT"
  git clone -q --depth=1 --branch "$BRANCH" "$REPO" "$WEBROOT"
fi
chmod -R a+rX "$WEBROOT"

echo "==> Writing the nginx site for $DOMAIN"
cat > /etc/nginx/sites-available/eduardo <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    root $WEBROOT;
    index index.html;

    # never serve repo internals
    location ~ /\.git   { return 404; }
    location /deploy/   { return 404; }
    location = /README.md { return 404; }

    # the background film: cacheable, seekable
    location ~* \.mp4$ {
        add_header Cache-Control "public, max-age=604800";
    }
    location ~* \.(jpg|jpeg|png|webp|svg|ico|css|js)$ {
        add_header Cache-Control "public, max-age=86400";
    }

    gzip on;
    gzip_types text/html text/css application/javascript image/svg+xml;
}
NGINX
ln -sf /etc/nginx/sites-available/eduardo /etc/nginx/sites-enabled/eduardo
nginx -t
systemctl enable -q nginx
systemctl reload nginx

if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  echo "==> Opening HTTP/HTTPS in ufw"
  ufw allow 'Nginx Full' >/dev/null
fi

echo "==> Auto-deploy: pull from GitHub every 5 minutes"
cat > /usr/local/bin/deploy-eduardo <<DEPLOY
#!/usr/bin/env bash
# Pull the latest $BRANCH from GitHub into $WEBROOT. Run by cron every 5 minutes; run by hand any time.
set -euo pipefail
cd "$WEBROOT"
before=\$(git rev-parse HEAD)
git fetch -q --depth=1 origin "$BRANCH"
git reset -q --hard "origin/$BRANCH"
chmod -R a+rX "$WEBROOT"
after=\$(git rev-parse HEAD)
if [ "\$before" != "\$after" ]; then
  echo "\$(date -Is) deployed \${after:0:7}" | tee -a /var/log/deploy-eduardo.log
else
  echo "already at \${after:0:7}"
fi
DEPLOY
chmod +x /usr/local/bin/deploy-eduardo
echo "*/5 * * * * root /usr/local/bin/deploy-eduardo >/dev/null 2>&1" > /etc/cron.d/deploy-eduardo

echo "==> HTTPS"
if [ -z "$CERT_EMAIL" ] && [ -r /dev/tty ]; then
  read -rp "Email for Let's Encrypt renewal notices (Enter to skip HTTPS for now): " CERT_EMAIL < /dev/tty || true
fi
if [ -n "$CERT_EMAIL" ]; then
  if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERT_EMAIL" --redirect; then
    echo "HTTPS is on. Renewal is automatic."
  else
    echo "certbot could not issue the certificate yet. Usually DNS for $DOMAIN hasn't reached this server."
    echo "Once it has, run:  certbot --nginx -d $DOMAIN --redirect"
  fi
else
  echo "Skipped HTTPS. When ready, run:  certbot --nginx -d $DOMAIN --redirect"
fi

echo
echo "Done."
echo "  Site:        http://$DOMAIN"
echo "  Files:       $WEBROOT  (at $(git -C "$WEBROOT" rev-parse --short HEAD))"
echo "  Update now:  deploy-eduardo   (cron also pulls every 5 minutes)"
