$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.IO.Compression.FileSystem

$rootObj = Get-ChildItem -Path 'D:\' -Directory | Where-Object { $_.Name -eq '铁路线路智能检测机器人' } | Select-Object -First 1
if (-not $rootObj) { throw '未找到目标目录' }
$root = $rootObj.FullName
$out = 'C:\Users\DELL\.openclaw\workspace\analysis_pass1.txt'
$textExt = @('.txt','.md','.py','.json','.csv','.log','.ps1','.js')
$files = Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue | Sort-Object FullName
$sb = New-Object System.Text.StringBuilder

[void]$sb.AppendLine("ROOT: $root")
[void]$sb.AppendLine("FILES: $($files.Count)")

foreach ($f in $files) {
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine("=== FILE: $($f.FullName) ===")
  try {
    $ext = $f.Extension.ToLower()
    if ($textExt -contains $ext) {
      $content = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
      if (-not $content) { $content = Get-Content -LiteralPath $f.FullName -Raw -ErrorAction SilentlyContinue }
      if ($content) {
        $content = $content -replace "`0", ' '
        $lines = $content -split "`r?`n" | Where-Object { $_.Trim() -ne '' } | Select-Object -First 40
        $joined = $lines -join "`n"
        if ($joined.Length -gt 4000) { $joined = $joined.Substring(0, 4000) }
        [void]$sb.AppendLine($joined)
      }
    }
    elseif ($ext -eq '.docx') {
      $zip = [System.IO.Compression.ZipFile]::OpenRead($f.FullName)
      $entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' } | Select-Object -First 1
      if ($entry) {
        $sr = New-Object IO.StreamReader($entry.Open())
        $xml = $sr.ReadToEnd()
        $sr.Close()
        $text = [regex]::Replace($xml, '<[^>]+>', "`n")
        $lines = $text -split "`r?`n" | Where-Object { $_.Trim() -ne '' } | Select-Object -First 80
        $joined = $lines -join "`n"
        if ($joined.Length -gt 5000) { $joined = $joined.Substring(0, 5000) }
        [void]$sb.AppendLine($joined)
      }
      $zip.Dispose()
    }
    else {
      [void]$sb.AppendLine("[SKIP_BINARY] $ext")
    }
  }
  catch {
    [void]$sb.AppendLine("[ERROR] $($_.Exception.Message)")
  }
}

Set-Content -LiteralPath $out -Value $sb.ToString() -Encoding UTF8
Write-Output $out
