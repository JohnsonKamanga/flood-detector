#!/bin/sh

# Generate runtime config from environment variables
cat > /usr/share/nginx/html/config.js << EOF
window.__RUNTIME_CONFIG__ = {
  API_BASE_URL: '${VITE_API_BASE_URL:-/api}',
  WS_URL: '${VITE_WS_URL:-ws://localhost/ws}'
};
EOF

echo "Runtime config generated:"
cat /usr/share/nginx/html/config.js

# Start nginx
exec nginx -g 'daemon off;'
