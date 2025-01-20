# PartCAD Index

This is a registry of all public PartCAD packages.

Add a reference to other public package by creating a pull request.
Add new files or extend the existing ones. Create your own directory if needed.
New files need to be referenced to by existing files.

## Syntax

Each `partcad.yaml` file in this repository follows the below syntax.
The part repositories maintained by the same party/owner are expected
to be placed in the same file.

```yaml
import:
    <package-name>:
        desc: <(optional) textual description>
        type: <git|tar|local>
        path: <(local only) relative path>
        url: <(git|tar only) url of the package>
        relPath: <(git|tar only) relative path within the repository>
        web: <(optional) package or maintainer's url>
        poc: <(optional) maintainer's email>
```

Please, note, `web` and `poc` are used for maintenance of this repository.
They won't be visible to PartCAD users.
The PartCAD users will be provided contact information defined in the package
itself.

## Example

Here is an example of making a reference to an external git repository. It shows how OpenVMP parts and blueprints can be published to PartCAD index.

```yaml
# robotics/multimodal/partcad.yaml
import:
    OpenVMP-custom-parts:
        desc: Custom parts for OpenVMP robots
        type: git
        url: https://github.com/openvmp/openvmp-models.git
        relPath: parts/custom
        web: https://openvmp.com/
        poc: openvmp@proton.me
    OpenVMP-robots:
        desc: OpenVMP robots
        type: git
        url: https://github.com/openvmp/openvmp-models.git
        relPath: robots
        web: https://openvmp.com/
        poc: openvmp@proton.me
```

## Usage

The top level of this repository is a PartCAD package by itself
(with it's own top level `partcad.yaml`).
It can be referenced in your PartCAD package by adding the below
to your own `partcad.yaml`:

```yaml
import:
    partcad-index:
        type: git
        url: https://github.com/partcad/partcad-index.git
```
