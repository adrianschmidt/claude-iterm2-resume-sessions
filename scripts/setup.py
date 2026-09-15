#!/usr/bin/env python3
"""Install or remove the login-time resume step.

Puts `claude-iterm2-resume-sessions` on the PATH and registers a LaunchAgent that
runs it shortly after login. Safe to re-run.

Usage: setup.py [--uninstall]
"""
import os
import subprocess
import sys

LABEL = "io.github.adrianschmidt.claude-iterm2-resume-sessions"
PLIST = os.path.expanduser("~/Library/LaunchAgents/%s.plist" % LABEL)
LOG = os.path.expanduser("~/Library/Logs/claude-iterm2-resume-sessions.log")
BIN_DIR = os.path.expanduser("~/.local/bin")
COMMAND_LINK = os.path.join(BIN_DIR, "claude-iterm2-resume-sessions")
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-iterm2-resume-sessions")

PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>sleep 20; exec "{command}" resume</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{bin_dir}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>StandardOutPath</key>
    <string>{log}</string>
    <key>StandardErrorPath</key>
    <string>{log}</string>
</dict>
</plist>
"""


def domain():
    return "gui/%d" % os.getuid()


def launchctl(*args):
    return subprocess.run(["launchctl"] + list(args), capture_output=True, text=True)


def is_loaded():
    return launchctl("print", "%s/%s" % (domain(), LABEL)).returncode == 0


def install():
    if sys.platform != "darwin":
        sys.exit("This plugin drives iTerm2 and only works on macOS.")
    os.makedirs(BIN_DIR, exist_ok=True)
    if os.path.lexists(COMMAND_LINK):
        os.remove(COMMAND_LINK)
    os.symlink(SCRIPT, COMMAND_LINK)
    print("linked %s -> %s" % (COMMAND_LINK, SCRIPT))
    if BIN_DIR not in os.environ.get("PATH", "").split(os.pathsep):
        print("note: %s is not on your PATH; add it to run claude-iterm2-resume-sessions by hand" % BIN_DIR)

    os.makedirs(os.path.dirname(PLIST), exist_ok=True)
    with open(PLIST, "w") as f:
        f.write(PLIST_TEMPLATE.format(label=LABEL, command=COMMAND_LINK, bin_dir=BIN_DIR, log=LOG))
    if is_loaded():
        launchctl("bootout", "%s/%s" % (domain(), LABEL))
    result = launchctl("bootstrap", domain(), PLIST)
    if result.returncode != 0:
        sys.exit("launchctl bootstrap failed: %s" % result.stderr.strip())
    print("LaunchAgent %s loaded; log at %s" % (LABEL, LOG))
    print(
        "\nFor sessions to come back in their original panes, iTerm2 must restore\n"
        "its windows at login:\n"
        "  - iTerm2 > Settings > General > Startup > Window restoration policy:\n"
        "    'Use System Window Restoration Setting'\n"
        "  - macOS > System Settings > Desktop & Dock > 'Close windows when quitting\n"
        "    an application' turned OFF\n"
        "  - iTerm2 must launch at login (System Settings > General > Login Items,\n"
        "    or leave it running when you restart so macOS reopens it)\n"
        "\nThe first run asks for permission to control iTerm2; allow it."
    )


def uninstall():
    if is_loaded():
        launchctl("bootout", "%s/%s" % (domain(), LABEL))
        print("LaunchAgent unloaded")
    for path in (PLIST, COMMAND_LINK):
        if os.path.lexists(path):
            os.remove(path)
            print("removed %s" % path)
    print("Session records in ~/.claude/resume-registry were left in place.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv[1:]:
        uninstall()
    else:
        install()
