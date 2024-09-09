# Determine the platform
platform=$(uname)

if [[ "$platform" == "Darwin" ]]; then
    echo "ENCRYPTION_KEY=\"`openssl rand -base64 32`\"" >> .env.local
    echo "NEXTAUTH_SECRET=\"`openssl rand -base64 32`\"" >> .env.local
    echo "DJANGO_SECRET_KEY=\"`env LC_ALL=C tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50`\"" >> .env.local
elif [[ "$platform" == "Linux" ]]; then
    echo "ENCRYPTION_KEY=\"`openssl rand -base64 32`\"" >> .env.local
    echo "NEXTAUTH_SECRET=\"`openssl rand -base64 32`\"" >> .env.local
    echo "DJANGO_SECRET_KEY=\"`< /dev/urandom tr -dc 'a-z0-9!@#$%^&*(-_=+)' | head -c 50`\"" >> .env.local
else
    echo "Unsupported platform: $platform"
fi