#!/usr/bin/fontforge -script

import sys
from pathlib import Path
import os.path
import json
import fontforge

IMPORT_OPTIONS = ('removeoverlap', 'correctdir')

try:
    unicode
except NameError:
    unicode = str

def loadConfig(filename='font.json'):
    with open(filename) as f:
        return json.load(f)

def setProperties(font, config):
    props = config['props']
    lang = props.pop('lang', 'English (En)')
    family = props.pop('family', None)
    style = props.pop('style', 'Regular')
    props['encoding'] = props.get('encoding', 'UnicodeFull')
    if family is not None:
        font.familyname = family
        font.fontname = family + '-' + style
        font.fullname = family + ' ' + style
    for k, v in config['props'].items():
        if hasattr(font, k):
            if isinstance(v, list):
                v = tuple(v)
            setattr(font, k, v)
        else:
            font.appendSFNTName(lang, k, v)
    for t in config.get('sfnt_names', []):
        font.appendSFNTName(str(t[0]), str(t[1]), unicode(t[2]))

def addGlyphs(font, config):
    for k, v in config['glyphs'].items():
        # print(int('0x41',0))
        # print(ord(k))
        g = font.createMappedChar('U+'+ k)
        
        # Get outlines
        src = '%s.svg' % k
        if not isinstance(v, dict):
            v = {'src': v or src}
        src = '%s%s%s' % (config.get('input', '.'), os.path.sep, v.pop('src', src))
        g.importOutlines(src, IMPORT_OPTIONS)
        g.removeOverlap()
        # Copy attributes
        for k2, v2 in v.items():
            if hasattr(g, k2):
                if isinstance(v2, list):
                    v2 = tuple(v2)
                setattr(g, k2, v2)

extension = ['.ttf', '.woff']

def svg2ttf(config_file, load_path, save_path, name):
    config = loadConfig(config_file)
    print(load_path,save_path,name)

    os.chdir(load_path)
    font = fontforge.font()
    setProperties(font, config)
    addGlyphs(font, config)
    
    Path(save_path).mkdir(parents=True, exist_ok=True)
    os.chdir(save_path)
    for ex in extension:
        outfile = name + ex
        sys.stderr.write('Generating %s...\n' % outfile)
        font.generate(outfile)
    
    return os.path.join(save_path, name+extension[0]),os.path.join(save_path, name+extension[1]) 

if __name__ == '__main__':
    if len(sys.argv) > 1:
        svg2ttf(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    else:
        sys.stderr.write("\nUsage: %s something.json\n" % sys.argv[0] )

# vim: set filetype=python:
