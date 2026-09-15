---
name: setup
description: Install or remove the login-time step of iterm2-resume-sessions (PATH symlink + LaunchAgent). Use when the user asks to set up, install, enable, disable, or uninstall iterm2-resume-sessions, or asks why sessions are not coming back after a reboot.
---

# iterm2-resume-sessions setup

The plugin's hooks record sessions automatically. Resuming them at login needs
a one-time install step, which this skill performs.

## Install

Run and show the user the output:

```bash
/usr/bin/python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup.py"
```

It links `~/.local/bin/claude-iterm2-resume-sessions` to the plugin's script and loads
a LaunchAgent that runs it 20 seconds after login. The script's final lines list
the iTerm2 and macOS settings that must be on for windows to be restored;
repeat them to the user, since without restored windows every session falls
back to a tab in a new window.

## Uninstall

If the user asked to remove or disable it:

```bash
/usr/bin/python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup.py" --uninstall
```

Tell them the hooks keep recording sessions until the plugin itself is
uninstalled with `/plugin`.

## Troubleshooting

- `claude-iterm2-resume-sessions list` shows every recorded session and why it would
  or would not be resumed.
- `claude-iterm2-resume-sessions resume --dry-run` shows what a login would do,
  including which sessions have a live pane to return to.
- `~/Library/Logs/claude-iterm2-resume-sessions.log` holds the output of the
  last login run.
- Sessions started before the plugin was enabled have no record; run
  `claude-iterm2-resume-sessions import-live` once to register the ones running now.
