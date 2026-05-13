#!/usr/bin/env bash
# One-time setup for the Southbound 35 mailer.
# Run from anywhere; the script changes into the mailer directory.
#
# Usage on the desktop:
#     bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "Southbound 35 mailer — setup"
echo "============================"
echo

# --- 1. Virtualenv -----------------------------------------------------------

if [ ! -d ".venv" ]; then
    echo "[1/4] Creating Python virtualenv (.venv) ..."
    python3 -m venv .venv
else
    echo "[1/4] Virtualenv already exists, skipping."
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# --- 2. Dependencies ---------------------------------------------------------

echo "[2/4] Installing dependencies ..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# --- 3. Config files ---------------------------------------------------------

if [ ! -f ".env" ]; then
    echo "[3/4] Creating .env from template ..."
    cp .env.example .env
    echo "      → Edit $SCRIPT_DIR/.env and fill in SMTP credentials"
else
    echo "[3/4] .env already exists, leaving alone."
fi

if [ ! -f "subscribers.csv" ]; then
    echo "[4/4] Creating subscribers.csv from template ..."
    cp subscribers.csv.example subscribers.csv
    echo "      → Edit $SCRIPT_DIR/subscribers.csv and add real subscribers"
else
    echo "[4/4] subscribers.csv already exists, leaving alone."
fi

echo
echo "Setup complete."
echo
echo "Next steps:"
echo "  1. Open $SCRIPT_DIR/.env and add SMTP_USER + SMTP_APP_PASSWORD."
echo "     Generate a Gmail App Password at: https://myaccount.google.com/apppasswords"
echo "  2. Set POSTS_DIR in .env to wherever your _posts/ folder lives on this machine."
echo "  3. Open $SCRIPT_DIR/subscribers.csv and add real subscriber rows."
echo "  4. Test with a dry run:"
echo "       source .venv/bin/activate"
echo "       python send_post.py --post 2026-05-25-hays-county-governance --dry-run"
echo "  5. Test send to yourself:"
echo "       python send_post.py --post 2026-05-25-hays-county-governance --only you@example.com"
echo "  6. Live send when ready:"
echo "       python send_post.py --post 2026-05-25-hays-county-governance"
echo
