$ErrorActionPreference = 'Stop'
$target = Join-Path $env:LOCALAPPDATA 'Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json'
$backup = "$target.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -LiteralPath $target -Destination $backup
$config = Get-Content -LiteralPath $target -Raw | ConvertFrom-Json -AsHashtable
$scheme = @{
 name='Sakura Cream';background='#FFF8F0';foreground='#51434E';cursorColor='#AC5980';selectionBackground='#F3D8E5'
 black='#51434E';red='#AD4968';green='#47765E';yellow='#906619';blue='#586FA3';purple='#8762A4';cyan='#377B83';white='#D7C7CC'
 brightBlack='#867580';brightRed='#BD5677';brightGreen='#527F67';brightYellow='#9B7326';brightBlue='#657CAF';brightPurple='#9670B0';brightCyan='#47858D';brightWhite='#FFFDFC'
}
$config.schemes = @($config.schemes | Where-Object { $_.name -ne 'Sakura Cream' }) + @($scheme)
$defaults=$config.profiles.defaults
$defaults.colorScheme='Sakura Cream'
if(-not $defaults.font){$defaults.font=@{}}
$defaults.font.face='Cascadia Mono'
$defaults.font.size=12
$defaults.padding='12, 8, 12, 8'
$defaults.cursorShape='bar'
foreach($profile in $config.profiles.list){if($profile.name -eq 'AIO'){$profile.colorScheme='Sakura Cream'}}
$config.initialCols=150
$config.initialRows=40
$config.theme='light'
$text=$config | ConvertTo-Json -Depth 100
$null=$text | ConvertFrom-Json
[IO.File]::WriteAllText($target,$text,[Text.UTF8Encoding]::new($false))
Write-Output "Terminal theme applied: Sakura Cream"
Write-Output "Backup: $backup"
