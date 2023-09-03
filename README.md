# DarkFox

This is a script-processed version of Shadowfox (a UserChrome/UserContent.css based Firefox theme tweak), which automatically adjust contrast by 45.

## Motivation

There are many themes provided for many software (xfwm, gnome, you name it) but I am not satisfied. I want some automatic conversion tool that can make light themes into dark themes, and darken existing greyish themes.

To do this, we can extract color definition in text config files, parse, adjust, serialize and replace original color with it. We can also read image files and adjust contrast or invert color.

In the end, it can be made into a fully-fleged tool which supports modifying many themes.

## Usage

To install, simply type `about:profile` in the Firefox address bar, then enter the "Root Directory", create or enter a folder named "chrome" under it, then copy all contents inside "new" of this repo to it.

To generate the modified version (under "new") on your own, run the following command:

```bash
pip install -r requirements.txt
python increase_contrast.py
```