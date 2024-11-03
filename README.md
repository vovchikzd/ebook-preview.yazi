# ebook-preview.yazi
[Yazi](https://github.com/sxyazi/yazi) plugin to preview ebook files

Supported formats are all those supported by ebook-meta by calibre

## Requirements
- [yazi](https://github.com/sxyazi/yazi)
- [calibre's](https://calibre-ebook.com/) ebook-meta
- [python](https://www.python.org/) and [pillow](https://pypi.org/project/pillow/)

## Install
```shell
git clone https://github.com/vovchikzd/ebook-preview.yazi.git ~/.config/yazi/plugins/ebook-preview.yazi
```
Make sure you have this folder or link to `get-ebook-cover.py` in your `PATH`.

`install.sh` creates symbolic link in `/usr/bin/`

## Usage
Add this to your `yazi.toml`:
```toml
[plugin]
prepend_previewers = [
    { name = "*.epub", run = "ebook-preview" },
    { name = "*.mobi", run = "ebook-preview" },
    { name = "*.fb2", run = "ebook-preview" },
    # and so on for needed formats
]
```
Now go to a book on Yazi, you should see the cover and book information in the preview pane.
