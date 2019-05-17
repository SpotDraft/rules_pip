#!/bin/bash

bazel build //src/bin:compile_pip_requirements.par --incompatible_remove_old_python_version_api=false
bazel build //src/bin:create_pip_repository.par --incompatible_remove_old_python_version_api=false

WORKSPACE=$(bazel info workspace)
cp $WORKSPACE/bazel-bin/src/bin/compile_pip_requirements.par $WORKSPACE/tools/compile_pip_requirements.par
cp $WORKSPACE/bazel-bin/src/bin/create_pip_repository.par $WORKSPACE/tools/create_pip_repository.par
