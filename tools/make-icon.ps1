# Generates WinForms\app.ico - a terminal/agent icon for cki-lite.
# Uses only System.Drawing (inbox, no installs).
Add-Type -AssemblyName System.Drawing

function New-Bitmap($size) {
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)

    # Rounded-terminal window
    $rect = New-Object System.Drawing.Rectangle(0, 0, $size, $size)
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        $rect,
        [System.Drawing.Color]::FromArgb(255, 34, 66, 34),
        [System.Drawing.Color]::FromArgb(255, 6, 18, 6),
        [System.Drawing.Drawing2D.LinearGradientMode]::Vertical)
    $g.FillRectangle($brush, $rect)

    # Title bar
    $bar = New-Object System.Drawing.Rectangle(0, 0, $size, [int]($size * 0.22))
    $barBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 16, 36, 16))
    $g.FillRectangle($barBrush, $bar)

    # Three title dots
    $dots = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 140, 220, 160))
    $r = [Math]::Max(1, [int]($size * 0.07))
    $y = [int]($size * 0.06)
    foreach ($fx in @(0.10, 0.24, 0.38)) {
        $g.FillEllipse($dots, [int]($size * $fx), $y, $r, $r)
    }

    # Prompt chevron ">_" in green
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 90, 230, 110), [Math]::Max(1, $size / 16))
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $g.DrawLine($pen, [int]($size * 0.26), [int]($size * 0.50), [int]($size * 0.42), [int]($size * 0.62))
    $g.DrawLine($pen, [int]($size * 0.42), [int]($size * 0.62), [int]($size * 0.26), [int]($size * 0.74))
    $g.DrawLine($pen, [int]($size * 0.48), [int]($size * 0.66), [int]($size * 0.76), [int]($size * 0.66))

    $pen.Dispose()
    $dots.Dispose()
    $barBrush.Dispose()
    $brush.Dispose()
    $g.Dispose()
    return $bmp
}

# Returns a 32bpp DIB (BITMAPINFOHEADER + ARGB pixel rows, bottom-up).
function ConvertTo-Dib {
    param([System.Drawing.Bitmap]$bmp)
    $size = $bmp.Width
    $bmpData = $bmp.LockBits(
        (New-Object System.Drawing.Rectangle(0, 0, $size, $size)),
        [System.Drawing.Imaging.ImageLockMode]::ReadOnly,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $stride = $bmpData.Stride
    $byteCount = $stride * $size
    $pixels = New-Object byte[] $byteCount
    [System.Runtime.InteropServices.Marshal]::Copy($bmpData.Scan0, $pixels, 0, $byteCount)
    $bmp.UnlockBits($bmpData)

    $ms = New-Object System.IO.MemoryStream
    $bw = New-Object System.IO.BinaryWriter($ms)
    $bw.Write([int]40)                       # biSize
    $bw.Write([int]$size)                    # biWidth
    $bw.Write([int]($size * 2))              # biHeight (double-height = alpha mask)
    $bw.Write([int16]1)                      # biPlanes
    $bw.Write([int16]32)                     # biBitCount
    $bw.Write([uint32]0)                     # biCompression BI_RGB
    $bw.Write([uint32]($size * $size * 4))   # biSizeImage
    $bw.Write([int]0); $bw.Write([int]0)
    $bw.Write([uint32]0); $bw.Write([uint32]0)
    $bw.Write($pixels)                       # AND mask: 1bpp, must be all-zero rows
    # XOR mask + AND mask are both included conceptually; AND mask omitted => all opaque alpha.
    return $ms.ToArray()
}

function Write-Ico {
    param([string]$path, [int[]]$sizes)
    $dibs = @()
    foreach ($s in $sizes) {
        $bmp = New-Bitmap $s
        $dibs += ,(ConvertTo-Dib $bmp)
        $bmp.Dispose()
    }
    $total = 6 + (16 * $sizes.Count)
    $entries = New-Object System.Collections.Generic.List[byte]
    for ($i = 0; $i -lt $sizes.Count; $i++) {
        $s = $sizes[$i]
        $len = $dibs[$i].Length
        $entries.Add([byte]$s)
        $entries.Add([byte]$s)
        $entries.Add(0); $entries.Add(0)
        $entries.Add(1); $entries.Add(0)
        $entries.Add(32); $entries.Add(0)
        $entries.Add([byte]($len -band 0xFF))
        $entries.Add([byte](($len -shr 8) -band 0xFF))
        $entries.Add([byte](($len -shr 16) -band 0xFF))
        $entries.Add([byte](($len -shr 24) -band 0xFF))
        $entries.Add([byte]($total -band 0xFF))
        $entries.Add([byte](($total -shr 8) -band 0xFF))
        $entries.Add([byte](($total -shr 16) -band 0xFF))
        $entries.Add([byte](($total -shr 24) -band 0xFF))
        $total += $len
    }
    $ico = New-Object System.Collections.Generic.List[byte]
    $ico.Add(0); $ico.Add(0)
    $ico.Add(1); $ico.Add(0)
    $ico.Add([byte]$sizes.Count); $ico.Add(0)
    foreach ($b in $entries) { $ico.Add($b) }
    for ($i = 0; $i -lt $dibs.Count; $i++) {
        foreach ($b in $dibs[$i]) { $ico.Add($b) }
    }
    [System.IO.File]::WriteAllBytes($path, $ico.ToArray())
    Write-Host "Gerado: $path"
}

$outPath = Join-Path $PSScriptRoot "..\WinForms\app.ico"
Write-Ico -path $outPath -sizes @(16, 32, 48)