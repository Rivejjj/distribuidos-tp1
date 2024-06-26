import logging
import subprocess


def revive(node):
    result = subprocess.run(['/revive.sh', node],
                            check=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    logging.warning('Command executed. Result={}\n. Output={}\n. Error={}\n'.
                    format(result.returncode, result.stdout, result.stderr))
