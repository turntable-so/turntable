# Generate a random base64 encryption key and append to .env.local file
$byteArray = New-Object 'System.Byte[]' (32)
(New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($byteArray)
$encryptionKey = [Convert]::ToBase64String($byteArray)
Set-Content -Path ".env.local" -Value "ENCRYPTION_KEY='$encryptionKey'"

# Generate a random base64 nextauth secret and append to .env.local file
$byteArray2 = New-Object 'System.Byte[]' (32)
(New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($byteArray2)
$nextAuthSecret = [Convert]::ToBase64String($byteArray2)
Add-Content -Path ".env.local" -Value "NEXTAUTH_SECRET='$nextAuthSecret'"

# Generate a random 50 character string and append to .env.local file
$chars = @(
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    '0','1','2','3','4','5','6','7','8','9',
    '!','@','#','$','%','^','&','*','(',')','-','=','_','+'
)
$djangoSecretKey = -join (1..50 | ForEach-Object { $chars[(Get-Random -Minimum 0 -Maximum $chars.Length)] })
Add-Content -Path ".env.local" -Value "DJANGO_SECRET_KEY='$djangoSecretKey'"