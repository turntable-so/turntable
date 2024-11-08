# Determine the platform
platform=$(uname)

if [[ "$platform" != "Darwin" && "$platform" != "Linux" ]]; then
    echo "Unsupported platform: $platform"
    exit 1
fi

echo "ENCRYPTION_KEY=\"`openssl rand -base64 32`\"" >> .env.local2
NEXTAUTH_SECRET="`openssl rand -base64 32`"
echo "NEXTAUTH_SECRET=\"$NEXTAUTH_SECRET\"" >> .env.local2
echo "NEXTAUTH_SECRET=\"$NEXTAUTH_SECRET\"" >> frontend/.env.local2
echo "API_URL=http://api:8000" >> frontend/.env.local2
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> frontend/.env.local2
echo "NEXT_PUBLIC_POSTHOG_KEY=phc_XL4KyheAjc4gJV4Fzpg1lbn7goFP1QNqsnNUhY1O1CU" >> frontend/.env.local2
echo "NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com" >> frontend/.env.local2


if [[ "$platform" == "Darwin" ]]; then
    echo "DJANGO_SECRET_KEY=\"`env LC_ALL=C tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50`\"" >> .env.local2
elif [[ "$platform" == "Linux" ]]; then
    echo "DJANGO_SECRET_KEY=\"`< /dev/urandom tr -dc 'a-z0-9!@#$%^&*(-_=+)' | head -c 50`\"" >> .env.local2
fi