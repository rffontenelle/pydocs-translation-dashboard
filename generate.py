# /// script
# dependencies = [
#     "gitpython",
#     "potodo",
#     "jinja2",
# ]
# ///
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from git import Repo, GitCommandError
from potodo.potodo import scan_path
from jinja2 import Template

completion_progress = []

with TemporaryDirectory() as tmpdir:
    for language in ('es', 'fr', 'id', 'it', 'ja', 'ko', 'pl', 'pt-br', 'tr', 'uk', 'zh-cn', 'zh-tw'):
        clone_path = Path(tmpdir, language)
        for branch in ('3.13', '3.12', '3.11', '3.10', '3.9'):
            try:
                Repo.clone_from(f'git@github.com:python/python-docs-{language}.git', clone_path, depth=1, branch=branch)
            except GitCommandError as e:
                print(f'failed to clone {language} {branch}')
                continue
            try:
                completion = scan_path(clone_path, no_cache=True, hide_reserved=False, api_url='').completion
            except OSError:
                print(f'failed to scan {language} {branch}')
                rmtree(clone_path)
                continue
            else:
                break
        completion_progress.append((language, completion, branch))
        print(completion_progress[-1])

template = Template("""
<html lang="en">
<body>
<table>
<tr><th>language</th><th>completion</th><th>branch</th></tr>
{% for language, completion, branch in completion_progress | sort(attribute=1) | reverse %}
<tr><td>{{ language }}</td><td>{{ completion | round(2) }}</td><td>{{ branch }}</td></tr>
{% endfor %}
</table>
</body>
</html>
""")

output = template.render(completion_progress=completion_progress)

with open("index.html", "w") as file:
    file.write(output)
