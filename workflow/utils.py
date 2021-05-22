import json
import os
import subprocess
import threading

import channels.layers
from asgiref.sync import async_to_sync
from django.core.serializers.json import DjangoJSONEncoder


def make_dir(dir: str):
    """A helper-function to create a directroy, if it does not exist.

    Args:
        dir (str): Path to the directroy.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def find_file(directory: str, search_file: str) -> str:
    """Finds relative path of file in given directory and its subdirectories.

    Args:
        directory (str): Directory to search in.
        search_file (str): File to search in directory.

    Returns:
        str:  Path to file.
    """

    paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(search_file.lower()):
                paths.append(os.path.join(root, file))

    if not paths:
        return ""

    paths = [ele for ele in paths if ".test" not in ele]
    shortest_path = min(paths, key=len)
    relative_path = shortest_path.replace(directory, "").strip("/")

    return relative_path


class CommandRunner(object):
    """
    Wrapper to use subprocess to run a command.
    This is shamelessly stolen from the VanessaSaurus. Greetings if you reading this :)
    https://github.com/snakemake/snakeface/blob/a13c6d8c63ab1563375d30fd960a28fb05bba57c/snakeface/apps/main/utils.py#L94
    https://vsoch.github.io/
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.error = []
        self.output = []
        self.retval = None

    def reader(self, stream, context):
        """Get output and error lines and save to command runner."""
        # Make sure we save to the correct field
        lines = self.error
        if context == "stdout":
            lines = self.output

        while True:
            s = stream.readline()
            if not s:
                break
            lines.append(s.decode("utf-8"))
        stream.close()

    def run_command(
        self,
        cmd,
        env=None,
        cancel_func=None,
        cancel_func_kwargs=None,
        shell=False,
        **kwargs
    ):
        self.reset()
        cancel_func_kwargs = cancel_func_kwargs or {}

        # If we need to update the environment
        # **IMPORTANT: this will include envars from host. Absolutely cannot
        # be any secrets (they should be defined in the app settings file)
        envars = os.environ.copy()
        if env:
            envars.update(env)

        p = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=envars,
            **kwargs
        )

        # Create threads for error and output
        t1 = threading.Thread(target=self.reader, args=(p.stdout, "stdout"))
        t1.start()
        t2 = threading.Thread(target=self.reader, args=(p.stderr, "stderr"))
        t2.start()

        # Continue running unless cancel function is called
        counter = 0
        while True:

            # Check on process for finished or cancelled
            if p.poll() is not None:
                print("Return value found, stopping.")
                break

            # Check the cancel function every 100 loops
            elif (
                counter % 10000 == 0
                and cancel_func
                and cancel_func(**cancel_func_kwargs)
            ):
                print("Process is terminated")
                p.terminate()
                break
            counter += 1

        # p.wait()
        t1.join()
        t2.join()
        self.retval = p.returncode
        return self.output


def broadcast_message(msg: list[dict], group_name: str):
    """Helper function to broadcast a message to a group.

    Args:
        msg (list[dict]): Message to broadcast
        group_name (str): Name of the group to broadcast to
    """
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "new_message",
            "content": json.dumps(msg,  sort_keys=True,
                indent=1,
                cls=DjangoJSONEncoder
                ),
        },
    )
