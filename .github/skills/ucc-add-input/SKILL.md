---
name: ucc-add-input
description: Add a new modular input (data input service) to a Splunk UCC add-on's globalConfig.json, including its entity fields, table columns, and the matching Python input/helper code. Use when the user asks to add a new input, create a new modular input, add a new data input, or add a new service to the Inputs page of a UCC-based add-on.
---

# UCC Add-on: Add a New Modular Input

Adds a new input `service` to `globalConfig.json` in a [Splunk UCC](https://splunk.github.io/addonfactory-ucc-generator/) add-on and scaffolds the Python code that backs it, without breaking `ucc-gen build`.

## When to Use

- User asks to "add a new input", "create a new data input", "add a modular input", or "add an input for X" in a UCC-based add-on (identified by a `globalConfig.json` file at the package root, e.g. `package/globalConfig.json`).
- Not for adding a field to an *existing* input — use the `ucc-add-field` skill for that.
- Not for adding a Configuration-page tab (account/proxy/logging/custom) — use the `ucc-add-config-tab` skill for that.

## Prerequisites

- Locate `globalConfig.json` (usually `<addon>/package/globalConfig.json` if the project came from `ucc-gen init`/`ucc-gen build`, or at the repo root for template projects like [resthandler_template](../../../resources/projects/resthandler_template)).
- Confirm `meta.restRoot` and check `pages.inputs.services` for existing naming conventions (snake_case names are typical, e.g. `example_input`).
- This repo already provides JSON Schema validation and IntelliSense for `globalConfig.json` (see [package.json](../../../package.json)) plus snippets in [snippets/globalConfig.json](../../../snippets/globalConfig.json) — prefer using known-good structures over inventing new JSON shapes.

## Procedure

1. **Gather requirements from the user** if not already clear:
   - Input `name` (unique, snake_case, becomes the stanza name in `inputs.conf`) and display `title`.
   - Which fields it needs (name/interval/index are common defaults for modular inputs) — or hand off to `ucc-add-field` for each field after the service skeleton exists.
   - Whether it needs a custom REST handler, OAuth, or just a plain modular input.

2. **Add the service entry** under `pages.inputs.services` in `globalConfig.json`:
   ```json
   {
       "name": "example_input",
       "title": "Example Input",
       "description": "Collects data for Example Input.",
       "entity": [
           {
               "type": "text",
               "label": "Name",
               "field": "name",
               "required": true,
               "help": "Enter a unique name for this input.",
               "validators": [
                   { "type": "regex", "errorMsg": "Input Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.", "pattern": "^[a-zA-Z]\\w*$" },
                   { "type": "string", "errorMsg": "Length of input name should be between 1 and 100.", "minLength": 1, "maxLength": 100 }
               ]
           },
           { "type": "interval", "field": "interval", "label": "Interval", "required": true },
           { "type": "index", "field": "index", "label": "Index" }
       ],
       "table": {
           "actions": ["edit", "enable", "delete", "clone"],
           "header": [
               { "field": "name", "label": "Name" },
               { "field": "interval", "label": "Interval" },
               { "field": "index", "label": "Index" },
               { "field": "disabled", "label": "Status" }
           ]
       }
   }
   ```
   - If this is the **first** service, `pages.inputs.services` may not exist yet — create the array.
   - If there will be **multiple** services, note that UCC shows a dropdown to pick which input to create; each needs its own `table` if you want the [tabs feature](https://splunk.github.io/addonfactory-ucc-generator/inputs/tabs/) (all services must have `table` for tabs to work — mixing tabbed and non-tabbed services is invalid).
   - Only include `name`/`interval`/`index` fields if they make sense for the input; otherwise ask the user which fields are actually needed (this is often the entry point into the `ucc-add-field` skill).

3. **Decide how the input's Python logic will be implemented** — ask the user if unclear:
   - **Helper module (preferred, safe across rebuilds)**: add `"inputHelperModule": "<module_name>"` to the service. Running `ucc-gen build` creates `<module_name>.py` in `bin/` (if it doesn't already exist) with stub functions. UCC never overwrites this file once created. Scaffold it now if the file doesn't exist:
     ```python
     from splunklib import modularinput as smi


     def validate_input(definition: smi.ValidationDefinition):
         pass


     def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
         pass
     ```
   - **Full custom input script**: if the user needs to fully control the modular input class (not just validation/streaming), tell them to run `ucc-gen build` first to generate the default input script into `output/<addon>/bin/<input_name>.py`, then copy it into `<addon>/package/bin/<input_name>.py` and edit it there — once present in `package/bin`, `ucc-gen` will use that version instead of regenerating it. Do not hand-write this file from scratch; base it on the generated output so the argument parsing stays correct.

4. **Validate the result**: re-open `globalConfig.json` and confirm it still matches the schema (the editor will flag schema errors), and that `pages.inputs.services[].name` values are unique.

5. **Tell the user the next steps**:
   - Run `ucc-gen build` (see the `npm: 0` / relevant build task, or `ucc-gen build --source <addon>/package`) to regenerate `inputs.conf`, `inputs.conf.spec`, and the UI.
   - Use the **Preview globalConfig.json** command in this extension (right-click the file) to visually check the new input form before building.
   - If fields were added with validators, remind them validators are strongly recommended for every field (UCC treats missing validators as a security risk).

## Notes

- Never hand-edit generated output under `output/`; always edit the source `package/globalConfig.json` and `package/bin/*.py`, then rebuild.
- Keep new `field` names consistent between the JSON entity and whatever the Python code reads (`definition.parameters["<field>"]` or the input's stanza settings).
- If the user wants inputs grouped visually, use `groups` in the service definition rather than creating unnecessary duplicate services.
