# Chinese Support Redux

[![Build Status](https://travis-ci.org/luoliyan/chinese-support-redux.svg?branch=master)](https://travis-ci.org/luoliyan/chinese-support-redux) [![Coverage Status](https://coveralls.io/repos/github/luoliyan/chinese-support-redux/badge.svg?branch=master)](https://coveralls.io/github/luoliyan/chinese-support-redux?branch=master)

A rewrite and port of the Chinese Support add-on to Anki 2.1.

## Features

* Automatic field filling
  * Translation (from built-in dictionary; supports English, German and French)
  * Romanisation (supports [Pīnyīn (拼音)](https://en.wikipedia.org/wiki/Pinyin) and Cantonese [Jyutping (粵拼)](https://en.wikipedia.org/wiki/Jyutping))
  * Mandarin Audio (fetched from Google or Baidu)
  * Traditional (繁體字) and simplified (簡體字) characters
  * [Bopomofo (ㄅㄆㄇㄈ)](https://en.wikipedia.org/wiki/Bopomofo), also known as Zhuyin (注音)
* Tone colours (applied to characters, romanisation and Bopomofo)
* Built-in note types (Basic and Advanced)

## Status

The vast majority of features have been successfully ported, and the add-on is in a usable state, albeit with some definite rough edges.

The add-on is still in beta. By this I mean “it works, but I wouldn’t trust it with my children”. Expect occasional issues, and please make a back-up before trying it. I use it myself and haven't experienced data loss, but _your_ mileage may vary.

Please report any issues [here](https://github.com/luoliyan/chinese-support-redux/issues) on GitHub. Feature requests are also welcome.

If you are new to the Chinese Support add-on, the wiki from the previous version is still relevant ([here](https://github.com/ttempe/chinese-support-addon/wiki)).

## Usage

The core feature of the add-on is the automatic field filling. To take advantage of this, you need to have an Anki note type with the appropriate fields (e.g., `Hanzi`, `Meaning`, `Reading`, `Sound`). If you don't already have such a note type, the easiest way to create one is to use the built-in model:

1. Navigate to Tools → Manage Note Types (or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd>)
2. Click `Add`
3. Select `Add: Chinese (basic)`
4. Click `OK`
5. Click `OK` again
6. Click `Close`

Then, to use the field filling features:

1. Add a new note to Anki (press <kbd>a</kbd>)
2. Select `Chinese (basic)` as the note type
3. Enable Chinese Support Redux for this note type (click `汉字`)
4. Enter a word (e.g., 電話) in the `Hanzi` field
5. Press <kbd>Tab</kbd>
6. The remaining fields should then be populated automatically

## History

- **2018.10.12**
  - Improve handling of pinyin (will no longer split)
  - Refactor start-up code
  - Expand and refactor tests
- **2018.10.11**
  - Bundle Google TTS dependencies
  - Improve character selection (courtesy of infernalis)
- **2018.10.10**
  - Refactor TTS code
  - Remove Cantonese TTS (discontinued by Google)
- **2018.10.09**
  - Restore Google TTS (again)
  - Begin seriously starting to wrap tests around this old, buggy code
- **2018.02.17**
  - Fix _Fill Incomplete Notes_ functionality
- **2017.11.14**
  - Fix more issues with automatic field population
  - Move field names into configuration file
- **2017.11.10**
  - Use Anki 2.1 built-in config facilities
- **2017.11.07**
  - Fix issues with automatic field population
- **2017.11.06**
  - Restore Google TTS (for Mandarin and Cantonese)
- **2017.11.05**
  - Initial port to Anki 2.1 (most features working)
  - Restore tone colours in editor
