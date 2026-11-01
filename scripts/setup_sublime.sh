#!/bin/bash
# Setup Sublime portable: config + plugin + Package Control + demo helper
set -x
APP=/home/z/my-project/workspace/apps/sublime_text
DATA=$APP/Data
PKG=$DATA/Packages
REPO=/home/z/my-project/workspace/algorithm-competition-assistant

mkdir -p "$DATA/Installed Packages" "$PKG/User" "$DATA/Local" "$HOME/.config/sublime-text"

# plugin as folder package
rm -rf "$PKG/Algorithm Competition Assistant"
cp -r "$REPO" "$PKG/Algorithm Competition Assistant"

# demo helper
cp /home/z/my-project/workspace/demo/demo_helper.py "$PKG/User/"

# preferences
cat > "$PKG/User/Preferences.sublime-settings" <<'EOF'
{
	"color_scheme": "Mariana.sublime-color-scheme",
	"theme": "Default Dark.sublime-theme",
	"font_face": "DejaVu Sans Mono",
	"font_size": 15,
	"translate_tabs_to_spaces": false,
	"detect_indentation": false,
	"hot_exit": false,
	"remember_open_files": false,
	"show_definitions": false,
	"highlight_line": true,
	"line_padding_top": 2,
	"line_padding_bottom": 2,
	"update_check": false,
	"enable_telemetry": false,
	"ignored_packages": ["Vintage"]
}
EOF

# plugin settings: Chinese UI
cat > "$PKG/User/Algorithm Competition Assistant.sublime-settings" <<'EOF'
{
	"language": "zh"
}
EOF

# Package Control
curl -sL --max-time 120 -o "$DATA/Installed Packages/Package Control.sublime-package" "https://packagecontrol.io/Package%20Control.sublime-package"
ls -la "$DATA/Installed Packages/"

echo "=== SUBLIME SETUP DONE"
