#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class libjpegConan(ConanFile):
    name = "libjpeg"
    version = "9b"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "http://github.com/bincrafters/conan-libjpeg"
    license = "BSD"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    source_subfolder = "source_subfolder"
    install = "libjpeg-install"

    def configure(self):
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.build_requires("mingw_installer/1.0@conan/stable")
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def source(self):
        # file name examples:  linux jpegsrc.v9b.tar.gz,  windows jpegsr9b.zip
        if self.settings.os == "Windows":
            tools.get("http://ijg.org/files/jpegsr%s.zip" % self.version)
        else:
            tools.get("http://ijg.org/files/jpegsrc.v%s.tar.gz" % self.version)
        os.rename("jpeg-" + self.version, self.source_subfolder)

    def build_vs(self):
        with tools.chdir(self.source_subfolder):
            tools.replace_in_file("makefile.vc", "!include <win32.mak>", "")
            vcvars_command = tools.vcvars_command(self.settings)
            self.run('%s && nmake -f makefile.vc setup-v10' % vcvars_command)
            # sometimes upgrading from 2010 to 2012 project fails with non-error exit code
            try:
                self.run('%s && devenv jpeg.sln /upgrade' % (vcvars_command, cmd))
            except:
                pass
            # run build
            cmd = tools.build_sln_command(self.settings, "jpeg.sln", upgrade_project=False, build_type='Release', arch="x86").\
                    replace('Platform="x86"', 'Platform="Win32"')
            self.run('%s && %s' % (vcvars_command, cmd))

    def build_configure(self):
        # works for unix and mingw environments
        env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os == 'Windows')
        env_build.fpic = True
        config_args = []
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])
        prefix = os.path.abspath(self.install)
        if self.settings.os == 'Windows':
            prefix = tools.unix_path(prefix)
        config_args.append("--prefix=%s" % prefix)

        # mingw-specific
        if self.settings.os == 'Windows':
            if self.settings.arch == "x86_64":
                config_args.append('--build=x86_64-w64-mingw32')
                config_args.append('--host=x86_64-w64-mingw32')
            if self.settings.arch == "x86":
                config_args.append('--build=i686-w64-mingw32')
                config_args.append('--host=i686-w64-mingw32')

        env_build.configure(configure_dir=self.source_subfolder, args=config_args)
        env_build.make()
        env_build.make(args=["install"])

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy("README", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", dst="include", src=self.source_subfolder, keep_path=True)
            self.copy(pattern="*.lib", dst="lib", src=self.source_subfolder, keep_path=False)
        else:
            self.copy("*.h", dst="include", src=os.path.join(self.install, "include"), keep_path=True)
            self.copy(pattern="*.so*", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)
            self.copy(pattern="*.dylib*", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)
            self.copy(pattern="*.dll", dst="bin", src=os.path.join(self.install, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['jpeg']
