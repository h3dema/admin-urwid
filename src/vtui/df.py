
try:
    from .vms import run_cmd
except ImportError:
    from vms import run_cmd


labels = ["Sist. Arq.", "Tam.", "Usado", "Disp.", "Uso%", "Montado em"]
positions = [0, 15, 20, 26, 32, 37, -1]


def df(host: str) -> list[dict]:
    cmd = f"ssh {host} 'df -h'"
    result = run_cmd(cmd)
    lines = [x for x in result.stdout.split("\n") if not any([x.startswith(r) for r in ["/dev/loop", "tmpfs"]])]
    entries = list()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        if len(lines[i]) == 0 or not lines[i].startswith("/"):
            continue
        entry = dict()
        for j in range(len(labels)):
            p0, p1 = positions[j:j + 2]
            if p1 == -1:
                p1 = len(lines[i]) + 1
            entry[labels[j]] = lines[i][p0:p1].strip()
        entries.append(entry)
    return entries


if __name__ == "__main__":
    _ = [print(r) for r in df("foice")]
