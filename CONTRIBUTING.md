# Contributing to the PartCAD index

This repository is `//pub`: the package every package created by `pc init` depends on, tracking its `main`
branch. Every `pc update` in one of those packages moves it to whatever `main` is then. So a change here is a
change to all of them, and these rules exist so that it is never a surprise.

## The rules

1. **Every pull request merges to `devel`.** Nothing merges to `main`.
2. **`main` only moves by fast-forward from `devel`.** That fast-forward is the release of the index (see
   [Releasing the index](#releasing-the-index)).
3. **The index always pins an exact revision.** Every `git` dependency names a commit id in `revision:`,
   under the `track:` of the branch it follows:

   ```yaml
   dependencies:
     bosl2:
       desc: Parametric BOSL2 shapes, gears, threading and hardware
       type: git
       url: https://github.com/partcad/partcad-bosl2/
       track: main
       revision: fdba57672e2bff7434386fa78428e13062ce4d46
   ```

   A dependency that follows no branch names a tag that is never moved instead. Nothing a consumer gets from
   the index changes until a pull request here changes a `revision:`.
4. **A tracked branch is a promise.** Once a dependency is added to `devel` or `main` tracking a branch, that
   branch is expected to keep working with every PartCAD release since the one this repository's top-level
   `partcad.yaml` required at that moment (its `partcad:`), or since the one the dependency itself required
   then, if that was newer: it cannot keep a support it never had. Moving the pin to the tip of that branch
   must never be what breaks somebody.
5. **Every dependency declares the oldest PartCAD it works with**, as `partcad:` in its own `partcad.yaml`
   (`partcad: ">=0.8.175"`). A PartCAD older than that then refuses the package with `Incompatible PartCAD
   version!` instead of reading it wrong. Packages outside the index should do the same.
6. **Every dependency is pinned to a particular revision**, with `track:` or without it.

PartCAD itself is released the same way (pull requests to `devel`, `main` fast-forwarded from it), and its
contributors follow the matching process for a change to PartCAD that breaks packages here: see [Branches,
releases and breaking changes](https://partcad.readthedocs.io/en/latest/contributing.html#release-process).

## Adding a package

1. Find the most appropriate parent package by browsing the directories, and create a directory of your own
   if none fits. A sub-directory holding a `partcad.yaml` is a package of the directory above it, so every
   directory on the way down from the top level needs one, if only an empty one.
2. Make sure the package's own `partcad.yaml` says `partcad:`, as low as it truthfully can (rule 5). `pc init`
   writes the version that ran it, which is truthful but often higher than it needs to be.
3. Add the dependency, pinned. From the parent package's directory:

   ```shell
   pc add dep <name> <url> --track <branch>
   ```

   writes `track:` and the commit that branch is at now into `revision:`. Add `desc:` (shown to users), and
   `web:`/`poc:` if you want the maintainers of this repository to know who to ask (they are not shown to
   users).
4. Open a pull request against `devel`.

From then on, the branch you named is the one rule 4 is about.

## Updating a package

A change that breaks nobody is pushed to the tracked branch as usual, and reaches the index when its pin is
moved: a pull request against `devel` that changes `revision:` to the new commit. `pc update`, run in a
checkout of this repository, moves every tracked dependency to the tip of its branch at once; to move only
yours, write the commit by hand (`git ls-remote <url> refs/heads/<branch>` says what it is).

What "breaks nobody" means for a tracked branch:

* it still works with every PartCAD release in its window (rule 4). Using a feature of a newer PartCAD on the
  same branch is possible by choosing between two forms in `partcad.yaml`, which is a Jinja2 template:
  `{% if partcad_version_at_least("0.8.200") %}` ([Serving two PartCADs at
  once](https://partcad.readthedocs.io/en/latest/config_package.html#serving-two-partcads));
* everything other packages may refer to is still there and still means the same: every part, assembly,
  sketch, interface, port, parameter and sub-package, with the same name, units, defaults and placement.
  Add new things beside the old ones, and say in `desc:` which old ones are deprecated.

## Making a breaking change

A change is breaking when anything that used the package stops working or comes out different:

* removing or renaming a part, assembly, sketch, interface, port, parameter or sub-package;
* changing what a parameter means, its units or its default, or where a port is, so that what is mated to it
  moves;
* raising `partcad:` above where the branch's window starts: requiring a newer PartCAD.

Such a change does not go to the tracked branch. Instead:

1. **Avoid it if you can.** Add the new beside the old (above); that is not a breaking change.
2. **Make it on a new branch** of your repository, for example `v2`, or `partcad-0.8.210` after the PartCAD it
   requires. Declare that requirement in `partcad:`.
3. **Leave the old branch alone.** Do not force-push, rebase or delete a branch the index tracks or has ever
   tracked: older commits of the index pin its commits, packages pin those commits of the index, and every one
   of them has to stay fetchable.
4. **Wait for PartCAD, if you need a new one.** A package may require a PartCAD only once it is released
   (PartCAD's `main`, which is what PyPI has): the index's `main` serves people who install from there.
5. **Open a pull request against `devel`** that switches the dependency's `track:` to the new branch and
   `revision:` to its commit. In the same pull request, fix every package of the index that uses what changed
   (search this repository and the repositories it pins for the package's path, `//pub/...`), or, if
   consumers need time, add the new branch as a dependency of its own beside the old one (a new package path)
   and retire the old one later. Say in the description what breaks, for whom, and which PartCAD the new
   branch requires.

The new branch's window under rule 4 starts when that pull request is merged.

## Releasing the index

For the maintainers of this repository:

1. **Move the pins**, when that is wanted: `pc update` in a checkout of `devel` moves every tracked dependency to
   the tip of its branch. Review the diff -- each moved pin is new commits of that dependency -- and open it as a
   pull request against `devel`.
2. **Test `devel`** with the PartCAD release the change needs, or the latest one: `pc --devel-index` (or
   `PC_DEVEL_INDEX=true`) makes any command in a package that imports the index use its `devel` instead of its
   `main`, wherever it appears in the dependency tree.
3. **Fast-forward `main`** to the tested commit of `devel`:

   ```shell
   git fetch origin
   git push origin <commit>:refs/heads/main
   ```

   A push without `--force` is refused unless it is a fast-forward, which is the point.

**Raising the index's own floor**, the top-level `partcad:`, is a breaking change of the whole index: a PartCAD
older than it refuses `//pub` at its root, with one message, rather than one package at a time. Do it when that
one message is better than the many -- when most of what the index pins requires a newer PartCAD anyway -- and in
a pull request of its own. Dependencies added from then on start their window (rule 4) at the new floor; those
added earlier keep theirs.
