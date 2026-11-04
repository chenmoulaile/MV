#!/bin/bash
# Recording environment setup (rerunnable)
set -e
S=/home/z/my-project/scripts
W=/home/z/my-project/workspace
SUB=~/.config/sublime-text
mkdir -p $SUB/Installed Packages $SUB/Packages/User /home/z/demo/cp /home/z/demo/ref

# ---- Package Control ----
if [ ! -f ""$SUB/Installed Packages/Package Control.sublime-package"" ] || [ $(stat -c%s ""$SUB/Installed Packages/Package Control.sublime-package"") -lt 100000 ]; then
  $S/pdl.sh "https://packagecontrol.io/Package%20Control.sublime-package" ""$SUB/Installed Packages/Package Control.sublime-package"" 8 | tail -1
fi

# ---- Preferences ----
cat > $SUB/Packages/User/Preferences.sublime-settings << 'EOF'
{
	"font_face": "DejaVu Sans Mono",
	"font_size": 15,
	"update_check": false,
	"hot_exit": false,
	"remember_open_files": false,
	"close_windows_when_empty": false,
	"color_scheme": "Mariana.sublime-color-scheme",
	"line_padding_top": 2,
	"line_padding_bottom": 2,
	"highlight_line": true,
	"index_files": false,
	"preview_on_click": false,
	"show_definitions": false,
	"auto_complete": false,
	"draw_white_space": "none",
	"translate_tabs_to_spaces": false,
	"tab_size": 4
}
EOF

# ---- Plugin settings (pre-seed; PC install will not touch User) ----
cat > "$SUB/Packages/User/Algorithm Competition Assistant.sublime-settings" << 'EOF'
{
	"language": "zh",
	"auto_create_dir": "/home/z/demo/cp",
	"auto_listen": true,
	"companion_auto_listen": true
}
EOF

# ---- demo code file (pre-created in ref dir; the take pastes it manually) ----
cp $W/demo_code.cpp /home/z/demo/ref/crystal.cpp 2>/dev/null || true

# ---- chrome profile ----
mkdir -p /tmp/chromeprof
echo ENV_SETUP_OK
