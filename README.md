# PartCAD Index

This is a registry of all public PartCAD packages.

Add a reference to other public package by creating a pull request against `devel`.
Add new files or extend the existing ones. Create your own directory if needed.
Every directory needs a `partcad.yaml` of its own, if only an empty one, for the
packages below it to be found.

Before opening one, read [CONTRIBUTING.md](CONTRIBUTING.md): every dependency
here is pinned to an exact commit, every dependency declares the oldest PartCAD
it works with, and a breaking change to a package goes to a new branch rather
than to the one the index tracks. It also says how the index is released:
nothing merges to `main`, which only ever moves by fast-forward from `devel`.

## Syntax

Each `partcad.yaml` file in this repository follows the below syntax.
The part repositories maintained by the same party/owner are expected
to be placed in the same file.

```yaml
dependencies:
    <package-name>:
        desc: <(optional) textual description>
        type: <git|tar|local>
        path: <(local only) relative path>
        url: <(git|tar only) url of the package>
        track: <(git only) the branch the pin follows>
        revision: <(git only) the commit id the package is pinned to>
        relPath: <(git|tar only) relative path within the repository>
        web: <(optional) package or maintainer's url>
        poc: <(optional) maintainer's email>
```

`pc add dep <package-name> <url> --track <branch>`, run in the directory of the
parent package, writes `track:` and the commit that branch is at now. `pc update`,
run in a checkout of this repository, moves every `revision:` to the tip of its
`track:`.

Please, note, `web` and `poc` are used for maintenance of this repository.
They won't be visible to PartCAD users.
The PartCAD users will be provided contact information defined in the package
itself.

## Example

Here is an example of making a reference to an external git repository. It shows how OpenVMP parts and blueprints can be published to PartCAD index.

```yaml
# robotics/multimodal/partcad.yaml
dependencies:
    OpenVMP-custom-parts:
        desc: Custom parts for OpenVMP robots
        type: git
        url: https://github.com/openvmp/openvmp-models.git
        track: main
        revision: 1272968cdf2d2ac0d296f9a53d899bce758fcaa5
        relPath: parts/custom
        web: https://openvmp.com/
        poc: openvmp@proton.me
    OpenVMP-robots:
        desc: OpenVMP robots
        type: git
        url: https://github.com/openvmp/openvmp-models.git
        track: main
        revision: 1272968cdf2d2ac0d296f9a53d899bce758fcaa5
        relPath: robots
        web: https://openvmp.com/
        poc: openvmp@proton.me
```

## Usage

The top level of this repository is a PartCAD package by itself
(with it's own top level `partcad.yaml`).
`pc init` adds it to every package it creates, as `pub`, tracking `main` and
pinned to the commit `main` is at then:

```yaml
dependencies:
    pub:
        type: git
        url: https://github.com/partcad/partcad-index.git
        track: main
        revision: <the commit `main` was at>
```

`main` is the released state of the index. `pc update` moves the pin to where
`main` is now; nothing else does. `pc --devel-index` uses the unreleased `devel`
instead, for trying out what is about to be released.
