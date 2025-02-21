# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/application/licdata_artifact_app.py

This script defines the LicdataArtifactApp class.

Copyright (C) 2024-today acmsl/licdata-artifact-application

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
from dbus_next import BusType
from pythoneda.shared import Event
from pythoneda.shared.application import enable, PythonEDA
from org.acmsl.artifact.licdata.domain import LicdataArtifact
from org.acmsl.artifact.licdata.infrastructure.cli import (
    RequestDockerImageCli,
    RequestDockerImagePushedCli,
)
from org.acmsl.artifact.licdata.infrastructure.dbus import (
    LicdataArtifactDbusSignalEmitter,
    LicdataArtifactDbusSignalListener,
)
from pythoneda.shared.artifact.events import (
    DockerImageRequested,
    DockerImagePushRequested,
)
from pythoneda.shared.artifact.events.infrastructure.dbus import (
    DbusDockerImageAvailable,
    DbusDockerImageRequested,
    DbusDockerImagePushed,
    DbusDockerImagePushRequested,
)
from pythoneda.shared.runtime.secrets.events.infrastructure.dbus import (
    DbusCredentialProvided,
    DbusCredentialRequested,
)
from typing import Dict, Type


@enable(
    LicdataArtifactDbusSignalListener,
    events=[
        {
            "event-class": DbusDockerImageRequested,
            "bus-type": BusType.SYSTEM,
        },
        {
            "event-class": DbusDockerImagePushRequested,
            "bus-type": BusType.SYSTEM,
        },
        {
            "event-class": DbusCredentialProvided,
            "bus-type": BusType.SYSTEM,
        },
    ],
)
@enable(
    LicdataArtifactDbusSignalEmitter,
    events=[
        {
            "event-class": DbusCredentialRequested,
            "bus-type": BusType.SYSTEM,
        },
        {
            "event-class": DbusDockerImageAvailable,
            "bus-type": BusType.SYSTEM,
        },
        {
            "event-class": DbusDockerImagePushed,
            "bus-type": BusType.SYSTEM,
        },
    ],
)
# @enable(RequestDockerImagePushedCli)
@enable(RequestDockerImageCli)
class LicdataArtifactApp(PythonEDA):
    """
    Licdata Artifact Application.

    Class name: LicdataArtifactApp

    Responsibilities:
        - Define the Licdata Artifact application.

    Collaborators:
        - None
    """

    def __init__(self, name: str):
        """
        Creates a new LicdataArtifactApp instance.
        :param name: The app name.
        :type name: str
        """
        # licdata_artifact_banner is automatically generated by the Nix flake.
        try:
            from org.acmsl.artifact.licdata.application.licdata_artifact_banner import (
                LicdataArtifactBanner,
            )

            banner = LicdataArtifactBanner()
        except ImportError:
            banner = None

        super().__init__("Licdata Artifact", banner, __file__)

    async def accept_docker_image_requested(self, options: Dict):
        """
        Annotates the Docker image requested event.
        :param options: The Docker image options.
        :type options: Dict
        """
        metadata = await self._build_docker_image_event_metadata(options)
        image_version = options.get("image_version", None)
        variant = options.get("variant", None)
        python_version = options.get("python_version", None)
        azure_base_version = options.get("azure_base_version", None)
        image_name = f"licdata-{variant}-python{python_version}"
        events = await LicdataArtifact.listen_DockerImageRequested(
            DockerImageRequested(
                image_name,
                image_version,
                metadata,
            )
        )

        for event in events:
            await self.emit(event)

    async def accept_docker_image_push_requested(self, options: Dict):
        """
        Annotates the Docker image push requested event.
        :param options: The Docker image push options.
        :type options: Dict
        """
        metadata = await self._build_docker_image_event_metadata(options)
        image_version = options.get("image_version", None)
        docker_registry_url = options.get("docker_registry_url", None)
        variant = options.get("variant", None)
        python_version = options.get("python_version", None)
        azure_base_version = options.get("azure_base_version", None)
        image_name = f"licdata-{variant}-python{python_version}"
        image_url = f"{docker_registry_url}/{image_name}:{image_version}"
        events = await LicdataArtifact.listen_DockerImagePushRequested(
            DockerImagePushRequested(
                image_name,
                image_version,
                image_url,
                docker_registry_url,
                metadata,
            )
        )

        for event in events:
            await self.emit(event)

    async def _build_docker_image_event_metadata(self, options: Dict) -> Dict:
        """
        Annotates the Docker image push requested event.
        :param options: The Docker image push options.
        :type options: Dict
        """
        result = {}
        for key, value in options.items():
            if key not in [
                "image_version",
                "docker_registry_url",
            ]:
                result[key] = value

        return result


if __name__ == "__main__":
    asyncio.run(LicdataArtifactApp.main())
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
