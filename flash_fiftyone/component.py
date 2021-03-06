import logging
import os.path
import shutil
import tempfile
from typing import Dict, List, Optional

import lightning as L
from flash.core.integrations.fiftyone import visualize
from lightning.app.components.python import TracerPythonScript
from lightning.app.storage.path import Path

from flash_fiftyone import tasks
from flash_fiftyone.utilities import generate_script


class FiftyOneBuildConfig(L.BuildConfig):
    def build_commands(self) -> List[str]:
        return [
            "pip install fiftyone",
            "pip uninstall -y opencv-python",
            "pip uninstall -y opencv-python-headless",
            "pip install opencv-python-headless==4.5.5.64",
        ]


class FlashFiftyOne(TracerPythonScript):
    def __init__(self, cache_calls=True, port=5151, *args, **kwargs):
        super().__init__(
            __file__,
            *args,
            cache_calls=cache_calls,
            parallel=True,
            port=port,
            cloud_build_config=FiftyOneBuildConfig(),
            **kwargs,
        )

        self.script_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(self.script_dir, "flash_fiftyone.py")
        self._session = None
        self._task_meta: Optional[tasks.TaskMeta] = None
        self.ready = False

    def run(
        self,
        task: str,
        url: str,
        data_config: Dict,
        checkpoint_path: Path,
    ):
        self._task_meta = getattr(tasks, task)

        generate_script(
            self.script_path,
            "flash_fiftyone.jinja",
            task=task,
            data_module_import_path=self._task_meta.data_module_import_path,
            data_module_class=self._task_meta.data_module_class,
            task_import_path=self._task_meta.task_import_path,
            task_class=self._task_meta.task_class,
            url=url,
            data_config=data_config,
            checkpoint_path=str(checkpoint_path),
        )
        super().run()

    def on_after_run(self, res):
        logging.info("Launching FiftyOne")

        if self._session is not None:
            self._session.close()

        predictions = res["predictions"]

        self._session = visualize(predictions, remote=True, address=self.host)
        self.ready = True

        logging.info(f"Launched at URL: {self._session.url}")

    def on_exit(self):
        if self._session is not None:
            self._session.close()
        shutil.rmtree(self.script_dir)
        self.ready = False
