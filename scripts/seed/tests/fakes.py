import subprocess

import seed_proc


class FakeRun:
    """Stands in for seed_proc.run: the first answer whose argv prefix matches wins; unknown calls succeed with ''."""

    def __init__(self, answers=None):
        self.answers = list(answers or [])
        self.calls = []

    def answer(self, prefix, stdout="", code=0):
        self.answers.append((tuple(prefix), code, stdout))
        return self

    def __call__(self, argv, cwd=None, input=None, ok=(0,)):
        argv = [str(a) for a in argv]
        self.calls.append(argv)
        for prefix, code, stdout in self.answers:
            if argv[:len(prefix)] == [str(p) for p in prefix]:
                if code not in ok:
                    raise seed_proc.SeedError(f"{' '.join(argv)} failed ({code})")
                return subprocess.CompletedProcess(argv, code, stdout, "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    def writes(self):
        """Calls that would change GitHub or a remote."""
        def is_write(a):
            return (a[:2] in (["gh", "repo"], ["gh", "pr"], ["gh", "issue"], ["gh", "label"], ["gh", "workflow"])
                    and len(a) > 2 and a[2] in ("create", "close", "run", "edit")) \
                or (a[:2] == ["gh", "api"] and "-X" in a) or ("push" in a and a[0] == "git")
        return [a for a in self.calls if is_write(a)]
