#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools

class libjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    version = "9b"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    license = "https://sourceforge.net/projects/libjpeg"
    exports = "CMakeLists.txt"
    url="http://github.com/ZaMaZaN4iK/conan-libjpeg"

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        #file name examples:  linux jpegsrc.v9b.tar.gz,  windows jpegsr9b.zip 
        download_url_base = "http://ijg.org/files/"
        archive_prefix = "jpegsr" if self.settings.os == "Windows" else "jpegsrc.v"
        archive_ext = ".zip" if self.settings.os == "Windows" else ".tar.gz"
        download_url =  download_url_base + archive_prefix + self.version + archive_ext
        self.output.info("trying download of url: " + download_url)
        tools.get(download_url)
        os.rename("jpeg-" + self.version, "sources")
        os.rename("CMakeLists.txt", os.path.join("sources", "CMakeLists.txt"))

    def build(self):
        if self.settings.os != "Windows":
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            confArgs = []
            if self.options.shared:
                confArgs.append("--enable-shared=yes --enable-static=no")
            else:
                confArgs.append("--enable-shared=no --enable-static=yes")

            env_build.configure("sources", args=confArgs, build=False, host=False, target=False)
            env_build.make()
        else:
            with tools.chdir("sources"):
                os.rename("jconfig.vc", "jconfig.h")
            cmake = CMake(self)
            cmake.configure(source_dir="sources")
            cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="sources")

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            self.copy(pattern="libjpeg.lib", dst="lib", src="Release", keep_path=False)
        else:
            self.copy(pattern="*.so", dst="lib", src="libs", keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="libs", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['libjpegd']
            else:
                self.cpp_info.libs = ['libjpeg']
        else:
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['jpeg']
            else:
                self.cpp_info.libs = ['jpeg']
