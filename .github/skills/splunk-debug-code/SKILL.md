---
name: splunk-debug-code
description: Insert Splunk add-on remote debugging code (to use with SA-VSCode) into Python files such as modular inputs, REST handlers, and search commands. Use when the user asks for help debugging a TA or add-on, add debug code to the add-on, insert debug code, enable debugging, add a breakpoint, or attach a remote debugger to a Splunk TA or add-on.
---

# Splunk Add-on Debug Code Insertion

Inserts the standard SA-VSCode remote-debugging snippet into Splunk add-on Python code so the developer can attach a remote debugger (e.g. via the SA-VSCode app / winpdb-style debugger) to a running Splunk component.

## When to Use

- User asks to "add debug code", "insert a breakpoint", "enable debugging", or "help me debug this add-on/TA" in a Python file.
- Applies to any Splunk add-on Python entry point: modular inputs (`bin/*.py`), custom REST handlers, custom search commands, alert actions, or other TA scripts run by splunkd.

## Prerequisites

- The `SA-VSCode` app must be installed under `$SPLUNK_HOME/etc/apps/SA-VSCode` and provide a `bin/splunk_debug.py` module with an `enable_debugging(timeout=...)` function. If the user doesn't have this app, tell them it's required before the snippet will work.

## Procedure

1. Identify the target Python file and the exact cursor location (or ask the user). Insert the snippet directly at the current cursor position in the file; do not move it to the top of the file.
2. Insert this exact snippet, unmodified, at the cursor location:

    ```python
    import sys, os
    sys.path.append(os.path.join(os.environ['SPLUNK_HOME'],'etc','apps','SA-VSCode','bin'))
    import splunk_debug as dbg
    dbg.enable_debugging(timeout=25)
    ```

3. Do not alter the snippet's logic (import path, module name, or function call) — only adjust the `timeout` value if the user explicitly requests a different wait time.
4. If the cursor is inside a function or method, place the snippet at that exact insertion point so it runs when that code path executes; if the cursor is elsewhere, insert it at the current caret location without reordering the file.
5. If `import sys` or `import os` already exist elsewhere in the file, do not move or merge imports; keep the snippet as a contiguous block at the insertion point so it is easy to find and remove later.
6. After inserting, remind the user:
   - Tell the user to run the add-on in Splunk (e.g., restart Splunk, disable/enable the modular input, run the search command, etc.) so that the snippet executes and waits for a debugger to attach.
   - Execution will pause at `dbg.enable_debugging(...)` for up to the timeout (seconds) waiting for a debugger to attach.
   - Start the Visual Studio Code debugger and choose the "Splunk Enterprise: Python Debugger" configuration to attach to the running add-on process.  Then, click the "Start" button in VSCode to attach the debugger.
   - Remove the snippet before shipping the add-on to production.

## Notes

- This snippet is specific to the Splunk SA-VSCode debugging workflow — do not substitute generic `pdb`/`breakpoint()` calls unless the user asks for a different debugging method.
- Keep insertions minimal: only add the 4-line block, don't refactor surrounding code.
