#!/usr/bin/env bash
# Runs 'pc test' and 'pc render' on each package named in $PACKAGES, one
# package at a time, from the root of the index (where the checkout is //pub).
#
# '--fast-only', as in every recursive run over //pub in PartCAD's own CI: an
# assembly or scene whose package declares 'timeout:' is one its author knows
# to be slow, and a gate is not where to spend that. Render it locally.
#
# Every package runs whatever happened to the ones before it, and both commands
# run whatever the other did, so one red package does not hide the rest. Which
# ones failed is said again at the end, and in the job summary with how long
# each package took, which is what the shard ranges are tuned from.
set -u

if [ -z "${PACKAGES:-}" ]; then
  echo "::error::No packages to test: \$PACKAGES is empty"
  exit 1
fi

summary="${GITHUB_STEP_SUMMARY:-/dev/null}"
{
  echo "| Package | \`pc test\` | \`pc render\` | Seconds |"
  echo "| --- | --- | --- | --- |"
} >>"${summary}"

failed=()
for package in ${PACKAGES}; do
  echo "::group::${package}"
  started=${SECONDS}
  pc --no-ansi --threads-max 4 test --fast-only --package "${package}"
  test_rc=$?
  pc --no-ansi --threads-max 4 render --fast-only --package "${package}"
  render_rc=$?
  seconds=$((SECONDS - started))
  echo "::endgroup::"

  echo "| \`${package}\` | ${test_rc} | ${render_rc} | ${seconds} |" >>"${summary}"
  if [ "${test_rc}" -ne 0 ] || [ "${render_rc}" -ne 0 ]; then
    failed+=("${package}: 'pc test' exited ${test_rc}, 'pc render' exited ${render_rc}")
    echo "::error title=${package}::'pc test' exited ${test_rc}, 'pc render' exited ${render_rc}"
  fi
done

if [ "${#failed[@]}" -ne 0 ]; then
  # Why, from the PartCAD service's own log: the command line prints only the
  # message of an error the service raised, while the service logs it with its
  # traceback. Every record that starts at ERROR or above, with the lines that
  # continue it.
  for log in "${HOME}"/.partcad/workspaces/*/partcad.log; do
    [ -f "${log}" ] || continue
    echo "::group::Errors the PartCAD service logged (${log})"
    awk '/^[0-9]{4}-[0-9]{2}-[0-9]{2} / { keep = ($3 == "ERROR" || $3 == "CRITICAL") } keep' "${log}" |
      cut -c1-500 | tail -n 400
    echo "::endgroup::"
  done
  echo "${#failed[@]} package(s) failed:"
  printf '  %s\n' "${failed[@]}"
  exit 1
fi
