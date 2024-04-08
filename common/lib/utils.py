import subprocess


def run(*args, **kwargs):
    # always run with text output for easier error reporting
    kwargs["text"] = True
    output = subprocess.run(*args, **kwargs)
    if output.returncode > 0:
        if output.stderr:
            raise Exception(output.stderr)
        else:
            raise Exception("Error running subprocess")

    return output
