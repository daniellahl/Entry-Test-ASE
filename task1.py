import json
import urllib.request
import urllib.error

def check_requirements(filename="requirements.txt"):
    # Try to read the requirements.txt file, if not found, use sample input.
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        sample_input = """requests==2.31.0
                        flask==1.3.0
                        huggingface-cli==0.1.0
                        numpy==1.16.0
                        pyyaml==5.1"""
        lines = [line.strip() for line in sample_input.splitlines()]

    dependencies_checked = len(lines)
    packages_not_on_pypi = 0
    versions_not_on_pypi = 0
    valid_releases = []  # stores tuple (upload_time, name, version, year)

    for line in lines:
        if "==" not in line:
            continue
        
        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()

        # Check package existence on PyPI
        base_url = f"https://pypi.org/pypi/{name}/json"
        try:
            req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                pass
        except urllib.error.HTTPError as e:
            if e.code == 404:
                packages_not_on_pypi += 1
            continue
        except Exception:
            continue

        # Check version existence on PyPI
        version_url = f"https://pypi.org/pypi/{name}/{version}/json"
        try:
            req = urllib.request.Request(version_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                urls = data.get('urls', [])
                if urls:
                    upload_time = urls[0].get('upload_time', '')
                    if upload_time:
                        # Extract the year (Format: YYYY-MM-DDTHH:MM:SS...)
                        year = upload_time[:4]
                        valid_releases.append((upload_time, name, version, year))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                versions_not_on_pypi += 1
        except Exception:
            pass

    # Find the oldest pinned release
    oldest_release_str = "N/A"
    if valid_releases:
        # Sort by upload_time to find the oldest release
        valid_releases.sort(key=lambda x: x[0])
        oldest = valid_releases[0]
        oldest_release_str = f"{oldest[1]}=={oldest[2]} ({oldest[3]})"

    # Output
    print(f"Dependencies checked: {dependencies_checked}")
    print(f"Packages not on PyPI: {packages_not_on_pypi}")
    print(f"Versions not on PyPI: {versions_not_on_pypi}")
    print(f"Oldest pinned release: {oldest_release_str}")

if __name__ == "__main__":
    check_requirements()