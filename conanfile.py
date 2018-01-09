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
    exports_sources = ['Win32.Mak']
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    install = "libjpeg-install"

    def configure(self):
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("msys2_installer/latest@bincrafters/stable")
            if self.settings.compiler != "Visual Studio":
                self.build_requires("mingw_installer/1.0@conan/stable")

    def source(self):
        # file name examples:  linux jpegsrc.v9b.tar.gz,  windows jpegsr9b.zip
        download_url_base = "http://ijg.org/files/"
        archive_prefix = "jpegsr" if self.settings.os == "Windows" else "jpegsrc.v"
        archive_ext = ".zip" if self.settings.os == "Windows" else ".tar.gz"
        download_url = download_url_base + archive_prefix + self.version + archive_ext
        self.output.info("trying download of url: " + download_url)
        tools.get(download_url)
        os.rename("jpeg-" + self.version, "sources")
        if self.settings.compiler == 'Visual Studio':
            shutil.copy('Win32.Mak', os.path.join('sources', 'Win32.Mak'))
            shutil.copy(os.path.join('sources', 'jconfig.vc'), os.path.join('sources', 'jconfig.h'))

    def build_nmake(self):
        with tools.chdir("sources"):
            vcvars_command = tools.vcvars_command(self.settings)
            self.run('%s && nmake -f makefile.vc' % vcvars_command)

    def build_configure(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        config_args = []
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])
        prefix = os.path.abspath(self.install)
        config_args.append("--prefix=%s" % prefix)

        env_build.configure(configure_dir="sources", args=config_args, build=False, host=False, target=False)
        env_build.make()
        env_build.make(args=["install"])

    def build_mingw(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        config_args = []
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])
        prefix = os.path.abspath(self.install)
        config_args.append("--prefix=%s" % prefix)

        # mingw-specific
        if self.settings.arch == "x86_64":
            configure_args.append('--host=x86_64-w64-mingw32')
        if self.settings.arch == "x86":
            configure_args.append('--build=i686-w64-mingw32')
            configure_args.append('--host=i686-w64-mingw32')

        env_build.configure(configure_dir="sources", args=config_args, build=False, host=False, target=False)
        env_build.make()
        env_build.make(args=["install"])

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.build_nmake()
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.build_mingw()
        else:
            self.build_configure()

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="libjpeg.lib", dst="lib", src="sources", keep_path=False)
            for filename in ['jpeglib.h', ' jerror.h', 'jconfig.h', 'jmorecfg.h']:
                self.copy(pattern=filename, dst="include", src="sources")
        else:
            self.copy("*.h", dst="include", src=os.path.join(self.install, "include"), keep_path=True)
            self.copy(pattern="*.so", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ['libjpeg']
        else:
            self.cpp_info.libs = ['jpeg']
