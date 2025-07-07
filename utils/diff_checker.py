import re


def find_line_info(diff_text, target_line):
    lines = diff_text.splitlines()
    old_lineno = new_lineno = 0
    hunk_old_start = hunk_new_start = 0

    for line in lines:
        if line.startswith("@@"):
            match = re.match(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if match:
                hunk_old_start = old_lineno = int(match.group(1))
                hunk_new_start = new_lineno = int(match.group(2))
            continue

        content = line[1:] if line else ""
        if line.startswith(" "):
            if content == target_line:
                return {
                    "line": new_lineno,
                    "start_line": hunk_new_start,
                    "start_side": "RIGHT",
                }
            old_lineno += 1
            new_lineno += 1
        elif line.startswith("-"):
            if content == target_line:
                return {
                    "line": old_lineno,
                    "start_line": hunk_old_start,
                    "start_side": "LEFT",
                    "side": "LEFT",
                }
            old_lineno += 1
        elif line.startswith("+"):
            if content == target_line:
                return {
                    "line": new_lineno,
                    "start_line": hunk_new_start,
                    "start_side": "RIGHT",
                    "side": "RIGHT",
                }
            new_lineno += 1
    return {"line": 1}
