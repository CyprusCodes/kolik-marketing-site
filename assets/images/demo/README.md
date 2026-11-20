# Product demonstration media

Images are localised by editing text regions of supplied product captures with the existing bundled Inter fonts. No generative image editing is used for these final assets. Layouts, controls and other source pixels are retained outside the documented edit regions. Example data is fictional.

## Locales and names

English pages use `*-en.png` captures, including the social preview and assistant video/poster. English example people include Alex Morgan, Emma Wilson, Olivia Taylor, James Parker, Daniel Clark and Sophie Turner. Turkish pages keep Turkish sample names. The company is Kolik Demo in both locales. Language-neutral icons are shared.

## Rebuild

Install `scripts/image-tools-requirements.txt`, then run `scripts/prepare_product_media.py --sources <source-capture-directory> --output assets/images/demo`. The source directory is supplied explicitly and is outside the published image tree. The script uses `assets/fonts/inter-*.woff2`; it does not download fonts. Run `scripts/localize_assistant_media.py` with the same arguments and `--ffmpeg <ffmpeg-executable>` for the English video and poster. This video is a text-localised demonstration of the supplied sequence, not an unmodified recording.

`manifest.json` records locale, font, source name, image dimensions and edited rectangles. `scripts/audit_media.py` checks published media references and locale assignments.
