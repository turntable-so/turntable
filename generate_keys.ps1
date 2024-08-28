# Generate a random base64 encryption key and append to .env file
$encryptionKey = [Convert]::ToBase64String((New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))
Add-Content -Path ".env" -Value "ENCRYPTION_KEY=""$encryptionKey"""

# Generate a random base64 nextauth secret and append to .env file
$nextAuthSecret = [Convert]::ToBase64String((New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))
Add-Content -Path ".env" -Value "NEXTAUTH_SECRET=""$nextAuthSecret"""

# Generate a random 50 character string and append to .env file
$chars = 'a'..'z' + '0'..'9' + '!@#$%^&*(-_=+)'
$randomString = -join (1..50 | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
Add-Content -Path ".env" -Value $randomString