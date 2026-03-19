# Signature Images

These files are embedded into generated PDF invoices on the cover letter page.

## Format Requirements

- **Format:** PNG with transparent background
- **Recommended size:** ~300 × 100 px
- **Color:** Black ink on transparent background works best
- **DPI:** 150–300 dpi

## Expected Files

| Filename | Signatory |
|---|---|
| `signature_claus.png` | Claus Johann Mayer |
| `signature_jorge.png` | Jorge Castellote |
| `signature_jose.png` | Jose Mino |
| `signature_craig.png` | Craig Harwerth |
| `signature_tim.png` | Tim Dunworth |
| `signature_default.png` | Fallback (used when signatory not found) |

## Adding a New Signatory

1. Add their signature image as `signature_{firstname}.png` in this folder.
2. Open `Backend/services/invoice_config.py` and add an entry to `SIGNATURE_FILES`:
   ```python
   SIGNATURE_FILES = {
       ...
       "Full Name Here": "signature_firstname.png",
   }
   ```
3. Rebuild the backend container (`docker-compose build backend`).

## Notes

- Files are read server-side only and never exposed via a public URL.
- If a signatory's file is missing, `signature_default.png` is used as a fallback.
- If `signature_default.png` is also missing, the signature block is rendered as text only.
