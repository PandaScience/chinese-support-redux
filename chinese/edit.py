# Copyright © 2012 Roland Sieker <ospalh@gmail.com>
# Copyright © 2012-2013 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright © 2017-2019 Joseph Lorimer <joseph@lorimer.me>
#
# This file is part of Chinese Support Redux.
#
# Chinese Support Redux is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Chinese Support Redux is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Chinese Support Redux.  If not, see <https://www.gnu.org/licenses/>.

import re
import json

import anki.buildinfo
from aqt import mw, gui_hooks
from aqt.theme import theme_manager
from aqt.editor import Editor
from aqt.utils import showWarning

from .behavior import update_fields
from .main import config


def webviewDidInit(web_content, context):
    if isinstance(context, Editor):            
        web_content.head += """<script>
        function chineseSupport_activateButton() {
            jQuery('#chineseSupport').addClass('active');
        }
        function chineseSupport_deactivateButton() {
            jQuery('#chineseSupport').removeClass('active');
        }
        </script>
        """

class EditManager:
    def __init__(self):
        gui_hooks.editor_did_init_buttons.append(self.setupButton)
        gui_hooks.editor_did_load_note.append(self.updateButton)
        gui_hooks.editor_did_unfocus_field.append(self.onFocusLost)
        gui_hooks.webview_will_set_content.append(webviewDidInit)
        self.editors = []

    def setupButton(self, buttons, editor):
        self.editors.append(editor)

        # setting toggleable=False because this is currently broken in Anki 2.1.49.
        # We implement our own toggleing mechanism here.
        button = editor.addButton(
            icon=None,
            func=self.onToggle,
            cmd='chineseSupport',
            tip='Chinese Support',
            label='<b>汉字</b>',
            id='chineseSupport',
            toggleable=False)  
        if theme_manager.night_mode:
            btnclass = "btn-night"
        else:
            btnclass = "btn-day"
        # this svelte-9lxpor class is required and was found by looking at the DOM
        # for the other buttons in Anki 2.1.49. No idea how stable this class
        # name is, though.
        button = button.replace('class="', f'class="btn {btnclass} svelte-9lxpor ')

        buttons.append(button)

    def onToggle(self, editor):
        mid = str(editor.note.note_type()['id'])
        enabled = mid in config['enabledModels']

        enabled = not enabled
        if enabled:
            config['enabledModels'].append(mid)
            editor.web.eval("chineseSupport_activateButton()")
        else:
            config['enabledModels'].remove(mid)
            editor.web.eval("chineseSupport_deactivateButton()")

        config.save()

    def updateButton(self, editor):
        enabled = str(editor.note.note_type()['id']) in config['enabledModels']
        if enabled:
            editor.web.eval("chineseSupport_activateButton()")
        else:
            editor.web.eval("chineseSupport_deactivateButton()")

    def _refreshAllEditors(self, focusTo):
        for editor in self.editors:
            editor.loadNote(focusTo=focusTo)

    def onFocusLost(self, _, note, index):
        enabled = str(note.note_type()['id']) in config['enabledModels']
        if not enabled:
            return False

        allFields = mw.col.models.field_names(note.note_type())
        field = allFields[index]

        if update_fields(note, field, allFields):
            focusTo = (index + 1) % len(allFields)
            self._refreshAllEditors(focusTo)

        return False


TONE_CSS_RULE = re.compile("(\\.tone\\d) *\\{([^}]*)\\}")

# append_tone_styling(editor: Editor)
#
# Extracts the CSS rules for tones (i.e. matching TONE_CSS_RULE) from the 
# user defined CSS style sheet. For the sake of simplicity, a tone CSS rule
# must be a one liner.
#
# IMPLEMENTATION NOTES:
#
# The code makes heavily use of internal APIs in Anki that may change in
# future releases. Hopefully, these notes are useful to adapt the code to
# new releases in case of breaking.
#
# The solution is based on Anki 2.1.54.
#
# The Javascript code being evaluated in the QWebView executes the following steps:
#   1. Wait until the UI has been loaded. The code for that is based on [1].
#   2. Loop through all RichTextInput Svelte component instances. They are
#      reachable via "require" because they have been registered before here [2].
#      Unfortunately, this method is only available since 2.1.54.
#   3. Using the RichTextInputAPI [3], we can query the associated CustomStyles
#      instance. A CustomStyles instance has a `styleMap` [4] that contains an 
#      "userBase" entry, which wraps a <style> HTML element. This style element's
#      intended function is to apply color, font family, font size, etc. [5,6].
#      It is the perfect place to add our own CSS tone rules.
#
# [1] https://github.com/ankitects/anki/blob/2.1.54/qt/aqt/editor.py#L184
# [2] https://github.com/ankitects/anki/blob/2.1.54/ts/editor/rich-text-input/RichTextInput.svelte#L40
# [3] https://github.com/ankitects/anki/blob/2.1.54/ts/editor/rich-text-input/RichTextInput.svelte#L21
# [4] https://github.com/ankitects/anki/blob/2.1.54/ts/editor/rich-text-input/CustomStyles.svelte#L37
# [5] https://github.com/ankitects/anki/blob/2.1.54/ts/editor/rich-text-input/RichTextStyles.svelte#L17
# [6] https://github.com/ankitects/anki/blob/2.1.54/ts/editor/rich-text-input/RichTextStyles.svelte#L33

def append_tone_styling_anki2_1_54(editor: Editor):
    rules = []
    for line in editor.note.note_type()['css'].split('\n'):
        if '.tone' in line:
            m = TONE_CSS_RULE.search(line)
            if m:
                rules.append(line)
            else:
                showWarning("WARN: could not parse CSS tone rule. "
                            "Currently, tone CSS rules need to be one liners.")

    js = f"var CSSRULES = {json.dumps(rules)};"
    js += """
    require("anki/ui").loaded.then(() => 
      require("anki/RichTextInput").instances.forEach(inst =>
        inst.customStyles.then(styles => {
          var sheet = styles.styleMap.get("userBase").element.sheet;
          CSSRULES.forEach(rule =>
            sheet.insertRule(rule)
          );
        })
      )
    );
    """
    editor.web.eval(js)

def append_tone_styling_anki2_1_49(editor):
    rules = []
    for line in editor.note.note_type()['css'].split('\n'):
        if line.startswith('.tone'):
            m = TONE_CSS_RULE.search(line)
            if m:
                rules.append((m.group(1), m.group(2)))
            else:
                showWarning("WARN: could not parse CSS tone rule. "
                            "Currently, tone CSS rules need to be one liners.")

    inner_js = ""
    for rulename, ruledef in rules:
        for part in ruledef.split(';'):
            if ':' in part:
                [property, value] = part.split(':', 1)
                inner_js += f"jQuery('{rulename.strip()}', this.shadowRoot).css('{property.strip()}', '{value.strip()}');\n"
    js = "jQuery('div.field').each(function () {\n%s})" % inner_js

    editor.web.eval(js)


__version = [int(x) for x in anki.buildinfo.version.split('.')]
if __version < [2,1,50]:
    append_tone_styling = append_tone_styling_anki2_1_49
elif __version >= [2,1,54]:
    append_tone_styling = append_tone_styling_anki2_1_54
else:
    showWarning("Chinese tone styling has not been implemented for your current Anki version. "
                "Supported versions are Anki 2.1.49 as well as 2.1.54 and later.")
    def append_tone_styling(editor):
        pass
