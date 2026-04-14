$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = 'D:\铁路线路智能检测机器人'
$logDir = Join-Path $root 'analysis'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$log = Join-Path $logDir "md_to_docx_pass2_$ts.log"
$sum = Join-Path $logDir "md_to_docx_pass2_summary_$ts.txt"

$mdFiles = Get-ChildItem -LiteralPath $root -Recurse -File -Filter *.md

function Escape-Xml([string]$s) {
  $s = $s -replace '&', '&amp;'
  $s = $s -replace '<', '&lt;'
  $s = $s -replace '>', '&gt;'
  $s = $s -replace '"', '&quot;'
  $s = $s -replace "'", '&apos;'
  return $s
}

function New-MinDocx([string]$docxPath, [string]$text) {
  Add-Type -AssemblyName System.IO.Compression.FileSystem

  $tmp = Join-Path $env:TEMP ("docx_" + [guid]::NewGuid().ToString())
  New-Item -ItemType Directory -Path $tmp | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $tmp '_rels') | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $tmp 'word') | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $tmp 'word\_rels') | Out-Null

  $contentTypes = @"
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>
  <Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>
  <Default Extension='xml' ContentType='application/xml'/>
  <Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/>
</Types>
"@
  Set-Content -Path (Join-Path $tmp '[Content_Types].xml') -Value $contentTypes -Encoding UTF8

  $rels = @"
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/>
</Relationships>
"@
  Set-Content -Path (Join-Path $tmp '_rels\.rels') -Value $rels -Encoding UTF8

  $docRels = @"
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'></Relationships>
"@
  Set-Content -Path (Join-Path $tmp 'word\_rels\document.xml.rels') -Value $docRels -Encoding UTF8

  $lines = $text -split "`r?`n"
  $paras = ''
  foreach ($line in $lines) {
    $escaped = Escape-Xml $line
    $paras += "<w:p><w:r><w:t xml:space='preserve'>$escaped</w:t></w:r></w:p>"
  }

  $document = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body>$paras<w:sectPr/></w:body></w:document>"
  Set-Content -Path (Join-Path $tmp 'word\document.xml') -Value $document -Encoding UTF8

  if (Test-Path -LiteralPath $docxPath) { Remove-Item -LiteralPath $docxPath -Force }
  [System.IO.Compression.ZipFile]::CreateFromDirectory($tmp, $docxPath)
  Remove-Item -LiteralPath $tmp -Recurse -Force
}

"START $(Get-Date)" | Out-File $log -Encoding UTF8
$ok = 0
$fail = 0
$deleted = 0

foreach ($md in $mdFiles) {
  $docx = [IO.Path]::ChangeExtension($md.FullName, '.docx')
  try {
    $txt = Get-Content -LiteralPath $md.FullName -Raw -Encoding UTF8
    New-MinDocx -docxPath $docx -text $txt
    if (Test-Path -LiteralPath $docx) {
      Remove-Item -LiteralPath $md.FullName -Force
      $ok++
      $deleted++
      "OK | $($md.FullName) -> $docx | MD_DELETED" | Out-File $log -Append -Encoding UTF8
    } else {
      $fail++
      "FAIL | $($md.FullName) -> DOCX_NOT_FOUND" | Out-File $log -Append -Encoding UTF8
    }
  } catch {
    $fail++
    "FAIL | $($md.FullName) | $($_.Exception.Message)" | Out-File $log -Append -Encoding UTF8
  }
}

"END $(Get-Date)" | Out-File $log -Append -Encoding UTF8
"转换成功: $ok" | Out-File $sum -Encoding UTF8
"转换失败: $fail" | Out-File $sum -Append -Encoding UTF8
"已删除MD: $deleted" | Out-File $sum -Append -Encoding UTF8
"日志文件: $log" | Out-File $sum -Append -Encoding UTF8
"剩余MD: $((Get-ChildItem -LiteralPath $root -Recurse -File -Filter *.md).Count)" | Out-File $sum -Append -Encoding UTF8

Write-Output "SUMMARY=$sum"
Get-Content $sum