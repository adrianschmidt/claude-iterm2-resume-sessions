# claude-iterm2-resume-sessions

A Claude Code plugin that brings every session back after a reboot, each in
the iTerm2 pane it was running in.

When a Mac restarts, iTerm2 restores its windows but the Claude Code sessions
inside them are gone. Reopening a dozen of them by hand, and remembering what
each one was, is tedious. This plugin records each running session and, at
login, types `claude --resume <id>` back into the pane it came from.

macOS and iTerm2 only.

## Install

In Claude Code:

```
/plugin marketplace add adrianschmidt/claude-iterm2-resume-sessions
/plugin install iterm2-resume-sessions@claude-iterm2-resume-sessions
/iterm2-resume-sessions:setup
```

The first two commands enable the hooks that record sessions. The third
installs the login step: a symlink at `~/.local/bin/claude-iterm2-resume-sessions`
and a LaunchAgent that runs it 20 seconds after login.

Sessions already running when you install have no record yet. Register them
once with:

```
claude-iterm2-resume-sessions import-live
```

## Required settings

The original panes only exist at login if iTerm2 restores its windows. Check:

- iTerm2 > Settings > General > Startup > **Window restoration policy** is
  "Use System Window Restoration Setting".
- macOS System Settings > Desktop & Dock > **Close windows when quitting an
  application** is off.
- iTerm2 launches at login, either as a Login Item or because it was running
  when you restarted and macOS reopened it.

Without restored windows everything still comes back, but in tabs of one new
window.

The first login run asks for permission for the script to control iTerm2.
Allow it.

## How it works

- A `SessionStart` hook writes one JSON file per interactive session to
  `~/.claude/resume-registry/`: session id, working directory, transcript
  path, name, and the iTerm2 pane id from `ITERM_SESSION_ID`.
- A `SessionEnd` hook deletes the file on a deliberate exit (`/exit`,
  `/clear`, logout, switching sessions) and otherwise marks how the session
  ended. A reboot ends sessions with reason `other`, so those files survive.
- At login, `claude-iterm2-resume-sessions resume` waits for iTerm2 to have windows,
  then for each surviving record checks that its pane is sitting at a shell
  prompt and types the resume command into it. Panes that are gone or busy
  get a tab in a new window instead.
- Sessions are always resumed by id, so several sessions with the same name
  are fine. Names come from the transcript, so a `/rename` done at any time
  is reflected.

Skipped: headless (`claude -p`) sessions, sessions already running, sessions
whose directory or transcript no longer exists, and records older than 30
days.

## Commands

```
claude-iterm2-resume-sessions list               # every record and why it would or wouldn't resume
claude-iterm2-resume-sessions resume --dry-run   # what a login would do
claude-iterm2-resume-sessions import-live        # register sessions running right now
claude-iterm2-resume-sessions prune              # drop records that can never resume
```

The last login run's output is in
`~/Library/Logs/claude-iterm2-resume-sessions.log`.

## Uninstall

```
/iterm2-resume-sessions:setup uninstall
/plugin uninstall iterm2-resume-sessions@claude-iterm2-resume-sessions
```

The first removes the LaunchAgent and symlink, the second the hooks. Records
in `~/.claude/resume-registry/` are left for you to delete.

## Credit

The idea comes from Will Laves at Anthropic, who described naming every
session and using SessionStart/SessionEnd hooks plus a boot script to get 19
sessions back in 30 seconds.
