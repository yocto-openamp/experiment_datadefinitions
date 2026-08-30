set -x

# Clean all temporary files
rm -r *
git checkout .

# Copy relevant source code
cp -r src/* ../uart-asyncio-sandbox/src
cp -r tests/* ../uart-asyncio-sandbox/tests
