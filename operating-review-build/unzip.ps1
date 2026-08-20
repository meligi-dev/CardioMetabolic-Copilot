param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ZipArgs
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

if ($ZipArgs.Count -lt 2) { throw 'Expected unzip arguments.' }
$mode = $ZipArgs[0]
$zipPath = $ZipArgs[-1]
$archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
  if ($mode -eq '-Z1') {
    $archive.Entries | ForEach-Object { [Console]::Out.WriteLine($_.FullName) }
    exit 0
  }
  if ($mode -eq '-p') {
    $entryName = $ZipArgs[2]
    $entry = $archive.GetEntry($entryName)
    if ($null -eq $entry) { throw "Entry not found: $entryName" }
    $stream = $entry.Open()
    try { $stream.CopyTo([Console]::OpenStandardOutput()) } finally { $stream.Dispose() }
    exit 0
  }
  throw "Unsupported unzip mode: $mode"
}
finally { $archive.Dispose() }
