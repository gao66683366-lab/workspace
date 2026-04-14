$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$csv = "D:\\铁路线路智能检测机器人\\analysis\\reorg_moves_20260307_175509.csv"
$rows = Import-Csv $csv
function UniqueTarget([string]$path){ if(-not (Test-Path -LiteralPath $path)){ return $path }; $dir=Split-Path $path -Parent; $name=[IO.Path]::GetFileNameWithoutExtension($path); $ext=[IO.Path]::GetExtension($path); $i=1; do { $cand=Join-Path $dir ("{0}__dup{1}_{2:yyyyMMdd_HHmmss}{3}" -f $name,$i,(Get-Date),$ext); $i++ } while(Test-Path -LiteralPath $cand); return $cand }
foreach($r in $rows){ $src=$r.Source; if(-not (Test-Path -LiteralPath $src)){ continue }; $target=$r.Target; $dir=Split-Path $target -Parent; New-Item -ItemType Directory -Force -Path $dir | Out-Null; $target=UniqueTarget $target; Move-Item -LiteralPath $src -Destination $target -Force }
Write-Host "Reorg done"
