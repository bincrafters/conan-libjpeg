#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


from bincrafters import build_template_default
import platform
import copy

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=True)

    items = []
    for item in builder.items:
        new_build_requires = copy.copy(item.build_requires)
        # add msys2 and mingw as a build requirement for mingw builds
        if platform.system() == "Windows" and item.settings["compiler"] == "gcc":
            new_build_requires["*"] = new_build_requires.get("*", []) + \
                ["mingw_installer/1.0@conan/stable",
                 "msys2_installer/latest@bincrafters/stable"]
            items.append([item.settings, item.options, item.env_vars,
                          new_build_requires, item.reference])
        else:
            # or just add build
            items.append(item)
    builder.items = items

    builder.run()
